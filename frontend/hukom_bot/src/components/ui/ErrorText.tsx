interface ErrorTextProp {
	text: string;
}

export default function ErrorText({ text }: ErrorTextProp) {
	return (
		<p className="text-xs text-danger" role="alert">
			{text}
		</p>
	);
}
