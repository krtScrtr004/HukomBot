import { useState } from 'react';

type TimeRange = '7d' | '30d' | '12m';

interface DummyGrowthData {
	label: string;
	users: number;
	active: number;
}

const DUMMY_DATA: Record<TimeRange, DummyGrowthData[]> = {
	'7d': [
		{ label: 'Mon', users: 12, active: 8 },
		{ label: 'Tue', users: 19, active: 14 },
		{ label: 'Wed', users: 15, active: 11 },
		{ label: 'Thu', users: 24, active: 18 },
		{ label: 'Fri', users: 32, active: 25 },
		{ label: 'Sat', users: 28, active: 20 },
		{ label: 'Sun', users: 38, active: 29 },
	],
	'30d': [
		{ label: 'Week 1', users: 85, active: 62 },
		{ label: 'Week 2', users: 120, active: 95 },
		{ label: 'Week 3', users: 165, active: 130 },
		{ label: 'Week 4', users: 210, active: 175 },
	],
	'12m': [
		{ label: 'Jan', users: 120, active: 90 },
		{ label: 'Feb', users: 180, active: 140 },
		{ label: 'Mar', users: 250, active: 195 },
		{ label: 'Apr', users: 310, active: 240 },
		{ label: 'May', users: 420, active: 330 },
		{ label: 'Jun', users: 510, active: 400 },
		{ label: 'Jul', users: 630, active: 510 },
		{ label: 'Aug', users: 780, active: 620 },
		{ label: 'Sep', users: 920, active: 750 },
		{ label: 'Oct', users: 1050, active: 840 },
		{ label: 'Nov', users: 1210, active: 960 },
		{ label: 'Dec', users: 1400, active: 1120 },
	],
};

const DUMMY_ROLES = [
	{ name: 'Standard Users', count: 1040, percent: 74, color: 'bg-primary' },
	{ name: 'Contributors', count: 280, percent: 20, color: 'bg-info' },
	{ name: 'Admins', count: 80, percent: 6, color: 'bg-warning' },
];

