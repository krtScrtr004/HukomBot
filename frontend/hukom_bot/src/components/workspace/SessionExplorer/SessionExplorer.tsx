import { useCallback, useState } from 'react';
import { useWorkspace } from '@/contexts/WorkspaceContext';
import EmptyState from '@/components/workspace/shared/EmptyState';
import LoadingSpinner from '@/components/workspace/shared/LoadingSpinner';
import SessionListItem from '@/components/workspace/SessionExplorer/SessionListItem';
import SessionSearchInput from '@/components/workspace/SessionExplorer/SessionSearchInput';

interface SessionExplorerProps {
	onSettingsClick?: () => void;
	onSignOut?: () => void;
}

export default function SessionExplorer({
	onSettingsClick,
	onSignOut,
}: SessionExplorerProps) {
	const {
		state,
		selectSession,
		loadMoreSessions,
		searchSessions,
		refreshSessions,
		requestNewAnalysis,
		requestDeleteSession,
	} = useWorkspace();

	const [dropdownOpen, setDropdownOpen] = useState(false);

	const isLoading = state.loading.sessions || state.loading.initializing;

	const handleSearch = useCallback(
		(q: string | null) => {
			void searchSessions(q);
		},
		[searchSessions],
	);

	const user = state.user;
	const profilePicture = user?.profile_picture;
	const avatarLetter = user?.first_name
		? user.first_name[0].toUpperCase()
		: '?';
	const firstName = user?.first_name || 'User';
	const fullName = user ? `${user.first_name} ${user.last_name}` : 'User';
	const email = user?.email || '';

	const planName =
		user?.role === 'admin'
			? 'Admin'
			: user?.role === 'contributor'
				? 'Contributor'
				: 'Free';

	return (
		<div className="flex flex-col h-full">
			{/* Search section */}
			<section className="p-3 border-b border-border space-y-3 shrink-0">
				<div className="flex items-center justify-between gap-2">
					<h2 className="text-sm font-semibold text-text-primary">
						<span className="mr-2">
							<i className="bi bi-briefcase" />
						</span>
						Sessions
					</h2>

					{/* Retry button */}
					<button
						type="button"
						onClick={() => void refreshSessions()}
						disabled={isLoading}
						className="p-1.5 rounded-sm text-text-secondary hover:bg-hover focus:outline-none focus-visible:ring-2 focus-visible:ring-primary disabled:opacity-50"
						aria-label="Refresh sessions"
					>
						<i
							className="bi bi-arrow-clockwise"
							aria-hidden="true"
						/>
					</button>
				</div>

				{/* Search bar */}
				<SessionSearchInput
					onSearch={handleSearch}
					disabled={isLoading}
				/>

				{/* Create new analysis button */}
				<button
					type="button"
					onClick={requestNewAnalysis}
					className="w-full flex items-center justify-center gap-2 px-4 py-2 rounded-sm text-sm font-medium bg-primary text-primary-foreground hover:opacity-90 focus:outline-none focus-visible:ring-2 focus-visible:ring-primary"
				>
					<i className="bi bi-plus-lg" aria-hidden="true" />
					New Analysis
				</button>
			</section>

			{/* Session list */}
			<section
				className="flex-1 overflow-y-auto p-2 space-y-1 scrollbar-thin"
				role="listbox"
				aria-label="Analysis sessions"
			>
				{isLoading && state.sessions.length === 0 ? (
					<LoadingSpinner
						label="Loading sessions"
						className="py-12"
					/>
				) : state.errors.sessions ? (
					<EmptyState
						icon="bi-exclamation-triangle"
						title="Failed to load sessions"
						description={state.errors.sessions}
						action={
							<button
								type="button"
								onClick={() => void refreshSessions()}
								className="text-sm text-text-link hover:underline focus:outline-none focus-visible:ring-2 focus-visible:ring-primary rounded-sm"
							>
								Retry
							</button>
						}
					/>
				) : state.sessions.length === 0 ? (
					<EmptyState
						title="No sessions yet"
						description="Create your first analysis to get started with legal research."
						action={
							<button
								type="button"
								onClick={requestNewAnalysis}
								className="mt-2 px-4 py-2 rounded-sm text-sm font-medium bg-primary text-primary-foreground hover:opacity-90 focus:outline-none focus-visible:ring-2 focus-visible:ring-primary"
							>
								New Analysis
							</button>
						}
					/>
				) : (
					<>
						{state.sessions
							.sort(
								// Render sessions with the most recent updates first
								(a, b) =>
									new Date(b.updated_at).getTime() -
									new Date(a.updated_at).getTime(),
							)
							.map((session) => (
								<SessionListItem
									key={session.case_analysis_session_id}
									session={session}
									isSelected={
										session.case_analysis_session_id ===
										state.selectedSessionId
									}
									onSelect={(id) => void selectSession(id)}
									onDelete={requestDeleteSession}
								/>
							))}

						{state.sessionsPagination.hasMore && (
							<div className="py-4 flex justify-center">
								{state.loading.sessionsMore ? (
									<LoadingSpinner
										size="sm"
										label="Loading more sessions"
									/>
								) : (
									<button
										type="button"
										onClick={() => void loadMoreSessions()}
										className="w-full mx-2 py-2 px-4 rounded-sm text-xs font-medium border border-border text-text-secondary hover:bg-hover hover:text-text-primary focus:outline-none focus-visible:ring-2 focus-visible:ring-primary transition-colors cursor-pointer"
									>
										Load More Sessions
									</button>
								)}
							</div>
						)}
					</>
				)}
			</section>

			{/* User Settings Toggle and Profile Footer */}
			<footer className="mt-auto border-t border-border bg-sidebar p-3 flex items-center justify-between gap-2 relative shrink-0">
				{/* Profile Toggle Button */}
				<button
					type="button"
					onClick={() => setDropdownOpen((prev) => !prev)}
					className="flex items-center gap-2.5 hover:bg-hover rounded-sm flex-1 text-left min-w-0 transition-colors cursor-pointer"
					aria-label="User menu"
					aria-expanded={dropdownOpen}
					aria-haspopup="true"
				>
					{/* Avatar */}
					<div className="w-8 h-8 rounded-full bg-neutral-700 dark:bg-neutral-800 text-white font-semibold flex items-center justify-center text-xs shrink-0 select-none">
						{profilePicture ? (
							<img
								src={profilePicture}
								alt="Avatar preview"
								className="w-full h-full object-cover rounded-full"
							/>
						) : (
							avatarLetter
						)}
					</div>

					{/* Name and Plan */}
					<div className="flex-1 min-w-0">
						<div className="flex items-center gap-1.5 text-xs text-text-secondary font-medium">
							<span className="text-sm font-semibold text-text-primary truncate">
								{firstName}
							</span>
							<span className="text-text-muted select-none">
								·
							</span>
							<span className="text-xs text-text-secondary truncate">
								{planName}
							</span>
						</div>
					</div>
					{/* Chevron Down */}
					<i
						className="bi bi-chevron-down text-text-secondary text-xs shrink-0"
						aria-hidden="true"
					/>
				</button>

				{/* Dropdown Menu */}
				{dropdownOpen && (
					<>
						<div
							className="fixed inset-0 z-popover cursor-default"
							onClick={() => setDropdownOpen(false)}
							aria-hidden="true"
						/>
						<div className="absolute bottom-full left-3 right-3 mb-2 z-popover bg-surface border border-border rounded-sm shadow-md p-1.5 min-w-50 flex flex-col text-sm fade-in">
							<div className="px-3 py-2 border-b border-border mb-1 select-none">
								<p className="font-semibold text-text-primary truncate">
									{fullName}
								</p>
								<p className="text-xs text-text-secondary truncate">
									{email}
								</p>
							</div>
							<button
								type="button"
								onClick={() => {
									setDropdownOpen(false);
									onSettingsClick?.();
								}}
								className="w-full flex items-center gap-2.5 px-3 py-2 text-left text-text-primary hover:bg-hover rounded-sm transition-colors cursor-pointer mt-1"
							>
								<i className="bi bi-gear" aria-hidden="true" />
								Settings
							</button>
							<button
								type="button"
								onClick={() => {
									setDropdownOpen(false);
									onSignOut?.();
								}}
								className="w-full flex items-center gap-2.5 px-3 py-2 text-left text-danger hover:bg-danger/10 rounded-sm transition-colors cursor-pointer"
							>
								<i
									className="bi bi-box-arrow-right"
									aria-hidden="true"
								/>
								Sign out
							</button>
						</div>
					</>
				)}
			</footer>
		</div>
	);
}
