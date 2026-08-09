import requests
import re
import json
import base64


URL = "https://www.xbox.com/en-US/games/browse"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    )
}


def try_decode(value):
    """Try to decode a Base64 JSON string."""

    if not isinstance(value, str):
        return None

    try:
        decoded = base64.b64decode(
            value + "=" * (-len(value) % 4)
        ).decode("utf-8")

        data = json.loads(decoded)

        if isinstance(data, dict):
            if (
                "HasMore" in data
                and "SkipCount" in data
                and "TotalCount" in data
            ):
                return data

    except Exception:
        pass

    return None


def find_continuation_tokens(obj, path="root"):
    """Recursively find Xbox continuation tokens."""

    results = []

    if isinstance(obj, dict):

        for key, value in obj.items():

            decoded = try_decode(value)

            if decoded:
                results.append({
                    "path": f"{path}.{key}",
                    "encoded": value,
                    "decoded": decoded,
                })

            results.extend(
                find_continuation_tokens(
                    value,
                    f"{path}.{key}"
                )
            )

    elif isinstance(obj, list):

        for i, value in enumerate(obj):

            results.extend(
                find_continuation_tokens(
                    value,
                    f"{path}[{i}]"
                )
            )

    return results


def main():

    print("================================")
    print("Xbox Continuation Token Test")
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
        raise RuntimeError(
            "PRELOADED_STATE not found"
        )

    state = json.loads(match.group(1))

    print("PRELOADED_STATE parsed")
    print()

    results = find_continuation_tokens(state)

    print(
        f"Continuation tokens found: "
        f"{len(results)}"
    )

    for i, result in enumerate(results, 1):

        print()
        print("=" * 70)
        print(f"TOKEN #{i}")
        print("=" * 70)

        print(f"Path:")
        print(result["path"])

        decoded = result["decoded"]

        print()
        print("Decoded:")
        print(json.dumps(
            decoded,
            indent=2
        )[:5000])

        print()
        print("EncodedCT length:")
        print(len(result["encoded"]))


if __name__ == "__main__":
    main()
