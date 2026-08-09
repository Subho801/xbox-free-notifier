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
    print("Xbox Authorization Discovery")
    print("================================")

    response = requests.get(
        PAGE_URL,
        headers=HEADERS,
        timeout=30,
    )

    response.raise_for_status()

    html = response.text

    scripts = re.findall(
        r'<script[^>]+src=["\']([^"\']+)["\']',
        html,
        re.IGNORECASE,
    )

    scripts = list(dict.fromkeys(
        urljoin(PAGE_URL, src)
        for src in scripts
    ))

    print(f"JavaScript files: {len(scripts)}")
    print()

    keywords = [
        "addAuthorization",
        "MsApiVersion",
        "Authorization",
        "x-s2s-authorization",
        "s2s-authorization",
        "getAuthorization",
        "authorizationToken",
        "accessToken",
    ]

    for index, script_url in enumerate(scripts, 1):

        try:

            r = requests.get(
                script_url,
                headers=HEADERS,
                timeout=30,
            )

            if r.status_code != 200:
                continue

            js = r.text

            found = False

            for keyword in keywords:

                positions = [
                    m.start()
                    for m in re.finditer(
                        re.escape(keyword),
                        js,
                        re.IGNORECASE
                    )
                ]

                if not positions:
                    continue

                found = True

                print()
                print("=" * 90)
                print(f"SCRIPT #{index}")
                print(script_url)
                print(f"KEYWORD: {keyword}")
                print(f"OCCURRENCES: {len(positions)}")
                print("=" * 90)

                # Only print the first 5 occurrences
                for position in positions[:5]:

                    start = max(0, position - 1200)
                    end = min(
                        len(js),
                        position + 2500
                    )

                    print()
                    print(js[start:end])
                    print()
                    print("-" * 90)

            if found:
                print()

        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()
