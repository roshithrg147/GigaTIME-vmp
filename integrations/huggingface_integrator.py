import requests
from config.settings import Settings

class HuggingFaceIntegrator:
    def __init__(self):
        self.settings = Settings()
        self.model_id = self.settings.hf_model_for_interpretation
        self.api_url = f"https://api-inference.huggingface.co/models/{self.model_id}"
        self.headers = {"Authorization": f"Bearer {self.settings.hf_token}"}

    def generate_completion(self, prompt: str, **kwargs):
        """Generates text completion using the GigaTIME model."""
        response = requests.post(
            self.api_url,
            headers=self.headers,
            json={"inputs": prompt, "parameters": kwargs}
        )
        response.raise_for_status()
        return response.json()
