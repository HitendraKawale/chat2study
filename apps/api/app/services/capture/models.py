from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class CaptureArtifacts:
    title: str
    final_url: str
    source_url: str
    html_path: Path
    text_path: Path
    screenshot_path: Path
    pdf_path: Path
