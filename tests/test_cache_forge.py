"""
Unit tests for Cache-Forge using standard unittest.
"""

import unittest
from cache_forge.models import SectionType, PromptSection
from cache_forge.prefix_canonicalizer import PrefixCanonicalizer
from cache_forge.cache_lock_arbiter import CacheLockArbiter


class TestCacheForge(unittest.TestCase):
    def test_canonical_ordering_and_tail_isolation(self):
        # Provide sections in chaotic order
        s_volatile = PromptSection(SectionType.VOLATILE_TAIL, "TIMESTAMP=12345", token_estimate=10)
        s_tools = PromptSection(SectionType.TOOL_SCHEMA, "tools list...", token_estimate=50)
        s_system = PromptSection(SectionType.SYSTEM_STATIC, "system prompt...", token_estimate=100)

        canonical = PrefixCanonicalizer.canonicalize([s_volatile, s_tools, s_system])

        # Prefix must contain system and tools in correct order
        self.assertTrue(canonical.prefix_content.startswith("system prompt..."))
        self.assertIn("tools list...", canonical.prefix_content)
        # Volatile tail must NOT be in prefix
        self.assertNotIn("TIMESTAMP=12345", canonical.prefix_content)
        self.assertIn("TIMESTAMP=12345", canonical.suffix_content)
        self.assertEqual(canonical.cached_prefix_tokens, 150)
        self.assertEqual(canonical.volatile_tokens, 10)

    def test_prefix_hash_stability(self):
        # Two prompts with different volatile tails must yield the EXACT same prefix SHA256
        s1 = [
            PromptSection(SectionType.SYSTEM_STATIC, "FIXED SYSTEM INSTRUCTION"),
            PromptSection(SectionType.VOLATILE_TAIL, "RANDOM_ID_001")
        ]
        s2 = [
            PromptSection(SectionType.SYSTEM_STATIC, "FIXED SYSTEM INSTRUCTION"),
            PromptSection(SectionType.VOLATILE_TAIL, "RANDOM_ID_999")
        ]

        c1 = PrefixCanonicalizer.canonicalize(s1)
        c2 = PrefixCanonicalizer.canonicalize(s2)

        self.assertEqual(c1.prefix_sha256, c2.prefix_sha256)

    def test_arbiter_swarm_economics(self):
        arbiter = CacheLockArbiter(cached_token_discount=0.90)
        metrics = arbiter.compute_swarm_economics(
            num_agents=5,
            steps_per_agent=10,
            prefix_tokens=30000,
            volatile_tokens_per_step=200,
            base_rate_per_million=3.00
        )

        self.assertEqual(metrics.total_calls, 50)
        self.assertGreater(metrics.forged_hit_rate, 95.0)
        self.assertGreater(metrics.savings_percentage, 75.0)
        self.assertLess(metrics.forged_cost_usd, metrics.raw_cost_usd)


if __name__ == "__main__":
    unittest.main()
