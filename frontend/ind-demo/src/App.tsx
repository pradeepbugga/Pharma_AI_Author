import { useState } from "react";
import PDFPanel from "./components/PDFPanel";
import ControlPanel from "./components/ControlPanel";
import StatusPanel from "./components/StatusPanel";
import FieldsPanel from "./components/FieldsPanel";
import FieldModal from "./components/FieldsModal";
import INDPanel from "./components/INDPanel";
import { runStream } from "./api";

export default function App() {

  const [status, setStatus] = useState<string[]>([]);
  const [fields, setFields] = useState<any>(null);
  const [ind, setInd] = useState<string | null>(null);
  const [selectedField, setSelectedField] = useState<any>(null);



  function handleStart() {
    setStatus([]);
    setFields(null);
    setInd(null);

    runStream((event) => {
      if (event.status !== "Done") {
        setStatus((prev) => [...prev, event.status]);
      } else {
        setFields(event.fields);
        setInd(event.intro);
      }
    });
  }

   return (
    
    <div className="h-screen flex flex-col">

  {/* TITLE */}
  <div className="px-6 py-4 border-b">
    <h1 className="text-xl font-semibold">
      Paper to IND | AI Authoring
    </h1>
  </div>

  {/* MAIN CONTENT */}
  <div className="flex-1 grid grid-cols-3 grid-rows-[1fr_250px]">

    {/* Left */}
    <div className="border h-full">
      <PDFPanel />
    </div>

    {/* Center */}
    <div className="border flex items-center justify-center">
      <ControlPanel onStart={handleStart} />
    </div>

    {/* Right */}
    <div className="border overflow-y-auto">
      <StatusPanel status={status} />
      <FieldsPanel fields={fields} onSelect={setSelectedField} />
    </div>

    {/* Bottom */}
    <div className="col-span-3 border">
      <INDPanel ind={ind} />
    </div>

  </div>

</div>
  );
}