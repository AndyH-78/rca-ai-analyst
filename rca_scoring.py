import json
import requests
from typing import Any, Dict
from prompts import EVAL_PROMPT, CRITIC_PROMPT, IMPROVE_PROMPT


class OllamaClient:
    def __init__(self, model: str = "llama3.1:8b", host: str = "http://localhost:11434"):
        self.model = model
        self.host = host.rstrip("/")

    def generate_json(self, prompt: str, temperature: float = 0.2, timeout_s: int = 180) -> Dict[str, Any]:
        """
        Calls Ollama /api/generate and tries to parse JSON reliably.
        """
        url = f"{self.host}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": float(temperature)},
        }
        r = requests.post(url, json=payload, timeout=timeout_s)
        r.raise_for_status()
        text = (r.json().get("response") or "").strip()

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            start = text.find("{")
            end = text.rfind("}")
            if start != -1 and end != -1 and end > start:
                return json.loads(text[start : end + 1])
            raise


def evaluate_incident(client: OllamaClient, row: Dict[str, Any]) -> Dict[str, Any]:
    prompt = EVAL_PROMPT.format(
        incident_id=row.get("incident_id", ""),
        summary=row.get("summary", ""),
        description=row.get("description", ""),
        root_cause=row.get("root_cause", ""),
        resolution=row.get("resolution", ""),
        preventive_action=row.get("preventive_action", ""),
    )
    return client.generate_json(prompt)


def critic_review(client: OllamaClient, row: Dict[str, Any], evaluation: Dict[str, Any]) -> Dict[str, Any]:
    prompt = CRITIC_PROMPT.format(
        root_cause=row.get("root_cause", ""),
        resolution=row.get("resolution", ""),
        preventive_action=row.get("preventive_action", ""),
        evaluation_json=json.dumps(evaluation, ensure_ascii=False),
    )
    return client.generate_json(prompt)


def improve_rca(client: OllamaClient, row: Dict[str, Any]) -> Dict[str, Any]:
    prompt = IMPROVE_PROMPT.format(
        incident_id=row.get("incident_id", ""),
        summary=row.get("summary", ""),
        root_cause=row.get("root_cause", ""),
        resolution=row.get("resolution", ""),
        preventive_action=row.get("preventive_action", ""),
    )
    return client.generate_json(prompt)
