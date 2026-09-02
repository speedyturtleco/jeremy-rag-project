"""
keep_app_awake.py
------------------
Visits the live Ask Jeremy Streamlit app and, if it's showing the
"gone to sleep due to inactivity" screen, clicks the wake-up button
and waits for it to come back online.

Run on a schedule via .github/workflows/keep_awake.yml (every ~10 hours,
comfortably under Streamlit Community Cloud's 12-hour sleep threshold).
Doesn't touch Neon or Decodo - just loads the public app URL like a
normal visitor would.
"""

from playwright.sync_api import sync_playwright

APP_URL = "https://ask-jeremy.streamlit.app/"
WAKE_BUTTON_TEXT = "Yes, get this app back up!"


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(APP_URL, timeout=30000)
        page.wait_for_timeout(3000)

        body_text = page.inner_text("body")

        if "gone to sleep" in body_text.lower():
            print("App is asleep - clicking wake button...")
            page.click(f"text={WAKE_BUTTON_TEXT}")
            # Waking can take up to a minute or two.
            for _ in range(6):
                page.wait_for_timeout(20000)
                body_text = page.inner_text("body")
                if "gone to sleep" not in body_text.lower() and "waking up" not in body_text.lower():
                    print("App is back up.")
                    break
            else:
                print("App did not finish waking within the wait window (it may still catch up).")
        else:
            print("App is already awake - a visit like this also resets its inactivity timer.")

        browser.close()


if __name__ == "__main__":
    main()
