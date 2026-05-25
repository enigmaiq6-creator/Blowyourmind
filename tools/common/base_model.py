from pydantic import BaseModel, ConfigDict


class BaseModelTool(BaseModel):
    """
    Common base class for all tools and logic components.
    Pre-configures Pydantic to allow arbitrary types.
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)
