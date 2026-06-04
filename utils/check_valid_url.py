import asyncio
import requests
import pandas as pd
from playwright.async_api import async_playwright

# check using requests ---
def fast_check(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    try:
        resp = requests.get(url, headers=headers, allow_redirects=True, timeout=10)
        return resp.status_code < 400
    except requests.exceptions.RequestException:
        return False


# check using Playwright (for JS/anti-bot sites) ---
async def playwright_check(url):
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            page.set_default_timeout(15000)
            try:
                await page.goto(url, wait_until="networkidle", timeout=15000)
                await page.wait_for_timeout(2000)  # give JS redirects a chance
                status = page.response.status if page.response else 200
            except Exception:
                status = None
            await browser.close()
            return status is not None and status < 400
    except Exception:
        return False


# try requests first, fallback to Playwright if False ---
async def check_url(url):
    if fast_check(url):
        return True
    return await playwright_check(url)


async def check_urls(input_csv, output_csv):
    df = pd.read_csv(input_csv)
    urls = df["Data broker primary website:"].dropna().tolist()

    results = []

    for url in urls:
        url = url.strip()
        print(f"Checking {url} ...")

        status = await check_url(url)

        # If failed, immediately re-check once
        if status is False:
            print(f"Initial check failed. Rechecking {url} ...")
            status = await check_url(url)

        results.append({
            "url": url,
            "status": status
        })

        print(f" → final status: {status}")

    out_df = pd.DataFrame(results)
    out_df.to_csv(output_csv, index=False)

    print(f"\n✅ Done! Results saved to {output_csv}")

if __name__ == "__main__":
    input_file = "input_data/unique_primary_websites.csv"
    output_file = "input_data/unique_primary_websites_verified.csv"
    asyncio.run(check_urls(input_csv=input_file, output_csv=output_file))

