from mlflow.models.evaluation import (
    evaluate,
    EvaluationResult,
    ModelEvaluator,
    MetricThreshold,
)
from mlflow.models.evaluation.validation import _MetricValidationResult
from mlflow.models.evaluation.evaluator_registry import _model_evaluation_registry
from unittest import mock
import pytest
from mlflow.exceptions import MlflowException

# pylint: disable=unused-import
from tests.models.test_evaluation import (
    multiclass_logistic_regressor_model_uri,
    iris_dataset,
)

message_separator = "\n"


class MockEvaluator(ModelEvaluator):
    def can_evaluate(self, *, model_type, evaluator_config, **kwargs):
        raise RuntimeError()

    def evaluate(self, *, model, model_type, dataset, run_id, evaluator_config, **kwargs):
        raise RuntimeError()


@pytest.fixture
def value_threshold_test_spec(request):
    acc_threshold = MetricThreshold(threshold=0.9, higher_is_better=True)
    acc_validation_result = _MetricValidationResult("accuracy", 0.8, acc_threshold, None)
    acc_validation_result.threshold_failed = True

    f1score_threshold = MetricThreshold(threshold=0.8, higher_is_better=True)
    f1score_validation_result = _MetricValidationResult("f1_score", 0.7, f1score_threshold, None)
    f1score_validation_result.threshold_failed = True

    log_loss_threshold = MetricThreshold(threshold=0.5, higher_is_better=False)
    log_loss_validation_result = _MetricValidationResult("log_loss", 0.3, log_loss_threshold, None)

    l1_loss_threshold = MetricThreshold(threshold=0.3, higher_is_better=False)
    l1_loss_validation_result = _MetricValidationResult(
        "custom_l1_loss", 0.5, l1_loss_threshold, None
    )
    l1_loss_validation_result.threshold_failed = True

    if request.param == "single_metric_not_satisfied_higher_better":
        return ({"accuracy": 0.8}, {"accuracy": acc_threshold}, {"accuracy": acc_validation_result})

    if request.param == "multiple_metrics_not_satisfied_higher_better":
        return (
            {"accuracy": 0.8, "f1_score": 0.7},
            {"accuracy": acc_threshold, "f1_score": f1score_threshold},
            {"accuracy": acc_validation_result, "f1_score": f1score_validation_result},
        )

    if request.param == "single_metric_not_satisfied_lower_better":
        return (
            {"custom_l1_loss": 0.5},
            {"custom_l1_loss": l1_loss_threshold},
            {"custom_l1_loss": l1_loss_validation_result},
        )

    if request.param == "multiple_metrics_not_satisfied_lower_better":
        log_loss_validation_result.candidate_metric_value = 0.8
        log_loss_validation_result.threshold_failed = True
        return (
            {"custom_l1_loss": 0.5, "log_loss": 0.8},
            {"custom_l1_loss": l1_loss_threshold, "log_loss": log_loss_threshold},
            {"custom_l1_loss": l1_loss_validation_result, "log_loss": log_loss_validation_result},
        )

    if request.param == "missing_metric":
        acc_validation_result.missing = True
        return ({}, {"accuracy": acc_threshold}, {"accuracy": acc_validation_result})

    if request.param == "multiple_metrics_not_all_satisfied":
        return (
            {"accuracy": 0.8, "f1_score": 0.7, "log_loss": 0.3},
            {
                "accuracy": acc_threshold,
                "f1_score": f1score_threshold,
                "log_loss": log_loss_threshold,
            },
            {"accuracy": acc_validation_result, "f1_score": f1score_validation_result},
        )

    if request.param == "equality_boundary":
        return (
            {"accuracy": 0.9, "log_loss": 0.5},
            {"accuracy": acc_threshold, "log_loss": log_loss_threshold},
            {},
        )

    if request.param == "single_metric_satisfied_higher_better":
        return ({"accuracy": 0.91}, {"accuracy": acc_threshold}, {})

    if request.param == "single_metric_satisfied_lower_better":
        return ({"log_loss": 0.3}, {"log_loss": log_loss_threshold}, {})

    if request.param == "multiple_metrics_all_satisfied":
        return (
            {"accuracy": 0.9, "f1_score": 0.8, "log_loss": 0.3},
            {
                "accuracy": acc_threshold,
                "f1_score": f1score_threshold,
                "log_loss": log_loss_threshold,
            },
            {},
        )


