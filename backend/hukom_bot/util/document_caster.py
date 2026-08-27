from backend.hukom_bot.model.document_model import Document
from backend.hukom_bot.schema.document_schema import *

class DocumentCaster:
    @staticmethod
    def base_to_upload_response(document: Document) -> DocumentUploadResponse:
        return DocumentUploadResponse(
            document_id=document.id,
            status=document.upload_status,
        )
        
    @staticmethod
    def create_to_base(document: DocumentCreate) -> Document:
        return Document(
            id=document.id,
            original_file_name=document.original_file_name,
            upload_file_name=document.upload_file_name,
            document_type=document.document_type,
            file_type=document.file_type,
            upload_status=document.upload_status,
            upload_error=document.upload_error,
            digest=document.digest,
            uploader_id=document.uploader_id,
            created_at=document.created_at
        )

    @staticmethod
    def metadata_to_create(document: DocumentMetadata) -> DocumentCreate:
        return DocumentCreate(
            original_file_name=document.original_file_name,
            upload_file_name=document.upload_file_name,
            document_type=document.document_type,
            file_type=document.suffix,
            digest=document.digest,
        )
        
    @staticmethod
    def update_payload_to_update(id: UUID, document: DocumentUpdatePayload) -> DocumentUpdate:
        return DocumentUpdate(
            id=id,
            original_file_name=document.original_file_name,
            upload_file_name=None,
            file_type=None,
            document_type=document.document_type,
            upload_status=document.upload_status,
            upload_error=None
        )