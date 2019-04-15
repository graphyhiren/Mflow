import sqlparse
from sqlparse.sql import Identifier as SqlIdentifier, Token as SqlToken, \
    Comparison as SqlComparison, Statement as SqlStatement
from sqlparse.tokens import Token as SqlTokenType

from mlflow.utils.search_utils.models import Comparison, ComparisonOperator, KeyType
from mlflow.exceptions import MlflowException
from mlflow.protos.databricks_pb2 import INVALID_PARAMETER_VALUE


KEY_TYPE_FROM_IDENTIFIER = {
    "metric": KeyType.METRIC,
    "metrics": KeyType.METRIC,
    "param": KeyType.PARAM,
    "params": KeyType.PARAM,
    "parameter": KeyType.PARAM,
    "tag": KeyType.TAG,
    "tags": KeyType.TAG
}

STRING_VALUE_SQL_TYPES = {SqlTokenType.Literal.String.Single}
NUMERIC_VALUE_SQL_TYPES = {SqlTokenType.Literal.Number.Integer, SqlTokenType.Literal.Number.Float}

INVALID_IDENTIFIER_TPL = (
    "Expected param, metric or tag identifier of format 'metric.<key> <comparator> <value>', "
    "'tag.<key> <comparator> <value>', or 'params.<key> <comparator> <value>' but found '{token}'."
)
INVALID_OPERATOR_TPL = "'{token}' is not a valid operator."


def parse_filter_string(string):
    try:
        parsed = sqlparse.parse(string)
    except Exception:
        raise MlflowException("Error on parsing filter '{}'".format(string),
                              error_code=INVALID_PARAMETER_VALUE)

    try:
        [statement] = parsed
    except ValueError:
        raise MlflowException("Invalid filter '{}'. Must be a single statement.".format(string),
                              error_code=INVALID_PARAMETER_VALUE)

    if not isinstance(statement, SqlStatement):
        raise MlflowException("Invalid filter '{}'. Must be a single statement.".format(string),
                              error_code=INVALID_PARAMETER_VALUE)

    return _parse_statement(statement)


def _parse_statement(statement):
    # check validity
    invalids = list(filter(_invalid_statement_token, statement.tokens))
    if len(invalids) > 0:
        invalid_clauses = ", ".join("'{}'".format(token) for token in invalids)
        raise MlflowException("Invalid clause(s) in filter string: {}".format(invalid_clauses),
                              error_code=INVALID_PARAMETER_VALUE)
    return [_parse_comparison(token)
            for token in statement.tokens if isinstance(token, SqlComparison)]


def _invalid_statement_token(token):
    if isinstance(token, SqlComparison):
        return False
    elif token.is_whitespace:
        return False
    elif token.match(ttype=SqlTokenType.Keyword, values=["AND"]):
        return False
    else:
        return True


def _parse_comparison(comparison):
    """
    Interpret a SQL comparison from  a filter string.

    :param sql_comparison: A sqlparse.sql.Comparison object.

    :return: A Comparison object.
    """

    stripped_comparison = [token for token in comparison.tokens if not token.is_whitespace]

    try:
        [identifier, operator, value] = stripped_comparison
    except ValueError:
        message = "Invalid comparison clause '{}'. Expected 3 tokens but found {}".format(
            comparison.value, len(stripped_comparison))
        raise MlflowException(message, error_code=INVALID_PARAMETER_VALUE)

    try:
        key_type, key = _parse_identifier(identifier)
        operator = _parse_operator(operator)
        value = _parse_value(key_type, value)
        comparison = Comparison(key_type, key, operator, value)
    except ValueError as e:
        raise MlflowException("Invalid comparison clause '{}'. {}".format(comparison.value, e),
                              error_code=INVALID_PARAMETER_VALUE)

    return comparison


def _parse_identifier(token):
    if not isinstance(token, SqlIdentifier):
        raise ValueError(INVALID_IDENTIFIER_TPL.format(token=token.value))

    try:
        key_type_string, key = token.value.split(".", 1)
    except ValueError:
        raise MlflowException(INVALID_IDENTIFIER_TPL.format(token=token.value))

    key_type = _key_type_from_string(_trim_backticks(key_type_string))
    key = _strip_quotes(key)

    return key_type, key


