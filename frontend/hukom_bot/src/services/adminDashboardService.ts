import { apiFetch } from '@/services/apiClient';
import type { AdminDashboardData } from '@/types/admin';

/** GET /admin/dashboard */
export async function getDashboardData(): Promise<AdminDashboardData> {
	return apiFetch<AdminDashboardData>('/admin/dashboard');
}
