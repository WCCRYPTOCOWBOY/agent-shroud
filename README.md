Agent Shroud

Vol. 2 of the S.M.A.K. (Social Media Agent Krew) series

Shroud is the brand-first, persona-driven chat + voice layer built on top of Agent Silhouette.
Where Silhouette handles the pit-lane scheduling, queues, and metrics, Shroud is the voice in the headset responding to users with personality, tone, and intent.

Together, they form the backbone of the Social Media Agent Krew (S.M.A.K.), a modular system for automated content scheduling, analytics, and engagement.

🚦 Core Features

FastAPI Webchat Endpoint → Accepts user text/voice and returns persona-driven replies.

Persona System → JSON-based tone/lexicon with presets (gritty pit crew slang, witty rider wisdom, etc.).

Silhouette Integration → Direct handoff to Silhouette’s queue/metrics API.

Natural Time Parsing → “Tonight,” “7:15pm,” etc. interpreted with timeparse.

Secure Handoff → Webhook secret validation ensures only trusted systems can pass events.

🏁 How it Fits (Vol. 1 → Vol. 2)

Agent Silhouette (Vol. 1) → The pit-lane operator. Handles posts, queues, metrics, scheduling.

Agent Shroud (Vol. 2) → The crew’s voice. Handles user interaction, intent parsing, persona style.

Together, they create a two-layered automation flow:
Interaction (Shroud) → Execution (Silhouette) → Analytics (back to Shroud/Silhouette).

shroud/
├─ app.py          # FastAPI app (chat + intent router + Silhouette client)
├─ config.py       # env & settings loader
├─ persona.json    # persona tone/lexicon
├─ clients/
│  └─ silhouette.py
├─ utils/
│  └─ timeparse.py
├─ requirements.txt
├─ .env.example
├─ requests.http   # sample REST calls
└─ README.md
