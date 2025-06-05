"""Search and company mapping functionality for SEC EDGAR."""
from .company_mapping import get_standardized_company_name, CompanyMapper

__all__ = ['get_standardized_company_name', 'CompanyMapper']