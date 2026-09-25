"""
Data models and typed schemas for Cache-Forge prompt prefix pinning.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any
import hashlib


class SectionType(str, Enum):
    SYSTEM_STATIC = "system_static"       # Immutable base instructions
    TOOL_SCHEMA = "tool_schema"           # Lexicographically sorted tool specs
    CODEBASE_AST = "codebase_ast"         # Static AST file map & class graph
    SWARM_ROLE = "swarm_role"             # Fixed role definition
    VOLATILE_TAIL = "volatile_tail"       # Dynamic timestamps, task inputs, fencing tokens


@dataclass
class PromptSection:
    section_type: SectionType
    content: str
    is_cache_pinned: bool = True
    token_estimate: int = 0

    def __post_init__(self):
        if self.token_estimate == 0:
            self.token_estimate = max(1, len(self.content) // 4)


@dataclass
class CanonicalizedPrompt:
    prefix_content: str
    suffix_content: str
    total_tokens: int
    cached_prefix_tokens: int
    volatile_tokens: int
    prefix_sha256: str = ""

    def __post_init__(self):
        if not self.prefix_sha256:
            self.prefix_sha256 = hashlib.sha256(self.prefix_content.encode("utf-8")).hexdigest()[:16]


@dataclass
class CacheForgeMetrics:
    total_calls: int
    unoptimized_hit_rate: float
    forged_hit_rate: float
    raw_cost_usd: float
    forged_cost_usd: float
    savings_percentage: float
    latency_reduction_ratio: float
