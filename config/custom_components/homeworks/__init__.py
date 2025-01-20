from __future__ import annotations

import asyncio
from collections.abc import Mapping
from dataclasses import dataclass, field
import logging
from typing import Any

@dataclass
class HomeworksData:
    """Container for config entry data."""

    controller: Homeworks
    controller_id: str
    keypads: dict[str, HomeworksKeypad]
    ccos: dict[str, dict[str, Any]] = field(default_factory=dict)
