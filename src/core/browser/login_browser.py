from playwright.async_api import async_playwright

async def login_and_get_cookies(url, username, password):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        context = await browser.new_context(ignore_https_errors=True)
        page = await context.new_page()

        await page.goto(url)

        await page.fill('input[type="text"]', username)
        await page.fill('input[type="password"]', password)
        await page.click('button')

        await page.wait_for_load_state("networkidle")

        cookies = await context.cookies()

        await browser.close()

        return cookies