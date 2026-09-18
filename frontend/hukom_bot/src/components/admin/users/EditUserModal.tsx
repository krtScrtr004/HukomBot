import { useEffect, useRef, useState } from 'react';
import { ApiError } from '@/services/apiClient';
import { updateUserProfile } from '@/services/userService';
import type { AdminUserListItem } from '@/types/admin';
import type { UserRole } from '@/types/user';
import { useAdmin } from '@/contexts/AdminContext';
import { useToast } from '@/contexts/ToastProvider';
import { getAdminErrorMessage } from '@/utils/adminErrors';
import CharacterCounter from '@/components/ui/CharacterCounter';
import ErrorText from '@/components/ui/ErrorText';
import { useFocusTrap } from '@/hooks/useFocusTrap';

interface EditUserModalProps {
	open: boolean;
	user: AdminUserListItem | null;
	onClose: () => void;
}

const MAX_NAME_LENGTH = 255;
const MAX_FILE_SIZE = 5 * 1024 * 1024;

export default function EditUserModal({
	open,
	user,
	onClose,
}: EditUserModalProps) {
	const { patchUser } = useAdmin();
	const { showToast } = useToast();
	const [firstName, setFirstName] = useState('');
	const [lastName, setLastName] = useState('');
	const [role, setRole] = useState<UserRole>('standard');
	const [profileFile, setProfileFile] = useState<File | null>(null);
	const [profilePreviewUrl, setProfilePreviewUrl] = useState<string | null>(
		null,
	);
	const [fieldErrors, setFieldErrors] = useState<Record<string, string>>(
		{},
	);
	const [fileError, setFileError] = useState<string | null>(null);
	const [saving, setSaving] = useState(false);
	const fileInputRef = useRef<HTMLInputElement>(null);
	const objectUrlRef = useRef<string | null>(null);
	const dialogRef = useRef<HTMLDivElement>(null);
	useFocusTrap(dialogRef, open);

	useEffect(() => {
		if (open && user) {
			setFirstName(user.first_name);
			setLastName(user.last_name);
			setRole(user.role);
			setProfileFile(null);
			setProfilePreviewUrl(user.profile_picture ?? null);
			setFieldErrors({});
			setFileError(null);
		}
	}, [open, user]);

	useEffect(() => {
		if (!open) return;
		const handleKey = (e: KeyboardEvent) => {
			if (e.key === 'Escape' && !saving) onClose();
		};
		document.addEventListener('keydown', handleKey);
		return () => document.removeEventListener('keydown', handleKey);
	}, [open, onClose, saving]);

	useEffect(
		() => () => {
			if (objectUrlRef.current) {
				URL.revokeObjectURL(objectUrlRef.current);
			}
		},
		[],
	);

	if (!open || !user) return null;

	const handleFileChange = (file: File | null) => {
		if (!file) return;
		if (file.size > MAX_FILE_SIZE) {
			setFileError('Profile picture file size must be under 5MB.');
			return;
		}
		if (!file.type.startsWith('image/')) {
			setFileError('Please upload a valid image file (PNG/JPEG/GIF).');
			return;
		}
		setFileError(null);
		setProfileFile(file);
		if (objectUrlRef.current) URL.revokeObjectURL(objectUrlRef.current);
		objectUrlRef.current = URL.createObjectURL(file);
		setProfilePreviewUrl(objectUrlRef.current);
	};

	const getInitials = () => {
		const first = firstName.trim().charAt(0) || '';
		const last = lastName.trim().charAt(0) || '';
		return `${first}${last}`.toUpperCase() || 'U';
	};

	const handleSubmit = async () => {
		const errors: Record<string, string> = {};
		if (!firstName.trim() || firstName.trim().length > MAX_NAME_LENGTH) {
			errors.first_name = 'First name is required (1–255 characters).';
		}
		if (!lastName.trim() || lastName.trim().length > MAX_NAME_LENGTH) {
			errors.last_name = 'Last name is required (1–255 characters).';
		}
		if (Object.keys(errors).length > 0) {
			setFieldErrors(errors);
			return;
		}
		if (fileError) return;

		setSaving(true);
		setFieldErrors({});
		try {
			const formData = new FormData();
			formData.append('first_name', firstName.trim());
			formData.append('last_name', lastName.trim());
			formData.append('role', role);
			if (profileFile) {
				formData.append('profile_picture', profileFile);
			}
			await updateUserProfile(user.id, formData);
			patchUser({
				...user,
				first_name: firstName.trim(),
				last_name: lastName.trim(),
				role,
				profile_picture: profilePreviewUrl ?? user.profile_picture,
			});
			showToast('User updated successfully.', 'success');
			onClose();
		} catch (error) {
			if (error instanceof ApiError && error.code === 'VALIDATION_ERROR') {
				const mapped: Record<string, string> = {};
				for (const detail of error.details ?? []) {
					if (detail.field) mapped[detail.field] = detail.issue;
				}
				setFieldErrors(mapped);
			} else {
				showToast(getAdminErrorMessage(error), 'error');
			}
		} finally {
			setSaving(false);
		}
	};

	return (
		<div className="fixed inset-0 z-(--z-dialog) flex items-center justify-center p-4">
			{/* Overlay */}
			<div
				className="absolute inset-0 bg-black/40"
				onClick={() => !saving && onClose()}
				aria-hidden="true"
			/>

			{/* Modal Container (Settings edit profile layout) */}
			<div
				ref={dialogRef}
				role="dialog"
				aria-modal="true"
				aria-labelledby="edit-user-title"
				className="relative z-10 w-150 rounded-lg bg-surface border border-border shadow-lg flex flex-col max-h-[90vh] overflow-hidden"
			>
				{/* Modal Header */}
				<header className="p-4 border-b border-border shrink-0 flex items-center justify-between bg-surface">
					<div>
						<h2
							id="edit-user-title"
							className="text-lg font-semibold text-text-primary"
						>
							Edit User Profile
						</h2>
						<p className="text-xs text-text-muted mt-0.5">
							Update user information, permissions, and profile image.
						</p>
					</div>
					<button
						type="button"
						onClick={onClose}
						disabled={saving}
						className="p-1 rounded-sm text-text-secondary hover:bg-hover focus:outline-none disabled:opacity-50"
						aria-label="Close edit user modal"
					>
						<i className="bi bi-x text-xl" />
					</button>
				</header>

				{/* Modal Body */}
				<div className="flex-1 overflow-y-auto p-6 space-y-5 scrollbar-thin">
					{/* Profile Avatar & Upload Section */}
					<div className="flex items-center gap-4">
						<div className="relative w-20 h-20 rounded-full border border-border bg-surface-muted flex items-center justify-center overflow-hidden shrink-0">
							{profilePreviewUrl ? (
								<img
									src={profilePreviewUrl}
									alt="Profile preview"
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
								Supports JPG, JPEG, or PNG. Maximum size 5MB.
							</p>
							<input
								ref={fileInputRef}
								type="file"
								accept="image/*"
								onChange={(e) =>
									handleFileChange(e.target.files?.[0] ?? null)
								}
								className="hidden"
								disabled={saving}
							/>
							<button
								type="button"
								onClick={() => fileInputRef.current?.click()}
								disabled={saving}
								className="px-3 py-1.5 rounded-sm text-xs font-medium border border-border text-text-primary bg-surface hover:bg-hover transition-colors disabled:opacity-50"
							>
								Upload Image
							</button>
							{fileError ? (
								<div className="mt-1">
									<ErrorText error={fileError} />
								</div>
							) : null}
							{fieldErrors.profile_picture ? (
								<div className="mt-1">
									<ErrorText error={fieldErrors.profile_picture} />
								</div>
							) : null}
						</div>
					</div>

					{/* Form Input Fields */}
					<div className="space-y-4">
						<div className="grid grid-cols-2 gap-4">
							<div className="space-y-1">
								<label
									htmlFor="edit-first-name"
									className="block text-sm font-medium text-text-primary"
								>
									First name
								</label>
								<input
									id="edit-first-name"
									type="text"
									value={firstName}
									maxLength={MAX_NAME_LENGTH}
									onChange={(e) => setFirstName(e.target.value)}
									disabled={saving}
									className="w-full h-(--input-height) rounded-sm border border-border bg-background px-3 text-sm text-text-primary focus:outline-none focus-visible:ring-2 focus-visible:ring-primary disabled:opacity-50"
								/>
								<div className="flex justify-between mt-1">
									{fieldErrors.first_name ? (
										<ErrorText error={fieldErrors.first_name} />
									) : (
										<span />
									)}
									<CharacterCounter
										text={firstName}
										maxLength={MAX_NAME_LENGTH}
									/>
								</div>
							</div>

							<div className="space-y-1">
								<label
									htmlFor="edit-last-name"
									className="block text-sm font-medium text-text-primary"
								>
									Last name
								</label>
								<input
									id="edit-last-name"
									type="text"
									value={lastName}
									maxLength={MAX_NAME_LENGTH}
									onChange={(e) => setLastName(e.target.value)}
									disabled={saving}
									className="w-full h-(--input-height) rounded-sm border border-border bg-background px-3 text-sm text-text-primary focus:outline-none focus-visible:ring-2 focus-visible:ring-primary disabled:opacity-50"
								/>
								<div className="flex justify-between mt-1">
									{fieldErrors.last_name ? (
										<ErrorText error={fieldErrors.last_name} />
									) : (
										<span />
									)}
									<CharacterCounter
										text={lastName}
										maxLength={MAX_NAME_LENGTH}
									/>
								</div>
							</div>
						</div>

						{/* Read-only User Email & Meta Info */}
						<div className="rounded-md border border-border bg-surface-muted p-3 space-y-2 text-xs">
							<div className="flex items-center justify-between">
								<span className="text-text-muted">Email address:</span>
								<span className="font-mono text-text-primary font-medium">{user.email}</span>
							</div>
							<div className="flex items-center justify-between">
								<span className="text-text-muted">Auth Provider:</span>
								<span className="capitalize text-text-primary font-medium">{user.provider}</span>
							</div>
							<div className="flex items-center justify-between">
								<span className="text-text-muted">Registered on:</span>
								<span className="text-text-primary font-medium">
									{new Date(user.created_at).toLocaleDateString(undefined, {
										year: 'numeric',
										month: 'long',
										day: 'numeric',
									})}
								</span>
							</div>
						</div>

						{/* User Role Selection */}
						<div className="space-y-1">
							<label
								htmlFor="edit-role"
								className="block text-sm font-medium text-text-primary"
							>
								Role & Access Level
							</label>
							<select
								id="edit-role"
								value={role}
								onChange={(e) =>
									setRole(e.target.value as UserRole)
								}
								disabled={saving}
								className="w-full h-(--input-height) rounded-sm border border-border bg-background px-3 text-sm text-text-primary focus:outline-none focus-visible:ring-2 focus-visible:ring-primary disabled:opacity-50"
							>
								<option value="standard">Standard User</option>
								<option value="contributor">Contributor</option>
								<option value="admin">Administrator</option>
							</select>
							{fieldErrors.role ? (
								<div className="mt-1">
									<ErrorText error={fieldErrors.role} />
								</div>
							) : null}
						</div>
					</div>
				</div>

				{/* Modal Footer */}
				<footer className="p-4 border-t border-border shrink-0 flex justify-end gap-3 bg-surface">
					<button
						type="button"
						onClick={onClose}
						disabled={saving}
						className="px-4 py-2 rounded-sm text-sm border border-border text-text-primary hover:bg-hover transition-colors disabled:opacity-50"
					>
						Cancel
					</button>
					<button
						type="button"
						onClick={() => void handleSubmit()}
						disabled={saving}
						className="px-4 py-2 rounded-sm text-sm bg-primary text-primary-foreground font-medium hover:opacity-90 transition-opacity disabled:opacity-50 flex items-center gap-2"
					>
						{saving && <i className="bi bi-arrow-repeat animate-spin text-sm" />}
						{saving ? 'Saving changes…' : 'Save Changes'}
					</button>
				</footer>
			</div>
		</div>
	);
}
