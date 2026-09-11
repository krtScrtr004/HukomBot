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

	if (loading) return <LoadingSpinner label="Loading" size="lg" />;
	if (error) return <ErrorText error={error} onRetry={onRetry} />;
	if (!rows.length) return <EmptyState title={emptyMessage} />;

	return (
		<table className="min-w-full table-auto border-collapse">
			<thead>
				<tr>
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
									className={`p-2 text-left ${sortable ? 'cursor-pointer select-none' : ''}`}
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
									{column.header}
								</th>
							);
					})}
				</tr>
			</thead>
			<tbody>
				{rows.map((row) => (
					<tr
						key={rowKey(row)}
						className={`border-t border-border ${onRowClick ? 'cursor-pointer hover:bg-hover' : ''}`}
						onClick={() => onRowClick?.(row)}
						{...(rowAttributes ? rowAttributes(row) : {})}
					>
						{columns.map((column) => (
							<td key={column.key} className="p-2">
								{column.render(row)}
							</td>
						))}
					</tr>
				))}
			</tbody>
		</table>
	);
}
