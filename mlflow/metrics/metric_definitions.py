import functools
import logging
import os

import numpy as np

from mlflow.metrics.base import MetricValue

_logger = logging.getLogger(__name__)


def standard_aggregations(scores):
    return {
        "mean": np.mean(scores),
        "variance": np.var(scores),
        "p90": np.percentile(scores, 90),
    }


def _validate_text_data(data, metric_name, column_name):
    """Validates that the data is text and is non-empty"""
    if len(data) == 0:
        return False

    for row, line in enumerate(data):
        if not isinstance(line, str):
            _logger.warning(
                f"Cannot calculate {metric_name} for non-string inputs. "
                + f"Non-string found for {column_name} on row {row}. skipping metric logging."
            )
            return False

    return True


# because single entry tuples get unpacked, put them back into a tuple if the entry is a string
def _validate_and_fix_text_tuple_data(data, metric_name, column_name):
    """Validates that the data is a list of a tuple of strings and is non-empty"""
    if data is None or len(data) == 0:
        return False

    for row, tup in enumerate(data):
        if not isinstance(tup, tuple) or not all(isinstance(val, str) for val in tup):
            if isinstance(tup, str):
                data[row] = (tup,)
                tup = data[row]
            else:
                _logger.warning(
                    f"Cannot calculate {metric_name} for non-tuple[str] inputs."
                    f"Row {row} of column {column_name} has a non-tuple[str] value of:"
                    f"{tup}. Skipping metric logging."
                )
                return False

    return True


def _token_count_eval_fn(predictions, targets, metrics):
    import tiktoken

    # ref: https://github.com/openai/tiktoken/issues/75
    os.environ["TIKTOKEN_CACHE_DIR"] = ""
    encoding = tiktoken.get_encoding("cl100k_base")

    num_tokens = []
    for prediction in predictions:
        if isinstance(prediction, str):
            num_tokens.append(len(encoding.encode(prediction)))
        else:
            num_tokens.append(None)

    return MetricValue(
        scores=num_tokens,
    )


@functools.lru_cache(maxsize=8)
def _cached_evaluate_load(path, module_type=None):
    import evaluate

    return evaluate.load(path, module_type=module_type)


def _toxicity_eval_fn(predictions, targets, metrics):
    if not _validate_text_data(predictions, "toxicity", "predictions"):
        return
    try:
        toxicity = _cached_evaluate_load("toxicity", module_type="measurement")
    except Exception as e:
        _logger.warning(
            f"Failed to load 'toxicity' metric (error: {e!r}), skipping metric logging."
        )
        return

    scores = toxicity.compute(predictions=predictions)["toxicity"]
    toxicity_ratio = toxicity.compute(predictions=predictions, aggregation="ratio")[
        "toxicity_ratio"
    ]
    return MetricValue(
        scores=scores,
        aggregate_results={
            **standard_aggregations(scores),
            "ratio": toxicity_ratio,
        },
    )


def _perplexity_eval_fn(predictions, targets, metrics):
    if not _validate_text_data(predictions, "perplexity", "predictions"):
        return

    try:
        perplexity = _cached_evaluate_load("perplexity", module_type="metric")
    except Exception as e:
        _logger.warning(
            f"Failed to load 'perplexity' metric (error: {e!r}), skipping metric logging."
        )
        return

    scores = perplexity.compute(predictions=predictions, model_id="gpt2")["perplexities"]
    return MetricValue(
        scores=scores,
        aggregate_results=standard_aggregations(scores),
    )


def _flesch_kincaid_eval_fn(predictions, targets, metrics):
    if not _validate_text_data(predictions, "flesch_kincaid", "predictions"):
        return

    try:
        import textstat
    except ImportError:
        _logger.warning("Failed to load flesch kincaid metric, skipping metric logging.")
        return

    scores = [textstat.flesch_kincaid_grade(prediction) for prediction in predictions]
    return MetricValue(
        scores=scores,
        aggregate_results=standard_aggregations(scores),
    )


