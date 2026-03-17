from typing import List
from llm.ollama_client import call_ollama
from llm.prompts import (build_missing_info_response_prompt, build_completion_response_prompt)
from models.housing_filters import HousingFilters


def generate_missing_info_reply_tool(filters: HousingFilters, missing_fields: List[str]) -> str:
    prompt = build_missing_info_response_prompt(current_filters=filters.model_dump(mode="json"), missing_fields=missing_fields)
    return call_ollama(prompt).strip()


def generate_completion_reply_tool(filters: HousingFilters) -> str:
    prompt = build_completion_response_prompt(current_filters=filters.model_dump(mode="json"))
    return call_ollama(prompt).strip()