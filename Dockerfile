FROM python:3.8

WORKDIR /app

ADD . /app

RUN groupadd --gid 10001 mlflow \
  && useradd --uid 10001 --gid mlflow --shell /bin/bash --create-home mlflow

ENV DEBIAN_FRONTEND=noninteractive
RUN curl -sL https://deb.nodesource.com/setup_16.x | bash - && \
    # install prequired modules to support install of mlflow and related components
    apt-get install -y nodejs build-essential openjdk-11-jre-headless \
    # cmake and protobuf-compiler required for onnx install
    cmake protobuf-compiler && \
    # install required python packages
    pip install --no-cache-dir -r requirements/dev-requirements.txt && \
    # install mlflow in editable form
    pip install --no-cache-dir -e .


# Build MLflow UI
RUN curl -sL https://deb.nodesource.com/setup_16.x | bash - && \
    apt-get update && apt-get install -y nodejs && \
    # Build MLflow UI
    npm install --global yarn && \
    cd mlflow/server/js && \
    yarn install && \
    yarn build && \
    # clear cache
    apt-get autoremove -yqq --purge && apt-get clean && rm -rf /var/lib/apt/lists/* && \
    npm cache clean --force && \
    yarn cache clean --all

# The "mlflow" user created above, represented numerically for optimal compatibility with Kubernetes security policies
USER 10001

CMD ["bash"]
