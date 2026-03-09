import os
import subprocess
import platform
import flet as ft


def open_video_at_timestamp(video_path: str, timestamp: float):
    """Open video in the system's default player, seeking to timestamp if possible."""
    system = platform.system()

    try:
        if system == "Windows":
            # Try VLC first (supports --start-time), fall back to default player
            vlc_paths = [
                r"C:\Program Files\VideoLAN\VLC\vlc.exe",
                r"C:\Program Files (x86)\VideoLAN\VLC\vlc.exe",
            ]
            vlc = next((p for p in vlc_paths if os.path.exists(p)), None)

            if vlc:
                subprocess.Popen([
                    vlc, video_path,
                    f"--start-time={int(timestamp)}",
                    "--play-and-exit"
                ])
            else:
                # Fallback: just open with default app (no timestamp seeking)
                os.startfile(video_path)

        elif system == "Darwin":  # macOS
            # Try IINA or VLC, fallback to open
            if os.path.exists("/Applications/IINA.app"):
                subprocess.Popen(["open", "-a", "IINA", video_path,
                                   "--args", f"--mpv-start={int(timestamp)}"])
            elif os.path.exists("/Applications/VLC.app"):
                subprocess.Popen([
                    "/Applications/VLC.app/Contents/MacOS/VLC",
                    video_path, f"--start-time={int(timestamp)}"
                ])
            else:
                subprocess.Popen(["open", video_path])

        else:  # Linux
            subprocess.Popen([
                "vlc", video_path, f"--start-time={int(timestamp)}"
            ])

    except Exception as ex:
        print(f"Could not open video: {ex}")


class ResultCard:

    def __init__(self, video, timestamp, score=None):
        self.video = video
        self.timestamp = timestamp
        self.score = score

    def build(self):
        filename = os.path.basename(self.video)
        score_text = f"  ·  Score: {self.score:.3f}" if self.score is not None else ""

        # Capture values for the closure
        video_path = self.video
        ts = self.timestamp

        def on_click(e):
            open_video_at_timestamp(video_path, ts)

        return ft.Container(
            padding=ft.padding.symmetric(horizontal=16, vertical=12),
            border_radius=10,
            bgcolor=ft.Colors.BLUE_GREY_800,
            border=ft.border.all(1, ft.Colors.BLUE_GREY_600),
            margin=ft.margin.only(bottom=8),
            ink=True,           # shows ripple on click
            on_click=on_click,  # ← makes the card clickable
            on_hover=lambda e: setattr(
                e.control, "bgcolor",
                ft.Colors.BLUE_GREY_700 if e.data == "true" else ft.Colors.BLUE_GREY_800
            ),
            content=ft.Row(
                controls=[
                    ft.Icon(
                        ft.Icons.PLAY_CIRCLE_OUTLINE,
                        color=ft.Colors.CYAN_300,
                        size=28
                    ),
                    ft.Column(
                        spacing=2,
                        expand=True,
                        controls=[
                            ft.Text(
                                filename,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.WHITE,
                                size=14,
                                no_wrap=True,
                                overflow=ft.TextOverflow.ELLIPSIS
                            ),
                            ft.Text(
                                f"⏱  {self.timestamp:.2f}s{score_text}",
                                color=ft.Colors.BLUE_GREY_200,
                                size=12
                            ),
                        ]
                    ),
                    ft.Icon(
                        ft.Icons.OPEN_IN_NEW,
                        color=ft.Colors.BLUE_GREY_400,
                        size=16
                    ),
                ],
                spacing=12
            )
        )