from __future__ import annotations

from pathlib import Path
import re

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright

from app.core.config import settings
from app.services.capture.models import CaptureArtifacts


class BrowserCaptureService:
    def capture_chat(
        self,
        chat_id: str,
        source_url: str,
        capture_strategy: str,
    ) -> CaptureArtifacts:
        chat_dir = settings.local_artifact_staging_dir / chat_id
        chat_dir.mkdir(parents=True, exist_ok=True)

        html_path = chat_dir / "raw.html"
        text_path = chat_dir / "visible_text.txt"
        screenshot_path = chat_dir / "screenshot.png"
        pdf_path = chat_dir / "snapshot.pdf"

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=settings.playwright_headless)

            context_kwargs: dict = {
                "viewport": {"width": 1440, "height": 1600},
            }

            auth_state_path = settings.playwright_auth_state_path
            if capture_strategy == "playwright_authenticated_browser" and auth_state_path.exists():
                context_kwargs["storage_state"] = str(auth_state_path)

            context = browser.new_context(**context_kwargs)
            page = context.new_page()

            # 1. Get to the page and wait only for a stable baseline.
            page.goto(source_url, wait_until="domcontentloaded", timeout=120000)

            try:
                page.wait_for_load_state("load", timeout=15000)
            except PlaywrightTimeoutError:
                pass

            # 2. Try networkidle briefly, but do NOT fail the whole ingest if it never happens.
            try:
                page.wait_for_load_state("networkidle", timeout=5000)
            except PlaywrightTimeoutError:
                pass

            # 3. Give the UI a short settle window.
            page.wait_for_timeout(2000)

            title = page.title() or "Untitled Chat"
            final_url = page.url
            html = page.content()
            visible_text = self._clean_text(page.locator("body").inner_text())

            html_path.write_text(html, encoding="utf-8")
            text_path.write_text(visible_text, encoding="utf-8")

            page.screenshot(
                path=str(screenshot_path),
                full_page=True,
                animations="disabled",
                caret="hide",
                scale="css",
            )

            page.emulate_media(media="screen")
            page.pdf(
                path=str(pdf_path),
                format="A4",
                print_background=True,
                margin={
                    "top": "12mm",
                    "right": "10mm",
                    "bottom": "12mm",
                    "left": "10mm",
                },
            )

            context.close()
            browser.close()

        return CaptureArtifacts(
            title=title,
            final_url=final_url,
            source_url=source_url,
            html_path=html_path,
            text_path=text_path,
            screenshot_path=screenshot_path,
            pdf_path=pdf_path,
        )

    @staticmethod
    def _clean_text(text: str) -> str:
        text = text.replace("\u00a0", " ")
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()
