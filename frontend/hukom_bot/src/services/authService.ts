import { apiFetch } from '@/services/apiClient';
import type { UserResponse } from '@/types/workspace';

export async function getCurrentUser(): Promise<UserResponse> {
	return apiFetch<UserResponse>('/api/v1/users/me');
}

export function getLogoutUrl(): string {
	const base = import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000';
	return `${base}/api/v1/auth/logout`;
}
