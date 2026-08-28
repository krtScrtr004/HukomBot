import { apiFetch } from '@/services/apiClient';
import type { UserTokenUsageResponse } from '@/types/user';

/**
 * Updates the profile of the user.
 * @param userId - The ID of the user to update.
 * @param formData - The FormData containing first_name, last_name, profile_picture, role.
 */
export async function updateUserProfile(
	userId: string,
	formData: FormData,
): Promise<{ id: string }> {
	return apiFetch<{ id: string }>(`/api/v1/users/${userId}`, {
		method: 'PATCH',
		body: formData,
	});
}

/**
 * Fetches the daily token usage of the current user.
 */
export async function getUserTokenUsage(): Promise<UserTokenUsageResponse> {
	return apiFetch<UserTokenUsageResponse>('/api/v1/users/me/usage');
}