def _ari_eval_fn(predictions, targets, metrics):
    if not _validate_text_data(predictions, "ari", "predictions"):
        return

    try:
        import textstat
    except ImportError:
        _logger.warning(
            "Failed to load automated readability index metric, skipping metric logging."
        )
        return

    scores = [textstat.automated_readability_index(prediction) for prediction in predictions]
    return MetricValue(
        scores=scores,
        aggregate_results=standard_aggregations(scores),
    )


def _accuracy_eval_fn(predictions, targets, metrics, sample_weight=None):
    if targets is not None and len(targets) != 0:
        from sklearn.metrics import accuracy_score

        acc = accuracy_score(y_true=targets, y_pred=predictions, sample_weight=sample_weight)
        return MetricValue(aggregate_results={"exact_match": acc})


def _rouge1_eval_fn(predictions, targets, metrics):
    if targets is not None and len(targets) != 0:
        if not _validate_text_data(targets, "rouge1", "targets") or not _validate_text_data(
            predictions, "rouge1", "predictions"
        ):
            return

        try:
            rouge = _cached_evaluate_load("rouge")
        except Exception as e:
            _logger.warning(
                f"Failed to load 'rouge' metric (error: {e!r}), skipping metric logging."
            )
            return

        scores = rouge.compute(
            predictions=predictions,
            references=targets,
            rouge_types=["rouge1"],
            use_aggregator=False,
        )["rouge1"]
        return MetricValue(
            scores=scores,
            aggregate_results=standard_aggregations(scores),
        )


def _rouge2_eval_fn(predictions, targets, metrics):
    if targets is not None and len(targets) != 0:
        if not _validate_text_data(targets, "rouge2", "targets") or not _validate_text_data(
            predictions, "rouge2", "predictions"
        ):
            return

        try:
            rouge = _cached_evaluate_load("rouge")
        except Exception as e:
            _logger.warning(
                f"Failed to load 'rouge' metric (error: {e!r}), skipping metric logging."
            )
            return

        scores = rouge.compute(
            predictions=predictions,
            references=targets,
            rouge_types=["rouge2"],
            use_aggregator=False,
        )["rouge2"]
        return MetricValue(
            scores=scores,
            aggregate_results=standard_aggregations(scores),
        )


def _rougeL_eval_fn(predictions, targets, metrics):
    if targets is not None and len(targets) != 0:
        if not _validate_text_data(targets, "rougeL", "targets") or not _validate_text_data(
            predictions, "rougeL", "predictions"
        ):
            return

        try:
            rouge = _cached_evaluate_load("rouge")
        except Exception as e:
            _logger.warning(
                f"Failed to load 'rouge' metric (error: {e!r}), skipping metric logging."
            )
            return

        scores = rouge.compute(
            predictions=predictions,
            references=targets,
            rouge_types=["rougeL"],
            use_aggregator=False,
        )["rougeL"]
        return MetricValue(
            scores=scores,
            aggregate_results=standard_aggregations(scores),
        )


def _rougeLsum_eval_fn(predictions, targets, metrics):
    if targets is not None and len(targets) != 0:
        if not _validate_text_data(targets, "rougeLsum", "targets") or not _validate_text_data(
            predictions, "rougeLsum", "predictions"
        ):
            return

        try:
            rouge = _cached_evaluate_load("rouge")
        except Exception as e:
            _logger.warning(
                f"Failed to load 'rouge' metric (error: {e!r}), skipping metric logging."
            )
            return

        scores = rouge.compute(
            predictions=predictions,
            references=targets,
            rouge_types=["rougeLsum"],
            use_aggregator=False,
        )["rougeLsum"]
        return MetricValue(
            scores=scores,
            aggregate_results=standard_aggregations(scores),
        )


def _precision_at_k_eval_fn(predictions, targets, k, metrics, sample_weight=None):
    assert targets is not None
    assert len(targets) != 0
    import pandas as pd

    if targets is not None and len(targets) != 0:
        assert isinstance(predictions, pd.Series)
        assert isinstance(targets, pd.Series)
        assert isinstance(k, pd.Series)
        assert (predictions == pd.Series([("doc1", "doc3")] * 3, name="prediction")).all()
        assert (targets == pd.Series([("doc1", "doc2")] * 3, name="target")).all()
        assert (k == pd.Series([2, 2, 2], name="k")).all()
        return MetricValue(scores=[2, 2, 2], aggregate_results=standard_aggregations([2, 2, 2]))


