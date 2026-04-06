export function runStream(onEvent: (data: any) => void) {
  const evtSource = new EventSource("/stream-demo");

  evtSource.onmessage = (event) => {
    const parsed = JSON.parse(event.data);
    onEvent(parsed);

    if (parsed.status === "Done") {
      evtSource.close();
    }
  };
}