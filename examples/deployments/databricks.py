"""
Usage
-----
databricks secrets create-scope <scope>
databricks secrets put-secret <scope> openai-api-key --string-value $OPENAI_API_KEY
python examples/deployments/databricks.py --secret <scope>/openai-api-key
-----
"""
import argparse
import uuid

from mlflow.deployments import get_deploy_client


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--secret", type=str, help="Secret (e.g. secrets/scope/key)")
    return parser.parse_args()


def main():
    args = parse_args()
    client = get_deploy_client("databricks")
    name = f"test-endpoint-{uuid.uuid4()}"
    client.create_endpoint(
        name=name,
        config={
            "served_entities": [
                {
                    "name": "test",
                    "external_model": {
                        "name": "gpt-4",
                        "provider": "openai",
                        "openai_config": {
                            "openai_api_key": "{{" + args.secret + "}}",
                        },
                    },
                }
            ],
            "task": "llm/v1/chat",
            "tags": [
                {
                    "key": "foo",
                    "value": "bar",
                }
            ],
        },
    )
    try:
        client.update_endpoint(
            endpoint=name,
            config={
                "served_entities": [
                    {
                        "name": "test",
                        "external_model": {
                            "name": "gpt-4",
                            "provider": "openai",
                            "openai_config": {
                                "openai_api_key": "{{" + args.secret + "}}",
                            },
                        },
                    }
                ],
            },
        )
        print(client.list_endpoints()["endpoints"][:3])
        print(client.get_endpoint(endpoint=name))
        print(
            client.predict(
                endpoint=name,
                inputs={
                    "messages": [
                        {"role": "user", "content": "Hello!"},
                    ],
                    "max_tokens": 128,
                },
            ),
        )
    finally:
        client.delete_endpoint(endpoint=name)


if __name__ == "__main__":
    main()
