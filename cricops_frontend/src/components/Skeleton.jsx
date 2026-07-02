export default function Skeleton({ rows = 4, className = '' }) {
    return (
      <div className={`space-y-2 ${className}`}>
        {Array.from({ length: rows }).map((_, i) => (
          <div key={i} className="animate-pulse bg-gray-200 rounded h-10 w-full" />
        ))}
      </div>
    );
  }