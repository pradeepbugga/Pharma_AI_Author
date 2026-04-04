export default function ControlPanel({ onStart }) {
  return (
    <div className="text-center">
      <p className="mb-2 text-sm">
        Generate IND Introduction
      </p>

      <button
        onClick={onStart}
        className="extract-button"
      >
        Extract
      </button>
    </div>
  );
}