from enum import StrEnum


class LegalDocumentType(StrEnum):    
    # Contracts & Agreements
    CONTRACT = "contract"
    NON_DISCLOSURE_AGREEMENT = "non_disclosure_agreement"
    SERVICE_AGREEMENT = "service_agreement"
    EMPLOYMENT_CONTRACT = "employment_contract"
    LEASE_AGREEMENT = "lease_agreement"
    PARTNERSHIP_AGREEMENT = "partnership_agreement"
    MEMORANDUM_OF_AGREEMENT = "memorandum_of_agreement"
    MEMORANDUM_OF_UNDERSTANDING = "memorandum_of_understanding"
    ADDENDUM_AMENDMENT = "addendum_amendment"  # Added: For changes to existing contracts
    FRANCHISE_AGREEMENT = "franchise_agreement"  # Added: Common commercial document
    INDEMNITY_AGREEMENT = "indemnity_agreement"  # Added: Liability waivers/hold harmless

    # Corporate Documents
    ARTICLES_OF_INCORPORATION = "articles_of_incorporation"
    BYLAWS = "bylaws"
    BOARD_RESOLUTION = "board_resolution"
    SHAREHOLDER_AGREEMENT = "shareholder_agreement"
    MINUTES_OF_MEETING = "minutes_of_meeting"
    SECRETARY_CERTIFICATE = "secretary_certificate"
    GENERAL_INFORMATION_SHEET = "general_information_sheet"

    # Court & Litigation
    COMPLAINT = "complaint"
    AFFIDAVIT = "affidavit"
    SUBPOENA = "subpoena"
    COURT_ORDER = "court_order"
    JUDGMENT = "judgment"
    SUPREME_COURT_DECISION = "supreme_court_decision"
    COURT_OF_APPEALS_DECISION = "court_of_appeals_decision"
    MOTION = "motion"
    SUMMONS = "summons"
    PLEADING = "pleading"
    BRIEF_MEMORANDUM = "brief_memorandum"

    # Personal & Estate
    LAST_WILL_AND_TESTAMENT = "last_will_and_testament"
    DEED_OF_SALE = "deed_of_sale"
    POWER_OF_ATTORNEY = "power_of_attorney"
    TRUST_DEED = "trust_deed"
    BIRTH_CERTIFICATE = "birth_certificate"
    MARRIAGE_CONTRACT = "marriage_contract"
    DEED_OF_DONATION = "deed_of_donation"  # Added: Common property transfer document
    PRENUPTIAL_AGREEMENT = "prenuptial_agreement"  # Added: Standard family law document

    # Government & Regulatory (Individual/Corporate Compliance)
    PERMIT = "permit"
    LICENSE = "license"
    GOVERNMENT_ISSUED_ID = "government_issued_id"
    TAX_DECLARATION = "tax_declaration"
    TAX_CLEARANCE = "tax_clearance"
    CERTIFICATE_OF_REGISTRATION = "certificate_of_registration"

    # Regulatory & Administrative
    CONSTITUTION = "constitution"
    REPUBLIC_ACT = "republic_act" 
    REVENUE_REGULATION = "revenue_regulation"
    REVENUE_MEMORANDUM_CIRCULAR = "revenue_memorandum_circular"
    EXECUTIVE_ORDER = "executive_order"
    MUNICIPAL_ORDINANCE = "municipal_ordinance"

    # Financial
    PROMISSORY_NOTE = "promissory_note"
    DEED_OF_MORTGAGE = "deed_of_mortgage"
    LOAN_AGREEMENT = "loan_agreement"
    INVOICE = "invoice"
    RECEIPT = "receipt"
    AUDITED_FINANCIAL_STATEMENT = "audited_financial_statement"

    # Intellectual Property
    PATENT = "patent"
    TRADEMARK_REGISTRATION = "trademark_registration"
    COPYRIGHT_REGISTRATION = "copyright_registration"
    IP_ASSIGNMENT = "ip_assignment"

    # Miscellaneous
    CERTIFICATION = "certification"
    WAIVER = "waiver"
    NOTICE = "notice"
    OTHER = "other"

    def display_name(self):
        match self:
            case LegalDocumentType.CONTRACT:
                return "Contract"
            case LegalDocumentType.NON_DISCLOSURE_AGREEMENT:
                return "Non-Disclosure Agreement"
            case LegalDocumentType.SERVICE_AGREEMENT:
                return "Service Agreement"
            case LegalDocumentType.EMPLOYMENT_CONTRACT:
                return "Employment Contract"
            case LegalDocumentType.LEASE_AGREEMENT:
                return "Lease Agreement"
            case LegalDocumentType.PARTNERSHIP_AGREEMENT:
                return "Partnership Agreement"
            case LegalDocumentType.MEMORANDUM_OF_AGREEMENT:
                return "Memorandum of Agreement"
            case LegalDocumentType.MEMORANDUM_OF_UNDERSTANDING:
                return "Memorandum of Understanding"
            case LegalDocumentType.ADDENDUM_AMENDMENT:
                return "Addendum/Amendment"
            case LegalDocumentType.FRANCHISE_AGREEMENT:
                return "Franchise Agreement"
            case LegalDocumentType.INDEMNITY_AGREEMENT:
                return "Indemnity Agreement"
            case LegalDocumentType.ARTICLES_OF_INCORPORATION:
                return "Articles of Incorporation"
            case LegalDocumentType.BYLAWS:
                return "Bylaws"
            case LegalDocumentType.BOARD_RESOLUTION:
                return "Board Resolution"
            case LegalDocumentType.SHAREHOLDER_AGREEMENT:
                return "Shareholder Agreement"
            case LegalDocumentType.MINUTES_OF_MEETING:
                return "Minutes of Meeting"
            case LegalDocumentType.SECRETARY_CERTIFICATE:
                return "Secretary's Certificate"
            case LegalDocumentType.GENERAL_INFORMATION_SHEET:
                return "General Information Sheet"
            case LegalDocumentType.COMPLAINT:
                return "Complaint"
            case LegalDocumentType.AFFIDAVIT:
                return "Affidavit"
            case LegalDocumentType.SUBPOENA:
                return "Subpoena"
            case LegalDocumentType.COURT_ORDER:
                return "Court Order"
            case LegalDocumentType.JUDGMENT:
                return "Judgment"
            case LegalDocumentType.SUPREME_COURT_DECISION:
                return "Supreme Court Decision"
            case LegalDocumentType.COURT_OF_APPEALS_DECISION:
                return "Court of Appeals Decision"
            case LegalDocumentType.MOTION:
                return "Motion"
            case LegalDocumentType.SUMMONS:
                return "Summons"
            case LegalDocumentType.PLEADING:
                return "Pleading"
            case LegalDocumentType.BRIEF_MEMORANDUM:
                return "Brief/Memorandum"
            case LegalDocumentType.LAST_WILL_AND_TESTAMENT:
                return "Last Will and Testament"
            case LegalDocumentType.DEED_OF_SALE:
                return "Deed of Sale"
            case LegalDocumentType.POWER_OF_ATTORNEY:
                return "Power of Attorney"
            case LegalDocumentType.TRUST_DEED:
                return "Trust Deed"
            case LegalDocumentType.BIRTH_CERTIFICATE:
                return "Birth Certificate"
            case LegalDocumentType.MARRIAGE_CONTRACT:
                return "Marriage Contract"
            case LegalDocumentType.DEED_OF_DONATION:
                return "Deed of Donation"
            case LegalDocumentType.PRENUPTIAL_AGREEMENT:
                return "Prenuptial Agreement"
            case LegalDocumentType.PERMIT:
                return "Permit"
            case LegalDocumentType.LICENSE:
                return "License"
            case LegalDocumentType.GOVERNMENT_ISSUED_ID:
                return "Government Issued ID"
            case LegalDocumentType.TAX_DECLARATION:
                return "Tax Declaration"
            case LegalDocumentType.TAX_CLEARANCE:
                return "Tax Clearance"
            case LegalDocumentType.CERTIFICATE_OF_REGISTRATION:
                return "Certificate of Registration"
            case LegalDocumentType.CONSTITUTION:
                return "Constitution"
            case LegalDocumentType.REPUBLIC_ACT:
                return "Republic Act"
            case LegalDocumentType.REVENUE_REGULATION:
                return "Revenue Regulation"
            case LegalDocumentType.REVENUE_MEMORANDUM_CIRCULAR:
                return "Revenue Memorandum Circular"
            case LegalDocumentType.EXECUTIVE_ORDER:
                return "Executive Order"
            case LegalDocumentType.MUNICIPAL_ORDINANCE:
                return "Municipal Ordinance"
            case LegalDocumentType.PROMISSORY_NOTE:
                return "Promissory Note"
            case LegalDocumentType.DEED_OF_MORTGAGE:
                return "Deed of Mortgage"
            case LegalDocumentType.LOAN_AGREEMENT:
                return "Loan Agreement"
            case LegalDocumentType.INVOICE:
                return "Invoice"
            case LegalDocumentType.RECEIPT:
                return "Receipt"
            case LegalDocumentType.AUDITED_FINANCIAL_STATEMENT:
                return "Audited Financial Statement"
            case LegalDocumentType.PATENT:
                return "Patent"
            case LegalDocumentType.TRADEMARK_REGISTRATION:
                return "Trademark Registration"
            case LegalDocumentType.COPYRIGHT_REGISTRATION:
                return "Copyright Registration"
            case LegalDocumentType.IP_ASSIGNMENT:
                return "IP Assignment"
            case LegalDocumentType.CERTIFICATION:
                return "Certification"
            case LegalDocumentType.WAIVER:
                return "Waiver"
            case LegalDocumentType.NOTICE:
                return "Notice"
            case LegalDocumentType.OTHER:
                return "Other"