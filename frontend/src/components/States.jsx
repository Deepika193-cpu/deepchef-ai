// Shared feedback states: loading, empty, and error — used across every screen
// so the app never shows a blank pane or a raw stack trace.

export function LoadingState({ message = 'Loading…' }) {
  return (
    <div className="flex flex-col items-center justify-center py-16 gap-3 animate-fade-in">
      <span className="h-8 w-8 border-[3px] border-primary border-t-transparent rounded-full animate-spin" />
      <p className="text-sm text-ink-600">{message}</p>
    </div>
  );
}

export function SkeletonCard() {
  return (
    <div className="rounded-card border border-slate-100 p-6 space-y-4">
      <div className="skeleton h-40 w-full" />
      <div className="skeleton h-4 w-2/3" />
      <div className="skeleton h-4 w-1/3" />
    </div>
  );
}

export function EmptyState({
  icon: Icon,
  title,
  description,
  action,
}) {
  return (
    <div className="flex flex-col items-center justify-center text-center py-16 px-6 animate-fade-in">
      {Icon && (
        <div className="h-14 w-14 rounded-full bg-secondary flex items-center justify-center mb-4">
          <Icon className="h-6 w-6 text-primary" />
        </div>
      )}
      <h3 className="font-display font-semibold text-ink-900 mb-1">{title}</h3>
      {description && (
        <p className="text-sm text-ink-600 max-w-sm mb-4">{description}</p>
      )}
      {action}
    </div>
  );
}

export function ErrorMessage({ title = 'Something went wrong', description, onRetry }) {
  return (
    <div className="flex items-start gap-3 rounded-card border border-red-100 bg-red-50 p-4 animate-fade-in">
      <span className="h-2 w-2 mt-1.5 rounded-full bg-danger shrink-0" />
      <div className="flex-1">
        <p className="text-sm font-medium text-ink-900">{title}</p>
        {description && <p className="text-sm text-ink-600 mt-0.5">{description}</p>}
        {onRetry && (
          <button
            onClick={onRetry}
            className="text-sm font-medium text-primary hover:text-primary-hover mt-2"
          >
            Try again
          </button>
        )}
      </div>
    </div>
  );
}
