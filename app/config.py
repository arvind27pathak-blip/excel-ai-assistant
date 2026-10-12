"""
Configuration manager for the Excel AI Assistant.
Handles loading, saving, and accessing application configuration settings.
"""

import json
import os
import tempfile
from copy import deepcopy
from dotenv import load_dotenv
import platform
from pathlib import Path


class AppConfig:
    """Application configuration manager"""

    def __init__(self):
        """Initialize configuration with default values"""
        # Default configuration
        self._config = {
            # API settings
            'api_type': 'openai',  # 'openai', 'openrouter' or 'ollama'
            'api_key': '',  # OpenAI API key
            'openrouter_api_key': '',  # Session-only OpenRouter credential
            'openrouter_model': 'openai/gpt-4o-mini',
            'model': 'gpt-3.5-turbo',  # Current selected model
            'ollama_url': 'http://localhost:11434',  # Ollama API URL
            'ollama_model': 'llama3',  # Default Ollama model

            # UI settings
            'theme': 'system',
            'recent_files': [],
            'max_recent_files': 10,

            # Default prompts
            'default_system_prompt': 'You are a data manipulation assistant. Transform the cell content according to the user\'s instructions.',

            # Processing settings
            'temperature': 0.3,
            'max_tokens': 150,
            'batch_size': 10,  # Number of cells to process in a batch

            # Display settings
            'column_width': 100,
            'auto_resize_columns': True,

            # Logging settings
            'save_logs': False,
            'log_level': 'INFO',

            # Predefined prompts
            'prompts': {
                # Basic text transformation
                'Capitalize': 'Capitalize all text in this cell.',
                'To Uppercase': 'Convert all text to uppercase.',
                'To Lowercase': 'Convert all text to lowercase.',
                'Sentence Case': 'Format the text in sentence case (capitalize first letter of each sentence).',
                'Title Case': 'Format the text in title case (capitalize first letter of each word, except for articles, prepositions, and conjunctions).',
                'Remove Extra Spaces': 'Remove all extra whitespace, including double spaces and leading/trailing spaces.',

                # Data formatting
                'Format Date': 'Format this as a standard date (YYYY-MM-DD).',
                'Format Phone Number': 'Format this as a standard phone number.',
                'Format Currency': 'Format this as a standard currency value.',
                'Format Percentage': 'Format this as a percentage.',
                'Extract Numbers': 'Extract all numbers from this text.',
                'Format Address': 'Format this as a properly structured address with standard capitalization.',
                'Format Email': 'Format this as a proper email address (lowercase, no extra spaces).',

                # Content transformation
                'Summarize': 'Summarize this text in one sentence.',
                'Expand': 'Expand this abbreviated or short text with more details while maintaining its meaning.',
                'Bullet Points': 'Convert this text into a bulleted list of key points.',
                'Fix Grammar': 'Fix any grammar or spelling errors in this text.',
                'Simplify': 'Simplify this text to make it easier to understand while preserving the key information.',
                'Formalize': 'Rewrite this text in a more formal, professional tone.',
                'Casualize': 'Rewrite this text in a more casual, conversational tone.',

                # Code and markup handling
                'Format JSON': 'Format this as valid, properly indented JSON.',
                'Format XML': 'Format this as valid, properly indented XML.',
                'Format CSV': 'Format this as valid CSV with proper delimiters and escaping.',
                'HTML to Text': 'Convert this HTML to well-structured plain text, preserving the semantic structure.',
                'Markdown to Text': 'Convert this Markdown to plain text while preserving the content structure.',
                'Clean Code': 'Clean up and format this code snippet with proper indentation and style.',

                # Multi-language translation
                'Translate to English': 'Translate this text to English.',
                'Translate to Arabic': 'Translate this text to Arabic.',
                'Translate to Hebrew': 'Translate this text to Hebrew.',

                # Data cleanup
                'Remove Duplicates': 'Remove any duplicate information from this text.',
                'Remove HTML Tags': 'Remove all HTML tags from this text, keeping only the content.',
                'Fix Encoding Issues': 'Fix text encoding issues like garbled characters or HTML entities.',
                'Fill Blank': 'Complete the blank or missing information in this cell based on context from surrounding cells.',
                'Standardize Format': 'Standardize the format of this data according to conventions.',
                'Extract Dates': 'Extract all dates from this text and format them consistently.',

                # Name handling
                'Split Name': 'Split this full name into separate first name and last name components.',
                'Format Name': 'Format this name with proper capitalization and spacing.',
                'Extract Initials': 'Extract the initials from this name.',

                # Special formats
                'Convert to Citation': 'Convert this reference information to a proper citation format.',
            }
        }

        # Load configuration from file
        self._config_file = self._get_config_path()
        self._load()
        self._normalize()
        load_dotenv(Path.cwd() / '.env')
        self._config['api_key'] = os.environ.get('OPENAI_API_KEY', self._config.get('api_key', ''))
        self._config['openrouter_api_key'] = os.environ.get('OPENROUTER_API_KEY', self._config.get('openrouter_api_key', ''))

    def _get_config_path(self):
        """Get the platform-specific configuration file path"""
        system = platform.system()
        home = Path.home()

        if system == 'Windows':
            config_dir = home / 'AppData' / 'Roaming' / 'ExcelAIAssistant'
        elif system == 'Darwin':  # macOS
            config_dir = home / 'Library' / 'Application Support' / 'ExcelAIAssistant'
        else:  # Linux and others
            config_dir = home / '.config' / 'excel-ai-assistant'

        # Create directory if it doesn't exist
        config_dir.mkdir(parents=True, exist_ok=True)

        return config_dir / 'config.json'

    def _load(self):
        """Load configuration from file"""
        try:
            if self._config_file.exists():
                with open(self._config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)

                    if not isinstance(loaded_config, dict):
                        raise ValueError("Configuration must be a JSON object")
                    if not isinstance(loaded_config.get('prompts', {}), dict):
                        loaded_config.pop('prompts', None)
                    # Special handling for prompt templates - merge instead of replace
                    if 'prompts' in loaded_config and 'prompts' in self._config:
                        # First, save the default prompts
                        default_prompts = self._config['prompts'].copy()

                        # Update with loaded prompts
                        self._config.update(loaded_config)

                        # Merge prompts dictionaries, giving priority to user's custom prompts
                        # but ensuring all default prompts are present
                        merged_prompts = default_prompts.copy()
                        merged_prompts.update(self._config['prompts'])
                        self._config['prompts'] = merged_prompts
                    else:
                        # Regular update for other config items
                        self._config.update(loaded_config)
        except Exception as e:
            print(f"Error loading configuration: {e}")
            # Continue with default configuration

    def _normalize(self):
        from app.services.processing import ProcessingSettings
        from app.services.ollama_api_manager import OllamaAPIManager
        for key, default in {'model': 'gpt-3.5-turbo', 'ollama_model': 'llama3',
                             'openrouter_model': 'openai/gpt-4o-mini', 'openrouter_api_key': '',
                             'api_key': '', 'default_system_prompt': 'Transform the cell content as instructed.'}.items():
            if not isinstance(self._config.get(key), str):
                self._config[key] = default
        self._config['api_type'] = str(self._config.get('api_type', 'openai')).lower()
        if self._config['api_type'] not in ('openai', 'openrouter', 'ollama'):
            self._config['api_type'] = 'openai'
        if self._config.get('theme') not in ('light', 'dark', 'system'):
            self._config['theme'] = 'system'
        try:
            settings = ProcessingSettings.parse(self.get('batch_size'), self.get('temperature'), self.get('max_tokens'))
        except ValueError:
            settings = ProcessingSettings(10, 0.3, 150)
        self._config.update(batch_size=settings.batch_size, temperature=settings.temperature, max_tokens=settings.max_tokens)
        try:
            OllamaAPIManager(base_url=self.get('ollama_url'))
        except (ValueError, TypeError, AttributeError):
            self._config['ollama_url'] = 'http://localhost:11434'
        for key, default, maximum in [('max_recent_files', 10, 100), ('rate_limit', 20, 1000), ('max_display_rows', 1000, 10000)]:
            try:
                self._config[key] = max(1, min(maximum, int(self.get(key, default))))
            except (ValueError, TypeError):
                self._config[key] = default
        if not isinstance(self.get('recent_files'), list):
            self._config['recent_files'] = []
        self._config['recent_files'] = [path for path in self.get('recent_files') if isinstance(path, str)]
        for key, default in [('autosave', False), ('save_logs', False)]:
            if not isinstance(self.get(key), bool):
                self._config[key] = default
        if self.get('log_level') not in ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'):
            self._config['log_level'] = 'INFO'

    def save(self):
        """Atomically persist preferences; credentials remain session-only."""
        temporary = None
        try:
            preferences = deepcopy(self._config)
            preferences.pop('api_key', None)
            preferences.pop('openrouter_api_key', None)
            fd, temporary = tempfile.mkstemp(suffix='.json', dir=self._config_file.parent)
            with os.fdopen(fd, 'w', encoding='utf-8') as handle:
                json.dump(preferences, handle, indent=2)
            os.replace(temporary, self._config_file)
            return True
        except Exception as error:
            print(f"Error saving configuration: {error}")
            return False
        finally:
            if temporary and os.path.exists(temporary):
                os.remove(temporary)

    def get(self, key, default=None):
        """Get a configuration value"""
        return self._config.get(key, default)

    def set(self, key, value):
        """Set a configuration value"""
        self._config[key] = value

    def get_all(self):
        """Get a copy of the entire configuration"""
        return deepcopy(self._config)

    def get_active_model(self):
        """Get the currently active model info"""
        api_type = self.get('api_type', 'openai')
        key, default = self.model_setting(api_type)
        return {'api_type': api_type, 'model': self.get(key, default)}

    @staticmethod
    def model_setting(api_type):
        return {'openai': ('model', 'gpt-3.5-turbo'),
                'openrouter': ('openrouter_model', 'openai/gpt-4o-mini'),
                'ollama': ('ollama_model', 'llama3')}[api_type]

    def set_active_model(self, api_type, model):
        """Set the active model"""
        self.set('api_type', api_type)
        key, _ = self.model_setting(api_type)
        self.set(key, model)

    def add_recent_file(self, file_path):
        """Add a file to the recent files list"""
        recent_files = self.get('recent_files', [])

        # Remove if already in list
        if file_path in recent_files:
            recent_files.remove(file_path)

        # Add to beginning of list
        recent_files.insert(0, file_path)

        # Trim to max size
        max_count = self.get('max_recent_files', 10)
        if len(recent_files) > max_count:
            recent_files = recent_files[:max_count]

        self.set('recent_files', recent_files)

    def clear_recent_files(self):
        """Clear the recent files list"""
        self.set('recent_files', [])

    def get_prompt_templates(self):
        """Get the saved prompt templates"""
        return self.get('prompts', {})

    def add_prompt_template(self, name, prompt):
        """Add or update a prompt template"""
        prompts = self.get_prompt_templates()
        prompts[name] = prompt
        self.set('prompts', prompts)

    def remove_prompt_template(self, name):
        """Remove a prompt template"""
        prompts = self.get_prompt_templates()
        if name in prompts:
            del prompts[name]
            self.set('prompts', prompts)

    def restore_defaults(self, include_prompts=False):
        """
        Reset configuration to default values

        Args:
            include_prompts: Whether to reset prompt templates as well
        """
        # Default settings
        defaults = {
            # API settings
            'api_type': 'openai',
            'api_key': '',
            'openrouter_api_key': '',
            'openrouter_model': 'openai/gpt-4o-mini',
            'model': 'gpt-3.5-turbo',
            'ollama_url': 'http://localhost:11434',
            'ollama_model': 'llama3',

            # UI settings
            'theme': 'system',
            'max_recent_files': 10,

            # Default prompts
            'default_system_prompt': 'You are a data manipulation assistant. Transform the cell content according to the user\'s instructions.',

            # Processing settings
            'temperature': 0.3,
            'max_tokens': 150,
            'batch_size': 10,

            # Display settings
            'column_width': 100,
            'auto_resize_columns': True,

            # Logging settings
            'save_logs': False,
            'log_level': 'INFO',
        }

        # Reset config to defaults (keeping recent files)
        recent_files = self._config.get('recent_files', [])

        for key, value in defaults.items():
            self._config[key] = value

        # Keep recent files unless explicitly resetting everything
        if not include_prompts:
            self._config['recent_files'] = recent_files
        else:
            self._config['recent_files'] = []
            # Reset prompts to defaults
            default_prompts = {
                # Basic text transformation
                'Capitalize': 'Capitalize all text in this cell.',
                'To Uppercase': 'Convert all text to uppercase.',
                'To Lowercase': 'Convert all text to lowercase.',
                'Sentence Case': 'Format the text in sentence case (capitalize first letter of each sentence).',
                'Title Case': 'Format the text in title case (capitalize first letter of each word, except for articles, prepositions, and conjunctions).',
                'Remove Extra Spaces': 'Remove all extra whitespace, including double spaces and leading/trailing spaces.',

                # Data formatting
                'Format Date': 'Format this as a standard date (YYYY-MM-DD).',
                'Format Phone Number': 'Format this as a standard phone number.',
                'Format Currency': 'Format this as a standard currency value.',
                'Format Percentage': 'Format this as a percentage.',
                'Extract Numbers': 'Extract all numbers from this text.',
                'Format Address': 'Format this as a properly structured address with standard capitalization.',
                'Format Email': 'Format this as a proper email address (lowercase, no extra spaces).',

                # Content transformation
                'Summarize': 'Summarize this text in one sentence.',
                'Expand': 'Expand this abbreviated or short text with more details while maintaining its meaning.',
                'Bullet Points': 'Convert this text into a bulleted list of key points.',
                'Fix Grammar': 'Fix any grammar or spelling errors in this text.',
                'Simplify': 'Simplify this text to make it easier to understand while preserving the key information.',
                'Formalize': 'Rewrite this text in a more formal, professional tone.',
                'Casualize': 'Rewrite this text in a more casual, conversational tone.',

                # Code and markup handling
                'Format JSON': 'Format this as valid, properly indented JSON.',
                'Format XML': 'Format this as valid, properly indented XML.',
                'Format CSV': 'Format this as valid CSV with proper delimiters and escaping.',
                'HTML to Text': 'Convert this HTML to well-structured plain text, preserving the semantic structure.',
                'Markdown to Text': 'Convert this Markdown to plain text while preserving the content structure.',
                'Clean Code': 'Clean up and format this code snippet with proper indentation and style.',

                # Multi-language translation
                'Translate to English': 'Translate this text to English.',
                'Translate to Arabic': 'Translate this text to Arabic.',
                'Translate to Hebrew': 'Translate this text to Hebrew.',

                # Data cleanup
                'Remove Duplicates': 'Remove any duplicate information from this text.',
                'Remove HTML Tags': 'Remove all HTML tags from this text, keeping only the content.',
                'Fix Encoding Issues': 'Fix text encoding issues like garbled characters or HTML entities.',
                'Fill Blank': 'Complete the blank or missing information in this cell based on context from surrounding cells.',
                'Standardize Format': 'Standardize the format of this data according to conventions.',
                'Extract Dates': 'Extract all dates from this text and format them consistently.',

                # Name handling
                'Split Name': 'Split this full name into separate first name and last name components.',
                'Format Name': 'Format this name with proper capitalization and spacing.',

                # Special formats
                'Convert to Citation': 'Convert this reference information to a proper citation format.',
            }
            self._config['prompts'] = default_prompts

        # Save the restored defaults
        self.save()
