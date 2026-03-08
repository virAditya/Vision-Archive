import flet as ft

class ResultCard(ft.Card):
    def __init__(self, video_name, timestamp, path, on_click_play):
        super().__init__()
        # Formatting seconds into MM:SS
        minutes = int(timestamp // 60)
        seconds = int(timestamp % 60)
        
        self.content = ft.Container(
            padding=20,
            content=ft.Column([
                ft.Icon(ft.icons.VIDEOCAM_ROUNDED, size=40, color=ft.colors.CYAN_400),
                ft.Text(video_name, weight=ft.FontWeight.BOLD, size=16, max_lines=1),
                ft.Text(f"Found at {minutes:02d}:{seconds:02d}", color=ft.colors.GREY_400),
                ft.ElevatedButton(
                    "Play in Windows Player", 
                    icon=ft.icons.PLAY_ARROW,
                    on_click=lambda _: on_click_play(path)
                )
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        )