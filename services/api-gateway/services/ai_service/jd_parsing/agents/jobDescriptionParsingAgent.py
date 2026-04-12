from services.ai_service.jd_parsing.schemas.parsedJobDescription import ParsedJobDescription
from services.ai_service.shared.geminiClient import GeminiClient
from services.ai_service.shared.structuredOutputHelper import parse_and_validate


class JobDescriptionParsingAgent:
    def __init__(self, gemini_client: GeminiClient | None = None):
        self.gemini_client = gemini_client or GeminiClient()

    async def parse(
        self,
        *,
        user_prompt: str,
        system_instruction: str,
    ) -> ParsedJobDescription:
        raw_json = await self.gemini_client.generate_json_text_async(
            user_content=user_prompt,
            system_instruction=system_instruction,
        )
        return parse_and_validate(raw_json, ParsedJobDescription)
