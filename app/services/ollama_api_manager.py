"""
Ollama API Manager for the Excel AI Assistant.
Handles interactions with locally running Ollama API for open-source models.
"""

import json
import logging
import time
from urllib.parse import urlsplit
from typing import Tuple, Optional, Generator

import requests


class OllamaAPIManager:
    """Manager for interacting with locally running Ollama API"""

    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3"):
        """Initialize the Ollama API manager"""
        self.set_base_url(base_url)
        self.model = model
        self.logger = logging.getLogger("OllamaAPIManager")

        # Rate limiting
        self.request_count = 0
        self.request_start_time = time.time()
        self.max_requests_per_minute = 30  # Default safe limit

    def set_base_url(self, base_url: str) -> None:
        """Set the base URL for Ollama API"""
        parsed = urlsplit(base_url)
        if parsed.scheme not in ('http', 'https') or not parsed.hostname or parsed.username or parsed.password or parsed.query or parsed.fragment:
            raise ValueError("Ollama URL must be an HTTP(S) URL without credentials, query or fragment.")
        self.base_url = base_url.rstrip('/')

    def set_model(self, model: str) -> None:
        """Set the model to use for API calls"""
        self.model = model

    def list_available_models(self) -> Tuple[bool, Optional[list], Optional[str]]:
        """
        Get list of available models from Ollama

        Returns:
            Tuple of (success, models_list, error_message)
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=(5, 30))
            if response.status_code == 200:
                data = response.json()
                # Extract just the model names from the response
                models = [model['name'] for model in data.get('models', [])]
                return True, models, None
            else:
                return False, None, f"Error {response.status_code}: {response.text}"
        except Exception as e:
            self.logger.error(f"Error listing Ollama models: {str(e)}")
            return False, None, f"Connection error: {str(e)}"

    def test_connection(self) -> Tuple[bool, str]:
        """Test the Ollama API connection"""
        try:
            # First try to get list of models
            success, models, error = self.list_available_models()
            if not success:
                return False, f"Failed to connect to Ollama: {error}"

            # Then try a simple generation to ensure the API is working
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": "Say hello in one word:",
                    "stream": False,
                    "options": {
                        "temperature": 0.1,
                        "num_predict": 10
                    }
                },
                timeout=(5, 120)
            )

            if response.status_code == 200:
                return True, "Connection successful"
            else:
                return False, f"Error {response.status_code}: {response.text}"
        except requests.exceptions.ConnectionError:
            return False, "Could not connect to Ollama. Is it running at the specified URL?"
        except Exception as e:
            self.logger.error(f"Ollama connection test error: {str(e)}")
            return False, f"Error: {str(e)}"

    def process_single_cell(
            self,
            cell_content: str,
            system_prompt: str,
            user_prompt: str,
            temperature: float = 0.3,
            max_tokens: int = 150,
            context_data: Optional[dict] = None
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Process a single cell using Ollama

        Args:
            cell_content: The content of the cell being processed
            system_prompt: System prompt for the AI
            user_prompt: User prompt for the AI
            temperature: Temperature parameter for generation
            max_tokens: Maximum tokens in response
            context_data: Optional dictionary with context data from other columns
            
        Returns:
            Tuple of (success, result, error_message)
        """
        if not self._check_rate_limit():
            return False, None, "Rate limit exceeded. Please try again later."

        formatted_prompt = f"{user_prompt}\n\nCell content: {cell_content}"
        
        # Add context information if available
        if context_data and len(context_data) > 0:
            context_text = "\n\nContext information:\n"
            for key, value in context_data.items():
                context_text += f"- {key}: {value}\n"
            formatted_prompt += context_text

        try:
            # Use streaming for more efficient processing with local models
            self._increment_request_count()
            result = ""
            for chunk in self._generate_streaming(formatted_prompt, system_prompt, temperature, max_tokens):
                result += chunk

            if not result.strip():
                return False, None, "The model returned an empty answer; the cell was left unchanged."
            return True, result.strip(), None

        except Exception as e:
            self.logger.error(f"Ollama API Error: {str(e)}")
            return False, None, f"Error: {str(e)}"

    def _generate_streaming(
            self,
            prompt: str,
            system: str,
            temperature: float = 0.3,
            max_tokens: int = 150
    ) -> Generator[str, None, None]:
        """
        Generate text from Ollama with streaming for better performance

        Args:
            prompt: The user prompt
            system: The system prompt
            temperature: Model temperature
            max_tokens: Maximum tokens to generate

        Yields:
            Text chunks as they are generated
        """
        # Construct the API request
        request_data = {
            "model": self.model,
            "prompt": prompt,
            "system": system,
            "stream": True,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }

        # Make streaming request
        response = requests.post(
            f"{self.base_url}/api/generate",
            json=request_data,
            stream=True,
            timeout=(5, 120)
        )

        try:
            if response.status_code != 200:
                raise RuntimeError(f"API Error: {response.status_code} - {response.text}")
            done = False
            for line in response.iter_lines():
                if not line:
                    continue
                chunk = json.loads(line)
                if chunk.get("error"):
                    raise RuntimeError(chunk["error"])
                if "response" in chunk:
                    yield chunk["response"]
                if chunk.get("done", False):
                    if chunk.get('done_reason') == 'length':
                        raise RuntimeError("Output reached the token limit; increase max tokens and retry.")
                    done = True
                    break
            if not done:
                raise RuntimeError("Ollama stream ended before generation completed")
        finally:
            response.close()

    def _increment_request_count(self) -> None:
        """Track API request count for rate limiting"""
        current_time = time.time()
        # Reset counter if a minute has passed
        if current_time - self.request_start_time > 60:
            self.request_count = 0
            self.request_start_time = current_time

        self.request_count += 1

    def _check_rate_limit(self) -> bool:
        """Check if we're under the rate limit"""
        current_time = time.time()
        # Reset counter if a minute has passed
        if current_time - self.request_start_time > 60:
            self.request_count = 0
            self.request_start_time = current_time
            return True

        # Check if we're still under the limit
        return self.request_count < self.max_requests_per_minute
