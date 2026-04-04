type Props = {
  fields: any;
  onSelect: (field: any) => void;
};

function renderHTML(text: string) {
  return (
    <span dangerouslySetInnerHTML={{ __html: text }} />
  );
}

function formatFormula(formula: string) {
  return formula.replace(/(\d+)/g, "<sub>$1</sub>");
}

function renderValue(value: any, fieldKey?: string) {
  if (value === null || value === undefined) return "";

  if (Array.isArray(value)) {
    return value.join(", ");
  }

  if (typeof value === "object") {
    if (value.raw) return value.raw;

    if (value.standard && value.abbreviation) {
      return `${value.standard} (${value.abbreviation})`;
    }

    if (value.standard) return value.standard;

    return JSON.stringify(value);
  }

  if (typeof value === "string") {

    if (fieldKey === "Structural Formula") {
      return renderHTML(formatFormula(value));
    }

    if (fieldKey === "Pharmacological Class") {
      return renderHTML(value);
    }

    return value;
  }

  return value;
}

export default function FieldsPanel({ fields, onSelect }: Props) {
  if (!fields) return null;

  return (
    <div className="card">
      {Object.entries(fields).map(([key, field]: any) => (
        <div
          key={key}
          className="field-item"
          onClick={() => {
            console.log("clicked", field);
            onSelect(field);
          }}
        >
          <div className="field-label">{key}</div>

          <div className="field-value">
            {renderValue(field.value, key)}
          </div>

          {field.status === "present" && (
            <div className="field-status">
              ✓ present
            </div>
          )}
        </div>
      ))}
    </div>
  );
}