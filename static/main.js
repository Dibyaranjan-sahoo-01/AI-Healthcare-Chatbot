/* =========================
   HEALTHCARE CHATBOT SCRIPT
   ========================= */

const sendSound = new Audio("/static/sounds/send.wav");
const receiveSound = new Audio("/static/sounds/receive.wav");

sendSound.volume = 0.6;
receiveSound.volume = 0.6;

let audioUnlocked = false;

const UI_TEXT = {
    en: {
        placeholder: "Type your message here...",
        typing: "Bot is typing",
        listen: "Listen",
        noMatch: "No matching conditions found. Please describe your symptoms in more detail.",
        diagnosisIntro: "Based on your symptoms, here are the most likely conditions:",
        diagnosisMatchSuffix: "symptoms match",
        diagnosisNote: "This is not a medical diagnosis. Please consult a healthcare professional for proper evaluation.",
        fallback: "Sorry, I didn't understand.",
        fetchError: "Unable to get response. Please try again.",
        ttsIntro: "Based on your symptoms, the most likely conditions are:",
        ttsRemember: "Remember, this is not a medical diagnosis. Please consult a healthcare professional.",
    },
    or: {
        placeholder: "ଏଠାରେ ଆପଣଙ୍କ ସନ୍ଦେଶ ଲେଖନ୍ତୁ...",
        typing: "ବଟ୍ ଉତ୍ତର ଲେଖୁଛି",
        listen: "ଶୁଣନ୍ତୁ",
        noMatch: "ମେଳ ଥିବା ରୋଗ ମିଳିଲା ନାହିଁ। ଦୟାକରି ଅଧିକ ସ୍ପଷ୍ଟ ଭାବେ ଲକ୍ଷଣ ଲେଖନ୍ତୁ।",
        diagnosisIntro: "ଆପଣଙ୍କ ଲକ୍ଷଣ ଅନୁସାରେ ସମ୍ଭାବ୍ୟ ରୋଗଗୁଡ଼ିକ:",
        diagnosisMatchSuffix: "ଲକ୍ଷଣ ମେଳିଛି",
        diagnosisNote: "ଏହା ଡାକ୍ତରୀ ନିଦାନ ନୁହେଁ। ଠିକ୍ ମୂଲ୍ୟାଙ୍କନ ପାଇଁ ଡାକ୍ତରଙ୍କୁ ଦେଖାନ୍ତୁ।",
        fallback: "ଦୁଃଖିତ, ମୁଁ ବୁଝିପାରିଲି ନାହିଁ।",
        fetchError: "ଉତ୍ତର ମିଳିଲା ନାହିଁ। ଦୟାକରି ପୁଣି ଚେଷ୍ଟା କରନ୍ତୁ।",
        ttsIntro: "ଆପଣଙ୍କ ଲକ୍ଷଣ ଅନୁସାରେ ସମ୍ଭାବ୍ୟ ରୋଗଗୁଡ଼ିକ ହେଲା:",
        ttsRemember: "ମନେ ରଖନ୍ତୁ, ଏହା ଡାକ୍ତରୀ ନିଦାନ ନୁହେଁ। ଦୟାକରି ଡାକ୍ତରଙ୍କ ପରାମର୍ଶ ନିଅନ୍ତୁ।",
    },
};

function getSelectedLanguage() {
    const select = document.getElementById("language-select");
    const fromSelect = select ? select.value : localStorage.getItem("chatLanguage");
    return fromSelect === "or" ? "or" : "en";
}

function t(key, lang) {
    return UI_TEXT[lang]?.[key] || UI_TEXT.en[key] || "";
}

function initializeDarkMode() {
    const isDarkMode = localStorage.getItem("darkMode") === "true";
    if (isDarkMode) {
        document.body.classList.add("dark");
    }
}

function initializeLanguage() {
    const languageSelect = document.getElementById("language-select");
    const input = document.getElementById("user-input");
    if (!input) return;

    const savedLang = localStorage.getItem("chatLanguage");
    if (languageSelect && (savedLang === "en" || savedLang === "or")) {
        languageSelect.value = savedLang;
    }

    const activeLang = getSelectedLanguage();
    input.placeholder = t("placeholder", activeLang);

    if (languageSelect) {
        languageSelect.addEventListener("change", () => {
            const lang = getSelectedLanguage();
            localStorage.setItem("chatLanguage", lang);
            input.placeholder = t("placeholder", lang);
        });
    }
}

document.addEventListener("DOMContentLoaded", () => {
    initializeDarkMode();
    initializeLanguage();

    const input = document.getElementById("user-input");
    if (!input) return;

    input.addEventListener("keydown", (event) => {
        if (event.key === "Enter") {
            event.preventDefault();
            sendMessage();
        }
    });
});

function sendMessage() {
    sendChatRequest("/chat");
}

function sendDiagnosis() {
    sendChatRequest("/diagnose");
}

