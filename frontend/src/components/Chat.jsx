import { useEffect, useRef, useState } from "react";

export default function Chat() {
  const [messages, setMessages] = useState([]);
  const [text, setText] = useState("");
  const chatRef = useRef(null);

  useEffect(() => {
    if (chatRef.current) {
      chatRef.current.scrollTop = chatRef.current.scrollHeight;
    }
  }, [messages]);

  const onSend = (e) => {
    e.preventDefault();
    const q = text.trim();
    if (!q) return;

    setMessages((prev) => [...prev, { role: "user", content: q }]);
    setText("");
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
        </div>

        <form className="bb-chatForm" onSubmit={onSend}>
          <input
            className="bb-chatInput"
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Ask me C++ questions..."
            autoComplete="off"
          />
          <button className="bb-sendBtn" type="submit">
            Send
          </button>
        </form>
      </div>
    </div>
  );
}
