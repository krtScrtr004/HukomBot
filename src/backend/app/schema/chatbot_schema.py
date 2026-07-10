from pydantic import BaseModel, Field, model_serializer, SerializerFunctionWrapHandler

from backend.app.schema.base_schema import BaseResponse


class ChatPipelineResponse(BaseResponse):
    answer: str = Field(default=None)

    @model_serializer(mode="wrap")
    def custom_serializer(self, handler: SerializerFunctionWrapHandler):
        result = handler(self)

        result["data"] = {
            "answer": result.pop("answer"),
        }

        return result