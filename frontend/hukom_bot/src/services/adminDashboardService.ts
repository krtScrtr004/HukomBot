import { apiFetch } from '@/services/apiClient';
import type { AdminDashboardData, AdminDashboardDateRange } from '@/types/admin';

/** GET /admin/dashboard */
export async function getDashboardData(
	dateRange: AdminDashboardDateRange,
): Promise<AdminDashboardData> {
	return apiFetch<AdminDashboardData>(
		`/admin/dashboard?date_range=${encodeURIComponent(dateRange)}`,
	);
}
