import httpx
from typing import Dict

class SilhouetteClient:
    def __init__(self, base_url: str):
        self.base = base_url.rstrip("/")
        self.cx = httpx.AsyncClient(timeout=15)

    async def enqueue(self, payload: Dict) -> Dict:
        r = await self.cx.post(f"{self.base}/v1/silhouette/enqueue", json=payload)
        r.raise_for_status()
        return r.json()

    async def metrics(self, rng: str = "24h") -> Dict:
        r = await self.cx.get(f"{self.base}/v1/silhouette/metrics", params={"range": rng})
        r.raise_for_status()
        return r.json()

    async def events(self, since: int = 0, limit: int = 50) -> Dict:
        r = await self.cx.get(f"{self.base}/v1/silhouette/events/stream", params={"since": since, "limit": limit})
        r.raise_for_status()
        return r.json()

    async def aclose(self):
        await self.cx.aclose()
