import requests
import re
import json


PAGE_URL = "https://www.xbox.com/en-US/games/browse"
API_URL = "https://emerald.xboxservices.com/xboxcomfd/browse?locale=en-US"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "x-ms-api-version": "1.1",
}


def main():
    print("================================")
    print("Xbox Browse Pagination Test")
    print("================================")

    session = requests.Session()
    session.headers.update(HEADERS)

    # Load Xbox browse page
    response = session.get(PAGE_URL, timeout=30)
    response.raise_for_status()

    print("✅ Xbox page loaded")

    # Extract PRELOADED_STATE
    match = re.search(
        r"window\.__PRELOADED_STATE__\s*=\s*(\{.*?\});",
        response.text,
        re.DOTALL,
    )

    if not match:
        print("❌ PRELOADED_STATE not found")
        return

    state = json.loads(match.group(1))

    print("✅ PRELOADED_STATE parsed")

    # Locate browse channel
    channel_data = (
        state["core2"]
        ["channels"]
        ["channelData"]
    )

    channel_key = "BROWSE_CHANNELID=_FILTERS="

    if channel_key not in channel_data:
        print("❌ Browse channel not found")
        print("Available channels:")
        print(list(channel_data.keys()))
        return

    channel = channel_data[channel_key]

    encoded_ct = channel["data"]["encodedCT"]

    print("Channel:", channel_key)
    print("Token length:", len(encoded_ct))

    # Request next page
    payload = {
        "Filters": channel["data"].get("encodedFilters", "e30="),
        "ReturnFilters": False,
        "ChannelKeyToBeUsedInResponse": channel_key,
        "EncodedCT": encoded_ct,
    }

    print()
    print("Requesting next page...")

    api_response = session.post(
        API_URL,
        json=payload,
        timeout=30,
    )

    print("HTTP Status:", api_response.status_code)

    print("Response:")
    print(api_response.text[:5000])

    api_response.raise_for_status()

    data = api_response.json()

    print()
    print("✅ JSON parsed")

    print("Top-level keys:")
    print(list(data.keys()))


if __name__ == "__main__":
    main()
