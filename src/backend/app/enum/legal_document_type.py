from enum import StrEnum


class LegalDocumentType(StrEnum):
    # Regulatory & Administrative (Public/Statutory Issuances)
    REPUBLIC_ACT = "republic_act"  # Added: Perfectly maps statutory laws (e.g., RA 11976)
    REVENUE_REGULATION = "revenue_regulation"
    REVENUE_MEMORANDUM_CIRCULAR = "revenue_memorandum_circular"
    EXECUTIVE_ORDER = "executive_order"
    MUNICIPAL_ORDINANCE = "municipal_ordinance"
    
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
