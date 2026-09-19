import { useEffect, useRef, useState } from 'react';
import { EVENT_BASE_URL_V1 } from '@/services/apiClient'; 
import { useAdmin } from '@/contexts/AdminContext';
import type { AdminDashboardData, AdminDashboardDateRange } from '@/types/admin';
import PendingFilesList from '@/components/PendingFilesList';
import LoadingSpinner from '@/components/workspace/shared/LoadingSpinner';

function isDashboardData(value: unknown): value is AdminDashboardData {
	if (!value || typeof value !== 'object') return false;

	const data = value as Record<string, unknown>;
	const status = data.document_status_count;
	const weekly = data.document_weekly_count;
	return typeof data.active_user_count === 'number' &&
		typeof data.documents_count === 'number' &&
		typeof data.chunks_count === 'number' &&
		!!status && typeof status === 'object' &&
		['pending', 'ongoing', 'completed', 'failed', 'rejected'].every((key) => typeof (status as Record<string, unknown>)[key] === 'number') &&
		!!weekly && typeof weekly === 'object' &&
		['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'].every((key) => typeof (weekly as Record<string, unknown>)[key] === 'number') &&
		!!data.document_type_count && typeof data.document_type_count === 'object';
}

function parseDashboardEvent(eventData: string): AdminDashboardData | null {
	try {
		const parsed: unknown = JSON.parse(eventData.trim());
		if (!parsed || typeof parsed !== 'object') return null;

		const payload = parsed as {
			success?: unknown;
			data?: unknown;
		};

		if ('success' in payload && payload.success !== true) return null;
		const data = 'data' in payload ? payload.data : parsed;
		return isDashboardData(data) ? data : null;
	} catch {
		return null;
	}
}

interface DashboardErrorStateProps {
	error: string;
	onRetry: () => void;
	loading: boolean;
}

function DashboardErrorState({
	error,
	onRetry,
	loading,
}: DashboardErrorStateProps) {
	return (
		<div
			className="flex min-h-72 items-center justify-center rounded-sm border border-danger/30 bg-danger/5 p-6"
			role="alert"
		>
			<div className="max-w-md text-center">
				<div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-danger/10 text-danger">
					<i className="bi bi-cloud-slash text-xl" aria-hidden="true" />
				</div>
				<h2 className="mt-4 text-lg font-semibold">Dashboard unavailable</h2>
				<p className="mt-2 text-sm leading-6 text-text-secondary">
					We couldn&apos;t load the latest dashboard data. Check your
					connection and try again.
				</p>
				<p className="mt-3 rounded-sm bg-background/60 px-3 py-2 text-xs text-danger">
					{error}
				</p>
				<button
					type="button"
					onClick={onRetry}
					disabled={loading}
					className="mt-5 inline-flex items-center gap-2 rounded-sm bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-60"
				>
					<i
						className={`bi ${loading ? 'bi-arrow-repeat animate-spin' : 'bi-arrow-clockwise'}`}
						aria-hidden="true"
					/>
					{loading ? 'Retrying...' : 'Try again'}
				</button>
			</div>
		</div>
	);
}

