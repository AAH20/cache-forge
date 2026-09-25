"""
Prefix Canonicalizer: Implements deterministic sorting and volatility tail isolation.
"""

from typing import List, Dict, Any, Tuple
from .models import SectionType, PromptSection, CanonicalizedPrompt


class PrefixCanonicalizer:
    """Sorts, normalizes, and binds prompt layers to guarantee bit-exact prefix cache hits."""

    ORDER_PRIORITY = {
        SectionType.SYSTEM_STATIC: 10,
        SectionType.TOOL_SCHEMA: 20,
        SectionType.CODEBASE_AST: 30,
        SectionType.SWARM_ROLE: 40,
        SectionType.VOLATILE_TAIL: 100,
    }

    @classmethod
    def canonicalize(cls, sections: List[PromptSection]) -> CanonicalizedPrompt:
        """Sorts prompt sections, consolidates immutable prefix, and quarantines volatile tail."""
        # 1. Sort sections by canonical layer priority
        sorted_sections = sorted(sections, key=lambda s: cls.ORDER_PRIORITY.get(s.section_type, 999))

        prefix_chunks: List[str] = []
        suffix_chunks: List[str] = []
        prefix_tokens = 0
        suffix_tokens = 0

        for sec in sorted_sections:
            clean_content = sec.content.strip()
            if sec.section_type == SectionType.VOLATILE_TAIL or not sec.is_cache_pinned:
                suffix_chunks.append(clean_content)
                suffix_tokens += sec.token_estimate
            else:
                prefix_chunks.append(clean_content)
                prefix_tokens += sec.token_estimate

        prefix_str = "\n\n".join(prefix_chunks)
        suffix_str = "\n\n".join(suffix_chunks)
        total_tokens = prefix_tokens + suffix_tokens

        return CanonicalizedPrompt(
            prefix_content=prefix_str,
            suffix_content=suffix_str,
            total_tokens=total_tokens,
            cached_prefix_tokens=prefix_tokens,
            volatile_tokens=suffix_tokens
        )

    @staticmethod
    def canonicalize_tool_schemas(tools: List[Dict[str, Any]]) -> str:
        """Sorts tool definitions deterministically by name and returns formatted block."""
        sorted_tools = sorted(tools, key=lambda t: t.get("name", ""))
        lines = ["# CANONICAL TOOL SCHEMAS:"]
        for t in sorted_tools:
            name = t.get("name", "unnamed")
            desc = t.get("description", "")
            lines.append(f"- tool: `{name}`: {desc}")
        return "\n".join(lines)
