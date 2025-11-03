export function Label({ className = "", children, ...props }) {
  return (
    <label className={`text-sm font-medium text-gray-700 ${className}`} {...props}>
      {children}
    </label>
  );
}
