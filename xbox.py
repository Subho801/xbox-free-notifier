import requests
import re
import json


URL = "https://www.xbox.com/en-US/games/browse"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    )
}


def find_keys(obj, wanted, path="root"):
    """Find every occurrence of selected keys recursively."""

    if isinstance(obj, dict):

        for key, value in obj.items():

            if str(key).lower() in wanted:
                print()
                print("=" * 70)
                print(f"FOUND: {key}")
                print(f"PATH:  {path}.{key}")
                print("=" * 70)

                if isinstance(value, (dict, list)):
                    print(json.dumps(value, indent=2)[:5000])
                else:
                    print(value)

            find_keys(value, wanted, f"{path}.{key}")

    elif isinstance(obj, list):

        for i, value in enumerate(obj):
            find_keys(value, wanted, f"{path}[{i}]")


def main():

    print("================================")
    print("Xbox Channel Structure Test")
    print("================================")

    response = requests.get(
        URL,
        headers=HEADERS,
        timeout=30,
    )

    print(f"HTTP Status: {response.status_code}")
    response.raise_for_status()

    match = re.search(
        r'window\.__PRELOADED_STATE__\s*=\s*(\{.*?\});',
        response.text,
        re.DOTALL,
    )

    if not match:
        raise RuntimeError("PRELOADED_STATE not found")

    state = json.loads(match.group(1))

    print("PRELOADED_STATE parsed")

    core2 = state.get("core2", {})

    print()
    print("core2 keys:")
    print(list(core2.keys()))

    # ----------------------------------------
    # channelData
    # ----------------------------------------

    channel_data = core2.get("channelData", {})

    print()
    print("channelData type:", type(channel_data).__name__)

    if isinstance(channel_data, dict):
        print("channelData keys:")
        for key in channel_data.keys():
            print(f"  - {key}")

    # ----------------------------------------
    # channelMetadata
    # ----------------------------------------

    channel_metadata = core2.get("channelMetadata", {})

    print()
    print("channelMetadata type:", type(channel_metadata).__name__)

    if isinstance(channel_metadata, dict):
        print("channelMetadata keys:")
        for key in channel_metadata.keys():
            print(f"  - {key}")

    # ----------------------------------------
    # Search recursively
    # ----------------------------------------

    print()
    print("================================")
    print("Searching for browse/token fields")
    print("================================")

    wanted = {
        "browsetype",
        "channelkey",
        "channelname",
        "encodedct",
        "continuationtoken",
        "productids",
        "productsummaries",
    }

    find_keys(state, wanted)

    print()
    print("================================")
    print("Searching for product fields")
    print("================================")

    wanted_products = {
        "productid",
        "producttitle",
        "title",
        "listprice",
        "msrp",
        "discountpercentage",
    }

    find_keys(core2, wanted_products)


if __name__ == "__main__":
    main()
