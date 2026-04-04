type Props = {
  fields: any;
  onSelect: (field: any) => void;
};

// --- VALUE FORMATTER  ---
function renderValue(value: any) {
  if (value === null || value === undefined) return "";

  // arrays
  if (Array.isArray(value)) {
    return value.join(", ");
  }

  // objects (your main issue)
  if (typeof value === "object") {
    if (value.raw) return value.raw;

    if (value.standard && value.abbreviation) {
      return `${value.standard} (${value.abbreviation})`;
    }

    if (value.standard) return value.standard;

    return JSON.stringify(value);
  }

  // string / number
  return value;
}

export default function FieldsPanel({ fields, onSelect }: Props) {
  if (!fields) return null;

  return (
    <div className="p-3 space-y-2">
      {Object.entries(fields).map(([key, field]: any) => (
        <div
          key={key}
          className="border p-2 rounded cursor-pointer hover:bg-gray-50"
          onClick={() => onSelect(field)}
        >
          {/* Label */}
          <div className="font-semibold text-sm">
            {key}
          </div>

          {/* Value */}
          <div className="text-sm">
            {renderValue(field.value)}
          </div>

          {/* Status (nice signal) */}
          {field.status === "present" && (
            <div className="text-xs text-green-600">
              ✓ present
            </div>
          )}
        </div>
      ))}
    </div>
  );
}