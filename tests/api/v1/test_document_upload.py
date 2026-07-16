import pytest

from uuid import UUID
from pathlib import Path

from backend.app.enum.upload_status import UploadStatus
from backend.app.schema.response_schema import SuccessResponse, ErrorResponse

from backend.app.util.utility import get_project_root

TESTS_PATH = get_project_root(5) / "tests/"
SAMPLE_DATA_PATH = TESTS_PATH / "api/data"

@pytest.mark.asyncio
async def test_invalid_file_type(client):
    file_path = Path(SAMPLE_DATA_PATH / "sample_text.txt")
    with open(file_path, "rb") as file:
        files = {"file": (file_path.name, file, "application/text")}

        response = await client.post("/documents", files=files)

    assert response.status_code == 422

    resp_object = ErrorResponse.model_validate_json(response)
    assert resp_object

    assert resp_object.success == False

    error = resp_object.error
    assert error

    assert error.code == "INVALID_FILE_TYPE"
    assert error.message == "File type not allowed"
    assert len(error.details) > 0


@pytest.mark.asyncio
async def test_new_upload(client):
    pdf_path = Path(f"{get_project_root(5)}/")
    with open(pdf_path, "rb") as pdf:
        files = {"file": (pdf_path.name, pdf, "application/pdf")}

        response = await client.post("/documents", files=files)

    assert response.status_code == 200

    resp_object = SuccessResponse.model_validate_json(response)
    assert resp_object

    assert resp_object.success == True
    assert resp_object.message == "File upload is pending for approval"

    data = resp_object.data
    assert data

    document_id = data.get("document_id")
    assert is_valid_uuid_4(document_id)

    assert data.get("status") == UploadStatus.PENDING


@pytest.mark.asyncio
async def test_existing_upload(client):
    pdf_path = Path(SAMPLE_DATA_PATH / "1899 PHILIPPINES CONSTITUTION.pdf")
    with open(pdf_path, "rb") as pdf:
        files = {"file": (pdf_path.name, pdf, "application/pdf")}

        response = await client.post("/documents", files=files)

    assert response.status_code == 200

    resp_object = SuccessResponse.model_validate_json(response)
    assert resp_object

    assert resp_object.success == True
    assert resp_object.message == "File already exists"

    data = resp_object.data
    assert data

    document_id = data.get("document_id")
    assert is_valid_uuid_4(document_id)

    assert UploadStatus(data.get("status"))


@pytest.mark.asyncio
async def test_existing_get_upload_status(client):
    document_id = "29b2b09f-e701-4838-8049-a6dbb01277b1"
    response = await client.get(f"/documents/{document_id}/upload-status")

    assert response.status_code == 200

    resp_object = SuccessResponse.model_validate_json(response)
    assert resp_object

    assert resp_object.success == True
    assert resp_object.message

    data = resp_object.data
    assert data

    assert UploadStatus(data.get("status_value"))


@pytest.mark.asyncio
async def test_non_existing_get_upload_status(client):
    document_id = "29b2b09f-e701-4838-8049-a6dbb01277b1"
    response = await client.get(f"/documents/{document_id}/upload-status")

    assert response.status_code == 404

    resp_object = ErrorResponse.model_validate_json(response)
    assert resp_object

    assert resp_object.success == False

    error = resp_object.error
    assert error

    assert error.code == "DOCUMENT_NOT_FOUND"
    assert error.message == "Document not found"


def is_valid_uuid_4(str_uuid: str):
    try:
        uuid = UUID(str(str_uuid))
        return uuid.version == 4
    except:
        return False
