from typing import Dict, Optional

# Simple implementation for now
_CIK_TO_COMPANY_MAP: Dict[str, str] = {
    "0000051143": "International Business Machines Corp",
    "0001318605": "Tesla Inc",
    # Add more mappings or, better yet, replace this hard-coded dictionary
    # object with a mapping function by calling the SEC website
}

def get_standardized_company_name(cik: str) -> Optional[str]:
    """Get standardized company name from CIK."""
    return _CIK_TO_COMPANY_MAP.get(cik)