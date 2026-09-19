import { useState } from 'react';
import LineGraph from '@/components/admin/shared/LineGraph';
import DonutChart from '@/components/admin/shared/DonutChart';

type TimeRange = '7d' | '30d' | '12m';

interface DummyUploadTrend {
	label: string;
	uploads: number;
	chunks: number;
}

const DUMMY_TRENDS: Record<TimeRange, DummyUploadTrend[]> = {
	'7d': [
		{ label: 'Mon', uploads: 15, chunks: 140 },
		{ label: 'Tue', uploads: 28, chunks: 260 },
		{ label: 'Wed', uploads: 22, chunks: 210 },
		{ label: 'Thu', uploads: 42, chunks: 390 },
		{ label: 'Fri', uploads: 55, chunks: 510 },
		{ label: 'Sat', uploads: 30, chunks: 280 },
		{ label: 'Sun', uploads: 48, chunks: 430 },
	],
	'30d': [
		{ label: 'Week 1', uploads: 140, chunks: 1250 },
		{ label: 'Week 2', uploads: 210, chunks: 1950 },
		{ label: 'Week 3', uploads: 320, chunks: 2800 },
		{ label: 'Week 4', uploads: 450, chunks: 4100 },
	],
	'12m': [
		{ label: 'Jan', uploads: 180, chunks: 1600 },
		{ label: 'Feb', uploads: 290, chunks: 2700 },
		{ label: 'Mar', uploads: 410, chunks: 3800 },
		{ label: 'Apr', uploads: 560, chunks: 5200 },
		{ label: 'May', uploads: 720, chunks: 6800 },
		{ label: 'Jun', uploads: 890, chunks: 8300 },
		{ label: 'Jul', uploads: 1050, chunks: 9800 },
		{ label: 'Aug', uploads: 1240, chunks: 11500 },
		{ label: 'Sep', uploads: 1480, chunks: 13900 },
		{ label: 'Oct', uploads: 1720, chunks: 16100 },
		{ label: 'Nov', uploads: 1980, chunks: 18400 },
		{ label: 'Dec', uploads: 2300, chunks: 21500 },
	],
};

const DUMMY_DOC_TYPES = [
	{ name: 'Supreme Court Decisions', count: 950, color: 'bg-primary', cssColor: 'var(--color-primary)' },
	{ name: 'Executive Orders / Acts', count: 620, color: 'bg-info', cssColor: 'var(--color-info)' },
	{ name: 'Legal Statutes & Codes', count: 480, color: 'bg-success', cssColor: 'var(--color-success)' },
	{ name: 'Other Documents', count: 250, color: 'bg-warning', cssColor: 'var(--color-warning)' },
];

