import { marked } from 'marked';
import DOMPurify from 'dompurify';

interface AnalysisContentProps {
	answer: string;
}

function renderAnalysisHtml(answer: string): string {
	return DOMPurify.sanitize(marked.parse(answer, { async: false }) as string);
}

export default function AnalysisContent({ answer }: AnalysisContentProps) {
	const html = renderAnalysisHtml(answer);

	return (
		<div
			className="prose prose-sm max-w-none text-text-primary [&_pre]:bg-transparent [&_pre]:p-0 [&_pre]:m-0 [&_pre]:font-sans [&_pre]:text-sm [&_pre]:leading-relaxed"
			dangerouslySetInnerHTML={{ __html: html }}
		/>
	);
}
