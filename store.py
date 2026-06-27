"""
store.py — File-based matter store (JSON).
Every matter that flows through the system lives here.
In production this would be Firestore/Postgres — for the hackathon a JSON file is enough.
"""

import json
import uuid
import os
from datetime import datetime, timezone

STORE_PATH = os.path.join(os.path.dirname(__file__), "matters.json")

# ---------------------------------------------------------------------------
# Team definition — who works at this firm
# ---------------------------------------------------------------------------
TEAM = {
    "partners": [
        {"id": "partner_1", "name": "Sarah Chen",    "speciality": "Corporate & Commercial"},
        {"id": "partner_2", "name": "David Okafor",  "speciality": "Finance & Banking"},
    ],
    "seniors": [
        {"id": "senior_1", "name": "James Wright",   "speciality": "Commercial Contracts"},
        {"id": "senior_2", "name": "Meera Nair",     "speciality": "Employment & IP"},
    ],
    "juniors": [
        {"id": "junior_1", "name": "Priya Patel",    "speciality": "Contract Review",     "workload": 0},
        {"id": "junior_2", "name": "Tom Davies",     "speciality": "Legal Research",       "workload": 0},
        {"id": "junior_3", "name": "Aisha Mensah",   "speciality": "Corporate Drafting",  "workload": 0},
    ],
}

# Matter status flow:
# submitted → assigned → draft_submitted → ai_reviewing →
#   → approved (→ completed) | flagged → senior_reviewing →
#       → accepted (→ completed) | rejected (→ draft_submitted)

STATUSES = {
    "submitted":        "📨 Submitted by Partner",
    "assigned":         "👤 Assigned to Junior",
    "draft_submitted":  "📝 Draft Submitted",
    "ai_reviewing":     "🤖 AI Reviewing",
    "flagged":          "🚩 Flagged to Senior",
    "senior_reviewing": "👁️ Senior Reviewing",
    "accepted":         "✅ Accepted",
    "rejected":         "↩️ Rejected — Returned to Junior",
    "completed":        "✅ Completed",
}


# ---------------------------------------------------------------------------
# Store helpers
# ---------------------------------------------------------------------------
def _load() -> dict:
    if not os.path.exists(STORE_PATH):
        return {"matters": {}}
    with open(STORE_PATH, "r") as f:
        return json.load(f)


def _save(data: dict):
    with open(STORE_PATH, "w") as f:
        json.dump(data, f, indent=2)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


# ---------------------------------------------------------------------------
# Matter CRUD
# ---------------------------------------------------------------------------
def create_matter(
    client: str,
    instructions: str,
    partner_id: str,
    matter_type: str = "Commercial Contract Review",
) -> dict:
    matter_id = str(uuid.uuid4())[:8].upper()
    matter = {
        "id":           matter_id,
        "client":       client,
        "instructions": instructions,
        "matter_type":  matter_type,
        "partner_id":   partner_id,
        "status":       "submitted",
        "assigned_to":  None,       # junior id
        "senior_id":    None,       # senior assigned for review
        "draft":        None,       # junior's submitted draft
        "ai_review":    None,       # supervisor output
        "senior_notes": None,
        "document_url": f"/matters/{matter_id}/document",
        "created_at":   _now(),
        "updated_at":   _now(),
        "actions": [
            {
                "timestamp":  _now(),
                "actor":      partner_id,
                "actor_type": "human",
                "role":       "partner",
                "action":     "submitted",
                "detail":     f"Matter submitted by partner. Client: {client}",
            }
        ],
    }
    data = _load()
    data["matters"][matter_id] = matter
    _save(data)
    return matter


def get_matter(matter_id: str) -> dict | None:
    return _load()["matters"].get(matter_id)


def get_all_matters() -> list[dict]:
    return list(_load()["matters"].values())


def update_matter(matter_id: str, **fields) -> dict:
    data = _load()
    if matter_id not in data["matters"]:
        raise KeyError(f"Matter {matter_id} not found")
    data["matters"][matter_id].update(fields)
    data["matters"][matter_id]["updated_at"] = _now()
    _save(data)
    return data["matters"][matter_id]


def add_action(
    matter_id: str,
    actor: str,
    actor_type: str,   # "human" | "ai"
    role: str,         # "partner" | "junior" | "senior" | "supervisor_ai" | "router_ai"
    action: str,
    detail: str,
) -> dict:
    data = _load()
    matter = data["matters"][matter_id]
    entry = {
        "timestamp":  _now(),
        "actor":      actor,
        "actor_type": actor_type,
        "role":       role,
        "action":     action,
        "detail":     detail,
    }
    matter["actions"].append(entry)
    matter["updated_at"] = _now()
    _save(data)
    return entry


# ---------------------------------------------------------------------------
# Workload helpers (for AI Router)
# ---------------------------------------------------------------------------
def get_junior_workload() -> dict:
    """Returns {junior_id: active_matter_count}."""
    matters = get_all_matters()
    workload = {j["id"]: 0 for j in TEAM["juniors"]}
    for m in matters:
        if m.get("assigned_to") and m["status"] not in ("completed", "accepted"):
            jid = m["assigned_to"]
            if jid in workload:
                workload[jid] += 1
    return workload


def get_team_summary() -> str:
    """Human-readable team summary for the AI Router."""
    workload = get_junior_workload()
    lines = ["Current team workload:"]
    for j in TEAM["juniors"]:
        count = workload.get(j["id"], 0)
        lines.append(f"  - {j['name']} ({j['speciality']}): {count} active matter(s)")
    lines.append("\nSenior lawyers available for review:")
    for s in TEAM["seniors"]:
        lines.append(f"  - {s['name']} ({s['speciality']})")
    return "\n".join(lines)
