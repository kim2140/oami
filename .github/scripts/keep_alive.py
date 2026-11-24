"""OAMI Streamlit 앱을 깨워 두는 스크립트.

Streamlit Community Cloud는 12시간 동안 접속이 없으면 앱을 재우고,
단순 HTTP 요청(curl, requests)으로는 앱이 실제로 깨어나지 않습니다.
브라우저에서 자바스크립트가 실행되고 웹소켓이 연결되어야 앱 프로세스가 뜨기 때문에
헤드리스 크롬(Playwright)으로 실제 방문합니다.

성공 기준:
- 앱이 잠들어 있으면 "Yes, get this app back up!" 버튼을 눌러 깨운다.
- 페이지 제목이 Streamlit 기본 껍데기("Streamlit")가 아니라 앱 이름으로 바뀌면 성공.
- 주소가 존재하지 않거나 앱이 뜨지 않으면 0이 아닌 코드로 끝나 워크플로가 실패로 표시된다.
"""

from __future__ import annotations

import sys
import time

from playwright.sync_api import sync_playwright

APP_URL = "https://oamigmscore.streamlit.app/"
SHELL_TITLE = "Streamlit"                      # 앱이 아직 뜨지 않았을 때의 기본 제목
WAKE_BUTTON_NAME = "Yes, get this app back up!"  # 잠든 앱 화면의 깨우기 버튼
LOAD_TIMEOUT_SEC = 240                          # 잠든 앱을 깨우면 1~2분 정도 걸린다


def log(message: str) -> None:
    print(message, flush=True)


def main() -> int:
    with sync_playwright() as p:
        browser = p.chromium.launch(args=["--no-sandbox"])
        context = browser.new_context(
            viewport={"width": 1280, "height": 900},
            locale="ko-KR",
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"
            ),
        )
        page = context.new_page()
        try:
            log(f"접속: {APP_URL}")
            page.goto(APP_URL, wait_until="domcontentloaded", timeout=120_000)
            page.wait_for_timeout(5_000)

            if "errors/not_found" in page.url:
                log(f"실패: 앱 주소를 찾을 수 없습니다. (제목: {page.title()})")
                return 1

            wake = page.get_by_role("button", name=WAKE_BUTTON_NAME)
            if wake.count() > 0:
                log("앱이 잠들어 있습니다. 깨우기 버튼을 누릅니다.")
                wake.first.click()
                page.wait_for_timeout(10_000)

            deadline = time.time() + LOAD_TIMEOUT_SEC
            title = page.title().strip()
            while time.time() < deadline:
                title = page.title().strip()
                if title and title != SHELL_TITLE:
                    break
                page.wait_for_timeout(3_000)

            title = page.title().strip()
            log(f"페이지 제목: {title!r}")
            log(f"현재 주소: {page.url}")

            if not title or title == SHELL_TITLE:
                log(f"실패: {LOAD_TIMEOUT_SEC}초 안에 앱 화면이 뜨지 않았습니다.")
                return 1

            # 화면에 실제 앱 본문이 그려졌는지 한 번 더 확인한다(앱은 iframe 안에 그려진다).
            rendered = False
            for frame in page.frames:
                try:
                    frame.wait_for_selector(
                        '[data-testid="stAppViewContainer"], [data-testid="stApp"]',
                        timeout=5_000,
                    )
                    rendered = True
                    break
                except Exception:
                    continue
            if not rendered:
                log("경고: 앱 이름은 떴지만 본문 영역을 확인하지 못했습니다.")
            else:
                log("앱 본문 확인 완료")

            log("성공: 앱이 깨어 있습니다.")
            return 0
        finally:
            browser.close()


if __name__ == "__main__":
    sys.exit(main())
