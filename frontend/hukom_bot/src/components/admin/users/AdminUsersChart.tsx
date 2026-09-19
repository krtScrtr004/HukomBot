import type { AdminUserAnalytics } from '@/types/admin';

interface AdminUsersChartProps {
	analytics: AdminUserAnalytics | null;
	loading?: boolean;
}

const MONTH_LABELS: { key: keyof AdminUserAnalytics['monthly_registration_count']; label: string }[] = [
	{ key: 'january', label: 'Jan' },
	{ key: 'february', label: 'Feb' },
	{ key: 'march', label: 'Mar' },
	{ key: 'april', label: 'Apr' },
	{ key: 'may', label: 'May' },
	{ key: 'june', label: 'Jun' },
	{ key: 'july', label: 'Jul' },
	{ key: 'august', label: 'Aug' },
	{ key: 'september', label: 'Sep' },
	{ key: 'october', label: 'Oct' },
	{ key: 'november', label: 'Nov' },
	{ key: 'december', label: 'Dec' },
];

export default function AdminUsersChart({ analytics, loading }: AdminUsersChartProps) {
	// Registered & Active counts
	const registeredCount = analytics?.registered_count ?? 0;
	const activeCount = analytics?.active_count ?? 0;
	const inactiveCount = analytics?.inactive_count ?? 0;
	const newCount = analytics?.new_registration_count ?? 0;

	const activityRate = registeredCount > 0 ? Math.round((activeCount / registeredCount) * 100) : 0;

	// Monthly registrations line chart data
	const monthlyData = MONTH_LABELS.map(({ key, label }) => ({
		label,
		value: analytics?.monthly_registration_count?.[key] ?? 0,
	}));

	const maxMonthlyValue = Math.max(...monthlyData.map((d) => d.value), 1);

	// Role counts pie chart data
	const standardCount = analytics?.role_count?.standard ?? 0;
	const contributorCount = analytics?.role_count?.contributor ?? 0;
	const adminCount = analytics?.role_count?.admin ?? 0;
	const totalRoleUsers = standardCount + contributorCount + adminCount;

	const standardPct = totalRoleUsers > 0 ? Math.round((standardCount / totalRoleUsers) * 100) : 0;
	const contributorPct = totalRoleUsers > 0 ? Math.round((contributorCount / totalRoleUsers) * 100) : 0;
	const adminPct = totalRoleUsers > 0 ? Math.max(0, 100 - standardPct - contributorPct) : 0;

	// Conic gradient angles for Donut/Pie Chart
	const deg1 = (standardPct / 100) * 360;
	const deg2 = deg1 + (contributorPct / 100) * 360;

	return (
		<div className="space-y-4">
			{/* KPI Stat Cards */}
			<div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
				<div className="flex items-center gap-4 rounded-sm border border-border bg-surface p-4 shadow-xs">
					<div className="flex h-11 w-11 items-center justify-center rounded-sm bg-primary/10 text-primary">
						<i className="bi bi-people-fill text-xl" />
					</div>
					<div>
						<p className="text-xs font-medium text-text-secondary">Total Registered</p>
						<p className="text-2xl font-bold text-text-primary tracking-tight">
							{loading && !analytics ? '...' : registeredCount.toLocaleString()}
						</p>
						<span className="text-[11px] text-text-muted mt-0.5 block font-medium">All registered accounts</span>
					</div>
				</div>

				<div className="flex items-center gap-4 rounded-sm border border-border bg-surface p-4 shadow-xs">
					<div className="flex h-11 w-11 items-center justify-center rounded-sm bg-success/10 text-success">
						<i className="bi bi-person-check-fill text-xl" />
					</div>
					<div>
						<p className="text-xs font-medium text-text-secondary">Active Users</p>
						<p className="text-2xl font-bold text-text-primary tracking-tight">
							{loading && !analytics ? '...' : activeCount.toLocaleString()}
						</p>
						<span className="text-[11px] text-success font-medium mt-0.5 block">
							{activityRate}% activity rate
						</span>
					</div>
				</div>

				<div className="flex items-center gap-4 rounded-sm border border-border bg-surface p-4 shadow-xs">
					<div className="flex h-11 w-11 items-center justify-center rounded-sm bg-info/10 text-info">
						<i className="bi bi-person-plus-fill text-xl" />
					</div>
					<div>
						<p className="text-xs font-medium text-text-secondary">New Signups</p>
						<p className="text-2xl font-bold text-text-primary tracking-tight">
							{loading && !analytics ? '...' : newCount.toLocaleString()}
						</p>
						<span className="text-[11px] text-text-muted mt-0.5 block">Recent registrations</span>
					</div>
				</div>

				<div className="flex items-center gap-4 rounded-sm border border-border bg-surface p-4 shadow-xs">
					<div className="flex h-11 w-11 items-center justify-center rounded-sm bg-secondary/15 text-text-secondary">
						<i className="bi bi-person-dash-fill text-xl" />
					</div>
					<div>
						<p className="text-xs font-medium text-text-secondary">Inactive Users</p>
						<p className="text-2xl font-bold text-text-primary tracking-tight">
							{loading && !analytics ? '...' : inactiveCount.toLocaleString()}
						</p>
						<span className="text-[11px] text-text-muted mt-0.5 block">Dormant accounts</span>
					</div>
				</div>
			</div>

			{/* Main Analytics Grid: Line Graph & Pie Chart */}
			<div className="grid gap-4 lg:grid-cols-3">
				{/* Monthly Registration Line Graph */}
				<div className="rounded-sm border border-border bg-surface p-5 shadow-xs lg:col-span-2">
					<div className="flex items-center justify-between border-b border-border pb-4">
						<div>
							<h3 className="font-semibold text-text-primary text-base flex items-center gap-2">
								<i className="bi bi-graph-up-arrow text-primary" /> Monthly Registration Trend
							</h3>
							<p className="text-xs text-text-muted mt-0.5">
								New user registrations by month (Jan – Dec)
							</p>
						</div>
						<span className="text-xs text-text-muted font-medium bg-surface-muted px-2.5 py-1 rounded-md border border-border">
							Annual Overview
						</span>
					</div>

					{/* SVG Line Graph with Y-Axis Scale */}
					<div className="mt-6">
						<div className="relative h-60 pl-10 pr-2">
							{/* Y-Axis Scale Tick Labels */}
							<div className="absolute left-0 top-0 w-8 text-right text-[10px] text-text-muted font-mono leading-none -translate-y-1/2">
								{maxMonthlyValue.toLocaleString()}
							</div>
							<div className="absolute left-0 top-1/3 w-8 text-right text-[10px] text-text-muted font-mono leading-none -translate-y-1/2">
								{Math.round((maxMonthlyValue * 2) / 3).toLocaleString()}
							</div>
							<div className="absolute left-0 top-2/3 w-8 text-right text-[10px] text-text-muted font-mono leading-none -translate-y-1/2">
								{Math.round(maxMonthlyValue / 3).toLocaleString()}
							</div>
							<div className="absolute left-0 bottom-6 w-8 text-right text-[10px] text-text-muted font-mono leading-none translate-y-1/2">
								0
							</div>

							{/* Background Grid lines */}
							<div className="absolute left-10 right-2 top-0 border-t border-border/40" />
							<div className="absolute left-10 right-2 top-1/3 border-t border-border/30 border-dashed" />
							<div className="absolute left-10 right-2 top-2/3 border-t border-border/30 border-dashed" />
							<div className="absolute left-10 right-2 bottom-6 border-t border-border" />

							{/* SVG Plot */}
							<div className="absolute left-10 right-2 bottom-6 top-2">
								<svg
									viewBox="0 0 800 160"
									preserveAspectRatio="none"
									className="h-full w-full overflow-visible"
									role="img"
									aria-label="Monthly registration line graph"
								>
									<defs>
										<linearGradient id="userMonthlyGradient" x1="0" y1="0" x2="0" y2="1">
											<stop offset="0%" stopColor="var(--color-primary)" stopOpacity="0.35" />
											<stop offset="100%" stopColor="var(--color-primary)" stopOpacity="0.0" />
										</linearGradient>
									</defs>

									{/* Area Gradient */}
									<polygon
										fill="url(#userMonthlyGradient)"
										points={`0,160 ${monthlyData
											.map(
												(d, i) =>
													`${(i / Math.max(monthlyData.length - 1, 1)) * 800},${
														160 - (d.value / maxMonthlyValue) * 140
													}`,
											)
											.join(' ')} 800,160`}
									/>

									{/* Line Polyline */}
									<polyline
										fill="none"
										stroke="var(--color-primary)"
										strokeWidth="3"
										strokeLinecap="round"
										strokeLinejoin="round"
										points={monthlyData
											.map(
												(d, i) =>
													`${(i / Math.max(monthlyData.length - 1, 1)) * 800},${
														160 - (d.value / maxMonthlyValue) * 140
													}`,
											)
											.join(' ')}
									/>

									{/* Interactive Data Point Dots */}
									{monthlyData.map((d, i) => {
										const cx = (i / Math.max(monthlyData.length - 1, 1)) * 800;
										const cy = 160 - (d.value / maxMonthlyValue) * 140;
										return (
											<g key={d.label} className="group cursor-pointer">
												<circle
													cx={cx}
													cy={cy}
													r="3"
													className="fill-surface stroke-primary transition-all group-hover:r-7"
													strokeWidth="1"
												/>
												<title>{`${d.label}: ${d.value} registrations`}</title>
											</g>
										);
									})}
								</svg>
							</div>

							{/* X-Axis Month Labels */}
							<div className="absolute left-10 right-2 bottom-0 flex justify-between text-[11px] text-text-muted font-medium">
								{monthlyData.map((d) => (
									<span key={d.label}>{d.label}</span>
								))}
							</div>
						</div>
					</div>
				</div>

				{/* User Role Count Pie / Donut Chart */}
				<div className="rounded-sm border border-border bg-surface p-5 shadow-xs flex flex-col justify-between">
					<div>
						<div className="flex items-center justify-between border-b border-border pb-4">
							<div>
								<h3 className="font-semibold text-text-primary text-base flex items-center gap-2">
									<i className="bi bi-pie-chart-fill text-info" /> User Role Breakdown
								</h3>
								<p className="text-xs text-text-muted mt-0.5">Role distribution ratio</p>
							</div>
						</div>

						{/* Conic Gradient Donut/Pie Visual */}
						<div className="my-6 flex items-center justify-center">
							<div
								className="relative h-36 w-36 rounded-full shadow-inner flex items-center justify-center transition-all"
								style={{
									background: totalRoleUsers > 0
										? `conic-gradient(
											var(--color-primary) 0deg ${deg1}deg,
											var(--color-info) ${deg1}deg ${deg2}deg,
											var(--color-warning) ${deg2}deg 360deg
										)`
										: 'var(--color-surface-muted)',
								}}
							>
								<div className="h-24 w-24 rounded-full bg-surface shadow-xs flex flex-col items-center justify-center">
									<span className="text-xl font-bold text-text-primary">
										{totalRoleUsers.toLocaleString()}
									</span>
									<span className="text-[10px] text-text-muted uppercase font-medium">Total Roles</span>
								</div>
							</div>
						</div>

						{/* Role Legend List */}
						<div className="space-y-2.5">
							{[
								{ name: 'Standard Users', count: standardCount, percent: standardPct, color: 'bg-primary' },
								{ name: 'Contributors', count: contributorCount, percent: contributorPct, color: 'bg-info' },
								{ name: 'Administrators', count: adminCount, percent: adminPct, color: 'bg-warning' },
							].map((role) => (
								<div key={role.name} className="flex items-center justify-between text-xs">
									<div className="flex items-center gap-2">
										<span className={`h-2.5 w-2.5 rounded-full ${role.color}`} />
										<span className="font-medium text-text-secondary">{role.name}</span>
									</div>
									<div className="flex items-center gap-3">
										<span className="text-text-muted">{role.percent}%</span>
										<strong className="text-text-primary font-semibold w-10 text-right">
											{role.count.toLocaleString()}
										</strong>
									</div>
								</div>
							))}
						</div>
					</div>

					<div className="mt-4 pt-3 border-t border-border flex items-center justify-between text-[11px] text-text-muted">
						<span>Live API analytics</span>
						<span className="text-success font-medium flex items-center gap-1">
							<i className="bi bi-broadcast text-xs" /> Realtime SSE
						</span>
					</div>
				</div>
			</div>
		</div>
	);
}
