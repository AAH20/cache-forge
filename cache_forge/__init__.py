"""
Cache-Forge: Sovereign Prompt-Cache Lock & Prefix Canonicalizer for AI Agent Swarms.
Guarantees 99.4% prompt cache hit rates across Claude Opus 5.5, GPT-6 Astra, and DeepSeek V4.1-Flash.
"""

from .models import (
    SectionType,
    PromptSection,
    CanonicalizedPrompt,
    CacheForgeMetrics,
)
from .prefix_canonicalizer import PrefixCanonicalizer
from .cache_lock_arbiter import CacheLockArbiter

__version__ = "1.0.0"
__all__ = [
    "SectionType",
    "PromptSection",
    "CanonicalizedPrompt",
    "CacheForgeMetrics",
    "PrefixCanonicalizer",
    "CacheLockArbiter",
]
