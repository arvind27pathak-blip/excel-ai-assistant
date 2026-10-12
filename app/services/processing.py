"""Validation and immutable run settings shared by preview and batch flows."""

from dataclasses import dataclass
import math


@dataclass(frozen=True)
class ProcessingSettings:
    batch_size: int
    temperature: float
    max_tokens: int

    @classmethod
    def parse(cls, batch_size, temperature, max_tokens):
        try:
            settings = cls(int(batch_size), float(temperature), int(max_tokens))
        except (TypeError, ValueError) as error:
            raise ValueError("Batch size, temperature and max tokens must be numbers.") from error
        if not 1 <= settings.batch_size <= 1000:
            raise ValueError("Batch size must be between 1 and 1000.")
        if not math.isfinite(settings.temperature) or not 0 <= settings.temperature <= 1:
            raise ValueError("Temperature must be between 0 and 1.")
        if not 1 <= settings.max_tokens <= 32768:
            raise ValueError("Max tokens must be between 1 and 32768.")
        return settings


def display_content(value):
    """Represent missing cells as blank, rather than sending 'None' to the model."""
    import pandas as pd
    return "" if value is None or pd.isna(value) else str(value)
