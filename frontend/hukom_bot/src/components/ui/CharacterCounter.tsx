interface CharacterCounterProp {
	text: string;
	maxLength: number;
}

export default function CharacterCounter({
	text,
	maxLength,
}: CharacterCounterProp) {
	return (
		<span
			className={`text-xs ml-auto ${
				text.trim().length > maxLength * 0.9
					? 'text-danger'
					: 'text-text-muted'
			}`}
		>
			{text.trim().length}/{maxLength}
		</span>
	);
}
