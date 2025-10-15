from __future__ import annotations

from pathlib import Path


class ThemeLoader:
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.styles_dir = project_root / "src" / "subtitleformatter" / "gui" / "styles"
        self._cache: dict[str, str] = {}

    def load_theme(self, theme_name: str = "default") -> str:
        if theme_name in self._cache:
            return self._cache[theme_name]
        qss_file = self.styles_dir / "themes" / f"{theme_name}.qss"
        if qss_file.exists():
            try:
                content = qss_file.read_text(encoding="utf-8")
                self._cache[theme_name] = content
                return content
            except Exception:
                return ""
        return ""

    def apply_base_style(self, app, theme_name: str = "default") -> None:
        if app:
            app.setStyle(self._get_base_style(theme_name))

    def _get_base_style(self, theme_name: str) -> str:
        config_file = self.styles_dir / "themes" / f"{theme_name}.json"
        if config_file.exists():
            try:
                import json

                with open(config_file, "r", encoding="utf-8") as f:
                    config = json.load(f)
                return config.get("base_style", "Fusion")
            except Exception:
                pass
        return "Fusion"
