import os
import json
import time
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from contextlib import contextmanager


class BenchmarkTracker:
    """Captures and logs execution metrics, agent routing history, and task durations."""

    def __init__(self, output_file: str = "benchmarks.json"):
        self.output_file = output_file
        self.start_wall_time = time.time()
        self.tasks: List[Dict[str, Any]] = []
        self.routing_history: List[Dict[str, Any]] = []
        self.total_duration_seconds: float = 0.0
        self.workflow_metadata: Dict[str, Any] = {
            "orchestrator": "CrewAI Hierarchical Process",
            "manager_role": "Hierarchical Supervisor",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

    @contextmanager
    def track(self, task_name: str, agent_role: str, description: Optional[str] = None):
        """Context manager to measure task execution time and trace task routing."""
        t_start = time.time()
        start_iso = datetime.now(timezone.utc).isoformat()
        
        # Log routing transition
        route_step = {
            "step": len(self.routing_history) + 1,
            "routed_by": "Manager LLM",
            "assigned_agent": agent_role,
            "task_name": task_name,
            "timestamp": start_iso,
        }
        self.routing_history.append(route_step)

        task_record: Dict[str, Any] = {
            "task_name": task_name,
            "agent_role": agent_role,
            "description": description or task_name,
            "start_time": start_iso,
            "end_time": None,
            "duration_seconds": 0.0,
            "status": "in_progress",
        }
        try:
            yield task_record
            task_record["status"] = "completed"
        except Exception as exc:
            task_record["status"] = "failed"
            task_record["error"] = str(exc)
            raise
        finally:
            t_end = time.time()
            task_record["end_time"] = datetime.now(timezone.utc).isoformat()
            task_record["duration_seconds"] = round(t_end - t_start, 3)
            self.tasks.append(task_record)

    def record_custom_task(self, task_name: str, agent_role: str, duration_seconds: float, status: str = "completed", metadata: Optional[Dict[str, Any]] = None):
        """Manually records a completed task metric."""
        iso_now = datetime.now(timezone.utc).isoformat()
        record = {
            "task_name": task_name,
            "agent_role": agent_role,
            "duration_seconds": round(duration_seconds, 3),
            "timestamp": iso_now,
            "status": status,
            "metadata": metadata or {},
        }
        self.tasks.append(record)
        self.routing_history.append({
            "step": len(self.routing_history) + 1,
            "routed_by": "Manager LLM",
            "assigned_agent": agent_role,
            "task_name": task_name,
            "timestamp": iso_now,
        })

    def finalize(self) -> Dict[str, Any]:
        """Calculates totals and writes benchmark metrics to json file."""
        self.total_duration_seconds = round(time.time() - self.start_wall_time, 3)
        summary = {
            "workflow_metadata": self.workflow_metadata,
            "total_duration_seconds": self.total_duration_seconds,
            "task_count": len(self.tasks),
            "routing_history": self.routing_history,
            "tasks": self.tasks,
        }
        
        # Ensure parent directory exists if specified
        dirname = os.path.dirname(self.output_file)
        if dirname:
            os.makedirs(dirname, exist_ok=True)
            
        with open(self.output_file, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)

        return summary
