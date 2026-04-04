export function runStream(onEvent: (data: any) => void) {
  const evtSource = new EventSource("http://localhost:8000/stream-demo");

  evtSource.onmessage = (event) => {
    const parsed = JSON.parse(event.data);
    onEvent(parsed);

    if (parsed.status === "Done") {
      evtSource.close();
    }
  };
}