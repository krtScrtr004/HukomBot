from datetime import datetime
from pydantic import BaseModel, Field

# Case Analysis Session ========================================

class CaseAnalysisSessionCreate(BaseModel):
    created_at: datetime = Field(default=datetime.now())
    updated_at: datetime = Field(default=datetime.now())