def _mae_eval_fn(predictions, targets, metrics, sample_weight=None):
    if targets is not None and len(targets) != 0:
        from sklearn.metrics import mean_absolute_error

        mae = mean_absolute_error(targets, predictions, sample_weight=sample_weight)
        return MetricValue(aggregate_results={"mean_absolute_error": mae})


def _mse_eval_fn(predictions, targets, metrics, sample_weight=None):
    if targets is not None and len(targets) != 0:
        from sklearn.metrics import mean_squared_error

        mse = mean_squared_error(targets, predictions, sample_weight=sample_weight)
        return MetricValue(aggregate_results={"mean_squared_error": mse})


def _rmse_eval_fn(predictions, targets, metrics, sample_weight=None):
    if targets is not None and len(targets) != 0:
        from sklearn.metrics import mean_squared_error

        rmse = mean_squared_error(targets, predictions, squared=False, sample_weight=sample_weight)
        return MetricValue(aggregate_results={"root_mean_squared_error": rmse})


def _r2_score_eval_fn(predictions, targets, metrics, sample_weight=None):
    if targets is not None and len(targets) != 0:
        from sklearn.metrics import r2_score

        r2 = r2_score(targets, predictions, sample_weight=sample_weight)
        return MetricValue(aggregate_results={"r2_score": r2})


def _max_error_eval_fn(predictions, targets, metrics):
    if targets is not None and len(targets) != 0:
        from sklearn.metrics import max_error

        error = max_error(targets, predictions)
        return MetricValue(aggregate_results={"max_error": error})


def _mape_eval_fn(predictions, targets, metrics, sample_weight=None):
    if targets is not None and len(targets) != 0:
        from sklearn.metrics import mean_absolute_percentage_error

        mape = mean_absolute_percentage_error(targets, predictions, sample_weight=sample_weight)
        return MetricValue(aggregate_results={"mean_absolute_percentage_error": mape})


def _recall_eval_fn(
    predictions, targets, metrics, pos_label=1, average="binary", sample_weight=None
):
    if targets is not None and len(targets) != 0:
        from sklearn.metrics import recall_score

        recall = recall_score(
            targets, predictions, pos_label=pos_label, average=average, sample_weight=sample_weight
        )
        return MetricValue(aggregate_results={"recall_score": recall})


def _precision_eval_fn(
    predictions, targets, metrics, pos_label=1, average="binary", sample_weight=None
):
    if targets is not None and len(targets) != 0:
        from sklearn.metrics import precision_score

        precision = precision_score(
            targets,
            predictions,
            pos_label=pos_label,
            average=average,
            sample_weight=sample_weight,
        )
        return MetricValue(aggregate_results={"precision_score": precision})


def _f1_score_eval_fn(
    predictions, targets, metrics, pos_label=1, average="binary", sample_weight=None
):
    if targets is not None and len(targets) != 0:
        from sklearn.metrics import f1_score

        f1 = f1_score(
            targets,
            predictions,
            pos_label=pos_label,
            average=average,
            sample_weight=sample_weight,
        )
        return MetricValue(aggregate_results={"f1_score": f1})


def _precision_at_k_eval_fn(predictions, targets, k, metrics, sample_weight=None):
    if (
        not _validate_and_fix_text_tuple_data(predictions, "precision_at_k", "predictions")
        or not _validate_and_fix_text_tuple_data(targets, "precision_at_k", "targets")
        or not isinstance(k, int)
        and k > 0
    ):
        return

    scores = []
    for i in range(len(predictions)):
        # only include the top k retrieved chunks
        ground_truth, retrieved = set(targets[i]), predictions[i][:k]
        relevant_doc_count = sum(1 for doc in retrieved if doc in ground_truth)
        if len(retrieved) > 0:
            scores.append(relevant_doc_count / len(retrieved))
        else:
            scores.append(1)

    return MetricValue(scores=scores, aggregate_results=standard_aggregations(scores))
