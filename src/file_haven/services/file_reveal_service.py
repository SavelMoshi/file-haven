import subprocess
import sys
from pathlib import Path


class FileRevealService:
    """Reveal and select a file in the operating system's file manager."""

    def reveal(self, path: Path) -> bool:
        file_path = path.expanduser().absolute()

        if not file_path.is_file():
            return False

        try:
            if sys.platform == "darwin":
                return self._reveal_on_macos(file_path)

            if sys.platform == "win32":
                subprocess.Popen(
                    [
                        "explorer.exe",
                        "/select,",
                        str(file_path),
                    ]
                )
                return True

            subprocess.run(
                ["xdg-open", str(file_path.parent)],
                check=True,
            )
            return True

        except (
            ImportError,
            OSError,
            subprocess.CalledProcessError,
        ):
            return False

    def _reveal_on_macos(self, path: Path) -> bool:
        from AppKit import NSWorkspace

        workspace = NSWorkspace.sharedWorkspace()

        selected = workspace.selectFile_inFileViewerRootedAtPath_(
            str(path),
            str(path.parent),
        )

        if selected:
            return True

        subprocess.run(
            ["open", "-R", str(path)],
            check=True,
        )

        return True
