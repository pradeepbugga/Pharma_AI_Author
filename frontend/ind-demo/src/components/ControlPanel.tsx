export default function ControlPanel({ onStart }:any) {
  return (
    <div className="control-panel">

      <p className="control-title">
        Generate <br/> 
        IND Introduction
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