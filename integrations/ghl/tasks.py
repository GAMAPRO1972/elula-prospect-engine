from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Dict, Optional


class GHLTasks:
    def __init__(self, client=None):
        self.client = client

    def bind(self, client) -> "GHLTasks":
        return GHLTasks(client)

    def create_task(
        self,
        contact_id: str,
        title: str,
        body: str,
        assigned_to: Optional[str] = None,
        due_date: Optional[datetime] = None,
        completed: bool = False,
    ) -> Dict[str, Any]:
        if self.client is None:
            raise ValueError("GHLTasks client is not configured.")

        if not contact_id:
            raise ValueError("contact_id is required to create a GHL task.")

        if due_date is None:
            due_date = datetime.utcnow() + timedelta(days=1)

        payload: Dict[str, Any] = {
            "title": title,
            "body": body,
            "dueDate": due_date.isoformat(timespec="milliseconds") + "Z",
            "completed": completed,
        }

        if assigned_to:
            payload["assignedTo"] = assigned_to

        return self.client.post(f"contacts/{contact_id}/tasks", payload)

    def create_initial_call(
        self,
        contact_id: str,
        owner_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        return self.create_task(
            contact_id=contact_id,
            title="Initial Prospect Call",
            body="Call this prospect to qualify the opportunity and attempt to book a discovery appointment.",
            assigned_to=owner_id,
            due_date=datetime.utcnow() + timedelta(days=1),
            completed=False,
        )


tasks = GHLTasks()
