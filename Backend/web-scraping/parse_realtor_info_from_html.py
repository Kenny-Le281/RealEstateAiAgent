from playwright.sync_api import sync_playwright

def scrape_agent_links():
    url = "https://www.redfin.ca/on/ottawa/270-W-Lake-Cir-K0A-1L0/home/148910071"

    with sync_playwright() as playwright_instance:
        browser = playwright_instance.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto(url, wait_until="networkidle")

        # Find all <a class="agent-name"> elements
        agent_links = page.locator("a.agent-name")

        results = []
        count = agent_links.count()

        for index in range(count):
            agent_link = agent_links.nth(index)
            agent_name = agent_link.inner_text().strip()
            agent_href = agent_link.get_attribute("href")
            results.append({"text": agent_name, "href": agent_href})

        browser.close()
        return results


if __name__ == "__main__":
    agents = scrape_agent_links()
    print(agents)