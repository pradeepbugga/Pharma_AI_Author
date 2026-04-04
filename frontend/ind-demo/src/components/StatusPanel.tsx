export default function StatusPanel({ statusLogs, currentEntity }: any) {
  return (
    <div className="card">

      {/* STATUS LOGS */}
      {statusLogs.map((s: any, i: number) => (
        <div key={i} className="status-line">
          ✓ {s.status}
        </div>
      ))}

      {/* CURRENT ENTITY (single, live updating) */}
      {currentEntity && (
        <div className="entity-status">
          <div className="entity-line">
            Processed <b>{currentEntity.entity}</b> as <b>{currentEntity.label}</b>
          </div>
          <div className="entity-reasoning">
            {currentEntity.reasoning}
          </div>
        </div>
      )}

    </div>
  );
}