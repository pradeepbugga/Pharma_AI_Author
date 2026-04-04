export default function PDFPanel() {
  return (
    <div className="pdf-container">
       <iframe
          src="/paper.pdf"
          className="pdf-frame"
        />
    </div>
  );
}