export default function ProgressBar({
  value,
  max = 100,
  label,
  showValue = true,
  color = 'primary',
  size = 'md',
}) {
  const pct = Math.min(100, Math.max(0, (value / max) * 100));

  const colors = {
    primary: 'bg-primary',
    accent: 'bg-accent',
    warning: 'bg-warning',
    danger: 'bg-danger',
  };

  const heights = { sm: 'h-1.5', md: 'h-2.5', lg: 'h-4' };

  return (
    <div className="w-full">
      {(label || showValue) && (
        <div className="flex items-center justify-between mb-1.5 text-sm">
          {label && <span className="text-ink-600">{label}</span>}
          {showValue && (
            <span className="font-medium text-ink-900">{Math.round(pct)}%</span>
          )}
        </div>
      )}
      <div className={`w-full bg-slate-100 rounded-full overflow-hidden ${heights[size]}`}>
        <div
          className={`${heights[size]} ${colors[color]} rounded-full transition-all duration-500 ease-out`}
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
}
