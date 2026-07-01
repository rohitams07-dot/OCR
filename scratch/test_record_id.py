import asyncio
from playwright.async_api import async_playwright
import os
from config import CLIENT_URL, CLIENT_USERNAME, CLIENT_PASSWORD

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        print("Navigating to:", CLIENT_URL)
        await page.goto(CLIENT_URL)
        await page.wait_for_load_state("networkidle")
        
        print("Entering Username...")
        await page.fill("#username", CLIENT_USERNAME)
        print("Entering Password...")
        await page.fill("#password", CLIENT_PASSWORD)
        print("Clicking Login...")
        await page.click("#btnLogin")
        await page.wait_for_load_state("networkidle")
        
        # Check MainContent_i100
        locator = page.locator("#MainContent_i100")
        count = await locator.count()
        print("Locator count:", count)
        if count > 0:
            print("Is visible:", await locator.is_visible())
            print("HTML:", await locator.evaluate("el => el.outerHTML"))
        else:
            print("Element not found!")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
