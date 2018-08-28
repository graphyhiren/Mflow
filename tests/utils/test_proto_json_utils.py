from mlflow.entities import Experiment
from mlflow.protos.service_pb2 import Experiment as ProtoExperiment
from mlflow.utils.proto_json_utils import message_to_json, parse_dict

def test_message_to_json():
  json = message_to_json(Experiment(123, "name", "arty").to_proto())
  assert json == (
    '{\n' +
    '  "experiment_id": "123",\n' +
    '  "name": "name",\n' +
    '  "artifact_location": "arty"\n' +
    '}'
  )

def test_parse_dict():
  in_json = {"experiment_id": "123", "name": "name", "unknown": "field"}
  message = ProtoExperiment()
  parse_dict(in_json, message)
  experiment = Experiment.from_proto(message)
  assert experiment.experiment_id == 123
  assert experiment.name == 'name'
  assert experiment.artifact_location == ''
