import cloudinary
import cloudinary.uploader
from fastapi import UploadFile
from backend.hukom_bot.core.settings import settings
from backend.hukom_bot.schema.util_schema import CloudinaryUploadResponse

cloudinary.config(
    cloud_name=settings.CLOUDINARY_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_SECRET,
    secure=True,
)


def upload_to_cloudinary(file: UploadFile) -> CloudinaryUploadResponse:
    result = cloudinary.uploader.upload(file.file, folder="hukom_bot/images")
    return CloudinaryUploadResponse.model_validate(result, extra="ignore")


def remove_from_cloudinary(public_id: str) -> bool:
    result = cloudinary.uploader.destroy(public_id=public_id)
    return result.get("result") == "ok"
