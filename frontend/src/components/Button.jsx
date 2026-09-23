export default function Button({
  children,
  variant = 'primary',
  size = 'md',
  disabled = false,
  loading = false,
  icon: Icon,
  onClick,
  type = 'button',
  className = '',
}) {
  const base =
    'inline-flex items-center justify-center gap-2 font-medium rounded-xl transition-all duration-150 focus:outline-none focus-visible:ring-2 focus-visible:ring-primary/50 disabled:opacity-50 disabled:cursor-not-allowed';

  const variants = {
    primary:
      'bg-primary text-white shadow-soft hover:bg-primary-hover hover:shadow-lift active:scale-[0.98]',
    secondary:
      'bg-secondary text-primary border border-primary/20 hover:bg-primary-light active:scale-[0.98]',
    outline:
      'bg-transparent text-ink-900 border border-slate-200 hover:border-slate-300 hover:bg-slate-50 active:scale-[0.98]',
    ghost: 'bg-transparent text-ink-600 hover:bg-slate-100 active:scale-[0.98]',
    danger: 'bg-danger text-white hover:bg-red-700 active:scale-[0.98]',
  };

  const sizes = {
    sm: 'text-sm px-3 py-1.5',
    md: 'text-sm px-4 py-2.5',
    lg: 'text-base px-6 py-3',
  };

  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled || loading}
      className={`${base} ${variants[variant]} ${sizes[size]} ${className}`}
    >
      {loading ? (
        <span className="h-4 w-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
      ) : (
        Icon && <Icon className="h-4 w-4" />
      )}
      {children}
    </button>
  );
}
