import { ApiError } from '@/services/apiClient';

export function getAdminErrorMessage(error: unknown): string {
	if (error instanceof ApiError) {
		if (error.code === 'RATE_LIMIT_EXCEEDED') {
			return 'Too many requests — please wait a moment';
		}
		return error.message;
	}
	if (error instanceof Error) {
		return error.message;
	}
	return 'Something went wrong. Please try again.';
}

export function isForbiddenError(error: unknown): boolean {
	return error instanceof ApiError && error.code === 'FORBIDDEN';
}
