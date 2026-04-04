export default function PDFPanel() {
  return (
    <div className="pdf-panel">

      {/* Panel title */}
      <div className="panel-header">
        Preclinical KRAS Drug Paper
      </div>

      {/* PDF */}
      <div className="pdf-container">
        <iframe
          src="/paper.pdf"
          className="pdf-frame"
        />
      </div>

    </div>
  );
}