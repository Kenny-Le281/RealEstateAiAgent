from models.housing_filters import HousingFilters
from tools.build_api_params_tool import build_api_params_tool
from tools.classify_intent_tool import classify_intent_tool
from tools.merge_filters_tool import merge_filters_tool
from tools.normal_chat_tool import normal_chat_tool
from tools.parse_filters_tool import parse_filters_tool
from tools.response_generation_tool import (generate_completion_reply_tool, generate_missing_info_reply_tool)
from tools.search_state_tool import has_required_info_tool, get_missing_fields_tool


def run_agent(user_input: str, current_filters: HousingFilters) -> dict:
    intent_result = classify_intent_tool(user_message=user_input,current_filters=current_filters.model_dump(mode="json"))

    intent = intent_result.intent

    if intent == "end_chat":
        return {
            "reply": "Okay, ending the chat.",
            "filters": current_filters,
            "done": True,
            "api_params": None,
            "intent": intent,
        }

    if intent in {"general_question", "conversation"}:
        reply = normal_chat_tool(
            user_message=user_input,
            current_filters=current_filters.model_dump(mode="json")
        )
        return {
            "reply": reply,
            "filters": current_filters,
            "done": False,
            "api_params": None,
            "intent": intent,
        }

    if intent in {"provide_search_info", "refine_search"}:
        parsed_filters = parse_filters_tool(user_input)
        updated_filters = merge_filters_tool(current_filters, parsed_filters)

        if has_required_info_tool(updated_filters):
            reply = generate_completion_reply_tool(updated_filters)
            api_params = build_api_params_tool(updated_filters)
            return {
                "reply": reply,
                "filters": updated_filters,
                "done": True,
                "api_params": api_params,
                "intent": intent,
            }

        missing_fields = get_missing_fields_tool(updated_filters)
        reply = generate_missing_info_reply_tool(updated_filters, missing_fields)

        return {
            "reply": reply,
            "filters": updated_filters,
            "done": False,
            "api_params": None,
            "intent": intent,
        }

    if intent == "confirm_search":
        if has_required_info_tool(current_filters):
            reply = generate_completion_reply_tool(current_filters)
            api_params = build_api_params_tool(current_filters)
            return {
                "reply": reply,
                "filters": current_filters,
                "done": True,
                "api_params": api_params,
                "intent": intent,
            }

        missing_fields = get_missing_fields_tool(current_filters)
        reply = generate_missing_info_reply_tool(current_filters, missing_fields)
        return {
            "reply": reply,
            "filters": current_filters,
            "done": False,
            "api_params": None,
            "intent": intent,
        }

    reply = normal_chat_tool(
        user_message=user_input,
        current_filters=current_filters.model_dump(mode="json")
    )
    return {
        "reply": reply,
        "filters": current_filters,
        "done": False,
        "api_params": None,
        "intent": intent,
    }