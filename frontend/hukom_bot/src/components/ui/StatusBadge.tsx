// src/components/ui/StatusBadge.tsx
import type { UploadStatus } from '@/types/workspace';

interface StatusBadgeProps {
  status: UploadStatus;
}

/**
 * Maps upload status to theme colors and displays a capitalized label.
 */
export default function StatusBadge({ status }: StatusBadgeProps) {
  const colorMap: Record<UploadStatus, string> = {
    pending: '--color-warning',
    ongoing: '--color-info',
    completed: '--color-success',
    failed: '--color-danger',
    rejected: '--color-danger',
  } as const;

  const bgColor = colorMap[status] || '--color-muted';

  return (
    <span
      className="inline-block px-2 py-1 text-xs font-medium rounded" style={{ backgroundColor: `var(${bgColor})` }}
    >
      {status.charAt(0).toUpperCase() + status.slice(1)}
    </span>
  );
}

