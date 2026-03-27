from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np


@dataclass
class Task:
    id: str
    name: str
    description: str
    deadline: Optional[str]
    dependencies: List[str]
    progress: float
    status: str
    assigned_to: str

    def to_dict(self) -> Dict:
        return asdict(self)


class MissionTracker:
    def __init__(self, storage_path: str = './mission_tracker.json') -> None:
        self.storage_path = Path(storage_path)
        self.tasks: Dict[str, Task] = {}
        self.global_progress = 0.0
        self.load()
        if not self.tasks:
            self._initialize_default_mission()

    def load(self) -> None:
        if self.storage_path.exists():
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.tasks = {tid: Task(**t) for tid, t in data.get('tasks', {}).items()}
            self.global_progress = float(data.get('global_progress', 0.0))

    def save(self) -> None:
        data = {
            'global_progress': float(self.global_progress),
            'tasks': {tid: t.to_dict() for tid, t in self.tasks.items()},
            'last_update': datetime.now().isoformat(),
        }
        with open(self.storage_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _initialize_default_mission(self) -> None:
        tasks_def = [
            {
                'id': 'T001',
                'name': 'Adam Core Extensions Implementation',
                'description': 'Implement Batch 21 core modules',
                'deadline': '2025-10-26',
                'dependencies': [],
                'progress': 0.8,
                'status': 'in_progress',
                'assigned_to': 'Adam',
            },
            {
                'id': 'T002',
                'name': 'Replicate Watanabe EEG-Quantum Experiment',
                'description': 'Setup 3 labs and execute protocol',
                'deadline': '2026-Q2',
                'dependencies': ['T003'],
                'progress': 0.0,
                'status': 'pending',
                'assigned_to': 'Team',
            },
            {
                'id': 'T003',
                'name': 'Secure Initial Funding',
                'description': 'Obtain $500k MVP budget',
                'deadline': '2025-Q4',
                'dependencies': ['T004'],
                'progress': 0.0,
                'status': 'pending',
                'assigned_to': 'Adrian',
            },
            {
                'id': 'T004',
                'name': 'Publish CIEL/0 Preprint',
                'description': 'Write and submit preprint',
                'deadline': '2025-11-30',
                'dependencies': ['T001'],
                'progress': 0.3,
                'status': 'in_progress',
                'assigned_to': 'Adrian+Adam',
            },
        ]
        for tdef in tasks_def:
            self.tasks[tdef['id']] = Task(**tdef)
        self._update_global_progress()
        self.save()

    def update_task(self, task_id: str, progress: Optional[float] = None, status: Optional[str] = None) -> None:
        if task_id not in self.tasks:
            return
        task = self.tasks[task_id]
        if progress is not None:
            task.progress = float(np.clip(progress, 0.0, 1.0))
            if task.progress >= 1.0:
                task.status = 'completed'
        if status is not None:
            task.status = str(status)
        self._update_global_progress()
        self.save()

    def _update_global_progress(self) -> None:
        if not self.tasks:
            self.global_progress = 0.0
            return
        total = float(sum(float(t.progress) for t in self.tasks.values()))
        self.global_progress = total / float(len(self.tasks))

    def get_status_report(self) -> str:
        report: List[str] = [
            '=' * 60,
            'MISSION STATUS REPORT - Planetary Healing',
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            f"Global Progress: {self.global_progress:.1%}",
            '=' * 60,
            '',
        ]

        by_status: Dict[str, List[Task]] = {'in_progress': [], 'pending': [], 'blocked': [], 'completed': []}
        for task in self.tasks.values():
            by_status.setdefault(task.status, []).append(task)

        for status in ['in_progress', 'blocked', 'pending', 'completed']:
            if by_status.get(status):
                report.append(f"\n{status.upper().replace('_', ' ')}:")
                for task in by_status[status]:
                    deps_str = f" (deps: {','.join(task.dependencies)})" if task.dependencies else ''
                    report.append(f"  [{task.id}] {task.name} - {task.progress:.0%}{deps_str}")
                    report.append(f"       Deadline: {task.deadline or 'None'} | Assigned: {task.assigned_to}")

        report.append('\n' + '=' * 60)
        return '\n'.join(report)

    def get_next_actions(self, n: int = 3) -> List[Task]:
        actionable = [
            t
            for t in self.tasks.values()
            if t.status in ['pending', 'in_progress']
            and all(self.tasks[dep].status == 'completed' for dep in t.dependencies if dep in self.tasks)
        ]
        actionable.sort(key=lambda t: (t.status != 'in_progress', t.progress, t.deadline or '9999'))
        return actionable[: int(n)]
