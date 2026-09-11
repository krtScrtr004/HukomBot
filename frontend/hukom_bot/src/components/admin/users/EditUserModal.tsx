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
			showToast('User updated', 'success');
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
			<div
				className="absolute inset-0 bg-black/40"
				onClick={() => !saving && onClose()}
				aria-hidden="true"
			/>
			<div
				ref={dialogRef}
				role="dialog"
				aria-modal="true"
				aria-labelledby="edit-user-title"
				className="relative z-10 w-full max-w-md rounded-lg bg-surface border border-border shadow-lg p-6"
			>
				<h2
					id="edit-user-title"
					className="text-lg font-semibold text-text-primary mb-4"
				>
					Edit User
				</h2>

				<div className="space-y-4">
					<div>
						<label
							htmlFor="edit-first-name"
							className="block text-sm text-text-secondary mb-1"
						>
							First name
						</label>
						<input
							id="edit-first-name"
							type="text"
							value={firstName}
							maxLength={MAX_NAME_LENGTH}
							onChange={(e) => setFirstName(e.target.value)}
							className="w-full border border-border rounded-sm px-3 py-2 text-sm bg-surface"
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

					<div>
						<label
							htmlFor="edit-last-name"
							className="block text-sm text-text-secondary mb-1"
						>
							Last name
						</label>
						<input
							id="edit-last-name"
							type="text"
							value={lastName}
							maxLength={MAX_NAME_LENGTH}
							onChange={(e) => setLastName(e.target.value)}
							className="w-full border border-border rounded-sm px-3 py-2 text-sm bg-surface"
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

					<div>
						<label
							htmlFor="edit-role"
							className="block text-sm text-text-secondary mb-1"
						>
							Role
						</label>
						<select
							id="edit-role"
							value={role}
							onChange={(e) =>
								setRole(e.target.value as UserRole)
							}
							className="w-full border border-border rounded-sm px-3 py-2 text-sm bg-surface"
						>
							<option value="standard">Standard</option>
							<option value="contributor">Contributor</option>
							<option value="admin">Admin</option>
						</select>
						{fieldErrors.role ? (
							<div className="mt-1">
								<ErrorText error={fieldErrors.role} />
							</div>
						) : null}
					</div>

					<div>
						<label
							htmlFor="edit-profile-picture"
							className="block text-sm text-text-secondary mb-1"
						>
							Profile picture
						</label>
						<input
							id="edit-profile-picture"
							ref={fileInputRef}
							type="file"
							accept="image/*"
							onChange={(e) =>
								handleFileChange(e.target.files?.[0] ?? null)
							}
							className="w-full text-sm"
						/>
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

				<div className="flex justify-end gap-3 mt-6">
					<button
						type="button"
						onClick={onClose}
						disabled={saving}
						className="px-4 py-2 rounded-sm text-sm border border-border hover:bg-hover"
					>
						Cancel
					</button>
					<button
						type="button"
						onClick={() => void handleSubmit()}
						disabled={saving}
						className="px-4 py-2 rounded-sm text-sm bg-primary text-primary-foreground hover:opacity-90 disabled:opacity-50"
					>
						{saving ? 'Saving…' : 'Save'}
					</button>
				</div>
			</div>
		</div>
	);
}
