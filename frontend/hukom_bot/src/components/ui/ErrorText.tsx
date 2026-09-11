interface ErrorTextProps {
  error: string;
  onRetry?: () => void;
}

export default function ErrorText({ error, onRetry }: ErrorTextProps) {
  return (
    <div className="flex items-center gap-2">
      <p className="text-xs text-danger" role="alert">
        {error}
      </p>
      {onRetry && (
        <button
          type="button"
          className="text-xs text-primary underline"
          onClick={onRetry}
        >
          Retry
        </button>
      )}
    </div>
  );
}

