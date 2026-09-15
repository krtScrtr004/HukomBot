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
  profile_picture?: string;
  created_at: string; // ISO8601
}

export interface AdminUsersQueryParams {
  query?: string;
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