@pytest.mark.parametrize(
    "value_threshold_test_spec",
    [
        ("single_metric_not_satisfied_higher_better"),
        ("multiple_metrics_not_satisfied_higher_better"),
        ("single_metric_not_satisfied_lower_better"),
        ("missing_metric"),
        ("multiple_metrics_not_satisfied_lower_better"),
        ("multiple_metrics_not_all_satisfied"),
    ],
    indirect=["value_threshold_test_spec"],
)
def test_validation_value_threshold_should_fail(
    multiclass_logistic_regressor_model_uri,
    iris_dataset,
    value_threshold_test_spec,
):
    metrics, validation_thresholds, validation_results = value_threshold_test_spec
    with mock.patch.object(
        _model_evaluation_registry, "_registry", {"test_evaluator1": MockEvaluator}
    ):
        evaluator1_config = {}
        evaluator1_return_value = EvaluationResult(
            metrics=metrics, artifacts={}, baseline_model_metrics=None
        )
        failure_message = message_separator.join(map(str, list(validation_results.values())))
        with mock.patch.object(
            MockEvaluator, "can_evaluate", return_value=True
        ) as _, mock.patch.object(
            MockEvaluator, "evaluate", return_value=evaluator1_return_value
        ) as _:
            with pytest.raises(
                MlflowException,
                match=failure_message,
            ):
                evaluate(
                    multiclass_logistic_regressor_model_uri,
                    data=iris_dataset._constructor_args["data"],
                    model_type="classifier",
                    targets=iris_dataset._constructor_args["targets"],
                    dataset_name=iris_dataset.name,
                    evaluators="test_evaluator1",
                    evaluator_config=evaluator1_config,
                    validation_thresholds=validation_thresholds,
                    baseline_model=None,
                )


@pytest.mark.parametrize(
    "value_threshold_test_spec",
    [
        ("single_metric_satisfied_higher_better"),
        ("single_metric_satisfied_lower_better"),
        ("equality_boundary"),
        ("multiple_metrics_all_satisfied"),
    ],
    indirect=["value_threshold_test_spec"],
)
def test_validation_value_threshold_should_pass(
    multiclass_logistic_regressor_model_uri,
    iris_dataset,
    value_threshold_test_spec,
):
    metrics, validation_thresholds, _ = value_threshold_test_spec
    with mock.patch.object(
        _model_evaluation_registry, "_registry", {"test_evaluator1": MockEvaluator}
    ):
        evaluator1_config = {}
        evaluator1_return_value = EvaluationResult(
            metrics=metrics, artifacts={}, baseline_model_metrics=None
        )
        with mock.patch.object(
            MockEvaluator, "can_evaluate", return_value=True
        ) as _, mock.patch.object(
            MockEvaluator, "evaluate", return_value=evaluator1_return_value
        ) as _:
            evaluate(
                multiclass_logistic_regressor_model_uri,
                data=iris_dataset._constructor_args["data"],
                model_type="classifier",
                targets=iris_dataset._constructor_args["targets"],
                dataset_name=iris_dataset.name,
                evaluators="test_evaluator1",
                evaluator_config=evaluator1_config,
                validation_thresholds=validation_thresholds,
                baseline_model=None,
            )


