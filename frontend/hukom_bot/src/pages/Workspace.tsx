import { useState } from 'react';
import { WorkspaceProvider, useWorkspace } from '@/contexts/WorkspaceContext';
import { getLogoutUrl } from '@/services/authService';
import WorkspaceLayout from '@/layouts/WorkspaceLayout';
import Header from '@/components/workspace/Header';
import SessionExplorer from '@/components/workspace/SessionExplorer/SessionExplorer';
import VersionExplorer from '@/components/workspace/VersionPanel/VersionExplorer';
import AnalysisViewer from '@/components/workspace/AnalysisWorkspace/AnalysisViewer';
import CaseFactsViewer from '@/components/workspace/AnalysisWorkspace/CaseFactsViewer';
import EditReanalyzeWorkspace from '@/components/workspace/AnalysisWorkspace/EditReanalyzeWorkspace';
import NewAnalysisModal from '@/components/workspace/AnalysisWorkspace/NewAnalysisModal';
import EmptyState from '@/components/workspace/shared/EmptyState';
import LoadingSpinner from '@/components/workspace/shared/LoadingSpinner';
import ConfirmDialog from '@/components/workspace/shared/ConfirmDialog';
import UploadDocumentModal from '@/components/workspace/shared/UploadDocumentModal';
import SettingsModal from '@/components/workspace/shared/SettingsModal';

function AnalysisWorkspaceContent() {
	const { state } = useWorkspace();

	if (state.loading.initializing && !state.selectedSessionId) {
		return <LoadingSpinner label="Loading workspace" className="py-24" />;
	}

	if (!state.selectedSessionId) {
		return (
			<EmptyState
				title="No analysis selected"
				description="Select an existing session from the sidebar or create a new analysis to get started."
			/>
		);
	}

	if (state.mode === 'edit') {
		return <EditReanalyzeWorkspace />;
	}

	return (
		<div className="flex flex-col gap-6 p-4 md:p-6 overflow-y-auto h-full scrollbar-thin">
			<AnalysisViewer />
			{state.currentAnalysis && (
				<CaseFactsViewer caseFacts={state.currentAnalysis.case_facts} />
			)}
		</div>
	);
}

function WorkspacePage() {
	const {
		state,
		confirmDialog,
		newAnalysisModalOpen,
		setNewAnalysisModalOpen,
	} = useWorkspace();

	const [sidebarOpen, setSidebarOpen] = useState(false);
	const [versionPanelOpen, setVersionPanelOpen] = useState(false);
	const [uploadDocumentModalOpen, setUploadDocumentModalOpen] =
		useState(false);
	const [settingsModalOpen, setSettingsModalOpen] = useState(false);

	if (state.loading.auth) {
		return (
			<div className="h-dvh flex items-center justify-center bg-background">
				<LoadingSpinner size="lg" label="Authenticating" />
			</div>
		);
	}

	const userName = state.user
		? `${state.user.first_name} ${state.user.last_name}`
		: undefined;

	return (
		<>
			<WorkspaceLayout
				sidebarOpen={sidebarOpen}
				versionPanelOpen={versionPanelOpen}
				onSidebarClose={() => setSidebarOpen(false)}
				onVersionPanelClose={() => setVersionPanelOpen(false)}
				header={
					<Header
						userName={userName}
						userRole={state.user?.role}
						onToggleSidebar={() => setSidebarOpen((v) => !v)}
						onToggleVersionPanel={() =>
							setVersionPanelOpen((v) => !v)
						}
						onSignOut={() => {
							window.location.href = getLogoutUrl();
						}}
						onUploadClick={() => setUploadDocumentModalOpen(true)}
						onSettingsClick={() => setSettingsModalOpen(true)}
					/>
				}
				sidebar={
					<SessionExplorer
						onSettingsClick={() => setSettingsModalOpen(true)}
						onSignOut={() => {
							window.location.href = getLogoutUrl();
						}}
					/>
				}
				workspace={<AnalysisWorkspaceContent />}
				versionPanel={<VersionExplorer />}
			/>

			<NewAnalysisModal
				open={newAnalysisModalOpen}
				onClose={() => setNewAnalysisModalOpen(false)}
			/>

			<UploadDocumentModal
				open={uploadDocumentModalOpen}
				onClose={() => setUploadDocumentModalOpen(false)}
			/>

			<SettingsModal
				open={settingsModalOpen}
				onClose={() => setSettingsModalOpen(false)}
			/>

			{confirmDialog && (
				<ConfirmDialog
					open={confirmDialog.open}
					title={confirmDialog.title}
					message={confirmDialog.message}
					confirmLabel={confirmDialog.confirmLabel}
					cancelLabel={confirmDialog.cancelLabel}
					variant={confirmDialog.variant}
					onConfirm={confirmDialog.onConfirm}
					onCancel={confirmDialog.onCancel}
				/>
			)}

			{state.loading.generating && state.mode === 'edit' && (
				<div className="fixed inset-0 z-(--z-dialog) bg-surface-overlay/80 flex items-center justify-center">
					<div className="flex flex-col items-center gap-3">
						<div className="w-10 h-10 border-3 border-border border-t-primary rounded-full animate-spin" />
						<p className="text-sm text-text-secondary">
							Generating analysis…
						</p>
					</div>
				</div>
			)}
		</>
	);
}

export default function Workspace() {
	return (
		<WorkspaceProvider>
			<WorkspacePage />
		</WorkspaceProvider>
	);
}
