from typing import Any, Dict, Optional

from mlflow.pyfunc.model import (
    _load_context_model_and_signature,
)
from mlflow.types.llm import ChatMessage, ChatParams, ChatRequest, ChatResponse
from mlflow.utils.annotations import experimental


def _load_pyfunc(model_path: str, model_config: Optional[Dict[str, Any]] = None):
    context, chat_model, signature = _load_context_model_and_signature(model_path, model_config)
    return _ChatModelPyfuncWrapper(chat_model=chat_model, context=context, signature=signature)


@experimental
class _ChatModelPyfuncWrapper:
    """
    Wrapper class that converts dict inputs to pydantic objects accepted by :class:`~ChatModel`.
    """

    def __init__(self, chat_model, context, signature):
        """
        Args:
            chat_model: An instance of a subclass of :class:`~ChatModel`.
            context: A :class:`~PythonModelContext` instance containing artifacts that
                        ``chat_model`` may use when performing inference.
            signature: :class:`~ModelSignature` instance describing model input and output.
        """
        self.chat_model = chat_model
        self.context = context
        self.signature = signature

    def _convert_input(self, model_input):
        # model_input should be correct from signature validation, so just convert it to dict here
        dict_input = {key: value[0] for key, value in model_input.to_dict(orient="list").items()}

        messages = [ChatMessage(**message) for message in dict_input.pop("messages", [])]
        params = ChatParams(**dict_input)

        return messages, params

    def predict(self, model_input: ChatRequest, params: Optional[Dict[str, Any]] = None):
        """
        Args:
            model_input: Model input data in the form of a chat request.
            params: Additional parameters to pass to the model for inference.
                       Unused in this implementation, as the params are handled
                       via ``self._convert_input()``.

        Returns:
            Model predictions in :py:class:`~ChatResponse` format.
        """
        messages, params = self._convert_input(model_input)
        response = self.chat_model.predict(self.context, messages, params)

        if isinstance(response, ChatResponse):
            return response.to_dict()

        # shouldn't happen since there is validation at save time ensuring that
        # the model returns a ChatResponse. however, just in case, return the
        # response as-is
        return response
