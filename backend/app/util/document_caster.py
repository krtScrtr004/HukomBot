from backend.app.model.document_model import Document
from backend.app.schema.document_schema import *

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