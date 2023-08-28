from mlflow import log_param, log_text
from mlflow.utils.autologging_utils import BatchMetricsLogger

try:
    from tensorflow import keras
except ImportError:
    pass


class MLflowMetricsLoggingCallback(keras.callbacks.Callback):
    """Callback for logging Tensorflow training metrics to MLflow.

    This callback logs training metrics every epoch or every n steps (defined by the user) to
    MLflow.

    Args:
        run_id: string, the MLflow run ID.
        log_every_epoch: bool, If True, log metrics every epoch. If False, log metrics every n
            steps.
        log_every_n_steps: int, log metrics every n steps. If None, log metrics every epoch.

    Examples:
        ```python
        from tensorflow import keras
        import mlflow
        import numpy as np

        # Prepare data for a 2-class classification.
        data = tf.random.uniform([8, 28, 28, 3])
        label = tf.convert_to_tensor(np.random.randint(2, size=8))

        model = keras.Sequential(
            [
                keras.Input([28, 28, 3]),
                keras.layers.Flatten(),
                keras.layers.Dense(2),
            ]
        )

        model.compile(
            loss=keras.losses.SparseCategoricalCrossentropy(from_logits=True),
            optimizer=keras.optimizers.Adam(0.001),
            metrics=[keras.metrics.SparseCategoricalAccuracy()],
        )

        with mlflow.start_run() as run:
            model.fit(
                data,
                label,
                batch_size=4,
                epochs=2,
                callbacks=[MLflowMetricsLoggingCallback(run_id=run.info.run_id)],
            )
        ```
    """

    def __init__(self, run_id, log_every_epoch=True, log_every_n_steps=None):
        self.metrics_logger = BatchMetricsLogger(run_id)
        self.log_every_epoch = log_every_epoch
        self.log_every_n_steps = log_every_n_steps

        if not log_every_epoch and log_every_n_steps is None:
            raise ValueError(
                "`log_every_n_steps` must be specified if `log_every_epoch=False`, received"
                "`log_every_n_steps=False` and `log_every_n_steps=None`."
            )

    def on_train_begin(self, logs=None):
        """Log model architecture and optimizer configuration when training begins."""
        config = self.model.optimizer.get_config()
        for attribute in config:
            log_param("optimizer_" + attribute, config[attribute])

        model_summary = []
        self.model.summary(print_fn=model_summary.append)
        summary = "\n".join(model_summary)
        log_text(summary, artifact_file="model_summary.txt")

    def on_epoch_end(self, epoch, logs=None):
        """Log metrics at the end of each epoch."""
        if not self.log_every_epoch:
            return
        self.metrics_logger.record_metrics(logs, epoch)

    def on_batch_end(self, batch, logs=None):
        """Log metrics at the end of each batch with user specified frequency."""
        if self.log_every_n_steps is None:
            return
        if (batch + 1) % self.log_every_n_steps == 0:
            self.metrics_logger.record_metrics(logs, batch)
