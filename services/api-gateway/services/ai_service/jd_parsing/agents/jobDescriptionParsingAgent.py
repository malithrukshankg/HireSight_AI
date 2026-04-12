from services.ai_service.jd_parsing.schemas.parsedJobDescription import ParsedJobDescription
from services.ai_service.shared.geminiClient import GeminiClient


class JobDescriptionParsingAgent:
    def __init__(self, gemini_client: GeminiClient | None = None):
        self.gemini_client = gemini_client or GeminiClient()

    async def parse(
        self,
        *,
        user_prompt: str,
        system_instruction: str,
    ) -> ParsedJobDescription:
        return await self.gemini_client.generate_structured_async(
            user_content=user_prompt,
            system_instruction=system_instruction,
            model_cls=ParsedJobDescription,
        )
