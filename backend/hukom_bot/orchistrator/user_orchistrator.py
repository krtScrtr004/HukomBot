import logging
from uuid import UUID
from datetime import datetime
from fastapi import UploadFile
from fastapi.concurrency import run_in_threadpool
from backend.hukom_bot.database.database import Database
from backend.hukom_bot.model.user_model import User
from backend.hukom_bot.enum.user_role import UserRole
from backend.hukom_bot.service.user_service import UserService
from backend.hukom_bot.schema.user_schema import UserUpdate, UserUpdateBase
from backend.hukom_bot.exception.app_exception import UnauthorizedException
from backend.hukom_bot.util.upload_image import (
    upload_to_cloudinary,
    remove_from_cloudinary,
)
from backend.hukom_bot.exception.app_exception import NotFoundException
from backend.hukom_bot.exception.file_exception import (
    InvalidFileTypeException,
    FileSizeTooLargeException,
)
from backend.hukom_bot.util.file_utilities import get_mime_type

logger = logging.getLogger(__name__)


class UserOrchistrator:
    def __init__(self, db: Database, user_service: UserService):
        self._db = db
        self._user_service = user_service

    async def update_pipeline(
        self,
        me: User,
        user_id: UUID,
        user: UserUpdateBase | None,
        profile_picture: UploadFile | None,
    ):
        is_me = me.id == user_id
        am_I_admin = me.role == UserRole.ADMIN

        async with self._db.connection() as con:
            # Allow only admins to modify others' profile
            if not am_I_admin and not is_me:
                raise UnauthorizedException(
                    details=[
                        "You are not allowed to perform update on other's information"
                    ]
                )

            if user.role is not None and not am_I_admin:
                raise UnauthorizedException(
                    details=["You are not allowed to update application role"]
                )

            existing_user = (
                await self._user_service.get_by_id(id=user_id, connection=con)
                if user
                else None
            )
            if not is_me and not existing_user:
                raise NotFoundException(message="User not found", code="USER_NOT_FOUND")

            upload_result = None

            try:
                # Extract and upload profile picture, if provided
                contents = await profile_picture.read() if profile_picture else None
                if contents:
                    if not self._user_service.is_valid_image_type(contents):
                        raise InvalidFileTypeException(
                            message="Invalid profile picture type",
                            code="INVALID_IMAGE_TYPE",
                            details=[
                                f"{", ".join(self._user_service.ALLOWED_IMAGE_TYPES)} are the only allowed image types"
                            ],
                        )

                    MAX_FILE_SIZE = 5 * 1024 * 1024  # MAX: 5MB
                    file_size = len(contents)
                    if file_size > MAX_FILE_SIZE:
                        raise FileSizeTooLargeException(
                            details=[f"Max size is {MAX_FILE_SIZE}"]
                        )

                    # Upload image to cloudinary, if not None
                    upload_result = await run_in_threadpool(
                        upload_to_cloudinary, contents
                    )

                    logger.info(
                        f"New image uploaded to image file storage. Size: {file_size}, Type: {get_mime_type(contents)}"
                    )

                update_schema = self._create_update_schema(
                    user_id=user_id,
                    user=user,
                    profile_url=upload_result.secure_url if upload_result else None,
                    existing_user=existing_user if not is_me else me,
                )
                if update_schema:
                    # Update database entry
                    await self._user_service.update(
                        user=update_schema,
                        connection=con,
                    )

                logger.info(
                    "User with id: %s updated their profile on %s",
                    user_id,
                    datetime.now(),
                )

                await con.commit()
            except Exception as ex:
                await con.rollback()

                logger.exception(
                    f"An error occured while updating user's info with id {user_id}"
                )

                # Remove uploaded profile picture from the file storage
                if upload_result:
                    remove_from_cloudinary(public_id=upload_result.public_id)

                    logger.info(
                        "Uploaded image with public id: %s is rolled back",
                        upload_result.public_id,
                    )

                raise

    def _create_update_schema(
        self,
        user_id: UUID,
        user: UserUpdateBase | None,
        profile_url: str | None,
        existing_user: User | None,
    ):
        if not user and not profile_url:
            return None

        to_return = UserUpdate(id=user_id)

        if user is not None:
            update_data = user.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                if field in UserUpdate.model_fields:
                    # Include only modified values
                    if value != getattr(existing_user, field):
                        setattr(to_return, field, value)

        if profile_url is not None and profile_url != existing_user.profile_picture:
            to_return.profile_picture = str(profile_url)

        return to_return
