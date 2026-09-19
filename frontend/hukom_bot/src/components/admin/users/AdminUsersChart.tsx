import type { AdminUserAnalytics } from '@/types/admin';
import LineGraph from '@/components/admin/shared/LineGraph';
import DonutChart from '@/components/admin/shared/DonutChart';

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

	// Role counts pie chart data
	const standardCount = analytics?.role_count?.standard ?? 0;
	const contributorCount = analytics?.role_count?.contributor ?? 0;
	const adminCount = analytics?.role_count?.admin ?? 0;

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
					<div className="flex h-11 w-11 items-center justify-center rounded-sm bg-primary/10 text-primary">
						<i className="bi bi-person-check-fill text-xl text-success" />
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
					<div className="flex h-11 w-11 items-center justify-center rounded-sm bg-primary/10 text-primary">
						<i className="bi bi-person-plus-fill text-xl text-info" />
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
						<i className="bi bi-person-dash-fill text-xl text-primary" />
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

					<LineGraph
						data={monthlyData}
						ariaLabel="Monthly registration line graph"
						gradientId="userMonthlyGradient"
						heightClass="h-60"
						className="mt-6"
					/>
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

						<DonutChart
							segments={[
								{ label: 'Standard Users', value: standardCount, color: 'bg-primary', cssColor: 'var(--color-primary)' },
								{ label: 'Contributors', value: contributorCount, color: 'bg-info', cssColor: 'var(--color-info)' },
								{ label: 'Administrators', value: adminCount, color: 'bg-warning', cssColor: 'var(--color-warning)' },
							]}
							centerLabel="Total Roles"
						/>
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
