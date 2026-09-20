// src/types/admin.ts

import type { UserRole } from './user';
import type { LegalDocumentType, UploadStatus } from './workspace';

export interface AdminDashboardData {
  active_user_count: number;
  documents_count: number;
  document_status_count: {
    pending: number;
    ongoing: number;
    completed: number;
    failed: number;
    rejected: number;
  };
  document_weekly_count: Record<'monday' | 'tuesday' | 'wednesday' | 'thursday' | 'friday' | 'saturday' | 'sunday', number>;
  document_type_count: Record<string, number>;
  chunks_count: number;
}

export interface UserRegistrationMonthlyCount {
  january: number;
  february: number;
  march: number;
  april: number;
  may: number;
  june: number;
  july: number;
  august: number;
  september: number;
  october: number;
  november: number;
  december: number;
}

export interface UserRoleCount {
  standard: number;
  contributor: number;
  admin: number;
}

export interface AdminUserAnalytics {
  registered_count: number;
  active_count: number;
  inactive_count: number;
  monthly_registration_count: UserRegistrationMonthlyCount;
  new_registration_count: number;
  role_count: UserRoleCount;
}

export interface AdminDocumentAnalytics {
  total_count: number;
  status_count: Record<'pending' | 'ongoing' | 'completed' | 'failed' | 'rejected', number>;
  type_count: Record<string, number>;
  monthly_upload_count: Record<string, number>;
  new_upload_count: number;
  most_upload_user: Array<AdminUserListItem & { upload_count: number }>;
}

export type AdminDashboardDateRange =
  | 'today'
  | 'yesterday'
  | 'this_week'
  | 'last_week'
  | 'this_month'
  | 'last_month'
  | 'last_7_days'
  | 'last_30_days'
  | 'last_90_days'
  | 'last_6_months'
  | 'this_year'
  | 'last_year'
  | 'all_time';

export interface AdminUserListItem {
  id: string;
  first_name: string;
  last_name: string;
  email: string;
  role: UserRole;
  provider: 'google' | 'facebook' | 'apple';
  is_active: boolean;
  profile_picture?: string;
  created_at: string; // ISO8601
}

export interface AdminUsersQueryParams {
  query?: string;
  is_active?: boolean;
  role?: UserRole;
  oauth_provider?: 'google' | 'facebook' | 'apple';
  limit?: number;
  offset?: number;
  column?: string[]; // e.g. ['last_name', 'first_name']
  order?: 'ASC' | 'DESC';
}

export interface AdminDocumentListItem {
  id: string;
  original_file_name: string;
  upload_file_name: string;
  document_type: LegalDocumentType;
  file_type: string;
  upload_status: UploadStatus; // 'pending' | 'ongoing' | 'rejected' | 'completed' | 'failed'
  upload_error: string | null;
  rejection_message: string | null;
  uploader: {
    id: string;
    first_name: string;
    last_name: string;
    email: string;
    role: UserRole;
  } | null;
  created_at: string; // ISO8601
}

export interface AdminDocumentsQueryParams {
  query?: string;
  upload_status?: UploadStatus;
  uploader_id?: string;
  limit?: number;
  offset?: number;
  column?: string[];
  order?: 'ASC' | 'DESC';
}

export const ADMIN_USERS_PAGE_SIZE = 10;
export const ADMIN_DOCUMENTS_PAGE_SIZE = 10;
export const ADMIN_USERS_MAX_OFFSET = 1000; // mirror MAX_SESSION_OFFSET pattern in workspace.ts
export const ADMIN_DOCUMENTS_MAX_OFFSET = 1000;

