from dataclasses import dataclass, field
from datetime import datetime
from utils import rnd_id


@dataclass
class MySkill:
    id: str = field(default_factory=lambda: f"SK_{rnd_id()}")
    name: str = "Skill"
    description: str = ""
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def is_valid(self):
        return bool(self.name)
