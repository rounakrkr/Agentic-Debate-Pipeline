# ⚔️ Multi-AI War Room
**Advanced Reasoning & Orchestration Engine**

Ek sequential, multi-agent AI pipeline jo LLM bias aur "Echo Chambers" ko khatam karne ke liye banayi gayi hai. Isme AIs aapas mein Socratic debate karte hain takki user ko sabse refined output mile.

---

## 🎧 The Origin Story (Analysis Paralysis)
Ye project tab shuru hua jab mujhe ek pair **IEMs (In-Ear Monitors)** kharidne the. Maine alag-alag AI models se pucha aur result ye raha:
- Ek ne "Neutral sound signature" suggest kiya.
- Dusre ne "Bass-heavy V-shape" recommend kiya.
- Teesre ne kaha ki budget double kar lo.

Mujhe answer milne ki jagah **Analysis Paralysis** ho gaya. Tab maine realize kiya ki problem information ki kami nahi, balki **Critical Debate** ki kami hai. Isliye maine ye War Room banaya takki AIs mere samne behas karein aur mujhe best decision lene mein help karein.

---

## 🧠 How it Works (The Sibling Socratic Method)
Ye system sirf API calls nahi karta, balki teen alag personas ke beech ek stateful debate orchestrate karta hai:

1. **Agent 1 (The Intellectual):** Powered by **Gemini 3 Pro Preview**. Iska focus deep reasoning, technical specs, aur first-principles logic par hota hai.
2. **Agent 2 (The Pragmatist):** Powered by **Gemini 2.5 Flash**. Ye Intellectual ke response ko filter karta hai aur dekhta hai ki "Real-world constraints" aur budget ke hisaab se kya sahi hai.
3. **Agent 3 (The Adversarial Critic):** Powered by **Llama 3 (via Groq)**. Ye ek "Red Team" ki tarah kaam karta hai jo edge cases dhundta hai aur apne siblings ki logic ko challenge karta hai.
4. **The Mediator:** Poori debate ko summarize karke ek bulletproof, actionable strategy deta hai.

---

## 🖼️ Debate in Action
<img width="1920" height="1200" alt="Screenshot 2026-04-20 132324" src="https://github.com/user-attachments/assets/a2c0c9aa-5919-4811-8ac5-65baf67d1c6a" />

<img width="1920" height="1200" alt="Screenshot 2026-04-20 132416" src="https://github.com/user-attachments/assets/a70cff0f-b4ee-40aa-be0c-f50536cfcfc8" />

---

## 🛠️ The Engineering Flex
- **Dual-Key Load Balancing:** Custom routing logic jo multiple API accounts ke beech traffic divide karti hai takki rate limits (429 errors) bypass ho sakein. 🔑🔑
- **Sequential State Management:** Ek stateful loop jahan har agent pichle agent ki baat "sunta" hai aur uske upar apni layer add karta hai. 🔄
- **Model-Agnostic Architecture:** Isse hum kisi bhi model (GPT-4o, Claude, etc.) ko as a plug-and-play component use kar sakte hain. 🔌
- **Clean Separation of Concerns:** Frontend (HTML/CSS/JS) aur Backend (FastAPI) ko modularly differentiate kiya gaya hai for high maintainability.

---

## 💻 Tech Stack
- **Backend:** Python, FastAPI, Uvicorn, HTTPX
- **AI Models:** Gemini 3 Pro Preview, Gemini 2.5 Flash, Llama 3.3 (Groq)
- **Frontend:** HTML5, CSS3 (Glassmorphism), Vanilla JavaScript
