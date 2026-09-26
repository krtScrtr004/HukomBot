// src/components/ui/DataTable.tsx
import React from 'react';
import LoadingSpinner from '@/components/workspace/shared/LoadingSpinner';
import ErrorText from '@/components/ui/ErrorText';
import EmptyState from '@/components/workspace/shared/EmptyState';

export interface DataTableColumn<T> {
	key: string; // used for sort column param and React key
	header: string;
	sortable?: boolean;
	render: (row: T) => React.ReactNode;
}

export interface DataTableProps<T> {
	columns: DataTableColumn<T>[];
	rows: T[];
	rowKey: (row: T) => string;
	loading: boolean;
	error: string | null;
	emptyMessage: string;
	sortColumn?: string;
	sortOrder?: 'ASC' | 'DESC';
	onSortChange?: (column: string, order: 'ASC' | 'DESC') => void;
	onRowClick?: (row: T) => void;
	onRetry?: () => void;
	/** Optional attributes for each row element */
	rowAttributes?: (row: T) => React.HTMLAttributes<HTMLTableRowElement>;
}

export default function DataTable<T>(props: DataTableProps<T>) {
	const {
		columns,
		rows,
		rowKey,
		loading,
		error,
		emptyMessage,
		sortColumn,
		sortOrder,
		onSortChange,
		onRowClick,
		onRetry,
		rowAttributes,
	} = props;

	if (loading) return <LoadingSpinner label="Loading" size="lg" className="min-h-100" />;
	if (error) return <ErrorText error={error} onRetry={onRetry} />;
	if (!rows.length) return <EmptyState title={emptyMessage} />;

	return (
		<div className="min-h-100 w-full overflow-x-auto scrollbar-thin">
			<table className="w-full min-w-full text-left text-sm border-collapse">

				<thead>
					<tr className="border-b border-border bg-surface-muted text-text-secondary text-xs uppercase tracking-wider">
						{columns.map((column) => {
							const sortable = column.sortable;
							const ariaSort =
								sortColumn === column.key
									? sortOrder === 'ASC'
										? 'ascending'
										: 'descending'
									: 'none';

							return (
								<th
									key={column.key}
									scope="col"
									className={`px-4 py-3 text-left font-semibold ${sortable ? 'cursor-pointer select-none hover:text-text-primary' : ''}`}
									aria-sort={ariaSort}
									onClick={() => {
										if (!sortable) return;
										const nextOrder =
											sortColumn === column.key &&
											sortOrder === 'ASC'
												? 'DESC'
												: 'ASC';
										onSortChange?.(column.key, nextOrder);
									}}
								>
									<div className="inline-flex items-center gap-1.5">
										<span>{column.header}</span>
										{sortable && (
											<i
												className={`bi ${
													sortColumn === column.key
														? sortOrder === 'ASC'
															? 'bi-sort-up text-primary'
															: 'bi-sort-down text-primary'
														: 'bi-arrow-down-up text-text-muted text-[10px]'
												}`}
											/>
										)}
									</div>
								</th>
							);
						})}
					</tr>
				</thead>

				<tbody className="divide-y divide-border">
					{rows.map((row) => (
						<tr
							key={rowKey(row)}
							className={`transition-colors ${onRowClick ? 'cursor-pointer hover:bg-hover/80' : ''}`}
							onClick={() => onRowClick?.(row)}
							{...(rowAttributes ? rowAttributes(row) : {})}
						>
							{columns.map((column) => (
								<td key={column.key} className="px-4 py-3 text-sm text-text-primary align-middle">
									{column.render(row)}
								</td>
							))}
						</tr>
					))}
				</tbody>

			</table>
		</div>
	);
}
