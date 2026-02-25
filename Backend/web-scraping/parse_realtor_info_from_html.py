import re
import json

def _iter_stingray_text_blobs(html: str):
    """
    The HTML contains cached API responses like:
      "text":"{}&&{\"version\":...\"payload\":{...}}"
    That "text" value is a JSON string, so quotes are escaped.

    This extracts each raw JSON-string value and decodes it.
    """
    for m in re.finditer(r'"text":"((?:\\.|[^"\\])*)"', html):
        raw = m.group(1)
        try:
            decoded = json.loads(f'"{raw}"')
        except Exception:
            continue
        yield decoded


def _extract_payload_json(decoded_text: str) -> dict | None:
    """
    decoded_text often looks like:
      {}&&{"version":...,"payload":{...}}
    We parse the JSON after the &&.
    """
    if "&&" not in decoded_text:
        return None
    _, after = decoded_text.split("&&", 1)
    after = after.strip()
    if not after.startswith("{"):
        return None
    try:
        return json.loads(after)
    except Exception:
        return None


def _collect_agents(obj, out: list[dict]) -> None:
    """
    Recursively walk payload dict/list and collect dicts that look like agents.
    """
    if isinstance(obj, dict):
        name = obj.get("fullName") or obj.get("name") or obj.get("agentDisplayName")
        brokerage = obj.get("brokerageName")
        phone = obj.get("phoneNumber") or obj.get("clientDisplayablePhoneNumber") or obj.get("phoneUrl")
        profile = obj.get("profileUrl") or obj.get("agentProfileUrl")

        if isinstance(name, str) and name.strip():
            agent = {}
            for k in [
                "fullName", "name", "firstName", "lastName",
                "brokerageName", "jobTitle", "teamName",
                "licenseNumber", "phoneNumber", "clientDisplayablePhoneNumber",
                "phoneUrl", "profileUrl",
                "photoUrl", "photoUrl74x110", "photoUrl120x120",
                "photoUrl150x150", "photoUrl270x360", "photoUrl500x500",
                "quote", "averageRating", "averageRatingForCustomerDisplay",
                "numReviews", "totalDealsInPastYear", "businessMarket",
                "officeCity", "officeState",
                "agentId", "agentFirstName", "agentDisplayName", "agentProfileUrl",
                "imgSrc", "dealCount", "hasPartnerSash", "isPartnerAgent",
            ]:
                if k in obj:
                    agent[k] = obj.get(k)
            if brokerage or phone or profile or ("licenseNumber" in agent) or ("quote" in agent):
                out.append(agent)

        for v in obj.values():
            _collect_agents(v, out)

    elif isinstance(obj, list):
        for item in obj:
            _collect_agents(item, out)


def parse_realtors_from_html(html: str) -> list[dict]:
    """
    Returns a list of agent dicts found in embedded stingray payloads.
    Dedupes by (fullName/name + brokerage + phone).
    """
    candidates: list[dict] = []

    for decoded in _iter_stingray_text_blobs(html):
        payload_obj = _extract_payload_json(decoded)
        if not payload_obj:
            continue
        _collect_agents(payload_obj, candidates)

    # Deduplicate
    seen = set()
    uniq = []
    for a in candidates:
        n = (a.get("fullName") or a.get("name") or a.get("agentDisplayName") or "").strip()
        b = (a.get("brokerageName") or "").strip()
        p = (a.get("clientDisplayablePhoneNumber") or a.get("phoneNumber") or a.get("phoneUrl") or "").strip()
        key = (n.lower(), b.lower(), p)
        if n and key not in seen:
            seen.add(key)
            uniq.append(a)

    return uniq


def pick_primary_realtor(agents: list[dict]) -> dict:
    """
    Heuristic: pick the 'most complete' agent (often has quote + phone + license).
    """
    def score(a: dict) -> int:
        s = 0
        for k in ["fullName", "name", "brokerageName", "clientDisplayablePhoneNumber", "phoneNumber", "licenseNumber", "quote", "profileUrl", "photoUrl150x150"]:
            if a.get(k):
                s += 1
        return s

    if not agents:
        return {}
    return max(agents, key=score)