function renderDiagnoses(diagnoses, lang = "en") {
    if (!diagnoses || diagnoses.length === 0) {
        return `<p>${t("noMatch", lang)}</p>`;
    }

    let html = `<p>${t("diagnosisIntro", lang)}</p><div class='diagnoses-list'>`;

    diagnoses.forEach((d) => {
        const percentage = Math.round(d.match_ratio * 100);
        html += `
            <div class="diagnosis-card">
                <h4>${d.disease}</h4>
                <div class="match-info">
                    <div class="match-bar">
                        <div class="match-fill" style="width: ${percentage}%"></div>
                    </div>
                    <span class="match-text">${d.match_count}/${d.total_symptoms} ${t("diagnosisMatchSuffix", lang)} (${percentage}%)</span>
                </div>
            </div>
        `;
    });

    html += `</div><p class='diagnosis-note'>${t("diagnosisNote", lang)}</p>`;
    return html;
}

function sendChatRequest(url) {
    const input = document.getElementById("user-input");
    const chatBox = document.getElementById("chat-box");

    if (!input || !chatBox) return;

    const message = input.value.trim();
    if (message === "") return;

    const lang = getSelectedLanguage();

    if (!audioUnlocked) {
        sendSound
            .play()
            .then(() => {
                sendSound.pause();
                sendSound.currentTime = 0;
                audioUnlocked = true;
            })
            .catch(() => {});
    }

    sendSound.currentTime = 0;
    sendSound.play().catch(() => {});

    const userDiv = document.createElement("div");
    userDiv.className = "user-message";
    userDiv.innerText = message;
    chatBox.appendChild(userDiv);

    input.value = "";

    const typingDiv = document.createElement("div");
    typingDiv.className = "typing";
    typingDiv.innerHTML = `${t("typing", lang)} <span></span><span></span><span></span>`;
    chatBox.appendChild(typingDiv);

    chatBox.scrollTop = chatBox.scrollHeight;

    fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message, lang }),
    })
        .then((res) => {
            if (!res.ok) {
                return res.json().then((errData) => {
                    throw errData;
                });
            }
            return res.json();
        })
        .then((data) => {
            if (chatBox.contains(typingDiv)) {
                chatBox.removeChild(typingDiv);
            }

            receiveSound.currentTime = 0;
            receiveSound.play().catch(() => {});

            const botDiv = document.createElement("div");
            botDiv.className = "bot-message";

            const botText = document.createElement("div");
            botText.className = "bot-text";

            const responseLang = data.lang === "or" ? "or" : lang;

            if (data.reply) {
                botText.innerText = data.reply;
            } else if (data.diagnoses) {
                botText.innerHTML = renderDiagnoses(data.diagnoses, responseLang);
            } else {
                botText.innerText = t("fallback", responseLang);
            }

            const voiceBtn = document.createElement("button");
            voiceBtn.className = "voice-btn";
            voiceBtn.innerText = t("listen", responseLang);
            voiceBtn.onclick = () => speakDiagnosis(data, responseLang);

            botDiv.appendChild(botText);
            botDiv.appendChild(voiceBtn);
            chatBox.appendChild(botDiv);

            chatBox.scrollTop = chatBox.scrollHeight;
        })
        .catch((err) => {
            console.error("Chat error:", err);
            if (chatBox.contains(typingDiv)) {
                chatBox.removeChild(typingDiv);
            }

            const botDiv = document.createElement("div");
            botDiv.className = "bot-message";
            const botText = document.createElement("div");
            botText.className = "bot-text";
            botText.innerText = err.message || err.reply || t("fetchError", lang);
            botDiv.appendChild(botText);
            chatBox.appendChild(botDiv);
            chatBox.scrollTop = chatBox.scrollHeight;
        });
}

function speakText(text, lang = "en") {
    if (!text) return;

    window.speechSynthesis.cancel();

    const speech = new SpeechSynthesisUtterance(text);
    speech.lang = lang === "or" ? "or-IN" : "en-IN";
    speech.rate = 0.9;
    speech.pitch = 1;

    window.speechSynthesis.speak(speech);
}

function speakDiagnosis(data, lang = "en") {
    let text = "";
    if (data.reply) {
        text = data.reply;
    } else if (data.diagnoses) {
        text = `${t("ttsIntro", lang)} `;
        data.diagnoses.forEach((d) => {
            const percentage = Math.round(d.match_ratio * 100);
            text += `${d.disease}, ${d.match_count}/${d.total_symptoms} ${t("diagnosisMatchSuffix", lang)}, ${percentage} percent. `;
        });
        text += t("ttsRemember", lang);
    }
    speakText(text, lang);
}

function toggleDarkMode() {
    document.body.classList.toggle("dark");
    const isDarkMode = document.body.classList.contains("dark");
    localStorage.setItem("darkMode", isDarkMode);
}
