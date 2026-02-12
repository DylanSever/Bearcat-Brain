import { useEffect, useRef, useState } from "react";

export default function Chat() {
  const [messages, setMessages] = useState([]);
  const [text, setText] = useState("");

  const [isLoading, setIsLoading] = useState(false);

  const chatRef = useRef(null);

  useEffect(() => {
    if (chatRef.current) {
      chatRef.current.scrollTop = chatRef.current.scrollHeight;
    }
  }, [messages, isLoading]);

  async function sendToBackend(nextMessages) {
    const response = await fetch("http://10.25.1.49:8000/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        model: "llama3.1:8b",
        messages: nextMessages,
      }),
    });
    if (!response.ok) {
      const tmp = await response.text();
      throw new Error(tmp || `Request failed: ${res.status}`);
    }
    return response.json();
  }

  const onSend = async (e) => {
    e.preventDefault();
    const q = text.trim();

    if (!q || isLoading) return;

    const userMsg = { role: "user", content: q };

    const nextMessages = [...messages, userMsg];
    setMessages(nextMessages);

    setText("");
    setIsLoading(true);

    try {
      const data = await sendToBackend(nextMessages);

      const botMsg = { role: "assistant", content: data.reply };
      setMessages((prev) => [...prev, botMsg]);
    } catch (err) {
      setMessages ((prev) => [
        ...prev,
        { role: "assistant", content: `Error: ${err.message}`},
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="bb-page">
      <h1 className="bb-title">Bearcat Brain</h1>

      <div className="bb-chatCard">
        <div className="bb-chatWindow" ref={chatRef}>
          {messages.length === 0 ? (
            <div className="bb-emptyHint">Ask me C++ questions...</div>
          ) : (
            messages.map((m, i) => (
              <div
                key={i}
                className={`bb-msgRow ${m.role === "user" ? "bb-user" : "bb-bot"}`}
              >
                <div className="bb-bubble">{m.content}</div>
              </div>
            ))
          )}

          {isLoading && (
            <div className="bb-msgRow bb-bot">
              <div className="bb-bubble">Thinking...</div>
            </div>
          )}

        </div>

        <form className="bb-chatForm" onSubmit={onSend}>
          <input
            className="bb-chatInput"
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Ask me C++ questions..."
            autoComplete="off"
            disabled={isLoading}
          />
          <button className="bb-sendBtn" type="submit" disabled={isLoading}>
            {isLoading ? "Thinking..." : "Send"}
          </button>
        </form>
      </div>
    </div>
  );
}
