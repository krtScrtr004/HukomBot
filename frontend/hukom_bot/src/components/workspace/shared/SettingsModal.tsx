import { useCallback, useContext, useEffect, useRef, useState } from 'react';
import { WorkspaceContext } from '@/contexts/WorkspaceContext';
import { useAuth } from '@/contexts/AuthContext';
import { updateUserProfile, getUserTokenUsage } from '@/services/userService';
import { getCurrentUser } from '@/services/authService';
import { ApiError } from '@/services/apiClient';
import { useToast } from '@/contexts/ToastProvider';
import type { UserRole, UserTokenUsageResponse } from '@/types/user';

interface SettingsModalProps {
	open: boolean;
	onClose: () => void;
	/** If provided, the modal will open on this tab instead of 'profile'. */
	initialTab?: TabType;
}

type TabType = 'profile' | 'usage';

export default function SettingsModal({ open, onClose, initialTab }: SettingsModalProps) {
	const workspaceCtx = useContext(WorkspaceContext);
	const { user: authUser, login: authLogin } = useAuth();

	// Use workspace context when available, otherwise fall back to AuthContext
	const user = workspaceCtx ? workspaceCtx.state.user : authUser;
	const refreshUser = workspaceCtx
		? workspaceCtx.refreshUser
		: async () => {
				const updated = await getCurrentUser();
				authLogin(updated);
			};
	const handleApiError = workspaceCtx
		? workspaceCtx.handleApiError
		: (err: unknown, context: string) => {
				console.error(`Error in ${context}:`, err);
			};
	const { showToast } = useToast();

	const [activeTab, setActiveTab] = useState<TabType>('profile');
	const [firstName, setFirstName] = useState('');
	const [lastName, setLastName] = useState('');
	const [role, setRole] = useState<UserRole>('standard');
	const [profileFile, setProfileFile] = useState<File | null>(null);
	const [profilePreviewUrl, setProfilePreviewUrl] = useState<string | null>(
		null,
	);
	const [error, setError] = useState<string | null>(null);
	const [saving, setSaving] = useState(false);

	// Token usage state
	const [tokenUsage, setTokenUsage] = useState<UserTokenUsageResponse | null>(
		null,
	);
	const [loadingUsage, setLoadingUsage] = useState(false);
	const [usageError, setUsageError] = useState<string | null>(null);

	const fileInputRef = useRef<HTMLInputElement>(null);
	const objectUrlRef = useRef<string | null>(null);

	const isAdmin = user?.role === 'admin';

	// Reset state and prefill form values when modal opens or user updates
	useEffect(() => {
		if (open && user) {
			setFirstName(user.first_name || '');
			setLastName(user.last_name || '');
			setRole(user.role || 'standard');
			setProfileFile(null);
			setProfilePreviewUrl(user.profile_picture || null);
			setError(null);
			setActiveTab(initialTab ?? 'profile');
		}
	}, [open, user, initialTab]);

	// Fetch token usage if we switch to usage tab
	const fetchUsage = useCallback(async () => {
		setLoadingUsage(true);
		setUsageError(null);
		try {
			const usage = await getUserTokenUsage();
			setTokenUsage(usage);
		} catch (err) {
			setUsageError('Failed to load token usage information.');
			handleApiError(err, 'fetching token usage');
			console.error(err);
		} finally {
			setLoadingUsage(false);
		}
	}, [handleApiError]);

	useEffect(() => {
		if (open && activeTab === 'usage') {
			void fetchUsage();
		}
	}, [open, activeTab, fetchUsage]);

	// Escape key to close modal
	useEffect(() => {
		if (!open) return;
		const handleKey = (e: KeyboardEvent) => {
			if (e.key === 'Escape' && !saving) {
				onClose();
			}
		};
		document.addEventListener('keydown', handleKey);
		return () => document.removeEventListener('keydown', handleKey);
	}, [open, onClose, saving]);

	// Revoke object URL on unmount or preview changes
	const revokePreviewUrl = useCallback(() => {
		if (objectUrlRef.current) {
			URL.revokeObjectURL(objectUrlRef.current);
			objectUrlRef.current = null;
		}
	}, []);

	useEffect(() => {
		return () => {
			revokePreviewUrl();
		};
	}, [revokePreviewUrl]);

	if (!open) return null;

	const handleFileChange = (file: File | null) => {
		if (!file) return;

		// Validation: Max size 5MB
		const maxSize = 5 * 1024 * 1024;
		if (file.size > maxSize) {
			setError('Profile picture file size must be under 5MB.');
			return;
		}

		// Validation: Image types only
		if (!file.type.startsWith('image/')) {
			setError('Please upload a valid image file (PNG/JPEG/GIF).');
			return;
		}

		setError(null);
		setProfileFile(file);

		// Generate local object URL for preview
		const objectUrl = URL.createObjectURL(file);
		revokePreviewUrl();
		objectUrlRef.current = objectUrl;
		setProfilePreviewUrl(objectUrl);
	};

	const handleSaveProfile = async () => {
		if (!user) return;
		if (!firstName.trim()) {
			setError('First name is required.');
			return;
		}
		if (!lastName.trim()) {
			setError('Last name is required.');
			return;
		}

		setSaving(true);
		setError(null);

		try {
			const formData = new FormData();
			formData.append('first_name', firstName.trim());
			formData.append('last_name', lastName.trim());

			// Only append role if it's admin (as non-admins can't change roles)
			if (isAdmin) {
				formData.append('role', role);
			}

			if (profileFile) {
				formData.append('profile_picture', profileFile);
			}

			await updateUserProfile(user.id, formData);
			await refreshUser();
			showToast('Profile updated successfully.', 'success');
			onClose();
		} catch (err) {
			const message =
				err instanceof ApiError
					? err.message
					: 'Failed to update profile info.';
			setError(message);
			showToast(message, 'error');
			console.error(err);
		} finally {
			setSaving(false);
		}
	};

	// Calculate initials for placeholder avatar
	const getInitials = () => {
		const first = firstName.trim().charAt(0) || '';
		const last = lastName.trim().charAt(0) || '';
		return `${first}${last}`.toUpperCase() || 'U';
	};

	// Format TTL to human readable time
	const formatTTL = (seconds: number) => {
		if (seconds <= 0) return 'Resets now';
		const h = Math.floor(seconds / 3600);
		const m = Math.floor((seconds % 3600) / 60);
		if (h > 0) {
			return `${h} hour${h > 1 ? 's' : ''} ${m} minute${m !== 1 ? 's' : ''}`;
		}
		return `${m} minute${m !== 1 ? 's' : ''}`;
	};

	return (
		<div className="fixed inset-0 z-(--z-dialog) flex items-center justify-center p-4">
			{/* Backdrop overlay */}
			<section
				className="absolute inset-0 bg-black/40"
				onClick={() => !saving && onClose()}
				aria-hidden="true"
			/>

			{/* Dialog content */}
			<section
				role="dialog"
				aria-modal="true"
				aria-labelledby="settings-title"
				className="relative z-10 w-150 max-w-lg rounded-sm bg-surface border border-border shadow-lg flex flex-col max-h-[90vh]"
			>
				{/* Header */}
				<header className="p-4 border-b border-border shrink-0 flex items-center justify-between">
					<div>
						<h2
							id="settings-title"
							className="text-lg font-semibold text-text-primary"
						>
							Settings
						</h2>
						<p className="text-sm text-text-muted mt-1">
							Manage your user account settings and daily token
							limits.
						</p>
					</div>
					<button
						type="button"
						onClick={onClose}
						disabled={saving}
						className="p-1 rounded-sm text-text-secondary hover:bg-hover focus:outline-none"
						aria-label="Close settings"
					>
						<i className="bi bi-x text-xl" />
					</button>
				</header>

				{/* Tabs Navigation */}
				<nav
					className="flex border-b border-border bg-surface-muted px-4"
					aria-label="Settings tabs"
				>
					<button
						type="button"
						onClick={() => setActiveTab('profile')}
						className={`py-3 px-4 text-sm font-medium border-b-2 transition-colors focus:outline-none ${
							activeTab === 'profile'
								? 'border-primary text-primary'
								: 'border-transparent text-text-secondary hover:text-text-primary'
						}`}
						aria-current={
							activeTab === 'profile' ? 'page' : undefined
						}
					>
						Profile Settings
					</button>
					{!isAdmin && (
					<button
						type="button"
						onClick={() => setActiveTab('usage')}
						className={`py-3 px-4 text-sm font-medium border-b-2 transition-colors focus:outline-none ${
							activeTab === 'usage'
								? 'border-primary text-primary'
								: 'border-transparent text-text-secondary hover:text-text-primary'
						}`}
						aria-current={
							activeTab === 'usage' ? 'page' : undefined
						}
					>
						Token Usage
					</button>
				)}
				</nav>

				{/* Content */}
				<section className="flex-1 overflow-y-auto p-6 scrollbar-thin">
					{activeTab === 'profile' && (
						<div className="space-y-5">
							{/* Profile Picture Upload & Preview */}
							<div className="flex items-center gap-4">
								<div className="relative w-20 h-20 rounded-full border border-border bg-surface-muted flex items-center justify-center overflow-hidden shrink-0">
									{profilePreviewUrl ? (
										<img
											src={profilePreviewUrl}
											alt="Avatar preview"
											className="w-full h-full object-cover"
										/>
									) : (
										<span className="text-2xl font-semibold text-text-secondary">
											{getInitials()}
										</span>
									)}
								</div>
								<div className="space-y-1">
									<label className="block text-sm font-medium text-text-primary">
										Profile Picture
									</label>
									<p className="text-xs text-text-muted">
										Supports JPG, JPEG, or PNG. Maximum size
										5MB.
									</p>
									<input
										ref={fileInputRef}
										type="file"
										accept="image/*"
										onChange={(e) =>
											handleFileChange(
												e.target.files?.[0] ?? null,
											)
										}
										className="hidden"
										disabled={saving}
									/>
									<button
										type="button"
										onClick={() =>
											fileInputRef.current?.click()
										}
										disabled={saving}
										className="px-3 py-1.5 rounded-sm text-xs font-medium border border-border text-text-primary bg-surface hover:bg-hover transition-colors disabled:opacity-50"
									>
										Upload Image
									</button>
								</div>
							</div>

							{/* Form Fields */}
							<div className="space-y-4">
								<div className="grid grid-cols-2 gap-4">
									<div className="space-y-2">
										<label
											htmlFor="first-name"
											className="block text-sm font-medium text-text-primary"
										>
											First name
										</label>
										<input
											id="first-name"
											type="text"
											value={firstName}
											onChange={(e) =>
												setFirstName(e.target.value)
											}
											disabled={saving}
											className="w-full h-(--input-height) rounded-sm border border-border bg-background px-3 text-sm text-text-primary focus:outline-none focus-visible:ring-2 focus-visible:ring-primary disabled:opacity-50"
										/>
									</div>
									<div className="space-y-2">
										<label
											htmlFor="last-name"
											className="block text-sm font-medium text-text-primary"
										>
											Last name
										</label>
										<input
											id="last-name"
											type="text"
											value={lastName}
											onChange={(e) =>
												setLastName(e.target.value)
											}
											disabled={saving}
											className="w-full h-(--input-height) rounded-sm border border-border bg-background px-3 text-sm text-text-primary focus:outline-none focus-visible:ring-2 focus-visible:ring-primary disabled:opacity-50"
										/>
									</div>
								</div>

								<div className="space-y-2">
									<label
										htmlFor="settings-email"
										className="block text-sm font-medium text-text-primary"
									>
										Email
									</label>
									<input
										id="settings-email"
										type="email"
										value={user?.email || ''}
										disabled
										className="w-full h-(--input-height) rounded-sm border border-border bg-surface-muted px-3 text-sm text-text-secondary cursor-not-allowed opacity-70"
									/>
								</div>

								<div className="space-y-2">
									<label
										htmlFor="settings-role"
										className="block text-sm font-medium text-text-primary"
									>
										Role
									</label>
									<select
										id="settings-role"
										value={role}
										disabled={saving || !isAdmin}
										onChange={(e) =>
											setRole(e.target.value as UserRole)
										}
										className={`w-full h-(--input-height) rounded-sm border border-border bg-background px-3 text-sm text-text-primary focus:outline-none focus-visible:ring-2 focus-visible:ring-primary ${
											!isAdmin
												? 'bg-surface-muted text-text-secondary cursor-not-allowed opacity-70'
												: ''
										}`}
									>
										<option value="standard">
											Standard
										</option>
										<option value="contributor">
											Contributor
										</option>
										<option value="admin">Admin</option>
									</select>
									{!isAdmin && (
										<span className="block text-xs text-text-muted mt-1">
											Role changes can only be performed
											by administrators.
										</span>
									)}
								</div>
							</div>

							{error && (
								<p
									className="text-sm text-danger mt-2"
									role="alert"
								>
									{error}
								</p>
							)}
						</div>
					)}

					{activeTab === 'usage' && (
						<div className="space-y-6">
							{loadingUsage && (
								<div className="flex flex-col items-center py-8 gap-2">
									<div className="w-8 h-8 border-3 border-border border-t-primary rounded-full animate-spin" />
									<p className="text-sm text-text-secondary">
										Loading token usage info...
									</p>
								</div>
							)}

							{usageError && !loadingUsage && (
								<div className="p-4 border border-danger/20 rounded bg-danger-foreground/5 flex items-center justify-between">
									<p className="text-sm text-danger">
										{usageError}
									</p>
									<button
										type="button"
										onClick={() => void fetchUsage()}
										className="text-xs font-semibold text-primary hover:underline"
									>
										Retry
									</button>
								</div>
							)}

							{tokenUsage && !loadingUsage && (
								<div className="space-y-6">
									{/* Progress bar info card */}
									<div className="p-4 rounded-md border border-border bg-surface-muted space-y-4">
										<div className="flex justify-between items-center">
											<span className="text-sm font-semibold text-text-primary">
												Daily Token Allocation
											</span>
											<span className="text-sm text-text-secondary">
												{(
													tokenUsage.quota -
													tokenUsage.remaining
												).toLocaleString()}{' '}
												/{' '}
												{tokenUsage.quota.toLocaleString()}{' '}
												tokens
											</span>
										</div>

										{/* Vibrant premium gradient progress bar */}
										<div className="w-full h-4 bg-background rounded-full overflow-hidden border border-border">
											<div
												className="h-full bg-active transition-all duration-500 ease-out"
												style={{
													width: `${Math.min(
														100,
														Math.max(
															0,
															((tokenUsage.quota -
																tokenUsage.remaining) /
																tokenUsage.quota) *
																100,
														),
													)}%`,
												}}
											/>
										</div>

										<div className="flex justify-between text-xs text-text-secondary">
											<span>
												{Math.round(
													((tokenUsage.quota -
														tokenUsage.remaining) /
														tokenUsage.quota) *
														100,
												)}
												% Used
											</span>
											<span>
												{tokenUsage.remaining.toLocaleString()}{' '}
												Tokens Remaining
											</span>
										</div>
									</div>

									{/* Detailed metadata */}
									<div className="grid grid-cols-2 gap-4">
										<div className="p-3 border border-border rounded-md bg-surface">
											<span className="block text-xs text-text-muted">
												TOTAL ALLOCATION
											</span>
											<span className="text-lg font-semibold text-text-primary mt-1 block">
												{tokenUsage.quota.toLocaleString()}
											</span>
										</div>
										<div className="p-3 border border-border rounded-md bg-surface">
											<span className="block text-xs text-text-muted">
												RESETS IN
											</span>
											<span className="text-lg font-semibold text-text-primary mt-1 block">
												{formatTTL(tokenUsage.ttl)}
											</span>
										</div>
									</div>
								</div>
							)}
						</div>
					)}
				</section>

				{/* Footer buttons */}
				<footer className="p-4 border-t border-border flex justify-end gap-3 shrink-0">
					<button
						type="button"
						onClick={onClose}
						disabled={saving}
						className="px-4 py-2 rounded-sm text-sm font-medium border border-border text-text-primary bg-surface hover:bg-hover focus:outline-none focus-visible:ring-2 focus-visible:ring-primary disabled:opacity-50"
					>
						Cancel
					</button>
					{activeTab === 'profile' && (
						<button
							type="button"
							onClick={() => void handleSaveProfile()}
							disabled={saving}
							className="px-4 py-2 rounded-sm text-sm font-medium bg-primary text-primary-foreground hover:opacity-90 focus:outline-none focus-visible:ring-2 focus-visible:ring-primary disabled:opacity-50"
						>
							{saving ? 'Saving...' : 'Save changes'}
						</button>
					)}
				</footer>

				{/* Loading overlay for profile saving */}
				{saving && (
					<div className="absolute inset-0 bg-surface-overlay/80 flex items-center justify-center rounded-lg z-50">
						<div className="flex flex-col items-center gap-3">
							<div className="w-10 h-10 border-3 border-border border-t-primary rounded-full animate-spin" />
							<p className="text-sm text-text-secondary">
								Saving profile...
							</p>
						</div>
					</div>
				)}
			</section>
		</div>
	);
}
