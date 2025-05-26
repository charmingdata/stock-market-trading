"""SEC EDGAR API constants."""
from typing import Literal

# Base URLs
SEC_EDGAR_BASE_URL = "https://www.sec.gov"
SEC_EDGAR_SEARCH_URL = f"{SEC_EDGAR_BASE_URL}/edgar/search/"
SEC_EDGAR_CIK_LOOKUP_URL = f"{SEC_EDGAR_BASE_URL}/edgar/company-cik-search/"

# Request Configuration
DEFAULT_HEADERS = {
    "User-Agent": "Sample Company Name sample@email.com",
    "Accept": "application/json",
    "Content-Type": "application/json"
}

# Form Types
FORM_10K = "10-K"
FORM_10Q = "10-Q"
SUPPORTED_FORM_TYPES = [FORM_10K, FORM_10Q]

# Fiscal Period Types
FiscalPeriodType = Literal["10-K", "Q1", "Q2", "Q3", "Q4"]