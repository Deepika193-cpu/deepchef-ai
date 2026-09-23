export default function Card({
  children,
  className = '',
  hover = false,
  padding = 'md',
}) {
  const paddings = {
    none: '',
    sm: 'p-4',
    md: 'p-6',
    lg: 'p-8',
  };

  return (
    <div
      className={`bg-surface-card rounded-card shadow-soft border border-slate-100 ${
        hover ? 'transition-shadow duration-200 hover:shadow-softer' : ''
      } ${paddings[padding]} ${className}`}
    >
      {children}
    </div>
  );
}
