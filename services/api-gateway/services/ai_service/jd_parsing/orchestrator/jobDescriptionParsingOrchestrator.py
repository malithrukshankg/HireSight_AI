from services.ai_service.jd_parsing.agents.jobDescriptionParsingAgent import (
    JobDescriptionParsingAgent,
)
from services.ai_service.jd_parsing.prompts.jobDescriptionParsingPrompt import (
    build_jd_parsing_system_instruction,
    build_jd_parsing_user_prompt,
)
from services.ai_service.jd_parsing.schemas.parsedJobDescription import ParsedJobDescription
from services.ai_service.jd_parsing.utils.mapper import normalize_parsed_job_description
from services.ai_service.jd_parsing.utils.validator import validate_jd_input


class JobDescriptionParsingOrchestrator:
    def __init__(self, parsing_agent: JobDescriptionParsingAgent | None = None):
        self.parsing_agent = parsing_agent or JobDescriptionParsingAgent()

    async def parse_job_description(
        self,
        *,
        description: str,
        title: str | None = None,
    ) -> ParsedJobDescription:
        clean_description, clean_title = validate_jd_input(description=description, title=title)

        system_instruction = build_jd_parsing_system_instruction()
        user_prompt = build_jd_parsing_user_prompt(
            description=clean_description,
            title=clean_title,
        )

        parsed = await self.parsing_agent.parse(
            user_prompt=user_prompt,
            system_instruction=system_instruction,
        )
        return normalize_parsed_job_description(parsed)
