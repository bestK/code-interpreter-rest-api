from typing import Optional

from pydantic import BaseModel


class UserRequest(BaseModel):
    prompt: str
    file_base64: Optional[str]
    filename: Optional[str]
    resp_type: Optional[str] = "json"
