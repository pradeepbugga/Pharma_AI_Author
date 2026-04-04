type Props = {
  ind: any;
};

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
    <div className="p-4">
      <h3 className="font-bold mb-2">IND Output</h3>

      <p className="text-sm whitespace-pre-wrap">
        {renderValue(ind)}
      </p>
    </div>
  );
}