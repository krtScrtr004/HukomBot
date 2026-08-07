import { useCallback } from 'react';
import { useWorkspace } from '@/contexts/WorkspaceContext';
import EmptyState from '@/components/workspace/shared/EmptyState';
import LoadingSpinner from '@/components/workspace/shared/LoadingSpinner';
import SessionListItem from '@/components/workspace/SessionExplorer/SessionListItem';
import SessionSearchInput from '@/components/workspace/SessionExplorer/SessionSearchInput';

export default function SessionExplorer() {
	const {
		state,
		selectSession,
		loadMoreSessions,
		searchSessions,
		refreshSessions,
		requestNewAnalysis,
		requestDeleteSession,
	} = useWorkspace();

	const isLoading = state.loading.sessions || state.loading.initializing;

	const handleSearch = useCallback(
		(q: string | null) => {
			void searchSessions(q);
		},
		[searchSessions],
	);

	return (
		<div className="flex flex-col h-full">
			<div className="p-3 border-b border-border space-y-3 shrink-0">
				<div className="flex items-center justify-between gap-2">
					<h2 className="text-sm font-semibold text-text-primary">
						Sessions
					</h2>
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
				<SessionSearchInput
					onSearch={handleSearch}
					disabled={isLoading}
				/>
				<button
					type="button"
					onClick={requestNewAnalysis}
					className="w-full flex items-center justify-center gap-2 px-4 py-2 rounded-sm text-sm font-medium bg-primary text-primary-foreground hover:opacity-90 focus:outline-none focus-visible:ring-2 focus-visible:ring-primary"
				>
					<i className="bi bi-plus-lg" aria-hidden="true" />
					New Analysis
				</button>
			</div>

			<div
				className="flex-1 overflow-y-auto p-2 space-y-1"
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
						{state.sessions.map((session) => (
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
			</div>
		</div>
	);
}
