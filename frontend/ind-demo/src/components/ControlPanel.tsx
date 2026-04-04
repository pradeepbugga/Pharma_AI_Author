export default function ControlPanel({ onStart }) {
  return (
    <div className="text-center">
      <p className="mb-2 text-sm">
        Extract structured IND fields
      </p>

      <button
        onClick={onStart}
        className="px-4 py-2 border rounded"
      >
        Extract
      </button>
    </div>
  );
}