import pytest
from integrations.huggingface_integrator import HuggingFaceIntegrator
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_hf_integration_connection():
    # We mock the client to avoid actual network calls during testing
    with patch("huggingface_hub.InferenceClient.text_generation", return_value="Test completion") as mock_gen:
        integrator = HuggingFaceIntegrator()
        
        # Manually set token for testing if not in environment
        integrator.client.token = "fake-token"
        
        response = await integrator.generate_completion("Test prompt")
        
        assert response == "Test completion"
        mock_gen.assert_called_once()
        assert mock_gen.call_args.kwargs['model'] == "prov-gigatime/GigaTIME"
        assert mock_gen.call_args.kwargs['prompt'] == "Test prompt"
