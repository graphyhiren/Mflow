import os

from sklearn.linear_model import ElasticNet

import mlflow
import mlflow.sklearn


if __name__ == "__main__":
    with mlflow.start_run():
        lr = ElasticNet()
        mlflow.sklearn.log_model(lr, "model")

    for r, ds, fs in os.walk("mlruns"):
        for f in fs:
            print(os.path.join(r, f))
