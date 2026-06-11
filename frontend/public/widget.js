(function () {
  const AICHA_API = "http://127.0.0.1:8000";
  let isOpen = false;
  let conversationHistory = [];

  const styles = `
    #nexsen-widget-btn {
      position: fixed;
      bottom: 28px;
      right: 28px;
      width: 64px;
      height: 64px;
      border-radius: 50%;
      background: #7c3aed;
      border: none;
      cursor: pointer;
      box-shadow: 0 4px 16px rgba(124,58,237,0.5);
      z-index: 9999;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 28px;
      transition: transform 0.2s;
    }
    #nexsen-widget-btn:hover { transform: scale(1.1); }

    #nexsen-chat-box {
      position: fixed;
      bottom: 110px;
      right: 28px;
      width: 380px;
      height: 520px;
      background: #fff;
      border-radius: 20px;
      box-shadow: 0 8px 32px rgba(0,0,0,0.15);
      z-index: 9998;
      display: none;
      flex-direction: column;
      overflow: hidden;
      font-family: Georgia, serif;
    }

    #nexsen-chat-header {
      background: #7c3aed;
      padding: 16px 20px;
      display: flex;
      align-items: center;
      gap: 12px;
      color: #fff;
    }

    #nexsen-chat-header img {
      width: 42px;
      height: 42px;
      border-radius: 50%;
      object-fit: cover;
      border: 2px solid #fff;
    }

    #nexsen-agent-info .name { font-weight: bold; font-size: 17px; }
    #nexsen-agent-info .status { font-size: 13px; color: #c4b5fd; }

    #nexsen-messages {
      flex: 1;
      overflow-y: auto;
      padding: 16px;
      display: flex;
      flex-direction: column;
      gap: 12px;
      background: #f7f7f8;
    }

    .nexsen-msg-user {
      align-self: flex-end;
      background: #7c3aed;
      color: #fff;
      padding: 10px 16px;
      border-radius: 18px 18px 4px 18px;
      max-width: 80%;
      font-size: 15px;
      line-height: 1.6;
    }

    .nexsen-msg-aicha {
      align-self: flex-start;
      background: #fff;
      color: #1a1a2e;
      padding: 10px 16px;
      border-radius: 18px 18px 18px 4px;
      max-width: 80%;
      font-size: 15px;
      line-height: 1.6;
      box-shadow: 0 2px 6px rgba(0,0,0,0.08);
    }

    #nexsen-input-area {
      padding: 12px 16px;
      background: #fff;
      display: flex;
      gap: 10px;
      border-top: 1px solid #ececec;
    }

    #nexsen-input {
      flex: 1;
      padding: 10px 16px;
      border-radius: 24px;
      border: 2px solid #ececec;
      font-size: 15px;
      outline: none;
      font-family: Georgia, serif;
    }

    #nexsen-send-btn {
      width: 44px;
      height: 44px;
      border-radius: 50%;
      background: #7c3aed;
      border: none;
      color: #fff;
      font-size: 18px;
      cursor: pointer;
    }

    #nexsen-powered {
      text-align: center;
      font-size: 11px;
      color: #aaa;
      padding: 4px;
      background: #fff;
    }
  `;

  const styleEl = document.createElement("style");
  styleEl.innerHTML = styles;
  document.head.appendChild(styleEl);

  const btn = document.createElement("button");
  btn.id = "nexsen-widget-btn";
  btn.innerHTML = "💬";
  document.body.appendChild(btn);

  const chatBox = document.createElement("div");
  chatBox.id = "nexsen-chat-box";
  chatBox.innerHTML = `
    <div id="nexsen-chat-header">
      <img src="http://127.0.0.1:3000/aicha_profile.png" onerror="this.style.display='none'" />
      <div id="nexsen-agent-info">
        <div class="name">AICHA</div>
        <div class="status">● En ligne — NexSen AI</div>
      </div>
    </div>
    <div id="nexsen-messages">
      <div class="nexsen-msg-aicha">Bonjour ! Je suis AICHA. Comment puis-je vous aider ? 😊</div>
    </div>
    <div id="nexsen-input-area">
      <input id="nexsen-input" placeholder="Votre message..." />
      <button id="nexsen-send-btn">➤</button>
    </div>
    <div id="nexsen-powered">Powered by <strong>NexSen AI</strong> 🌍</div>
  `;
  document.body.appendChild(chatBox);

  btn.addEventListener("click", () => {
    isOpen = !isOpen;
    chatBox.style.display = isOpen ? "flex" : "none";
    btn.innerHTML = isOpen ? "✕" : "💬";
  });

  async function sendMessage() {
    const input = document.getElementById("nexsen-input");
    const msg = input.value.trim();
    if (!msg) return;

    addMessage(msg, "user");
    input.value = "";

    try {
      const res = await fetch(`${AICHA_API}/aicha/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: msg, history: conversationHistory }),
      });
      const data = await res.json();
      addMessage(data.response, "aicha");
      conversationHistory.push({ role: "user", content: msg });
      conversationHistory.push({ role: "assistant", content: data.response });
    } catch {
      addMessage("⚠️ Erreur de connexion.", "aicha");
    }
  }

  function addMessage(text, sender) {
    const messages = document.getElementById("nexsen-messages");
    const div = document.createElement("div");
    div.className = sender === "user" ? "nexsen-msg-user" : "nexsen-msg-aicha";
    div.textContent = text;
    messages.appendChild(div);
    messages.scrollTop = messages.scrollHeight;
  }

  document.getElementById("nexsen-send-btn").addEventListener("click", sendMessage);
  document.getElementById("nexsen-input").addEventListener("keypress", (e) => {
    if (e.key === "Enter") sendMessage();
  });
})();