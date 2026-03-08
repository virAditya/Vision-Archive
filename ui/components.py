import flet as ft

class ResultCard(ft.Card):
    def __init__(self, video_name, timestamp, path, on_click_play):
        super().__init__()
        self.path = path
        self.timestamp = timestamp
        self.content = ft.Container(
            padding=15,
            content=ft.Column([
                ft.Icon(ft.icons.PLAY_CIRCLE_FILL, size=40, color=ft.colors.BLUE_ACCENT),
                ft.Text(video_name, weight=ft.FontWeight.BOLD, max_lines=1),
                ft.Text(f"Timestamp: {int(timestamp // 60):02d}:{int(timestamp % 60):02d}"),
                ft.ElevatedButton("Open Video", on_click=lambda _: on_click_play(path, timestamp))
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        )