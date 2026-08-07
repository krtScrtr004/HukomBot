import { useEffect, useRef, useState } from 'react';

interface SessionSearchInputProps {
	onSearch: (query: string | null) => void;
	disabled?: boolean;
}

export default function SessionSearchInput({
	onSearch,
	disabled,
}: SessionSearchInputProps) {
	const [value, setValue] = useState('');
	const onSearchRef = useRef(onSearch);

	useEffect(() => {
		onSearchRef.current = onSearch;
	}, [onSearch]);

	useEffect(() => {
		const timer = setTimeout(() => {
			const trimmed = value.trim();
			onSearchRef.current(trimmed.length > 0 ? trimmed : null);
		}, 300);
		return () => clearTimeout(timer);
	}, [value]);

	return (
		<div className="relative">
			<i
				className="bi bi-search absolute left-3 top-1/2 -translate-y-1/2 text-text-muted"
				aria-hidden="true"
			/>
			<input
				type="search"
				value={value}
				onChange={(e) => setValue(e.target.value)}
				placeholder="Search sessions..."
				disabled={disabled}
				maxLength={100}
				className="w-full pl-9 pr-3 py-2 text-sm rounded-sm border border-border bg-surface text-text-primary placeholder:text-text-muted focus:outline-none focus-visible:ring-2 focus-visible:ring-primary disabled:opacity-50"
				aria-label="Search analysis sessions"
			/>
		</div>
	);
}
