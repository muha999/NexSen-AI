import React, { useState, useRef, useEffect } from "react";
import aichaProfile from "./assets/aichaprofile.png";

const API_URL = "http://127.0.0.1:8000";

function App() {
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content: "Bonjour ! Je suis AICHA, votre assistante NexSen AI. Comment puis-je vous aider aujourd'hui ?",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim()) return;
    const userMessage = { role: "user", content: input };
    const newMessages = [...messages, userMessage];
    setMessages(newMessages);
    setInput("");
    setLoading(true);
    try {
      const history = newMessages.slice(0, -1).map((m) => ({ role: m.role, content: m.content }));
      const response = await fetch(`${API_URL}/aicha/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: input, history }),
      });
      const data = await response.json();
      setMessages([...newMessages, { role: "assistant", content: data.response }]);
    } catch (error) {
      setMessages([...newMessages, { role: "assistant", content: "⚠️ Erreur de connexion à AICHA." }]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div style={styles.container}>
      {/* Header */}
      <div style={styles.header}>
        <div style={styles.headerLeft}>
          <img src={aichaProfile} alt="AICHA" style={styles.avatarImg} />
          <div>
            <div style={styles.agentName}>AICHA</div>
            <div style={styles.agentStatus}>● En ligne — NexSen AI</div>
          </div>
        </div>
        <div style={styles.nexsenBadge}>🌍 NexSen AI</div>
      </div>

      {/* Messages */}
      <div style={styles.messagesContainer}>
        {messages.map((msg, i) => (
          <div key={i} style={{ display: "flex", justifyContent: msg.role === "user" ? "flex-end" : "flex-start", marginBottom: 24, alignItems: "flex-end", gap: 12 }}>
            {msg.role === "assistant" && (
              <img src={aichaProfile} alt="AICHA" style={styles.avatarImgSmall} />
            )}
            <div style={msg.role === "user" ? styles.userBubble : styles.aichaBubble}>
              {msg.content}
            </div>
          </div>
        ))}
        {loading && (
          <div style={{ display: "flex", justifyContent: "flex-start", marginBottom: 24, alignItems: "flex-end", gap: 12 }}>
            <img src={aichaProfile} alt="AICHA" style={styles.avatarImgSmall} />
            <div style={styles.typingBubble}>● &nbsp; ● &nbsp; ●</div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div style={styles.inputContainer}>
        <input
          style={styles.input}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Écrivez votre message à AICHA..."
          disabled={loading}
        />
        <button style={styles.button} onClick={sendMessage} disabled={loading}>
          ➤
        </button>
      </div>
    </div>
  );
}

const styles = {
  container: {
    display: "flex", flexDirection: "column", height: "100vh",
    backgroundColor: "#f7f7f8", color: "#1a1a2e",
    fontFamily: "'Georgia', 'Times New Roman', serif",
  },
  header: {
    backgroundColor: "#ffffff", padding: "20px 32px",
    display: "flex", alignItems: "center", justifyContent: "space-between",
    borderBottom: "2px solid #ececec", boxShadow: "0 2px 8px rgba(0,0,0,0.06)",
  },
  headerLeft: { display: "flex", alignItems: "center", gap: 16 },
  avatarImg: {
    width: 54, height: 54, borderRadius: "50%",
    objectFit: "cover",
    boxShadow: "0 2px 8px rgba(124,58,237,0.4)",
    border: "2px solid #7c3aed",
  },
  avatarImgSmall: {
    width: 40, height: 40, borderRadius: "50%",
    objectFit: "cover", flexShrink: 0,
    border: "2px solid #7c3aed",
  },
  agentName: { fontWeight: "bold", fontSize: 24, color: "#1a1a2e" },
  agentStatus: { fontSize: 16, color: "#22c55e", marginTop: 3 },
  nexsenBadge: {
    fontSize: 17, color: "#7c3aed", fontWeight: "bold",
    backgroundColor: "#f3f0ff", padding: "8px 18px", borderRadius: 20,
  },
  messagesContainer: {
    flex: 1, overflowY: "auto", padding: "36px 10%",
    display: "flex", flexDirection: "column",
  },
  userBubble: {
    backgroundColor: "#7c3aed", color: "#fff",
    padding: "16px 22px", borderRadius: "20px 20px 4px 20px",
    maxWidth: "65%", fontSize: 20, lineHeight: 1.8,
    fontFamily: "'Georgia', 'Times New Roman', serif",
    boxShadow: "0 2px 8px rgba(124,58,237,0.25)",
  },
  aichaBubble: {
    backgroundColor: "#ffffff", color: "#1a1a2e",
    padding: "16px 22px", borderRadius: "20px 20px 20px 4px",
    maxWidth: "65%", fontSize: 20, lineHeight: 1.8,
    fontFamily: "'Georgia', 'Times New Roman', serif",
    boxShadow: "0 2px 8px rgba(0,0,0,0.08)",
    border: "1px solid #ececec",
  },
  typingBubble: {
    backgroundColor: "#ffffff", padding: "16px 22px",
    borderRadius: "20px 20px 20px 4px",
    fontSize: 22, color: "#7c3aed",
    border: "1px solid #ececec",
    boxShadow: "0 2px 8px rgba(0,0,0,0.08)",
  },
  inputContainer: {
    padding: "20px 10%", backgroundColor: "#ffffff",
    display: "flex", gap: 14, borderTop: "2px solid #ececec",
    boxShadow: "0 -2px 8px rgba(0,0,0,0.04)",
  },
  input: {
    flex: 1, padding: "16px 24px", borderRadius: 32,
    border: "2px solid #ececec", backgroundColor: "#f7f7f8",
    color: "#1a1a2e", fontSize: 20, outline: "none",
    fontFamily: "'Georgia', 'Times New Roman', serif",
  },
  button: {
    width: 58, height: 58, borderRadius: "50%", border: "none",
    backgroundColor: "#7c3aed", color: "#fff",
    fontWeight: "bold", cursor: "pointer", fontSize: 22,
    boxShadow: "0 2px 8px rgba(124,58,237,0.4)",
  },
};

export default App;