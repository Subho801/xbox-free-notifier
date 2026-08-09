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

KEYWORDS = [
    "Search/GetMoreData",
    "Search/GetInitialChannelData",
    "ChannelKeyToBeUsedInResponse",
    "EncodedCT",
    "ChannelId",
    "addAuthorization",
    "RequestFactory"
]


def main():
    print("================================")
    print("Xbox Emerald Request Discovery")
    print("================================")

    page = requests.get(
        PAGE_URL,
        headers=HEADERS,
        timeout=30
    )
    page.raise_for_status()

    scripts = re.findall(
        r'<script[^>]+src=["\']([^"\']+)["\']',
        page.text,
        re.I
    )

    scripts = list(dict.fromkeys(
        urljoin(PAGE_URL, x)
        for x in scripts
    ))

    print(f"JavaScript files: {len(scripts)}")

    for number, url in enumerate(scripts, 1):

        try:
            r = requests.get(
                url,
                headers=HEADERS,
                timeout=30
            )

            if r.status_code != 200:
                continue

            js = r.text

            matches = []

            for keyword in KEYWORDS:
                for m in re.finditer(
                    re.escape(keyword),
                    js,
                    re.I
                ):
                    matches.append((m.start(), keyword))

            if not matches:
                continue

            print()
            print("=" * 100)
            print(f"SCRIPT #{number}")
            print(url)
            print("=" * 100)

            # Deduplicate nearby matches
            positions = []
            seen = set()

            for pos, keyword in sorted(matches):

                bucket = pos // 3000

                if bucket in seen:
                    continue

                seen.add(bucket)
                positions.append((pos, keyword))

            for pos, keyword in positions[:15]:

                start = max(0, pos - 5000)
                end = min(len(js), pos + 8000)

                print()
                print(f"KEYWORD: {keyword}")
                print("-" * 100)
                print(js[start:end])
                print("-" * 100)

        except Exception as e:
            print(f"ERROR {url}: {e}")


if __name__ == "__main__":
    main()
