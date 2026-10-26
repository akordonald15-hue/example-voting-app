"""Bounded read-only Robot Shop catalogue traffic. Only loopback port-forward allowed."""
import argparse
import time
import urllib.parse
import urllib.request

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://127.0.0.1:18082")
    parser.add_argument("--requests", type=int, default=60)
    args = parser.parse_args()
    url = urllib.parse.urlsplit(args.url)
    if url.scheme != "http" or url.hostname != "127.0.0.1" or not 1 <= args.requests <= 600:
        raise SystemExit("STOP: loopback only, 1..600 requests")
    success = 0
    for _ in range(args.requests):
        try:
            with urllib.request.urlopen(args.url + "/api/catalogue/products", timeout=5) as response:
                success += int(response.status == 200 and b'sku' in response.read(1024 * 1024))
        except (OSError, ValueError):
            pass
        time.sleep(1)
    print(f"catalogue success={success} attempted={args.requests}")
    if success != args.requests:
        raise SystemExit(1)

if __name__ == "__main__":
    main()
