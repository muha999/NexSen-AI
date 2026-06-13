import React, { useState, useEffect } from "react";
import muhaImg from "./assets/Muha.jpeg";
import aichaImg from "./assets/Aicha.jpeg";
import fabiImg from "./assets/Fabi.jpeg";
import zaraImg from "./assets/Zara.jpeg";
import dijaImg from "./assets/Dija.jpeg";
import ibrahimaImg from "./assets/Ibrahima.jpeg";

const API_URL = "http://127.0.0.1:8000";

const AGENTS = [
  { name: "AICHA", role: "Service Client", img: aichaImg },
  { name: "FABI", role: "Data Analyst", img: fabiImg },
  { name: "ZARA", role: "Commercial", img: zaraImg },
  { name: "DIJA", role: "Recrutement", img: dijaImg },
  { name: "IBRAHIMA", role: "Évaluateur", img: ibrahimaImg },
];

function Dashboard() {
  const [apiStatus, setApiStatus] = useState(null);
  const [stats, setStats] = useState({ totalMessages: 0, scoreMoyen: 0 });
  const [conversations, setConversations] = useState([]);
  const [activeTab, setActiveTab] = useState("agents");
  const [testMessage, setTestMessage] = useState("");
  const [testLoading, setTestLoading] = useState(false);

  useEffect(() => {
    checkApiStatus();
    const interval = setInterval(checkApiStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  const checkApiStatus = async () => {
    try {
      const res = await fetch(`${API_URL}/health`);
      const data = await res.json();
      setApiStatus(data);
    } catch {
      setApiStatus(null);
    }
  };

  const addConversation = (agent, message, response, score) => {
    const newConv = { id: Date.now(), agent, message, response, score, time: new Date().toLocaleTimeString() };
    setConversations(prev => [newConv, ...prev].slice(0, 20));
    setStats(prev => ({ ...prev, totalMessages: prev.totalMessages + 1, scoreMoyen: score }));
  };

  const testAgent = async () => {
    if (!testMessage.trim()) return;
    setTestLoading(true);
    try {
      const res = await fetch(`${API_URL}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: testMessage, history: [] })
      });
      const data = await res.json();
      addConversation(data.agent, testMessage, data.response, data.evaluation?.score || 0);
      setTestMessage("");
    } catch (e) {
      console.error(e);
    } finally {
      setTestLoading(false);
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <div style={styles.headerLeft}>
          <span style={styles.logo}>🌍</span>
          <div>
            <div style={styles.title}>NexSen AI</div>
            <div style={styles.subtitle}>Dashboard Admin</div>
          </div>
        </div>
        <div style={apiStatus ? styles.statusOnline : styles.statusOffline}>
          {apiStatus ? "● Système en ligne" : "● Système hors ligne"}
        </div>
      </div>

      <div style={styles.statsRow}>
        <div style={styles.statCard}>
          <div style={styles.statNumber}>{stats.totalMessages}</div>
          <div style={styles.statLabel}>Messages traités</div>
        </div>
        <div style={styles.statCard}>
          <div style={styles.statNumber}>6</div>
          <div style={styles.statLabel}>Agents actifs</div>
        </div>
        <div style={styles.statCard}>
          <div style={styles.statNumber}>{stats.scoreMoyen}/10</div>
          <div style={styles.statLabel}>Dernier score IBRAHIMA</div>
        </div>
        <div style={styles.statCard}>
          <div style={styles.statNumber}>{conversations.length}</div>
          <div style={styles.statLabel}>Conversations</div>
        </div>
      </div>

      <div style={styles.tabs}>
        {["agents", "conversations", "test"].map(tab => (
          <button
            key={tab}
            style={activeTab === tab ? styles.tabActive : styles.tab}
            onClick={() => setActiveTab(tab)}
          >
            {tab === "agents" ? "👥 Équipe" : tab === "conversations" ? "💬 Historique" : "🧪 Tester"}
          </button>
        ))}
      </div>

      {activeTab === "agents" && (
        <div>
          <div style={styles.muhaCard}>
            <img src={muhaImg} alt="MUHA" style={styles.muhaImg} />
            <div style={styles.muhaName}>MUHA</div>
            <div style={styles.muhaRole}>Orchestrateur — Chef d'équipe</div>
            <div style={styles.agentOnline}>● En ligne</div>
          </div>

          <div style={styles.agentsGrid}>
            {AGENTS.map(agent => (
              <div key={agent.name} style={styles.agentCard}>
                <img src={agent.img} alt={agent.name} style={styles.agentImg} />
                <div style={styles.agentName}>{agent.name}</div>
                <div style={styles.agentRole}>{agent.role}</div>
                <div style={styles.agentOnline}>● En ligne</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {activeTab === "conversations" && (
        <div style={styles.convList}>
          {conversations.length === 0 ? (
            <div style={styles.empty}>Aucune conversation — testez les agents ! 🤖</div>
          ) : (
            conversations.map(conv => (
              <div key={conv.id} style={styles.convCard}>
                <div style={styles.convHeader}>
                  <span style={styles.convAgent}>{conv.agent}</span>
                  <span style={styles.convScore}>Score : {conv.score}/10</span>
                  <span style={styles.convTime}>{conv.time}</span>
                </div>
                <div style={styles.convMessage}>👤 {conv.message}</div>
                <div style={styles.convResponse}>🤖 {conv.response.slice(0, 150)}...</div>
              </div>
            ))
          )}
        </div>
      )}

      {activeTab === "test" && (
        <div style={styles.testSection}>
          <div style={styles.testTitle}>🧪 Tester les agents en direct</div>
          <div style={styles.testInput}>
            <input
              style={styles.input}
              value={testMessage}
              onChange={e => setTestMessage(e.target.value)}
              onKeyPress={e => e.key === "Enter" && testAgent()}
              placeholder="Ex: Je cherche un développeur Python..."
              disabled={testLoading}
            />
            <button style={styles.button} onClick={testAgent} disabled={testLoading}>
              {testLoading ? "..." : "Envoyer"}
            </button>
          </div>
          <div style={styles.testHints}>
            <div style={styles.hint} onClick={() => setTestMessage("J'ai un problème avec ma commande")}>🤖 AICHA</div>
            <div style={styles.hint} onClick={() => setTestMessage("Analyse les ventes du mois")}>📊 FABI</div>
            <div style={styles.hint} onClick={() => setTestMessage("J'aimerais une offre commerciale")}>💼 ZARA</div>
            <div style={styles.hint} onClick={() => setTestMessage("Je cherche un développeur senior")}>👥 DIJA</div>
          </div>
        </div>
      )}
    </div>
  );
}

const styles = {
  container: { minHeight: "100vh", backgroundColor: "#0a0a0f", fontFamily: "Georgia, serif", paddingBottom: 40 },
  header: { backgroundColor: "#13131f", padding: "20px 32px", display: "flex", alignItems: "center", justifyContent: "space-between", borderBottom: "1px solid #2a2a40" },
  headerLeft: { display: "flex", alignItems: "center", gap: 16 },
  logo: { fontSize: 36 },
  title: { fontSize: 24, fontWeight: "bold", color: "#f4f1fe" },
  subtitle: { fontSize: 14, color: "#9a94c2" },
  statusOnline: { fontSize: 15, color: "#5dcaa5", fontWeight: "bold" },
  statusOffline: { fontSize: 15, color: "#e24b4a", fontWeight: "bold" },
  statsRow: { display: "flex", gap: 20, padding: "24px 32px" },
  statCard: { flex: 1, backgroundColor: "#13131f", borderRadius: 16, padding: "20px 24px", textAlign: "center", border: "1px solid #2a2a40" },
  statNumber: { fontSize: 32, fontWeight: "bold", color: "#b9a6f7" },
  statLabel: { fontSize: 14, color: "#9a94c2", marginTop: 4 },
  tabs: { display: "flex", gap: 12, padding: "0 32px 24px" },
  tab: { padding: "10px 24px", borderRadius: 24, border: "1px solid #2a2a40", backgroundColor: "#13131f", cursor: "pointer", fontSize: 16, color: "#9a94c2" },
  tabActive: { padding: "10px 24px", borderRadius: 24, border: "1px solid #7c3aed", backgroundColor: "#7c3aed", cursor: "pointer", fontSize: 16, color: "#fff", fontWeight: "bold" },
  muhaCard: { backgroundColor: "#13131f", borderRadius: 24, padding: "32px", textAlign: "center", border: "1px solid #7c3aed", margin: "0 32px 24px", boxShadow: "0 0 40px rgba(124,58,237,0.15)" },
  muhaImg: { width: 160, height: 160, borderRadius: "50%", objectFit: "cover", marginBottom: 16, border: "2px solid #7c3aed" },
  muhaName: { fontSize: 26, fontWeight: "bold", color: "#f4f1fe" },
  muhaRole: { fontSize: 16, color: "#b9a6f7", marginTop: 4, marginBottom: 8 },
  agentsGrid: { display: "grid", gridTemplateColumns: "repeat(5, 1fr)", gap: 20, padding: "0 32px" },
  agentCard: { backgroundColor: "#13131f", borderRadius: 16, padding: 20, textAlign: "center", border: "1px solid #2a2a40" },
  agentImg: { width: 110, height: 110, borderRadius: "50%", objectFit: "cover", marginBottom: 10, border: "1px solid #2a2a40" },
  agentName: { fontSize: 17, fontWeight: "bold", color: "#f4f1fe" },
  agentRole: { fontSize: 13, color: "#9a94c2", marginTop: 2 },
  agentOnline: { fontSize: 12, color: "#5dcaa5", marginTop: 6, fontWeight: "bold" },
  convList: { padding: "0 32px", display: "flex", flexDirection: "column", gap: 16 },
  empty: { textAlign: "center", color: "#9a94c2", fontSize: 18, padding: 40 },
  convCard: { backgroundColor: "#13131f", borderRadius: 16, padding: 20, border: "1px solid #2a2a40" },
  convHeader: { display: "flex", gap: 12, alignItems: "center", marginBottom: 10 },
  convAgent: { backgroundColor: "#7c3aed", color: "#fff", padding: "4px 12px", borderRadius: 20, fontSize: 14, fontWeight: "bold" },
  convScore: { backgroundColor: "#0d2a20", color: "#5dcaa5", padding: "4px 12px", borderRadius: 20, fontSize: 14, fontWeight: "bold" },
  convTime: { color: "#9a94c2", fontSize: 13, marginLeft: "auto" },
  convMessage: { fontSize: 16, color: "#f4f1fe", marginBottom: 8 },
  convResponse: { fontSize: 15, color: "#9a94c2", fontStyle: "italic" },
  testSection: { padding: "0 32px" },
  testTitle: { fontSize: 22, fontWeight: "bold", color: "#f4f1fe", marginBottom: 20 },
  testInput: { display: "flex", gap: 12, marginBottom: 20 },
  input: { flex: 1, padding: "14px 20px", borderRadius: 28, border: "1px solid #2a2a40", fontSize: 18, outline: "none", fontFamily: "Georgia, serif", backgroundColor: "#13131f", color: "#f4f1fe" },
  button: { padding: "14px 28px", borderRadius: 28, border: "none", backgroundColor: "#7c3aed", color: "#fff", fontSize: 18, fontWeight: "bold", cursor: "pointer" },
  testHints: { display: "flex", gap: 12, flexWrap: "wrap" },
  hint: { padding: "10px 20px", borderRadius: 24, border: "1px solid #2a2a40", backgroundColor: "#13131f", cursor: "pointer", fontSize: 15, color: "#9a94c2" },
};

export default Dashboard;