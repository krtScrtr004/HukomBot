// src/components/ui/StatusBadge.tsx
import type { UploadStatus } from '@/types/workspace';

interface StatusBadgeProps {
  status: UploadStatus;
}

const STATUS_STYLES: Record<UploadStatus, string> = {
  pending:   'bg-warning/15 text-warning border-warning/30',
  ongoing:   'bg-info/15 text-info border-info/30',
  completed: 'bg-success/15 text-success border-success/30',
  failed:    'bg-danger/15 text-danger border-danger/30',
  rejected:  'bg-danger/15 text-danger border-danger/30',
};

/**
 * Maps upload status to a pill badge consistent with the Users table role badge design.
 */
export default function StatusBadge({ status }: StatusBadgeProps) {
  const colorClass = STATUS_STYLES[status] ?? 'bg-surface-muted text-text-secondary border-border';

  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border capitalize whitespace-nowrap ${colorClass}`}
    >
      {status}
    </span>
  );
}
