// API client for authenticated cookie-based requests to the HukomBot backend.
import type { ApiErrorBody } from '@/types/workspace';

export class ApiError extends Error {
	code: string;
	details: ApiErrorBody['details'];
	status: number;

	constructor(status: number, error: ApiErrorBody) {
		super(error.message);
		this.name = 'ApiError';
		this.code = error.code;
		this.details = error.details;
		this.status = status;
	}
}

export const API_BASE_URL_V1 = import.meta.env.VITE_BASE_API_URL_V1;
export const EVENT_BASE_URL_V1 = import.meta.env.VITE_BASE_EVENT_URL_V1;

interface ApiSuccessEnvelope<T> {
	success: true;
	message: string | null;
	data: T;
}

interface ApiErrorEnvelope {
	success: false;
	error: ApiErrorBody;
}

type ApiEnvelope<T> = ApiSuccessEnvelope<T> | ApiErrorEnvelope;

export interface ApiFetchOptions extends Omit<RequestInit, 'body'> {
	body?: unknown;
	headers?: Record<string, string>;
}

export async function apiFetch<T>(
	path: string,
	options: ApiFetchOptions = {},
): Promise<T> {
	const { body, headers = {}, ...rest } = options;

	const isFormData = body instanceof FormData;

	const response = await fetch(`${API_BASE_URL_V1}${path}`, {
		...rest,
		credentials: 'include',
		headers: {
			...(body !== undefined && !isFormData
				? { 'Content-Type': 'application/json' }
				: {}),
			...headers,
		},
		body: isFormData
			? body
			: body !== undefined
				? JSON.stringify(body)
				: undefined,
	});

	let envelope: ApiEnvelope<T>;
	try {
		envelope = (await response.json()) as ApiEnvelope<T>;
	} catch {
		throw new ApiError(response.status, {
			code: 'NETWORK_ERROR',
			message:
				'Unable to reach the server. Please check your connection.',
			details: [],
		});
	}

	if (!envelope.success) {
		throw new ApiError(response.status, envelope.error);
	}

	return envelope.data;
}

export function isAuthError(error: unknown): boolean {
	return (
		error instanceof ApiError &&
		(error.code === 'TOKEN_EXPIRED' ||
			error.code === 'INVALID_TOKEN' ||
			error.code === 'REVOKED_TOKEN' ||
			error.code === 'UNAUTHORIZED')
	);
}

export function isNotFoundError(error: unknown): boolean {
	return error instanceof ApiError && error.code === 'NOT_FOUND';
}
