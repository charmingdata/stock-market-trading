from typing import Dict, Optional

"""
Get 10Q and 10K reports
https://pypi.org/project/secedgar/

Finding Company CIKs
The secedgar.cik_lookup.get_cik_map function is provided as a utility to easily fetch CIKs based on a company’s ticker or name.
https://sec-edgar.github.io/sec-edgar/cikmap.html
"""
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