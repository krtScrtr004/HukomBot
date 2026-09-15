from pydantic import BaseModel, HttpUrl, Field


class CloudinaryUploadResponse(BaseModel):
    public_id: str
    secure_url: HttpUrl
