import requests
import re
from urllib.parse import urljoin


PAGE_URL = "https://www.xbox.com/en-US/games/browse"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    )
}


def main():

    print("================================")
    print("Xbox JavaScript API Discovery")
    print("================================")

    response = requests.get(
        PAGE_URL,
        headers=HEADERS,
        timeout=30,
    )

    print(f"HTTP Status: {response.status_code}")

    response.raise_for_status()

    html = response.text

    # Find JS files
    scripts = re.findall(
        r'<script[^>]+src=["\']([^"\']+)["\']',
        html,
        re.IGNORECASE,
    )

    scripts = list(dict.fromkeys(
        urljoin(PAGE_URL, src)
        for src in scripts
    ))

    print(f"JavaScript files found: {len(scripts)}")
    print()

    interesting = [
        "x-s2s-authorization",
        "emerald.xboxservices.com",
        "xboxcomfd",
        "EncodedCT",
        "ChannelKeyToBeUsedInResponse",
    ]

    found_any = False

    for index, script_url in enumerate(scripts, 1):

        print(
            f"[{index}/{len(scripts)}] "
            f"{script_url}"
        )

        try:

            js_response = requests.get(
                script_url,
                headers=HEADERS,
                timeout=30,
            )

            if js_response.status_code != 200:
                continue

            js = js_response.text

            matches = []

            for keyword in interesting:

                if keyword.lower() in js.lower():
                    matches.append(keyword)

            if not matches:
                continue

            found_any = True

            print("  ✅ MATCH:", ", ".join(matches))

            for keyword in matches:

                pos = js.lower().find(
                    keyword.lower()
                )

                start = max(0, pos - 500)
                end = min(
                    len(js),
                    pos + 1500
                )

                print()
                print(
                    js[start:end]
                )
                print()
                print("-" * 80)

        except Exception as e:

            print(
                f"  ⚠️ Error: {e}"
            )

    print()

    if not found_any:
        print(
            "❌ No relevant API references "
            "found in downloaded scripts."
        )
    else:
        print(
            "✅ Relevant Xbox API code found."
        )


if __name__ == "__main__":
    main()