def _key_type_from_string(string):
    try:
        return KEY_TYPE_FROM_IDENTIFIER[string]
    except KeyError:
        message = "Invalid search expression type '{}'. Valid values are {}".format(
            string, set(KEY_TYPE_FROM_IDENTIFIER.keys()))
        raise MlflowException(message, error_code=INVALID_PARAMETER_VALUE)


def _parse_operator(token):
    if not isinstance(token, SqlToken) and token.ttype != SqlTokenType.Operator.Comparison:
        raise ValueError(INVALID_OPERATOR_TPL.format(token=token.value))

    try:
        return ComparisonOperator(token.value)
    except ValueError:
        raise ValueError(INVALID_OPERATOR_TPL.format(token=token.value))


def _parse_value(key_type, token):
    if not isinstance(token, SqlToken):
        raise ValueError("Expected value but found '{}'".format(token.value))

    if key_type == KeyType.METRIC:
        if token.ttype not in NUMERIC_VALUE_SQL_TYPES:
            raise ValueError("Expected a numeric value for metric but found {}".format(token.value))
        return token.value
    elif key_type == KeyType.PARAM or key_type == KeyType.TAG:
        if token.ttype in STRING_VALUE_SQL_TYPES or isinstance(token, SqlIdentifier):
            return _strip_quotes(token.value, expect_quoted_value=True)
        raise ValueError("Expected a quoted string value for {} (e.g. 'my-value') "
                         "but found {} ".format(key_type.value, token.value))
    else:
        raise ValueError("Invalid key type {}".format(key_type))


def _strip_quotes(value, expect_quoted_value=False):
    """
    Remove quotes for input string.
    Values of type strings are expected to have quotes.
    Keys containing special characters are also expected to be enclose in quotes.
    """
    if _is_quoted(value, "'") or _is_quoted(value, '"'):
        return _trim_ends(value)
    elif expect_quoted_value:
        raise MlflowException("Parameter value is either not quoted or unidentified quote "
                              "types used for string value %s. Use either single or double "
                              "quotes." % value, error_code=INVALID_PARAMETER_VALUE)
    else:
        return value


def _trim_backticks(entity_type):
    """Remove backticks from identifier like `param`, if they exist."""
    if _is_quoted(entity_type, "`"):
        return _trim_ends(entity_type)
    return entity_type


def _is_quoted(value, pattern):
    return len(value) >= 2 and value.startswith(pattern) and value.endswith(pattern)


def _trim_ends(string_value):
    return string_value[1:-1]


def search_expression_to_comparison(search_expression):
    """
    Build a Comparison from a search expression.

    Deprecated: Use filter strings instead.
    """

    key_type = _key_type_from_string(search_expression.WhichOneof('expression'))

    if key_type == KeyType.METRIC:
        key = search_expression.metric.key
        metric_type = search_expression.metric.WhichOneof('clause')
        if metric_type == 'float':
            comparator = search_expression.metric.float.comparator
            value = search_expression.metric.float.value
        elif metric_type == 'double':
            comparator = search_expression.metric.double.comparator
            value = search_expression.metric.double.value
        else:
            raise MlflowException(
                "Invalid metric type: '{}', expected float or double".format(metric_type),
                error_code=INVALID_PARAMETER_VALUE)
        return Comparison(KeyType.METRIC, key, _comparison_operator_from_string(comparator), value)

    elif key_type == KeyType.PARAM:
        key = search_expression.parameter.key
        comparator = search_expression.parameter.string.comparator
        value = search_expression.parameter.string.value
        return Comparison(KeyType.PARAM, key, _comparison_operator_from_string(comparator), value)

    else:
        raise MlflowException("Invalid search expression type '{}'".format(key_type),
                              error_code=INVALID_PARAMETER_VALUE)


def _comparison_operator_from_string(string):
    try:
        return ComparisonOperator(string)
    except ValueError:
        raise MlflowException("Invalid comparator '{}'".format(string),
                              error_code=INVALID_PARAMETER_VALUE)
