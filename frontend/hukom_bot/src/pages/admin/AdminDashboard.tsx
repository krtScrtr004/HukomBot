import { useEffect, useRef } from 'react';
import { API_BASE_URL } from '@/services/apiClient';
import { useAdmin } from '@/contexts/AdminContext';
import StatCard from '@/components/ui/StatCard';
import PendingFilesList from '@/components/admin/dashboard/PendingFilesList';
import LoadingSpinner from '@/components/workspace/shared/LoadingSpinner';
import ErrorText from '@/components/ui/ErrorText';

export default function AdminDashboardPage() {
	const { state, fetchDashboard, fetchPendingFiles, dispatch } = useAdmin();
	const { dashboard } = state;
	const initRef = useRef(false);

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
			es = new EventSource(
				`${API_BASE_URL}/events/v1/admin/dashboard`,
				{ withCredentials: true },
			);
			es.onmessage = (event) => {
				if (event.data == null) return;
				try {
					const parsed = JSON.parse(event.data) as {
						success?: boolean;
						data?: typeof dashboard.data;
					};
					if (parsed.success && parsed.data) {
						dispatch({
							type: 'DISPATCH_DASHBOARD_UPDATE',
							payload: parsed.data,
						});
					}
				} catch {
					// Ignore malformed SSE payloads; REST data remains visible.
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
		<div className="space-y-8">
			<section aria-label="Dashboard statistics">
				{dashboard.loading && !dashboard.data ? (
					<LoadingSpinner label="Loading dashboard" size="lg" />
				) : dashboard.error && !dashboard.data ? (
					<ErrorText
						error={dashboard.error}
						onRetry={() => void fetchDashboard()}
					/>
				) : dashboard.data ? (
					<div className="grid grid-cols-2 md:grid-cols-4 gap-4">
						<StatCard
							label="Total Users"
							value={dashboard.data.active_user_count}
							icon="bi-people"
						/>
						<StatCard
							label="Documents Count"
							value={dashboard.data.documents_count}
							icon="bi-folder"
							className="md:col-span-2 border-2 border-primary/30"
						/>
						<StatCard
							label="Pending"
							value={dashboard.data.pending_document_count}
							icon="bi-hourglass-split"
						/>
						<StatCard
							label="Ongoing"
							value={dashboard.data.ongoing_document_count}
							icon="bi-arrow-repeat"
						/>
						<StatCard
							label="Completed"
							value={dashboard.data.completed_document_count}
							icon="bi-check-circle"
						/>
						<StatCard
							label="Failed"
							value={dashboard.data.failed_document_count}
							icon="bi-x-circle"
						/>
						<StatCard
							label="Rejected"
							value={dashboard.data.rejected_document_count}
							icon="bi-slash-circle"
						/>
						<StatCard
							label="Chunks"
							value={dashboard.data.chunks_count}
							icon="bi-puzzle"
						/>
					</div>
				) : null}
				{dashboard.error && dashboard.data ? (
					<div className="mt-2">
						<ErrorText
							error={dashboard.error}
							onRetry={() => void fetchDashboard()}
						/>
					</div>
				) : null}
			</section>

			<PendingFilesList />
		</div>
	);
}
