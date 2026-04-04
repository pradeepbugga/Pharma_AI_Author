type Props = {
  ind: any;
};

function renderHTML(text: string) {
  return (
    <span dangerouslySetInnerHTML={{ __html: text }} />
  );
}

// reuse same logic as FieldsPanel
function renderValue(value: any) {
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

    return JSON.stringify(value, null, 2);
  }

  return value;
}

export default function INDPanel({ ind }: Props) {
  if (!ind) return null;

  return (
    <div className="ind-container">
      <h3 className="ind-text">IND Output</h3>

      <p className="text-sm whitespace-pre-wrap">
        {renderHTML(renderValue(ind))}  
      </p>
    </div>
  );
}