export default function AdminDashboardPage() {
	const { state, fetchDashboard, fetchPendingFiles, dispatch } = useAdmin();
	const { dashboard } = state;
	const initRef = useRef(false);
	const [dateRange, setDateRange] = useState<AdminDashboardDateRange>('last_30_days');
	const weeklyMax = dashboard.data
		? Math.max(...Object.values(dashboard.data.document_weekly_count), 1)
		: 1;
	const documentTotal = dashboard.data?.documents_count ?? 1;
	const dateRangeLabels: Record<AdminDashboardDateRange, string> = {
		today: 'Today', yesterday: 'Yesterday', this_week: 'This week', last_week: 'Last week', this_month: 'This month', last_month: 'Last month', last_7_days: 'Last 7 days', last_30_days: 'Last 30 days', last_90_days: 'Last 90 days', last_6_months: 'Last 6 months', this_year: 'This year', last_year: 'Last year', all_time: 'All time',
	};

	useEffect(() => {
		if (initRef.current) return;
		initRef.current = true;
		void fetchPendingFiles();
	}, [fetchPendingFiles]);

	useEffect(() => {
		void fetchDashboard(dateRange);
	}, [dateRange, fetchDashboard]);

	useEffect(() => {
		let es: EventSource | null = null;
		const openStream = () => {
			if (document.hidden || es) return;
			es = new EventSource(`${EVENT_BASE_URL_V1}/admin/dashboard?date_range=${encodeURIComponent(dateRange)}`, {
				withCredentials: true,
			});
			es.onmessage = (event) => {
				if (event.data == null) return;
				const data = parseDashboardEvent(event.data);
				if (data) {
					dispatch({
						type: 'DISPATCH_DASHBOARD_UPDATE',
						payload: data,
					});
				}
			};
		};
		openStream();
		const handleVisibility = () => {
			if (document.hidden) {
				es?.close();
				es = null;
			} else {
				openStream();
			}
		};
		document.addEventListener('visibilitychange', handleVisibility);
		return () => {
			es?.close();
			document.removeEventListener('visibilitychange', handleVisibility);
		};
	}, [dateRange, dispatch]);

	return (
		<div className=" space-y-8">
			<header className="flex flex-col justify-between gap-4 md:flex-row md:items-end">
				<div>
					<p className="text-sm text-text-secondary">
						Friday, September 11, 2026
					</p>
					<h1 className="mt-1 text-3xl font-semibold tracking-tight">
						Dashboard
					</h1>
					<p className="mt-2 text-sm text-text-secondary">
						Welcome back,{' '}
						{state.dashboard.data ? 'Kurtz' : 'Administrator'}. Here
						is today&apos;s overview.
					</p>
				</div>
				
				<div className="flex gap-2">
					<div
						className="flex items-center gap-2 rounded-sm border border-border bg-surface px-3 py-2 text-sm text-text-secondary hover:bg-hover"
					>
						<i className="bi bi-calendar3" aria-hidden="true" />
						<select
							aria-label="Dashboard date range"
							value={dateRange}
							onChange={(event) => setDateRange(event.target.value as AdminDashboardDateRange)}
							className="cursor-pointer bg-transparent outline-none"
						>
							{Object.entries(dateRangeLabels).map(([value, label]) => (
								<option key={value} value={value}>{label}</option>
							))}
						</select>
					</div>
				</div>
			</header>

			<section aria-label="Dashboard statistics">
				{dashboard.loading && !dashboard.data ? (
					<div className="flex min-h-72 items-center justify-center rounded-sm border border-border bg-surface">
						<LoadingSpinner label="Loading dashboard" size="lg" />
					</div>
				) : dashboard.error && !dashboard.data ? (
					<DashboardErrorState
						error={dashboard.error}
						onRetry={() => void fetchDashboard()}
						loading={dashboard.loading}
					/>
				) : dashboard.data ? (
					<div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
						{[
							[
								'Total Users',
								dashboard.data.active_user_count,
								'bi-people-fill',
								'text-info',
							],
							[
								'Documents Count',
								dashboard.data.documents_count,
								'bi-file-earmark-text-fill',
								'text-primary',
							],
							[
								'Chunks Processed',
								dashboard.data.chunks_count,
								'bi-layers-fill',
								'text-warning',
							],
							[
								'Processing Activity',
								dashboard.data.document_status_count.ongoing,
								'bi-activity',
								'text-success',
							],
						].map(([label, value, icon, color]) => (
							<article
								key={label}
								className="flex items-center gap-5 rounded-sm border border-border bg-surface p-5 shadow-sm transition-shadow hover:shadow-md"
							>
								<span
									className={`flex h-10 w-10 items-center justify-center rounded-sm bg-hover ${color}`}
								>
									<i
										className={`bi ${icon} text-lg`}
										aria-hidden="true"
									/>
								</span>

								<div className="flex flex-col">
									<p className="text-sm text-text-secondary">
										{label}
									</p>

									<p className="mt-1 text-2xl font-semibold tracking-tight">
										{value.toLocaleString()}
									</p>
								</div>
							</article>
						))}
					</div>
				) : null}

				{dashboard.error && dashboard.data ? (
					<div className="mt-4 flex items-center justify-between gap-4 rounded-sm border border-warning/30 bg-warning/5 px-4 py-3" role="alert">
						<div className="flex items-start gap-3">
							<i className="bi bi-exclamation-triangle mt-0.5 text-warning" aria-hidden="true" />
							<div><p className="text-sm font-medium">Showing previously loaded data</p><p className="mt-1 text-xs text-text-secondary">The latest dashboard refresh failed: {dashboard.error}</p></div>
						</div>
						<button type="button" onClick={() => void fetchDashboard()} disabled={dashboard.loading} className="shrink-0 rounded-sm border border-warning/30 px-3 py-1.5 text-xs font-medium text-warning hover:bg-warning/10 disabled:opacity-60">{dashboard.loading ? 'Retrying...' : 'Retry'}</button>
					</div>
				) : null}
			</section>

			{dashboard.data && (
				<>
					<section
						className="grid gap-5.5 xl:grid-cols-[0.8fr_1.2fr]"
						aria-label="Analytics overview"
					>
						<article className="rounded-sm border border-border bg-surface p-5">
							<div className="flex items-center justify-between">
								<div>
									<h2 className="font-semibold">
										Document status
									</h2>

									<p className="mt-1 text-xs text-text-secondary">
										Current distribution
									</p>
								</div>
								<i
									className="bi bi-pie-chart text-primary"
									aria-hidden="true"
								/>
							</div>

							<div className="mt-6 flex items-center gap-6">
								<div
									className="relative h-36 w-36 shrink-0 rounded-full"
									style={{
										background: `conic-gradient(var(--color-success) 0 ${(dashboard.data.document_status_count.completed / Math.max(dashboard.data.documents_count, 1)) * 100}%, var(--color-info) 0 ${((dashboard.data.document_status_count.completed + dashboard.data.document_status_count.ongoing) / Math.max(dashboard.data.documents_count, 1)) * 100}%, var(--color-warning) 0 ${((dashboard.data.document_status_count.completed + dashboard.data.document_status_count.ongoing + dashboard.data.document_status_count.pending) / Math.max(dashboard.data.documents_count, 1)) * 100}%, var(--color-danger) 0 100%)`,
									}}
								>
									<div className="absolute inset-4 flex flex-col items-center justify-center rounded-full bg-surface">
										<strong className="text-xl">
											{dashboard.data.documents_count}
										</strong>
										<span className="text-[10px] text-text-muted">
											documents
										</span>
									</div>
								</div>

								<div className="space-y-3 text-xs">
									{[
										[
											'Completed',
											dashboard.data.document_status_count.completed,
											'bg-success',
										],
										[
											'Ongoing',
											dashboard.data.document_status_count.ongoing,
											'bg-info',
										],
										[
											'Pending',
											dashboard.data.document_status_count.pending,
											'bg-warning',
										],
										[
											'Failed / rejected',
											dashboard.data.document_status_count.failed +
											dashboard.data.document_status_count.rejected,
											'bg-danger',
										],
									].map(([name, value, color]) => (
										<div
											key={name}
											className="flex items-center justify-between gap-6"
										>
											<span className="flex items-center gap-2 text-text-secondary text-1">
												<i
													className={`h-2 w-2 rounded-full ${color}`}
												/>
												{name}
											</span>

											<strong>{value}</strong>
										</div>
									))}
								</div>
							</div>
						</article>

						<article className="rounded-sm border border-border bg-surface p-5">
							<div className="flex items-center justify-between">
								<div>
									<h2 className="font-semibold">
										Processing activity
									</h2>
									<p className="mt-1 text-xs text-text-secondary">
										Documents and chunks over the last 7
										days
									</p>
								</div>
								<i
									className="bi bi-bar-chart-line text-primary"
									aria-hidden="true"
								/>
							</div>

							<div className="relative mt-8 h-44 pl-10 pr-2">
								{/* Y-Axis Scale Tick Labels */}
								<div className="absolute left-0 top-0 w-8 text-right text-[10px] text-text-muted font-mono leading-none -translate-y-1/2">
									{weeklyMax.toLocaleString()}
								</div>
								<div className="absolute left-0 top-1/2 w-8 text-right text-[10px] text-text-muted font-mono leading-none -translate-y-1/2">
									{Math.round(weeklyMax / 2).toLocaleString()}
								</div>
								<div className="absolute left-0 bottom-6 w-8 text-right text-[10px] text-text-muted font-mono leading-none translate-y-1/2">
									0
								</div>

								{/* Background Grid Lines */}
								<div className="absolute left-10 right-2 top-0 border-t border-border" />
								<div className="absolute left-10 right-2 top-1/2 border-t border-border/60 border-dashed" />
								<div className="absolute left-10 right-2 bottom-6 border-t border-border" />

								{/* SVG Plot */}
								<div className="absolute left-10 right-2 bottom-6 top-0">
									<svg viewBox="0 0 700 140" preserveAspectRatio="none" className="h-full w-full overflow-visible" role="img" aria-label="Weekly document processing activity">
										<polyline fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" className="text-primary" points={Object.entries(dashboard.data.document_weekly_count).map(([, value], index, entries) => `${(index / Math.max(entries.length - 1, 1)) * 700},${140 - (value / weeklyMax) * 120}`).join(' ')} />
										{Object.entries(dashboard.data.document_weekly_count).map(([day, value], index, entries) => <circle key={day} cx={(index / Math.max(entries.length - 1, 1)) * 700} cy={140 - (value / weeklyMax) * 120} r="5" className="fill-surface stroke-primary" strokeWidth="3"><title>{day}: {value}</title></circle>)}
									</svg>
								</div>
								<div className="absolute left-10 right-2 bottom-0 flex justify-between text-[10px] text-text-muted">{Object.keys(dashboard.data.document_weekly_count).map((day) => <span key={day}>{day.slice(0, 3)}</span>)}</div>
							</div>
						</article>

						<article className="rounded-sm border border-border bg-surface p-5 xl:col-span-2">
							<div className="flex items-center justify-between">
								<div>
									<h2 className="font-semibold">Documents by type</h2>
									<p className="mt-1 text-xs text-text-secondary">Most common legal document categories</p>
								</div>
								<i className="bi bi-bar-chart-fill text-primary" aria-hidden="true" />
							</div>
							<div className="mt-6 space-y-4">
								{Object.entries(dashboard.data.document_type_count)
									.filter(([, value]) => value > 0)
									.sort(([, first], [, second]) => second - first)
									.slice(0, 8)
									.map(([type, value], _, entries) => {
										const largestValue = Math.max(...entries.map(([, entryValue]) => entryValue), documentTotal);
										const percentage = (value / largestValue) * 100;
											return <div key={type} className="grid grid-cols-[minmax(7rem,13rem)_1fr_2rem] items-center gap-3 text-xs">
												<span className="truncate text-text-secondary">{type.replaceAll('_', ' ')}</span>
												<div className="relative h-5 border-b border-border"><div className="absolute inset-x-0 top-1/2 border-t border-border/60" /><div className="absolute left-0 top-1/2 h-2 -translate-y-1/2 rounded-r-full bg-primary" style={{ width: `${Math.max(percentage, 3)}%` }} /></div>
												<strong className="text-right">{value}</strong>
											</div>;
									})}
								{Object.values(dashboard.data.document_type_count).every((value) => value === 0) && <p className="text-sm text-text-muted">No document type activity for this range.</p>}
							</div>
						</article>
					</section>

					<PendingFilesList />
				</>
			)}
		</div>
	);
}
