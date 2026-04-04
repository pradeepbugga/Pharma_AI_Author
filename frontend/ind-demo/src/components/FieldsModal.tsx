export default function FieldModal({ field, onClose }: any) {
  if (!field) return null;

  function renderHTML(text: string) {
    return (
      <span dangerouslySetInnerHTML={{ __html: text }} />
    );
  }

  function splitEvidence(text: string) {
    return text
      .split("...")
      .map((s) => s.trim())
      .filter(Boolean);
  }

  function renderValue(value: any) {
    if (value === null || value === undefined) return null;

    if (typeof value === "object" && !Array.isArray(value)) {
      if (value.raw) return renderHTML(value.raw);

      if (value.standard && value.abbreviation) {
        return renderHTML(`${value.standard} (${value.abbreviation})`);
      }

      return <pre>{JSON.stringify(value, null, 2)}</pre>;
    }

    if (Array.isArray(value)) {
      return (
        <ul>
          {value.map((v, i) => (
            <li key={i}>
              {typeof v === "string"
                ? renderHTML(v)
                : JSON.stringify(v)}
            </li>
          ))}
        </ul>
      );
    }

    if (typeof value === "string") {
      return renderHTML(value);
    }

    return value;
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-card" onClick={(e) => e.stopPropagation()}>

        <h3 className="modal-title">Field Details</h3>

        <div className="modal-row">
          <b>Value:</b> <span>{renderValue(field.value)}</span>
        </div>

        <div className="modal-row">
          <b>Confidence:</b> {field.confidence}
        </div>

        <div className="modal-row">
          <b>Evidence:</b>
          <div className="modal-evidence">
            {typeof field.evidence === "string" ? (
              <ul>
                {splitEvidence(field.evidence).map((item, i) => (
                  <li key={i}>{renderHTML(item)}</li>
                ))}
              </ul>
            ) : (
              renderValue(field.evidence)
            )}
          </div>
        </div>

        {field.validation?.mechanistically_supported && (
          <div className="modal-success">
            ✓ Mechanistically Supported
          </div>
        )}

        <button onClick={onClose} className="modal-close">
          Close
        </button>

      </div>
    </div>
  );
}