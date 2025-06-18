from utils.recommender import get_semantic_matches

def get_response(user_input, memory):
    if user_input.lower() in ["more", "show more", "next"]:
        return get_more_results(memory)

    # Otherwise it's a new query
    results = get_semantic_matches(user_input)
    memory["last_results"] = results
    memory["current_index"] = 3  # first 3 shown now

    return format_results(results[:3]), memory

def get_more_results(memory):
    results = memory.get("last_results", [])
    index = memory.get("current_index", 0)

    if index >= len(results):
        return "No more matches to show. Try a new query?", memory

    next_index = index + 3
    next_batch = results[index:next_index]
    memory["current_index"] = next_index

    return format_results(next_batch), memory

def format_results(matches):
    if not matches:
        return "I couldn't find any good matches."

    return "\n".join(matches)
