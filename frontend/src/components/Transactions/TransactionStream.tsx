import { useEffect, useRef } from "react";

const TransactionStream = ({ onMessage }: { onMessage: (data: any) => void }) => {
  const evtSourceRef = useRef<EventSource | null>(null);

  useEffect(() => {
    if (evtSourceRef.current) return; // already connected

    const evtSource = new EventSource("http://localhost:8080⁠/transactions/stream");
    evtSourceRef.current = evtSource;

    evtSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data); // parse the string
        onMessage(data);
      } catch (err) {
        console.error("Failed to parse SSE data:", err);
      }
    };

    evtSource.onerror = (err) => {
      console.error("SSE error:", err);
      // optionally close or retry
      // evtSource.close();
    };

    return () => {
      evtSource.close();
      evtSourceRef.current = null;
    };
  }, []); // empty dependency array ensures this effect runs only once

  return null; // no UI
};

export default TransactionStream;
