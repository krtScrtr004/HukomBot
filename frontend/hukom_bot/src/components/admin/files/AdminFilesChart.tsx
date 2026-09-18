import { useState } from 'react';

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
	{ name: 'Supreme Court Decisions', count: 950, percent: 41, color: 'bg-primary' },
	{ name: 'Executive Orders / Acts', count: 620, percent: 27, color: 'bg-info' },
	{ name: 'Legal Statutes & Codes', count: 480, percent: 21, color: 'bg-success' },
	{ name: 'Other Documents', count: 250, percent: 11, color: 'bg-warning' },
];

export default function AdminFilesChart() {
	const [timeRange, setTimeRange] = useState<TimeRange>('12m');
	const [activeMetric, setActiveMetric] = useState<'uploads' | 'chunks'>('uploads');

	const trendData = DUMMY_TRENDS[timeRange];
	const maxValue = Math.max(...trendData.map((d) => d[activeMetric]), 1);

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

					{/* SVG Trend Graph */}
					<div className="mt-6">
						<div className="relative h-48 px-1">
							{/* Background Grid Lines */}
							<div className="absolute inset-x-0 top-0 border-t border-border/40" />
							<div className="absolute inset-x-0 top-1/3 border-t border-border/30 border-dashed" />
							<div className="absolute inset-x-0 top-2/3 border-t border-border/30 border-dashed" />
							<div className="absolute inset-x-0 bottom-6 border-t border-border" />

							{/* SVG Plot */}
							<div className="absolute inset-x-1 bottom-6 top-2">
								<svg
									viewBox="0 0 800 160"
									preserveAspectRatio="none"
									className="h-full w-full overflow-visible"
									role="img"
									aria-label="Upload activity chart"
								>
									<defs>
										<linearGradient id="docTrendGradient" x1="0" y1="0" x2="0" y2="1">
											<stop offset="0%" stopColor="var(--color-primary)" stopOpacity="0.35" />
											<stop offset="100%" stopColor="var(--color-primary)" stopOpacity="0.0" />
										</linearGradient>
									</defs>

									{/* Gradient Area */}
									<polygon
										fill="url(#docTrendGradient)"
										points={`0,160 ${trendData
											.map(
												(d, i) =>
													`${(i / Math.max(trendData.length - 1, 1)) * 800},${
														160 - (d[activeMetric] / maxValue) * 140
													}`,
											)
											.join(' ')} 800,160`}
									/>

									{/* Line */}
									<polyline
										fill="none"
										stroke="var(--color-primary)"
										strokeWidth="3"
										strokeLinecap="round"
										strokeLinejoin="round"
										points={trendData
											.map(
												(d, i) =>
													`${(i / Math.max(trendData.length - 1, 1)) * 800},${
														160 - (d[activeMetric] / maxValue) * 140
													}`,
											)
											.join(' ')}
									/>

									{/* Data Point Circles */}
									{trendData.map((d, i) => {
										const cx = (i / Math.max(trendData.length - 1, 1)) * 800;
										const cy = 160 - (d[activeMetric] / maxValue) * 140;
										return (
											<g key={d.label} className="group cursor-pointer">
												<circle
													cx={cx}
													cy={cy}
													r="5"
													className="fill-surface stroke-primary transition-all group-hover:r-7"
													strokeWidth="3"
												/>
												<title>{`${d.label}: ${d[activeMetric]} ${activeMetric}`}</title>
											</g>
										);
									})}
								</svg>
							</div>

							{/* X-Axis Labels */}
							<div className="absolute inset-x-1 bottom-0 flex justify-between text-[11px] text-text-muted font-medium">
								{trendData.map((d) => (
									<span key={d.label}>{d.label}</span>
								))}
							</div>
						</div>
					</div>
				</div>

				{/* Document Categories / Types Breakdown */}
				<div className="rounded-lg border border-border bg-surface p-5 shadow-xs flex flex-col justify-between">
					<div>
						<div className="flex items-center justify-between border-b border-border pb-4">
							<div>
								<h3 className="font-semibold text-text-primary text-base flex items-center gap-2">
									<i className="bi bi-[folder2-open] text-primary" /> Document Types
								</h3>
								<p className="text-xs text-text-muted mt-0.5">Distribution by legal category</p>
							</div>
						</div>

						{/* Conic Gradient Donut Visual */}
						<div className="my-6 flex items-center justify-center">
							<div
								className="relative h-36 w-36 rounded-full shadow-inner flex items-center justify-center"
								style={{
									background: `conic-gradient(
										var(--color-primary) 0% 41%,
										var(--color-info) 41% 68%,
										var(--color-success) 68% 89%,
										var(--color-warning) 89% 100%
									)`,
								}}
							>
								<div className="h-24 w-24 rounded-full bg-surface shadow-xs flex flex-col items-center justify-center">
									<span className="text-xl font-bold text-text-primary">2,300</span>
									<span className="text-[10px] text-text-muted uppercase font-medium">Files</span>
								</div>
							</div>
						</div>

						{/* Types List */}
						<div className="space-y-2.5">
							{DUMMY_DOC_TYPES.map((docType) => (
								<div key={docType.name} className="flex items-center justify-between text-xs">
									<div className="flex items-center gap-2">
										<span className={`h-2.5 w-2.5 rounded-full ${docType.color}`} />
										<span className="font-medium text-text-secondary truncate max-w-[140px]" title={docType.name}>
											{docType.name}
										</span>
									</div>
									<div className="flex items-center gap-3">
										<span className="text-text-muted">{docType.percent}%</span>
										<strong className="text-text-primary font-semibold w-10 text-right">
											{docType.count}
										</strong>
									</div>
								</div>
							))}
						</div>
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

