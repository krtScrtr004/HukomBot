import pytest

from uuid import UUID
from pathlib import Path

from backend.app.enum.upload_status import UploadStatus

from backend.app.util.utility import get_project_root


@pytest.mark.asyncio
async def test_document_upload(client):
    pdf_path = Path(f"{get_project_root(5)}/data/Legislations/RR No. 1-2025.pdf")
    with open(pdf_path, "rb") as pdf:
        files = {"file": (pdf_path.name, pdf, "application/pdf")}

        response = await client.post("/documents", files=files)

    assert response.status_code == 200

    response_json = response.json()
    assert response_json
    data = response_json.get("data")
    assert data
    assert data.get("document_id") and is_valid_uuid_4(data.get("document_id"))
    assert (
        data.get("status") and data.get("status") == UploadStatus.ONGOING
    )


def is_valid_uuid_4(str_uuid: str):
    try:
        uuid = UUID(str(str_uuid))
        return uuid.version == 4
    except:
        return False
