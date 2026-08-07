import { marked } from 'marked';
import DOMPurify from 'dompurify';
import type { CaseAnalysisAnswerFormat } from '@/types/workspace';

interface AnalysisContentProps {
	answer: string;
	answerFormat: CaseAnalysisAnswerFormat;
}

function renderAnalysisHtml(
	answer: string,
	answerFormat: CaseAnalysisAnswerFormat,
): string {
	switch (answerFormat) {
		case 'html':
			return DOMPurify.sanitize(answer);
		case 'markdown':
			return DOMPurify.sanitize(
				marked.parse(answer, { async: false }) as string,
			);
		case 'plaintext':
		default:
			return DOMPurify.sanitize(
				`<pre class="whitespace-pre-wrap font-sans text-sm leading-relaxed">${answer.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')}</pre>`,
			);
	}
}

export default function AnalysisContent({
	answer,
	answerFormat,
}: AnalysisContentProps) {
	const html = renderAnalysisHtml(answer, answerFormat);

	return (
		<div
			className="prose prose-sm max-w-none text-text-primary [&_pre]:bg-transparent [&_pre]:p-0 [&_pre]:m-0 [&_pre]:font-sans [&_pre]:text-sm [&_pre]:leading-relaxed"
			dangerouslySetInnerHTML={{ __html: html }}
		/>
	);
}
