from google import genai
from config.settings import Settings

class GeminiIntegrator:
    def __init__(self):
        self.settings = Settings()
        self.client = genai.Client(api_key=self.settings.gemini_api_key)

    def generate_completion(self, prompt: str):
        """Generates text completion using the Gemini model."""
        response = self.client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        return response.text
