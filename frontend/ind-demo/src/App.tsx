import { useState } from "react";
import PDFPanel from "./components/PDFPanel";
import ControlPanel from "./components/ControlPanel";
import StatusPanel from "./components/StatusPanel";
import FieldsPanel from "./components/FieldsPanel";
import FieldModal from "./components/FieldsModal";
import INDPanel from "./components/INDPanel";
import { runStream } from "./api";

export default function App() {


  const [fields, setFields] = useState<any>(null);
  const [ind, setInd] = useState<string | null>(null);
  const [selectedField, setSelectedField] = useState<any>(null);
  const [statusLogs, setStatusLogs] = useState<any[]>([]);
  const [currentEntity, setCurrentEntity] = useState<any>(null);


  function handleStart() {
    setFields(null);
    setInd(null);
    setStatusLogs([]);
    setCurrentEntity(null);

    runStream((event) => {

      if (event.type === "entity") {
        setCurrentEntity(event);
      }

      if (event.status && event.status !== "Done") {
        setCurrentEntity(null);
        setStatusLogs((prev) => [
          ...prev,
          { status: event.status }
        ]);
      }

      if (event.type === "Done" || event.status === "Done") {
        setCurrentEntity(null);
        setFields(event.fields);
        setInd(event.intro);
      }

    });
  }

  return (
  <div className="app-container">

    {/* HEADER */}
    <div className="app-header">
      <h1 className="app-title">
        Paper to IND | AI Authoring
      </h1>
    </div>

    {/* MAIN GRID */}
    <div className="app-main">

      {/* Left */}
      <div className="panel-left">
        <PDFPanel />
      </div>

      {/* Center */}
      <div className="panel-center">
        <ControlPanel onStart={handleStart} />
      </div>

      {/* Right */}
      <div className="panel-right">
        
      {!fields && (
        <StatusPanel 
          statusLogs={statusLogs} 
          currentEntity={currentEntity} 
        />
      )}

      {fields && (
        <FieldsPanel 
          fields={fields} 
          onSelect={setSelectedField} 
        />
      )}

    </div>

      {/* Bottom */}
      <div className="ind-container">
        <INDPanel ind={ind} />
      </div>

    </div>

    {selectedField && (
      <FieldModal
        field={selectedField}
        onClose={() => setSelectedField(null)}
      />
    )}

  </div>
);
} 


