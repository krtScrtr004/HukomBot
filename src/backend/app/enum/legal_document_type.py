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

    # Corporate Documents
    ARTICLES_OF_INCORPORATION = "articles_of_incorporation"
    BYLAWS = "bylaws"
    BOARD_RESOLUTION = "board_resolution"
    SHAREHOLDER_AGREEMENT = "shareholder_agreement"
    MINUTES_OF_MEETING = "minutes_of_meeting"

    # Court & Litigation
    COMPLAINT = "complaint"
    AFFIDAVIT = "affidavit"
    SUBPOENA = "subpoena"
    COURT_ORDER = "court_order"
    JUDGMENT = "judgment"
    MOTION = "motion"
    SUMMONS = "summons"

    # Personal & Estate
    LAST_WILL_AND_TESTAMENT = "last_will_and_testament"
    DEED_OF_SALE = "deed_of_sale"
    POWER_OF_ATTORNEY = "power_of_attorney"
    TRUST_DEED = "trust_deed"
    BIRTH_CERTIFICATE = "birth_certificate"
    MARRIAGE_CONTRACT = "marriage_contract"

    # Government & Regulatory
    PERMIT = "permit"
    LICENSE = "license"
    GOVERNMENT_ISSUED_ID = "government_issued_id"
    TAX_DECLARATION = "tax_declaration"

    # Financial
    PROMISSORY_NOTE = "promissory_note"
    DEED_OF_MORTGAGE = "deed_of_mortgage"
    LOAN_AGREEMENT = "loan_agreement"
    INVOICE = "invoice"
    RECEIPT = "receipt"

    # Intellectual Property
    PATENT = "patent"
    TRADEMARK_REGISTRATION = "trademark_registration"
    COPYRIGHT_REGISTRATION = "copyright_registration"

    # Miscellaneous
    CERTIFICATION = "certification"
    WAIVER = "waiver"
    NOTICE = "notice"
    OTHER = "other"