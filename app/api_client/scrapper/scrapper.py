from playwright.sync_api import sync_playwright


with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)  # Set headless=True for background
    page = browser.new_page()
    page.goto("https://www.youtube.com/results?search_query=play&sp=EgIQAg%253D%253D")
    channels = page.query_selector_all("ytd-channel-renderer")
    print(f"Found {len(channels)} channels")
    
    for channel in channels:
        channel_name = channel.query_selector("ytd-channel-name")
        if channel_name:
            print(channel_name.inner_text())
            
        subscribers = channel.query_selector("metadata")
        if subscribers:
            print(subscribers.inner_text())
    
    browser.close()

