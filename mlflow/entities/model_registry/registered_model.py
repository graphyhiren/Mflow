from mlflow.entities.model_registry._model_registry_entity import _ModelRegistryEntity
from mlflow.protos.model_registry_pb2 import RegisteredModel as ProtoRegisteredModel
from mlflow.utils import experimental


@experimental
class RegisteredModel(_ModelRegistryEntity):
    """
    MLflow entity for Registered Model
    """

    def __init__(self, name):
        """
        Construct a :py:class:`mlflow.entities.model_registry.RegisteredModel`
        :param name: Unique string name.
        """
        super(RegisteredModel, self).__init__()
        self._name = name

    @property
    def name(self):
        """String. Unique name for this registered model within Model Registry."""
        return self._name

    # proto mappers
    @classmethod
    def from_proto(cls, proto):
        # input: mlflow.protos.model_registry_pb2.RegisteredModel
        # returns: RegisteredModel entity
        return cls(proto.name)

    def to_proto(self):
        # returns mlflow.protos.model_registry_pb2.RegisteredModel
        registered_model = ProtoRegisteredModel()
        registered_model.name = self.name
        return registered_model
