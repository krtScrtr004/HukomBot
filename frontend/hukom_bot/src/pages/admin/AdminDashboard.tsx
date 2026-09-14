import { useEffect, useRef, useState } from 'react';
import { EVENT_BASE_URL_V1 } from '@/services/apiClient'; 
import { useAdmin } from '@/contexts/AdminContext';
import type { AdminDashboardData } from '@/types/admin';
import PendingFilesList from '@/components/PendingFilesList';
import LoadingSpinner from '@/components/workspace/shared/LoadingSpinner';
import UploadDocumentModal from '@/components/UploadDocumentModal';

function isDashboardData(value: unknown): value is AdminDashboardData {
	if (!value || typeof value !== 'object') return false;

	const data = value as Record<string, unknown>;
	return [
		'active_user_count',
		'documents_count',
		'pending_document_count',
		'ongoing_document_count',
		'completed_document_count',
		'failed_document_count',
		'rejected_document_count',
		'chunks_count',
	].every((key) => typeof data[key] === 'number');
}

function parseDashboardEvent(eventData: string): AdminDashboardData | null {
	try {
		// Remove trailing ':heartbeat
		// Cut at the last colon in the string
		const lastColonIndex = eventData.lastIndexOf(":");
		const jsonString = eventData.substring(0, lastColonIndex).trim();
		const validJson = jsonString.replace(/'/g, '"');

		const parsed: unknown = JSON.parse(validJson);
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
	const [uploadModalOpen, setUploadModalOpen] = useState(false);

	useEffect(() => {
		if (initRef.current) return;
		initRef.current = true;
		void fetchDashboard();
		void fetchPendingFiles();
	}, [fetchDashboard, fetchPendingFiles]);

	useEffect(() => {
		let es: EventSource | null = null;
		const openStream = () => {
			if (document.hidden || es) return;
			es = new EventSource(`${EVENT_BASE_URL_V1}/admin/dashboard`, {
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
	}, [dispatch]);

	return (
		<div className="mx-auto max-w-7xl space-y-8">
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
					<button
						type="button"
						className="flex items-center gap-2 rounded-sm border border-border bg-surface px-3 py-2 text-sm text-text-secondary hover:bg-hover"
					>
						<i className="bi bi-calendar3" aria-hidden="true" />
						Last 30 days
						<i
							className="bi bi-chevron-down text-xs"
							aria-hidden="true"
						/>
					</button>
					<button
						type="button"
						onClick={() => setUploadModalOpen(true)}
						className="flex items-center gap-2 rounded-sm bg-primary px-3 py-2 text-sm font-semibold text-primary-foreground shadow-sm hover:opacity-90"
					>
						<i className="bi bi-plus-lg" aria-hidden="true" />
						Upload Document
					</button>
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
								dashboard.data.ongoing_document_count,
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
						className="grid gap-4 xl:grid-cols-[0.8fr_1.2fr]"
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
										background: `conic-gradient(var(--color-success) 0 ${(dashboard.data.completed_document_count / Math.max(dashboard.data.documents_count, 1)) * 100}%, var(--color-info) 0 ${((dashboard.data.completed_document_count + dashboard.data.ongoing_document_count) / Math.max(dashboard.data.documents_count, 1)) * 100}%, var(--color-warning) 0 ${((dashboard.data.completed_document_count + dashboard.data.ongoing_document_count + dashboard.data.pending_document_count) / Math.max(dashboard.data.documents_count, 1)) * 100}%, var(--color-danger) 0 100%)`,
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
											dashboard.data
												.completed_document_count,
											'bg-success',
										],
										[
											'Ongoing',
											dashboard.data
												.ongoing_document_count,
											'bg-info',
										],
										[
											'Pending',
											dashboard.data
												.pending_document_count,
											'bg-warning',
										],
										[
											'Failed / rejected',
											dashboard.data
												.failed_document_count +
												dashboard.data
													.rejected_document_count,
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

							<div className="mt-8 flex h-36 items-end gap-3 border-b border-border px-2">
								{[38, 56, 44, 72, 61, 88, 76].map(
									(height, index) => (
										<div
											key={index}
											className="group flex flex-1 flex-col items-center gap-2"
										>
											<div
												className="w-full rounded-t-sm bg-primary/70 transition-all group-hover:bg-primary"
												style={{ height: `${height}%` }}
											/>
											<span className="text-[10px] text-text-muted">
												{
													[
														'Mon',
														'Tue',
														'Wed',
														'Thu',
														'Fri',
														'Sat',
														'Sun',
													][index]
												}
											</span>
										</div>
									),
								)}
							</div>
						</article>
					</section>

					<PendingFilesList />
				</>
			)}
			<UploadDocumentModal
				open={uploadModalOpen}
				onClose={() => setUploadModalOpen(false)}
			/>
		</div>
	);
}
