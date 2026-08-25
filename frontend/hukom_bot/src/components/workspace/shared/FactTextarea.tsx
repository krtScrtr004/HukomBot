import type { ChangeEvent } from 'react';

interface FactTextAreaProp {
    id: string;
	value: string;
	disabled: boolean;
	maxLength: number;
	rows?: number;
    ref? : React.Ref<HTMLTextAreaElement> | undefined;
	className?: string;
	hasError?: boolean;
	onChange?: (e: ChangeEvent<HTMLTextAreaElement>) => void;
}

export default function FactTextArea({
    id,
	value,
	disabled,
	maxLength,
	rows = 2,
    ref = undefined,
	className = '',
	hasError = false,
	onChange = () => {},
}: FactTextAreaProp) {
	return (
		<textarea
            id={id}
			value={value}
			onChange={onChange}
			disabled={disabled}
			maxLength={maxLength}
			rows={rows}
            ref={ref}
			className={`flex-1 w-full min-h-20 max-h-40 text-sm rounded-sm border border-border bg-surface px-3 py-2 text-text-secondary resize-y scrollbar-thin focus:outline-none focus-visible:ring-2 focus-visible:ring-primary disabled:opacity-60 ${disabled ? 'line-through' : ''} ${className}`}
			aria-label="Case fact"
			aria-invalid={hasError}
		/>
	);
}
