import { apiFetch } from '@/services/apiClient';
import type { UserResponse } from '@/types/user';

export async function getCurrentUser(): Promise<UserResponse> {
	return apiFetch<UserResponse>('/users/me');
}

export function logout(): void {
	apiFetch<string>('/auth/logout').then(() => {
		window.location.href = '/login';
	});
}