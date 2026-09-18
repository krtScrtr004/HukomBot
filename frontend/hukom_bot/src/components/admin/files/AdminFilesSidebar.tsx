const DUMMY_DOC_TYPES = [
	{ name: 'Supreme Court Decisions', count: 950, percent: 41, color: 'bg-primary' },
	{ name: 'Executive Orders / Acts', count: 620, percent: 27, color: 'bg-info' },
	{ name: 'Legal Statutes & Codes', count: 480, percent: 21, color: 'bg-success' },
	{ name: 'Other Documents', count: 250, percent: 11, color: 'bg-warning' },
];

export default function AdminFilesSidebar() {
	return (
		<aside className="space-y-4">
			{/* Pipeline Ingestion Pipeline Widget */}
			<div className="rounded-lg border border-border bg-surface p-5 shadow-xs space-y-4">
				<div className="flex items-center justify-between border-b border-border pb-3">
					<div>
						<h3 className="font-semibold text-text-primary text-sm flex items-center gap-2">
							<i className="bi bi-diagram-3-fill text-primary" /> Ingestion Pipeline
						</h3>
						<p className="text-[11px] text-text-muted mt-0.5">Realtime chunking & indexing flow</p>
					</div>
					<span className="flex h-2 w-2 rounded-full bg-success animate-pulse" />
				</div>

				<div className="space-y-3">
					<div className="flex items-center justify-between rounded-md bg-surface-muted p-2.5 border border-border/60">
						<div className="flex items-center gap-2.5">
							<div className="flex h-7 w-7 items-center justify-center rounded-md bg-warning/15 text-warning font-bold text-xs">
								1
							</div>
							<div>
								<p className="text-xs font-medium text-text-primary">Pending Approval</p>
								<p className="text-[10px] text-text-muted">Awaiting admin review</p>
							</div>
						</div>
						<span className="rounded-full bg-warning/10 px-2 py-0.5 text-xs font-bold text-warning">
							14 files
						</span>
					</div>

					<div className="flex items-center justify-between rounded-md bg-surface-muted p-2.5 border border-border/60">
						<div className="flex items-center gap-2.5">
							<div className="flex h-7 w-7 items-center justify-center rounded-md bg-info/15 text-info font-bold text-xs">
								2
							</div>
							<div>
								<p className="text-xs font-medium text-text-primary">Vector Chunking</p>
								<p className="text-[10px] text-text-muted">Splitting text into embeddings</p>
							</div>
						</div>
						<span className="rounded-full bg-info/10 px-2 py-0.5 text-xs font-bold text-info">
							8 processing
						</span>
					</div>

					<div className="flex items-center justify-between rounded-md bg-surface-muted p-2.5 border border-border/60">
						<div className="flex items-center gap-2.5">
							<div className="flex h-7 w-7 items-center justify-center rounded-md bg-success/15 text-success font-bold text-xs">
								3
							</div>
							<div>
								<p className="text-xs font-medium text-text-primary">Indexed in Knowledge Base</p>
								<p className="text-[10px] text-text-muted">RAG search active</p>
							</div>
						</div>
						<span className="rounded-full bg-success/10 px-2 py-0.5 text-xs font-bold text-success">
							2,210 ready
						</span>
					</div>
				</div>
			</div>

			{/* Category Distribution Donut Chart */}
			<div className="rounded-lg border border-border bg-surface p-5 shadow-xs space-y-4">
				<div className="flex items-center justify-between border-b border-border pb-3">
					<div>
						<h3 className="font-semibold text-text-primary text-sm flex items-center gap-2">
							<i className="bi bi-pie-chart-fill text-info" /> Legal Categories
						</h3>
						<p className="text-[11px] text-text-muted mt-0.5">Knowledge base distribution</p>
					</div>
				</div>

				{/* Conic Donut Chart */}
				<div className="my-3 flex items-center justify-center">
					<div
						className="relative h-32 w-32 rounded-full shadow-inner flex items-center justify-center"
						style={{
							background: `conic-gradient(
								var(--color-primary) 0% 41%,
								var(--color-info) 41% 68%,
								var(--color-success) 68% 89%,
								var(--color-warning) 89% 100%
							)`,
						}}
					>
						<div className="h-20 w-20 rounded-full bg-surface shadow-xs flex flex-col items-center justify-center">
							<span className="text-base font-bold text-text-primary">2,300</span>
							<span className="text-[9px] text-text-muted uppercase font-medium">Docs</span>
						</div>
					</div>
				</div>

				{/* Category list */}
				<div className="space-y-2">
					{DUMMY_DOC_TYPES.map((type) => (
						<div key={type.name} className="flex items-center justify-between text-xs">
							<div className="flex items-center gap-2">
								<span className={`h-2.5 w-2.5 rounded-full ${type.color}`} />
								<span className="text-text-secondary font-medium truncate max-w-[130px]" title={type.name}>
									{type.name}
								</span>
							</div>
							<span className="font-semibold text-text-primary">{type.count}</span>
						</div>
					))}
				</div>
			</div>

			{/* System Metrics Banner */}
			<div className="rounded-lg border border-border bg-surface-muted p-4 space-y-2">
				<div className="flex items-center justify-between text-xs">
					<span className="text-text-muted">Total Extract Chunks:</span>
					<span className="font-mono font-bold text-text-primary">21,500</span>
				</div>
				<div className="flex items-center justify-between text-xs">
					<span className="text-text-muted">Vector Index Status:</span>
					<span className="text-success font-semibold flex items-center gap-1">
						<i className="bi bi-check-circle-fill text-[10px]" /> Operational
					</span>
				</div>
			</div>
		</aside>
	);
}

