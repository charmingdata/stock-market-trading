async def get_filing_history(
            cik: str,
            form_type: str,
            year: int
        ) -> list[SecFiling]:
            """Get filing history for a specific company.
            
            Args:
                cik: Company CIK number
                form_type: Form type (10-K or 10-Q)
                year: Fiscal year
                
            Returns:
                List of SecFiling objects representing filing history
                
            Raises:
                ValueError: If CIK is invalid
                ConnectionError: If MCP server request fails
            """
            filings = await self.get_company_filings(cik, [form_type], start_date=None, end_date=None)
            return [f for f in filings if f.form_type == form_type and f.year == year]
        