export default function AdminUsersChart() {
	const [timeRange, setTimeRange] = useState<TimeRange>('12m');
	const [activeMetric, setActiveMetric] = useState<'users' | 'active'>('users');

	const chartData = DUMMY_DATA[timeRange];
	const maxValue = Math.max(...chartData.map((d) => d[activeMetric]), 1);

	return (
		<div className="space-y-4">
			{/* Quick KPI Stat Cards */}
			<div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
				<div className="flex items-center gap-4 rounded-lg border border-border bg-surface p-4 shadow-xs">
					<div className="flex h-11 w-11 items-center justify-center rounded-lg bg-primary/10 text-primary">
						<i className="bi bi-people-fill text-xl" />
					</div>
					<div>
						<p className="text-xs font-medium text-text-secondary">Total Registered</p>
						<p className="text-2xl font-bold text-text-primary tracking-tight">1,400</p>
						<span className="text-[11px] text-success flex items-center gap-1 font-medium mt-0.5">
							<i className="bi bi-arrow-up-right" /> +14% this month
						</span>
					</div>
				</div>

				<div className="flex items-center gap-4 rounded-lg border border-border bg-surface p-4 shadow-xs">
					<div className="flex h-11 w-11 items-center justify-center rounded-lg bg-success/10 text-success">
						<i className="bi bi-person-check-fill text-xl" />
					</div>
					<div>
						<p className="text-xs font-medium text-text-secondary">Active Users</p>
						<p className="text-2xl font-bold text-text-primary tracking-tight">1,120</p>
						<span className="text-[11px] text-text-muted mt-0.5 block">80% activity rate</span>
					</div>
				</div>

				<div className="flex items-center gap-4 rounded-lg border border-border bg-surface p-4 shadow-xs">
					<div className="flex h-11 w-11 items-center justify-center rounded-lg bg-info/10 text-info">
						<i className="bi bi-person-plus-fill text-xl" />
					</div>
					<div>
						<p className="text-xs font-medium text-text-secondary">New Signups</p>
						<p className="text-2xl font-bold text-text-primary tracking-tight">190</p>
						<span className="text-[11px] text-success flex items-center gap-1 font-medium mt-0.5">
							<i className="bi bi-arrow-up-right" /> +8% vs last week
						</span>
					</div>
				</div>

				<div className="flex items-center gap-4 rounded-lg border border-border bg-surface p-4 shadow-xs">
					<div className="flex h-11 w-11 items-center justify-center rounded-lg bg-warning/10 text-warning">
						<i className="bi bi-shield-lock-fill text-xl" />
					</div>
					<div>
						<p className="text-xs font-medium text-text-secondary">Administrators</p>
						<p className="text-2xl font-bold text-text-primary tracking-tight">80</p>
						<span className="text-[11px] text-text-muted mt-0.5 block">Security verified</span>
					</div>
				</div>
			</div>

			{/* Main Charts Section */}
			<div className="grid gap-4 lg:grid-cols-3">
				{/* Growth Chart */}
				<div className="rounded-lg border border-border bg-surface p-5 shadow-xs lg:col-span-2">
					<div className="flex flex-wrap items-center justify-between gap-3 border-b border-border pb-4">
						<div>
							<h3 className="font-semibold text-text-primary text-base flex items-center gap-2">
								<i className="bi bi-graph-up-arrow text-primary" /> User Growth & Engagement
							</h3>
							<p className="text-xs text-text-muted mt-0.5">
								Overview of registered users and active sessions over time
							</p>
						</div>

						<div className="flex items-center gap-2">
							{/* Metric Switcher */}
							<div className="flex rounded-md border border-border bg-background p-0.5 text-xs">
								<button
									type="button"
									onClick={() => setActiveMetric('users')}
									className={`px-2.5 py-1 rounded-xs font-medium transition-colors ${
										activeMetric === 'users'
											? 'bg-primary text-primary-foreground shadow-xs'
											: 'text-text-secondary hover:text-text-primary'
									}`}
								>
									Total Users
								</button>
								<button
									type="button"
									onClick={() => setActiveMetric('active')}
									className={`px-2.5 py-1 rounded-xs font-medium transition-colors ${
										activeMetric === 'active'
											? 'bg-primary text-primary-foreground shadow-xs'
											: 'text-text-secondary hover:text-text-primary'
									}`}
								>
									Active Users
								</button>
							</div>

							{/* Range Switcher */}
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

					{/* SVG Line / Area Graph */}
					<div className="mt-6">
						<div className="relative h-48 px-1">
							{/* Grid lines */}
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
									aria-label="User growth chart"
								>
									<defs>
										<linearGradient id="userGrowthGradient" x1="0" y1="0" x2="0" y2="1">
											<stop offset="0%" stopColor="var(--color-primary)" stopOpacity="0.3" />
											<stop offset="100%" stopColor="var(--color-primary)" stopOpacity="0.0" />
										</linearGradient>
									</defs>

									{/* Area Fill */}
									<polygon
										fill="url(#userGrowthGradient)"
										points={`0,160 ${chartData
											.map(
												(d, i) =>
													`${(i / Math.max(chartData.length - 1, 1)) * 800},${
														160 - (d[activeMetric] / maxValue) * 140
													}`,
											)
											.join(' ')} 800,160`}
									/>

									{/* Polyline */}
									<polyline
										fill="none"
										stroke="var(--color-primary)"
										strokeWidth="3"
										strokeLinecap="round"
										strokeLinejoin="round"
										points={chartData
											.map(
												(d, i) =>
													`${(i / Math.max(chartData.length - 1, 1)) * 800},${
														160 - (d[activeMetric] / maxValue) * 140
													}`,
											)
											.join(' ')}
									/>

									{/* Interactive Data Points */}
									{chartData.map((d, i) => {
										const cx = (i / Math.max(chartData.length - 1, 1)) * 800;
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
								{chartData.map((d) => (
									<span key={d.label}>{d.label}</span>
								))}
							</div>
						</div>
					</div>
				</div>

				{/* Role Breakdown Distribution */}
				<div className="rounded-lg border border-border bg-surface p-5 shadow-xs flex flex-col justify-between">
					<div>
						<div className="flex items-center justify-between border-b border-border pb-4">
							<div>
								<h3 className="font-semibold text-text-primary text-base flex items-center gap-2">
									<i className="bi bi-pie-chart-fill text-info" /> Role Distribution
								</h3>
								<p className="text-xs text-text-muted mt-0.5">User permissions breakdown</p>
							</div>
						</div>

						{/* Conic Gradient Donut Visual */}
						<div className="my-6 flex items-center justify-center">
							<div
								className="relative h-36 w-36 rounded-full shadow-inner flex items-center justify-center"
								style={{
									background: `conic-gradient(
										var(--color-primary) 0% 74%,
										var(--color-info) 74% 94%,
										var(--color-warning) 94% 100%
									)`,
								}}
							>
								<div className="h-24 w-24 rounded-full bg-surface shadow-xs flex flex-col items-center justify-center">
									<span className="text-xl font-bold text-text-primary">1,400</span>
									<span className="text-[10px] text-text-muted uppercase font-medium">Users</span>
								</div>
							</div>
						</div>

						{/* Legend List */}
						<div className="space-y-2.5">
							{DUMMY_ROLES.map((role) => (
								<div key={role.name} className="flex items-center justify-between text-xs">
									<div className="flex items-center gap-2">
										<span className={`h-2.5 w-2.5 rounded-full ${role.color}`} />
										<span className="font-medium text-text-secondary">{role.name}</span>
									</div>
									<div className="flex items-center gap-3">
										<span className="text-text-muted">{role.percent}%</span>
										<strong className="text-text-primary font-semibold w-10 text-right">
											{role.count}
										</strong>
									</div>
								</div>
							))}
						</div>
					</div>

					<div className="mt-4 pt-3 border-t border-border flex items-center justify-between text-[11px] text-text-muted">
						<span>Data updated live</span>
						<span className="text-primary font-medium cursor-pointer hover:underline">
							View security audit
						</span>
					</div>
				</div>
			</div>
		</div>
	);
}

