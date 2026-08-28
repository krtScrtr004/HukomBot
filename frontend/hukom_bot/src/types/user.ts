export type UserRole = 'standard' | 'contributor' | 'admin';

export interface UserResponse {
    id: string;
    first_name: string;
    last_name: string;
    email: string;
    role: UserRole;
    profile_picture?: string;
}

export interface UserTokenUsageResponse {
    quota: number;
    remaining: number;
    ttl: number;
}