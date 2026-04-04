export default function StatusPanel({ status }) {
  return (
    <div className="p-2 text-sm">
      {status.map((s, i) => (
        <div key={i}>✓ {s}</div>
      ))}
    </div>
  );
}