@pytest.fixture
def min_absolute_change_threshold_test_spec(request):
    acc_threshold = MetricThreshold(min_absolute_change=0.1, higher_is_better=True)
    f1score_threshold = MetricThreshold(min_absolute_change=0.15, higher_is_better=True)
    log_loss_threshold = MetricThreshold(min_absolute_change=-0.1, higher_is_better=False)
    l1_loss_threshold = MetricThreshold(min_absolute_change=-0.15, higher_is_better=False)

    _ = _MetricValidationResult("log_loss", 0.5, log_loss_threshold, 0.6)

    if request.param == "single_metric_not_satisfied_higher_better":
        acc_validation_result = _MetricValidationResult("accuracy", 0.79, acc_threshold, 0.7)
        acc_validation_result.min_absolute_change_failed = True
        return (
            {"accuracy": 0.79},
            {"accuracy": 0.7},
            {"accuracy": acc_threshold},
            {"accuracy": acc_validation_result},
        )

    if request.param == "multiple_metrics_not_satisified_higher_better":
        acc_validation_result = _MetricValidationResult("accuracy", 0.79, acc_threshold, 0.7)
        acc_validation_result.min_absolute_change_failed = True
        f1score_validation_result = _MetricValidationResult("f1_score", 0.8, f1score_threshold, 0.7)
        f1score_validation_result.min_absolute_change_failed = True
        return (
            {"accuracy": 0.79, "f1_score": 0.8},
            {"accuracy": 0.7, "f1_score": 0.7},
            {"accuracy": acc_threshold, "f1_score": f1score_threshold},
            {"accuracy": acc_validation_result, "f1_score": f1score_validation_result},
        )

    if request.param == "single_metric_not_satisfied_lower_better":
        l1_loss_validation_result = _MetricValidationResult(
            "custom_l1_loss", 0.5, l1_loss_threshold, 0.6
        )
        l1_loss_validation_result.min_absolute_change_failed = True
        return (
            {"custom_l1_loss": 0.5},
            {"custom_l1_loss": 0.6},
            {"custom_l1_loss": l1_loss_threshold},
            {"custom_l1_loss": l1_loss_validation_result},
        )

    if request.param == "multiple_metrics_not_satisified_lower_better":
        l1_loss_validation_result = _MetricValidationResult(
            "custom_l1_loss", 0.5, l1_loss_threshold, 0.6
        )
        l1_loss_validation_result.min_absolute_change_failed = True
        log_loss_validation_result = _MetricValidationResult(
            "custom_log_loss", 0.45, log_loss_threshold, 0.3
        )
        log_loss_validation_result.min_absolute_change_failed = True
        return (
            {"custom_l1_loss": 0.5, "custom_log_loss": 0.45},
            {"custom_l1_loss": 0.6, "custom_log_loss": 0.3},
            {"custom_l1_loss": l1_loss_threshold, "custom_log_loss": log_loss_threshold},
            {
                "custom_l1_loss": l1_loss_validation_result,
                "custom_log_loss": log_loss_validation_result,
            },
        )


@pytest.mark.parametrize(
    "min_absolute_change_threshold_test_spec",
    [
        ("single_metric_not_satisfied_higher_better"),
        ("multiple_metrics_not_satisified_higher_better"),
        ("single_metric_not_satisfied_lower_better"),
        ("multiple_metrics_not_satisified_lower_better"),
    ],
    indirect=["min_absolute_change_threshold_test_spec"],
)
def test_validation_model_comparison_absolute_threshold_should_fail(
    multiclass_logistic_regressor_model_uri,
    iris_dataset,
    min_absolute_change_threshold_test_spec,
):
    (
        metrics,
        baseline_model_metrics,
        validation_thresholds,
        validation_results,
    ) = min_absolute_change_threshold_test_spec

    with mock.patch.object(
        _model_evaluation_registry, "_registry", {"test_evaluator1": MockEvaluator}
    ):
        evaluator1_config = {}
        evaluator1_return_value = EvaluationResult(
            metrics=metrics, artifacts={}, baseline_model_metrics=baseline_model_metrics
        )
        failure_message = message_separator.join(map(str, list(validation_results.values())))
        with mock.patch.object(
            MockEvaluator, "can_evaluate", return_value=True
        ) as _, mock.patch.object(
            MockEvaluator, "evaluate", return_value=evaluator1_return_value
        ) as _:
            with pytest.raises(
                MlflowException,
                match=failure_message,
            ):
                evaluate(
                    multiclass_logistic_regressor_model_uri,
                    data=iris_dataset._constructor_args["data"],
                    model_type="classifier",
                    targets=iris_dataset._constructor_args["targets"],
                    dataset_name=iris_dataset.name,
                    evaluators="test_evaluator1",
                    evaluator_config=evaluator1_config,
                    validation_thresholds=validation_thresholds,
                    baseline_model=multiclass_logistic_regressor_model_uri,
                )
