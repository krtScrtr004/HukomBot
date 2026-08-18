from pydantic import BaseModel, HttpUrl


class CloudinaryUploadResponse(BaseModel):
    public_id: str
    secure_url: HttpUrl