export default function AdminFilesChart() {
	const [timeRange, setTimeRange] = useState<TimeRange>('12m');
	const [activeMetric, setActiveMetric] = useState<'uploads' | 'chunks'>('uploads');

	const trendData = DUMMY_TRENDS[timeRange];

	return (
		<div className="space-y-4">
			{/* Document KPI Stat Cards */}
			<div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
				<div className="flex items-center gap-3.5 rounded-lg border border-border bg-surface p-4 shadow-xs">
					<div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10 text-primary">
						<i className="bi bi-file-earmark-text-fill text-lg" />
					</div>
					<div>
						<p className="text-xs font-medium text-text-secondary">Total Files</p>
						<p className="text-xl font-bold text-text-primary tracking-tight">2,300</p>
						<span className="text-[11px] text-success font-medium flex items-center gap-0.5 mt-0.5">
							<i className="bi bi-arrow-up-right" /> +18% mo
						</span>
					</div>
				</div>

				<div className="flex items-center gap-3.5 rounded-lg border border-border bg-surface p-4 shadow-xs">
					<div className="flex h-10 w-10 items-center justify-center rounded-lg bg-warning/10 text-warning">
						<i className="bi bi-clock-history text-lg" />
					</div>
					<div>
						<p className="text-xs font-medium text-text-secondary">Pending Review</p>
						<p className="text-xl font-bold text-text-primary tracking-tight">14</p>
						<span className="text-[11px] text-warning font-medium mt-0.5 block">Requires action</span>
					</div>
				</div>

				<div className="flex items-center gap-3.5 rounded-lg border border-border bg-surface p-4 shadow-xs">
					<div className="flex h-10 w-10 items-center justify-center rounded-lg bg-info/10 text-info">
						<i className="bi bi-gear-wide-connected text-lg" />
					</div>
					<div>
						<p className="text-xs font-medium text-text-secondary">Processing</p>
						<p className="text-xl font-bold text-text-primary tracking-tight">8</p>
						<span className="text-[11px] text-info font-medium mt-0.5 block">Active chunking</span>
					</div>
				</div>

				<div className="flex items-center gap-3.5 rounded-lg border border-border bg-surface p-4 shadow-xs">
					<div className="flex h-10 w-10 items-center justify-center rounded-lg bg-success/10 text-success">
						<i className="bi bi-check-circle-fill text-lg" />
					</div>
					<div>
						<p className="text-xs font-medium text-text-secondary">Completed</p>
						<p className="text-xl font-bold text-text-primary tracking-tight">2,210</p>
						<span className="text-[11px] text-text-muted mt-0.5 block">96% success rate</span>
					</div>
				</div>

				<div className="flex items-center gap-3.5 rounded-lg border border-border bg-surface p-4 shadow-xs">
					<div className="flex h-10 w-10 items-center justify-center rounded-lg bg-purple-500/10 text-purple-600">
						<i className="bi bi-layers-fill text-lg" />
					</div>
					<div>
						<p className="text-xs font-medium text-text-secondary">Total Chunks</p>
						<p className="text-xl font-bold text-text-primary tracking-tight">21,500</p>
						<span className="text-[11px] text-text-muted mt-0.5 block">Vector index ready</span>
					</div>
				</div>
			</div>

			{/* Main Document Analytics Section */}
			<div className="grid gap-4 lg:grid-cols-3">
				{/* Upload Volume & Chunking Trend */}
				<div className="rounded-lg border border-border bg-surface p-5 shadow-xs lg:col-span-2">
					<div className="flex flex-wrap items-center justify-between gap-3 border-b border-border pb-4">
						<div>
							<h3 className="font-semibold text-text-primary text-base flex items-center gap-2">
								<i className="bi bi-cloud-arrow-up-fill text-primary" /> Upload & Chunking Activity
							</h3>
							<p className="text-xs text-text-muted mt-0.5">
								Volume of ingested legal documents and extracted text chunks over time
							</p>
						</div>

						<div className="flex items-center gap-2">
							{/* Metric Switcher */}
							<div className="flex rounded-md border border-border bg-background p-0.5 text-xs">
								<button
									type="button"
									onClick={() => setActiveMetric('uploads')}
									className={`px-2.5 py-1 rounded-xs font-medium transition-colors ${
										activeMetric === 'uploads'
											? 'bg-primary text-primary-foreground shadow-xs'
											: 'text-text-secondary hover:text-text-primary'
									}`}
								>
									Uploads
								</button>
								<button
									type="button"
									onClick={() => setActiveMetric('chunks')}
									className={`px-2.5 py-1 rounded-xs font-medium transition-colors ${
										activeMetric === 'chunks'
											? 'bg-primary text-primary-foreground shadow-xs'
											: 'text-text-secondary hover:text-text-primary'
									}`}
								>
									Extracted Chunks
								</button>
							</div>

							{/* Time Range Switcher */}
							<div className="flex rounded-md border border-border bg-background p-0.5 text-xs">
								{(['7d', '30d', '12m'] as TimeRange[]).map((range) => (
									<button
										key={range}
										type="button"
										onClick={() => setTimeRange(range)}
										className={`px-2 py-1 rounded-xs uppercase font-medium transition-colors ${
											timeRange === range
												? 'bg-surface text-text-primary shadow-xs border border-border'
												: 'text-text-secondary hover:text-text-primary'
										}`}
									>
										{range}
									</button>
								))}
							</div>
						</div>
					</div>

					<LineGraph
						data={trendData.map((d) => ({ label: d.label, value: d[activeMetric] }))}
						ariaLabel="Upload activity chart"
						gradientId="docTrendGradient"
						heightClass="h-48"
						className="mt-6"
					/>
				</div>

				{/* Document Categories / Types Breakdown */}
				<div className="rounded-lg border border-border bg-surface p-5 shadow-xs flex flex-col justify-between">
					<div>
						<div className="flex items-center justify-between border-b border-border pb-4">
							<div>
								<h3 className="font-semibold text-text-primary text-base flex items-center gap-2">
									<i className="bi bi-folder2-open text-primary" /> Document Types
								</h3>
								<p className="text-xs text-text-muted mt-0.5">Distribution by legal category</p>
							</div>
						</div>

						<DonutChart
							segments={DUMMY_DOC_TYPES.map((d) => ({
								label: d.name,
								value: d.count,
								color: d.color,
								cssColor: d.cssColor,
							}))}
							centerValue={2300}
							centerLabel="Files"
						/>
					</div>

					<div className="mt-4 pt-3 border-t border-border flex items-center justify-between text-[11px] text-text-muted">
						<span>Vector database status</span>
						<span className="text-success font-medium flex items-center gap-1">
							<i className="bi bi-check-circle-fill text-[10px]" /> Healthy
						</span>
					</div>
				</div>
			</div>
		</div>
	);
}
