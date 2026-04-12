"""
JD parsing agent: mock Gemini at the GeminiClient boundary (Phase 4).

Run from services/api-gateway with the service root on PYTHONPATH, for example:

    python -m unittest discover -s tests -p "test_*.py"

Uses a stub config module so tests do not require a full .env or every
service dependency at import time (production still loads real config).
"""

from __future__ import annotations

import sys
import unittest
from types import ModuleType, SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

# Register before importing gateway packages that pull in ``config.settings``.
_cfg = ModuleType("config")
_cfg.settings = SimpleNamespace(
    GEMINI_API_KEY="test-key",
    GEMINI_MODEL="gemini-2.5-flash",
    GEMINI_TIMEOUT_SECONDS=60,
    GEMINI_API_VERSION=None,
)
sys.modules["config"] = _cfg

from services.ai_service.jd_parsing.agents.jobDescriptionParsingAgent import (
    JobDescriptionParsingAgent,
)
from services.ai_service.shared.aiExceptions import StructuredOutputValidationError
from services.ai_service.shared.geminiClient import GeminiClient

_VALID_MINIMAL_JSON = (
    '{"summary":"Build widgets","responsibilities":["Ship code"],'
    '"required_skills":["Python"],"preferred_skills":[],"qualifications":[],'
    '"experience_requirements":"","seniority_level":"","employment_type":"",'
    '"tools_technologies":[],"domain_keywords":[]}'
)


class TestJobDescriptionParsingAgent(unittest.IsolatedAsyncioTestCase):
    async def test_parse_uses_generate_json_text_async_and_returns_model(self) -> None:
        gemini = MagicMock(spec=GeminiClient)
        gemini.generate_json_text_async = AsyncMock(return_value=_VALID_MINIMAL_JSON)
        agent = JobDescriptionParsingAgent(gemini_client=gemini)

        result = await agent.parse(
            user_prompt="prompt body",
            system_instruction="sys",
        )

        gemini.generate_json_text_async.assert_awaited_once_with(
            user_content="prompt body",
            system_instruction="sys",
        )
        self.assertEqual(result.summary, "Build widgets")
        self.assertEqual(result.responsibilities, ["Ship code"])
        self.assertEqual(result.required_skills, ["Python"])

    async def test_parse_invalid_json_raises_structured_output_error(self) -> None:
        gemini = MagicMock(spec=GeminiClient)
        gemini.generate_json_text_async = AsyncMock(return_value="not json")
        agent = JobDescriptionParsingAgent(gemini_client=gemini)

        with self.assertRaises(StructuredOutputValidationError):
            await agent.parse(user_prompt="x", system_instruction="y")


if __name__ == "__main__":
    unittest.main()
