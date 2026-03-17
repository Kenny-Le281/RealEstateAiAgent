import json

from agent.agent_orchestrator import run_agent
from models.housing_filters import HousingFilters


def run_listing_chatbot() -> None:
    print("Bot: Hi! Tell me what kind of property you're looking for.")
    print()

    current_filters = HousingFilters()

    while True:
        user_input = input("You: ").strip()

        if not user_input:
            print("Bot: Please type something.")
            print()
            continue

        try:
            result = run_agent(user_input, current_filters)
        except Exception as exception:
            print(f"Bot: I ran into a problem: {exception}")
            print()
            continue

        current_filters = result["filters"]

        print(f"Bot: {result['reply']}")
        print()

        print("=== CURRENT FILTER OBJECT ===")
        print(json.dumps(current_filters.model_dump(mode="json"), indent=2))
        print()

        if result["api_params"] is not None:
            print("=== DETERMINISTIC API PARAMS ===")
            print(json.dumps(result["api_params"], indent=2))
            print()

        if result["done"] and result["intent"] == "end_chat":
            break


run_listing_chatbot()