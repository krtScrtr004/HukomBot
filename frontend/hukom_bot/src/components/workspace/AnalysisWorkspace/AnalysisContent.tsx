import { marked } from 'marked';
import DOMPurify from 'dompurify';
import '@/styles/analysisContent.css';

interface AnalysisContentProps {
	answer: string;
}

function renderAnalysisHtml(answer: string): string {
	const trimmed = answer.trim();
	// If the answer appears to be raw HTML (starts with a '<' tag), skip markdown parsing.
	if (trimmed.startsWith('<')) {
		return DOMPurify.sanitize(trimmed) as string;
	}

	// Otherwise, treat as markdown.
	return DOMPurify.sanitize(marked.parse(answer, { async: false })) as string;
}

export default function AnalysisContent({ answer }: AnalysisContentProps) {
	const html = renderAnalysisHtml(answer);

	return (
		<div
			id="analysis-answer"
			className="prose prose-sm max-w-none text-text-primary leading-relaxed [&_pre]:bg-transparent [&_pre]:p-0 [&_pre]:m-0 [&_pre]:font-sans [&_pre]:text-sm [&_pre]:leading-relaxed"
			dangerouslySetInnerHTML={{ __html: html }}
		/>
	);
}
