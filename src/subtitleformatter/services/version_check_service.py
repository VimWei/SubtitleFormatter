from __future__ import annotations

import json
import os
import urllib.request
from typing import Optional, Tuple

from subtitleformatter.version import compare_version, get_version


class VersionCheckService:
    GITHUB_API_URL = "https://api.github.com/repos/VimWei/SubtitleFormatter/releases/latest"

    def __init__(self) -> None:
        self._latest_version: Optional[str] = None
        self._check_error: Optional[str] = None

    def check_for_updates(self) -> Tuple[bool, str, Optional[str]]:
        try:
            headers = {
                "User-Agent": f"SubtitleFormatter/{get_version()}",
                "Accept": "application/vnd.github+json",
            }
            token = os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")
            if token:
                headers["Authorization"] = f"Bearer {token}"

            req = urllib.request.Request(self.GITHUB_API_URL, headers=headers, method="GET")
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode())
                latest_version = data["tag_name"].lstrip("v")
                self._latest_version = latest_version
                self._check_error = None

                current_version = get_version()
                comparison = compare_version(latest_version)

                if comparison >= 0:
                    return True, "You are using the latest version.", latest_version
                else:
                    return (
                        False,
                        f"New version {latest_version} available. Please visit homepage to update.",
                        latest_version,
                    )

        except urllib.error.URLError as e:
            self._check_error = str(e)
            return (
                False,
                "Failed to check for updates. Please check your internet connection.",
                None,
            )
        except (json.JSONDecodeError, KeyError) as e:
            self._check_error = str(e)
            return False, "Failed to parse update information.", None
        except Exception as e:
            self._check_error = str(e)
            return False, "An error occurred while checking for updates.", None

    def get_latest_version(self) -> Optional[str]:
        return self._latest_version

    def get_last_error(self) -> Optional[str]:
        return self._check_error
