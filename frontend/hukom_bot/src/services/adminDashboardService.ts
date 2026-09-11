import { apiFetch } from '@/services/apiClient';
import type { AdminDashboardData } from '@/types/admin';

/** GET /api/v1/admin/dashboard */
export async function getDashboardData(): Promise<AdminDashboardData> {
	return apiFetch<AdminDashboardData>('/api/v1/admin/dashboard');
}
