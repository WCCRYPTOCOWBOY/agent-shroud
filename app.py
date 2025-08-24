from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import Dict, List
import json

from config import SIL_BASE, PERSONA_FILE
from clients.silhouette import SilhouetteClient
from utils.timeparse import parse_when

app = FastAPI(title="Shroud", version="0.1.0")
SIL = SilhouetteClient(SIL_BASE)

# ---- Models ----
class WebchatMessage(BaseModel):
    user_id: str
    text: str
    metadata: Dict = Field(default_factory=dict)

# ---- Persona loader ----
with open(PERSONA_FILE, "r", encoding="utf-8") as f:
    PERSONA = json.load(f)

# ---- Tiny persona renderer ----
def say(tag: str, fallback: str) -> str:
    choices: List[str] = PERSONA.get("lexicon", {}).get(tag, [])
    return choices[0] if choices else fallback

# ---- NLU (rule-based MVP) ----
def nlu(text: str) -> Dict:
    low = text.lower()
    if any(k in low for k in ["metrics", "stats", "ctr", "views"]):
        return {"intent": "METRICS", "slots": {"range": "24h"}}
    if any(k in low for k in ["schedule", "post", "line up", "queue this", "publish"]):
        return {"intent": "SCHEDULE_POST", "slots": {"when": parse_when(low), "channel": "tiktok"}}
    if any(k in low for k in ["queue", "what's lined up", "whats lined up", "tonight"]):
        return {"intent": "LIST_QUEUE", "slots": {"window": "tonight"}}
    if any(k in low for k in ["refund", "defective", "broken", "angry"]):
        return {"intent": "HANDOFF_REQUEST", "slots": {"reason": "support_issue"}}
    return {"intent": "UNKNOWN", "slots": {}}

# ---- Routes ----
@app.get("/health")
async def health():
    return {"ok": True, "silhouette": SIL_BASE}

@app.post("/integrations/webchat")
async def webchat(msg: WebchatMessage):
    intent = nlu(msg.text)
    name = intent["intent"]
    slots = intent["slots"]

    if name == "METRICS":
        data = await SIL.metrics(slots.get("range", "24h"))
        total = data.get("total", {})
        reply = f"{say('metrics','Metrics')} — {total.get('published',0)} clean laps, {total.get('failed',0)} bum laps in the last {slots.get('range','24h')}"
        return {"reply": reply, "intent": intent}

    if name == "SCHEDULE_POST":
        when = slots.get("when")
        if not when:
            return {"reply": "Clock me a time (e.g., 7:15pm) and I’ll line it up.", "intent": intent}
        payload = {
            "channel": slots.get("channel", "tiktok"),
            "when": when.isoformat(),
            "body": {"text": msg.text, "media_ids": [], "tags": ["webchat"]},
            "options": {"dry_run": True, "priority": 5, "idempotency_key": f"{msg.user_id}|{when.isoformat()}"}
        }
        res = await SIL.enqueue(payload)
        job_short = res["job_id"][:4].upper()
        reply = f"{say('queued','Queued')} — {when.isoformat()} on {payload['channel']}. Job #{job_short}."
        return {"reply": reply, "job_id": res["job_id"], "intent": intent}

    if name == "LIST_QUEUE":
        ev = await SIL.events(0, 50)
        count = sum(1 for e in ev.get("events", []) if e.get("type") == "post.published")
        reply = f"Track’s hot — {count} clean laps logged in the stream. (Detailed queue endpoint TBD)"
        return {"reply": reply, "intent": intent}

    if name == "HANDOFF_REQUEST":
        return {"reply": "That’s a rough spill. I’ll pull this into the pit — drop a number and I’ll line up a crew call.", "needs_contact": True, "intent": intent}

    return {"reply": "Copy — do you want metrics, schedule a post, or check the queue?", "intent": intent}

@app.on_event("shutdown")
async def shutdown():
    await SIL.aclose()
