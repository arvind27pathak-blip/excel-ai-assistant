"""
API Manager for the Excel AI Assistant.
Handles OpenAI, OpenRouter and Ollama requests.
"""

import logging
import time
from enum import Enum
from typing import List, Dict, Any, Optional, Tuple

from openai import OpenAI, APIError, RateLimitError

from app.services.ollama_api_manager import OllamaAPIManager


class APIType(Enum):
    """Enum for API types"""
    OPENAI = "openai"
    OPENROUTER = "openrouter"
    OLLAMA = "ollama"


class APIManager:
    """Manager for OpenAI, OpenRouter and Ollama requests."""

    def __init__(self, api_key: str = "", model: str = "gpt-3.5-turbo",
                 api_type: str = "openai", ollama_url: str = "http://localhost:11434"):
        """Initialize the API manager"""
        self.api_key = api_key
        self.model = model
        self.api_type = APIType(api_type)
        self.client = None
        self.logger = logging.getLogger("APIManager")

        # Initialize Ollama manager
        self.ollama_url = ollama_url
        self.ollama_manager = OllamaAPIManager(base_url=ollama_url, model=model)

        # Rate limiting
        self.request_count = 0
        self.request_start_time = time.time()
        self.max_requests_per_minute = 20  # Default safe limit

        # Initialize if API key is provided for OpenAI
        if api_key and self.api_type != APIType.OLLAMA:
            self.initialize()

    def initialize(self, api_key: Optional[str] = None) -> bool:
        """Initialize the API client"""
        if self.api_type != APIType.OLLAMA:
            if api_key is not None:
                self.api_key = api_key.strip()
                self.client = None

            if not self.api_key:
                self.logger.error("API key is required for %s", self.api_type.value)
                return False

            try:
                options = dict(api_key=self.api_key, timeout=60.0, max_retries=0)
                if self.api_type == APIType.OPENROUTER:
                    options.update(base_url="https://openrouter.ai/api/v1",
                                   default_headers={"X-OpenRouter-Title": "Excel AI Assistant"})
                self.client = OpenAI(**options)
                return True
            except Exception as e:
                self.logger.error("Failed to initialize %s client: %s", self.api_type.value, e)
                return False
        else:  # OLLAMA
            # No initialization needed for Ollama as it's handled by requests
            return True

    def set_api_type(self, api_type: str) -> None:
        """Select the provider, invalidating credentials when it changes."""
        selected = APIType(api_type)
        if selected != self.api_type:
            # A client/key from one cloud provider must never be reused for another.
            self.client = None
            self.api_key = ""
        self.api_type = selected

    def set_model(self, model: str) -> None:
        """Set the model to use for API calls"""
        self.model = model
        if self.api_type == APIType.OLLAMA:
            self.ollama_manager.set_model(model)

    def set_ollama_url(self, url: str) -> None:
        """Set the Ollama API URL"""
        self.ollama_manager.set_base_url(url)
        self.ollama_url = url

    def get_available_models(self) -> List[Dict[str, Any]]:
        """Get list of available models based on current API type"""
        if self.api_type == APIType.OPENAI:
            # Return standard OpenAI models (static list)
            return [
                {"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo", "api": "openai"},
                {"id": "gpt-4", "name": "GPT-4", "api": "openai"},
                {"id": "gpt-4-turbo", "name": "GPT-4 Turbo", "api": "openai"},
                {"id": "gpt-4o", "name": "GPT-4o", "api": "openai"},
                {"id": "gpt-4o-mini", "name": "GPT-4o Mini", "api": "openai"},
                {"id": "gpt-3.5-turbo-16k", "name": "GPT-3.5 Turbo 16k", "api": "openai"}
            ]
        elif self.api_type == APIType.OPENROUTER:
            return [{"id": "openai/gpt-4o-mini", "name": "openai/gpt-4o-mini", "api": "openrouter"}]
        else:  # OLLAMA
            # Fetch models from Ollama
            success, models, error = self.ollama_manager.list_available_models()
            if success and models:
                return [{"id": model, "name": model, "api": "ollama"} for model in models]
            else:
                # Return empty list if error
                self.logger.error(f"Error getting Ollama models: {error}")
                return []

    def test_connection(self) -> Tuple[bool, str]:
        """Test the API connection"""
        if self.api_type != APIType.OLLAMA:
            if not self.client:
                if not self.initialize():
                    return False, "API client not initialized"

            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": "Test connection"}
                    ],
                    max_tokens=5  # Minimal tokens for quick test
                )

                # Check if response is valid
                if hasattr(response, 'choices') and len(response.choices) > 0:
                    return True, "Connection successful"
                else:
                    return False, "Invalid response from API"

            except RateLimitError as e:
                return False, f"Rate limit exceeded: {str(e)}"
            except APIError as e:
                return False, f"API Error: {str(e)}"
            except Exception as e:
                return False, f"Error: {str(e)}"
        else:  # OLLAMA
            # Use Ollama manager to test connection
            return self.ollama_manager.test_connection()

    def process_single_cell(
            self,
            cell_content: str,
            system_prompt: str,
            user_prompt: str,
            temperature: float = 0.3,
            max_tokens: int = 150,
            context_data: Optional[Dict[str, Any]] = None
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Process a single cell using the selected API

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
        if self.api_type != APIType.OLLAMA:
            return self._process_openai(cell_content, system_prompt, user_prompt, temperature, max_tokens, context_data)
        else:  # OLLAMA
            return self.ollama_manager.process_single_cell(
                cell_content, system_prompt, user_prompt, temperature, max_tokens, context_data
            )

    def _process_openai(
            self,
            cell_content: str,
            system_prompt: str,
            user_prompt: str,
            temperature: float = 0.3,
            max_tokens: int = 150,
            context_data: Optional[Dict[str, Any]] = None
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """Process a single cell using the selected cloud chat endpoint."""
        if not self.client:
            if not self.initialize():
                return False, None, "API client not initialized"

        # Check rate limits
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
            self._increment_request_count()
            # Make API call
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": formatted_prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )

            # Extract result text
            choice = response.choices[0]
            if choice.finish_reason != 'stop' or choice.message.content is None:
                return False, None, "The model did not return a complete answer. Increase max tokens or revise the prompt."
            result = choice.message.content.strip()
            if not result:
                return False, None, "The model returned an empty answer; the cell was left unchanged."
            return True, result, None

        except RateLimitError as e:
            return False, None, f"Rate limit exceeded: {str(e)}"
        except APIError as e:
            return False, None, f"API Error: {str(e)}"
        except Exception as e:
            self.logger.error(f"API Error: {str(e)}")
            return False, None, f"Error: {str(e)}"

    def rate_limit_delay(self):
        manager = self.ollama_manager if self.api_type == APIType.OLLAMA else self
        elapsed = time.time() - manager.request_start_time
        if manager.request_count >= manager.max_requests_per_minute and elapsed < 60:
            return max(0.0, 60 - elapsed) + 0.01
        return 0.0

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
