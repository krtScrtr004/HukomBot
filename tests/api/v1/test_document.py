import pytest
from pathlib import Path

from src.backend.app.util.utility import get_project_root


@pytest.mark.asyncio
async def test_document_upload(client):
    pdf_path = Path(f"{get_project_root(3)}/data/Legislations/R.A. 12234.pdf")
    with open(pdf_path, "rb") as pdf:
        files = {"file": (pdf_path.name, pdf, "application/pdf")}

        response = await client.post("/documents", files=files)

    assert response.status_code == 200
