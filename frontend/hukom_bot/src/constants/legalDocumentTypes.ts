import type { LegalDocumentType } from '@/types/workspace';

export const LEGAL_DOCUMENT_TYPES: {
	value: LegalDocumentType;
	label: string;
}[] = [
	{ value: 'contract', label: 'Contract' },
	{ value: 'non_disclosure_agreement', label: 'Non-Disclosure Agreement' },
	{ value: 'service_agreement', label: 'Service Agreement' },
	{ value: 'employment_contract', label: 'Employment Contract' },
	{ value: 'lease_agreement', label: 'Lease Agreement' },
	{ value: 'partnership_agreement', label: 'Partnership Agreement' },
	{ value: 'memorandum_of_agreement', label: 'Memorandum of Agreement' },
	{
		value: 'memorandum_of_understanding',
		label: 'Memorandum of Understanding',
	},
	{ value: 'addendum_amendment', label: 'Addendum/Amendment' },
	{ value: 'franchise_agreement', label: 'Franchise Agreement' },
	{ value: 'indemnity_agreement', label: 'Indemnity Agreement' },
	{
		value: 'articles_of_incorporation',
		label: 'Articles of Incorporation',
	},
	{ value: 'bylaws', label: 'Bylaws' },
	{ value: 'board_resolution', label: 'Board Resolution' },
	{ value: 'shareholder_agreement', label: 'Shareholder Agreement' },
	{ value: 'minutes_of_meeting', label: 'Minutes of Meeting' },
	{ value: 'secretary_certificate', label: "Secretary's Certificate" },
	{
		value: 'general_information_sheet',
		label: 'General Information Sheet',
	},
	{ value: 'complaint', label: 'Complaint' },
	{ value: 'affidavit', label: 'Affidavit' },
	{ value: 'subpoena', label: 'Subpoena' },
	{ value: 'court_order', label: 'Court Order' },
	{ value: 'judgment', label: 'Judgment' },
	{
		value: 'supreme_court_decision',
		label: 'Supreme Court Decision',
	},
	{
		value: 'court_of_appeals_decision',
		label: 'Court of Appeals Decision',
	},
	{ value: 'motion', label: 'Motion' },
	{ value: 'summons', label: 'Summons' },
	{ value: 'pleading', label: 'Pleading' },
	{ value: 'brief_memorandum', label: 'Brief/Memorandum' },
	{
		value: 'last_will_and_testament',
		label: 'Last Will and Testament',
	},
	{ value: 'deed_of_sale', label: 'Deed of Sale' },
	{ value: 'power_of_attorney', label: 'Power of Attorney' },
	{ value: 'trust_deed', label: 'Trust Deed' },
	{ value: 'birth_certificate', label: 'Birth Certificate' },
	{ value: 'marriage_contract', label: 'Marriage Contract' },
	{ value: 'deed_of_donation', label: 'Deed of Donation' },
	{ value: 'prenuptial_agreement', label: 'Prenuptial Agreement' },
	{ value: 'permit', label: 'Permit' },
	{ value: 'license', label: 'License' },
	{ value: 'government_issued_id', label: 'Government Issued ID' },
	{ value: 'tax_declaration', label: 'Tax Declaration' },
	{ value: 'tax_clearance', label: 'Tax Clearance' },
	{
		value: 'certificate_of_registration',
		label: 'Certificate of Registration',
	},
];
