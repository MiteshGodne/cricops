export default function Input({ label, error, className = '', ...props }) {
  return (
    <div className="mb-3">
      {label && <label className="block text-sm font-medium mb-1">{label}</label>}
      <input
        className={`w-full border rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 ${error ? 'border-red-500' : 'border-gray-300'} ${className}`}
        {...props}
      />
      {error && <p className="text-red-500 text-xs mt-1">{error}</p>}
    </div>
  );
}
