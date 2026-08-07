import { useCallback, useRef } from 'react';
import { useWorkspace } from '@/contexts/WorkspaceContext';
import EmptyState from '@/components/workspace/shared/EmptyState';
import LoadingSpinner from '@/components/workspace/shared/LoadingSpinner';
import VersionListItem from '@/components/workspace/VersionPanel/VersionListItem';

export default function VersionExplorer() {
	const { state, selectVersion, loadMoreVersions } = useWorkspace();
	const observerRef = useRef<IntersectionObserver | null>(null);

	const loadMoreVersionsRef = useRef(loadMoreVersions);
	loadMoreVersionsRef.current = loadMoreVersions;

	const attachSentinel = useCallback(
		(node: HTMLDivElement | null) => {
			if (observerRef.current) {
				observerRef.current.disconnect();
			}

			if (!node) {
				return;
			}

			observerRef.current = new IntersectionObserver(
				(entries) => {
					if (entries[0]?.isIntersecting) {
						void loadMoreVersionsRef.current();
					}
				},
				{ threshold: 0.1 },
			);
			observerRef.current.observe(node);
		},
		[loadMoreVersions],
	);

	if (!state.selectedSessionId) {
		return (
			<EmptyState
				title="No session selected"
				description="Select a session to view its analysis versions."
			/>
		);
	}

	const isLoading = state.loading.versions;

	return (
		<div className="flex flex-col h-full">
			<section className="p-3 border-b border-border shrink-0">
				<h2 className="text-sm font-semibold text-text-primary">
					<span className="mr-2">
						<i className="bi bi-clock-history" />
					</span>
					Versions
				</h2>
			</section>

			{/* Version list */}
			<section
				className="flex-1 overflow-y-auto p-2 space-y-1 scrollbar-thin"
				role="listbox"
				aria-label="Analysis versions"
			>
				{isLoading && state.versions.length === 0 ? (
					<LoadingSpinner
						label="Loading versions"
						className="py-12"
					/>
				) : state.errors.versions ? (
					<EmptyState
						icon="bi-exclamation-triangle"
						title="Failed to load versions"
						description={state.errors.versions}
						action={
							<button
								type="button"
								className="p-1.5 rounded-sm text-text-secondary hover:bg-hover focus:outline-none focus-visible:ring-2 focus-visible:ring-primary"
								aria-label="Retry loading versions"
								onClick={() => void loadMoreVersions()}
							>
								<i
									className="bi bi-arrow-clockwise"
									aria-hidden="true"
								/>
								Retry
							</button>
						}
					/>
				) : state.versions.length === 0 ? (
					<EmptyState
						title="No versions"
						description="No analysis versions exist for this session."
					/>
				) : (
					<>
						{[...state.versions]
							.sort((a, b) => b.version_number - a.version_number)
							.map((version) => (
								<VersionListItem
									key={version.id}
									version={version}
									isSelected={
										version.version_number ===
										state.selectedVersionNumber
									}
									onSelect={(n) => void selectVersion(n)}
								/>
							))}
						{state.versionsPagination.hasMore && (
							<div
								ref={attachSentinel}
								className="py-4 flex justify-center"
							>
								{state.loading.versionsMore && (
									<LoadingSpinner
										size="sm"
										label="Loading more versions"
									/>
								)}
							</div>
						)}
					</>
				)}
			</section>
		</div>
	);
}
