import { apiFetch } from '@/services/apiClient';
import type { AdminUserListItem, AdminUsersQueryParams } from '@/types/admin';

/** GET /users/ (admin) with query params */
export async function listUsers(
	params: AdminUsersQueryParams,
): Promise<AdminUserListItem[]> {
	const query = new URLSearchParams();
	if (params.query) query.set('query', params.query);
	if (params.limit !== undefined) query.set('limit', String(params.limit));
	if (params.offset !== undefined) query.set('offset', String(params.offset));
	if (params.column?.length) query.set('column', params.column.join(','));
	if (params.order) query.set('order', params.order);
	const qs = query.toString();
	return apiFetch<AdminUserListItem[]>(
		`/users/${qs ? `?${qs}` : ''}`,
	);
}
