export function Textarea({ className = "", ...props }) {
  return (
    <textarea
      className={`w-full rounded-xl border px-3 py-2 text-sm shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 ${className}`}
      {...props}
    />
  );
}
