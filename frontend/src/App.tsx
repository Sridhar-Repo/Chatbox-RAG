import { ChatThread } from "./components/ChatThread";
import { Composer } from "./components/Composer";
import { DocumentPanel } from "./components/DocumentPanel";
import { useChat } from "./hooks/useChat";
import { useDocuments } from "./hooks/useDocuments";

export default function App() {
  const { docs, status, upload, remove } = useDocuments();
  const { messages, busy, ask } = useChat();

  return (
    <div className="app">
      <DocumentPanel docs={docs} status={status} onUpload={upload} onRemove={remove} />
      <main className="chat">
        <ChatThread messages={messages} hasDocs={docs.length > 0} />
        <Composer disabled={busy} onSubmit={ask} />
      </main>
    </div>
  );
}
