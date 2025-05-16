from datetime import datetime
from pydantic import BaseModel, Field, validator

class SecFiling(BaseModel):
    cik: str
    form_type: str
    filing_date: datetime
    document_url: str
    accession_number: str
    file_number: str
    description: str = ""

    @validator('cik')
    def validate_cik(cls, v):
        if not v.isdigit() or len(v) > 10:
            raise ValueError('CIK must be a numeric string of up to 10 digits')
        return v.zfill(10)  # Pad with leading zeros to 10 digits

    @validator('form_type')
    def validate_form_type(cls, v):
        valid_types = {'10-K', '10-Q', '8-K', '20-F', '6-K'}
        if v not in valid_types:
            raise ValueError(f'Form type must be one of: {valid_types}')
        return v

    @validator('document_url')
    def validate_url(cls, v):
        if not v.startswith('https://www.sec.gov/'):
            raise ValueError('Document URL must be from sec.gov domain')
        return v