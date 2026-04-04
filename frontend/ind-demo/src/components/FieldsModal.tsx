export default function FieldModal({ field, onClose }) {
  if (!field) return null;

  return (
    <div className="fixed inset-0 bg-black/30 flex justify-center items-center">
      <div className="bg-white p-4 w-96">

        <h3 className="font-bold mb-2">
          Field Details
        </h3>

        <div><b>Value:</b> {field.value}</div>
        <div><b>Confidence:</b> {field.confidence}</div>

        <div className="mt-2">
          <b>Evidence:</b>
          <div>{field.evidence}</div>
        </div>

        {field.validation?.mechanistically_supported && (
          <div className="text-green-600 mt-2">
            ✓ Mechanistically Supported
          </div>
        )}

        <button onClick={onClose} className="mt-4">
          Close
        </button>

      </div>
    </div>
  );
}