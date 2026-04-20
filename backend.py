import os
import httpx
import asyncio
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def read_index():
    return FileResponse('static/index.html')

# =================================================================
# 🔑 SMART DUAL-KEY SETUP (With Fallbacks to prevent crashes)
# =================================================================
GEMINI_KEY_1 = os.getenv("GEMINI_API_KEY_1") or os.getenv("GEMINI_API_KEY")
GEMINI_KEY_2 = os.getenv("GEMINI_API_KEY_2") or os.getenv("GEMINI_API_KEY")
GROQ_KEY = os.getenv("GROQ_API_KEY")

BASE_GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

# =================================================================
# ⚙️ SYSTEM PROMPTS
# =================================================================
ELDEST_SYS = "You are the Eldest Sibling. Answer intelligently but STRICTLY KEEP IT CONCISE (under 100 words). Be direct, wise, and authoritative. Do NOT mention your AI model name. No markdown. Be respectful to the user."
MIDDLE_SYS = "You are the Middle Sibling. Review your Eldest Sibling's answer. STRICTLY KEEP IT SHORT AND PUNCHY (under 80 words). Add practical value. Do NOT mention your AI model name. No markdown.  Be respectful to the user."
YOUNGEST_SYS = "You are the Youngest Sibling. You are sharp, witty, and offer out-of-the-box perspectives. Build on right answers or playfully point out flaws. Keep it under 80 words. Do NOT mention your model name. No markdown.  Be respectful to the user."
MEDIATOR_SYS = "You are the Mediator. Provide a concise, balanced final verdict resolving the siblings' discussion (under 100 words). Plain text."

# =================================================================
# 🔄 ROBUST API CALLERS
# =================================================================
async def call_gemini(prompt: str, model: str, api_key: str) -> str:
    if not api_key: return "Error: API Key is missing."
    url = f"{BASE_GEMINI_URL}/{model}:generateContent?key={api_key}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    
    last_error = "Unknown Error"
    for attempt in range(3):
        try:
            await asyncio.sleep(1.5) # Anti-Burst Delay 🛑
            async with httpx.AsyncClient(timeout=60.0) as client:
                resp = await client.post(url, json=payload)
                if resp.status_code == 200:
                    try:
                        return resp.json()["candidates"][0]["content"]["parts"][0]["text"]
                    except (KeyError, IndexError):
                        return "Error: Safety filters blocked this response."
                elif resp.status_code == 429:  
                    last_error = f"Error 429: Rate Limit. Retrying..."
                    await asyncio.sleep(2 ** attempt) 
                    continue
                elif resp.status_code == 503:
                    last_error = "Error 503: Server Busy. Retrying..."
                    await asyncio.sleep(2)
                    continue
                return f"Error {resp.status_code}: {resp.text}"
        except Exception as e:
            last_error = f"Connection Error: {str(e)}"
            await asyncio.sleep(1)
    return last_error 

async def call_groq(messages: list) -> str:
    if not GROQ_KEY: return "Error: Groq API Key is missing."
    headers = {"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"}
    payload = {"model": "llama-3.3-70b-versatile", "messages": messages}
    
    for attempt in range(3):
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                resp = await client.post(GROQ_URL, headers=headers, json=payload)
                if resp.status_code == 200:
                    return resp.json()["choices"][0]["message"]["content"]
                elif resp.status_code == 429:
                    await asyncio.sleep(2)
                    continue
                return f"Error {resp.status_code}: {resp.text}"
        except Exception as e:
            await asyncio.sleep(1)
    return "Error: Groq failed after retries."

# =================================================================
# 🚀 ENDPOINTS (Reverted to GET so your untouched index.html works perfectly!)
# =================================================================

@app.get("/ask/agent1")
async def ask_agent1(query: str):
    prompt = f"{ELDEST_SYS}\n\nQuestion: {query}"
    response = await call_gemini(prompt, "gemini-3-pro-preview", GEMINI_KEY_1)
    return {"response": response}

@app.get("/ask/agent2")
async def ask_agent2(query: str, agent1_response: str):
    prompt = f"{MIDDLE_SYS}\n\nQuestion: {query}\nEldest Sibling said: {agent1_response}"
    response = await call_gemini(prompt, "gemini-2.5-flash", GEMINI_KEY_2)
    return {"response": response}

@app.get("/ask/agent3")
async def ask_agent3(query: str, agent1_response: str, agent2_response: str):
    usr = f"Question: {query}\nEldest Sibling said: {agent1_response}\nMiddle Sibling said: {agent2_response}\n\nAdd your fresh perspective."
    response = await call_groq([{"role": "system", "content": YOUNGEST_SYS}, {"role": "user", "content": usr}])
    return {"response": response}

# =================================================================
# 🔄 DEBATE & SYNTHESIS
# =================================================================

class Exchange(BaseModel):
    user: str
    agent1: Optional[str] = ""
    agent2: Optional[str] = ""
    agent3: Optional[str] = ""

class DebateHistoryRequest(BaseModel):
    history: List[Exchange]

@app.post("/debate_with_history")
async def debate_with_history(req: DebateHistoryRequest):
    if not req.history: return {"error": "No history provided"}
    last = req.history[-1]
    new_user_message = last.user
    
    lines = []
    for exch in req.history[:-1]:
        lines.append(f"User: {exch.user}\nEldest: {exch.agent1}\nMiddle: {exch.agent2}\nYoungest: {exch.agent3}\n---")
    context = "\n".join(lines)

    p1 = f"History:\n{context}\n\nUser: {new_user_message}\nYou are the Eldest Sibling. Concise response (under 80 words). No markdown."
    # FIX: Correctly assigned to gemini-pro-latest
    r1 = await call_gemini(p1, "gemini-3-pro-preview", GEMINI_KEY_1)

    p2 = f"History:\n{context}\n\nUser: {new_user_message}\nEldest just said: {r1}\nYou are the Middle Sibling. Refine it practically (under 80 words). No markdown."
    # FIX: Correctly assigned to gemini-flash-latest
    r2 = await call_gemini(p2, "gemini-2.5-flash", GEMINI_KEY_2)

    usr3 = f"History:\n{context}\n\nUser: {new_user_message}\nEldest: {r1}\nMiddle: {r2}\nRespond."
    r3 = await call_groq([{"role": "system", "content": YOUNGEST_SYS}, {"role": "user", "content": usr3}])

    return {"refined_agent1": r1, "refined_agent2": r2, "refined_agent3": r3}

class SynthesisRequest(BaseModel):
    query: str; agent1: str; agent2: str; agent3: str

@app.post("/synthesize")
async def synthesize(req: SynthesisRequest):
    usr = f"Query: {req.query}\nEldest Sibling: {req.agent1}\nMiddle Sibling: {req.agent2}\nYoungest Sibling: {req.agent3}"
    response = await call_groq([{"role": "system", "content": MEDIATOR_SYS}, {"role": "user", "content": usr}])
    return {"synthesis": response}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)