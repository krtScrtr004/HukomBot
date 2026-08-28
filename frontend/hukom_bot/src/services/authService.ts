import { apiFetch } from '@/services/apiClient';
import type { UserResponse } from '@/types/user';

export async function getCurrentUser(): Promise<UserResponse> {
	return apiFetch<UserResponse>('/api/v1/users/me');
}

export function logout(): void {
	apiFetch<string>('/api/v1/auth/logout').then(url => {
		window.location.href = url;
	})
}