import flet as ft
from core.processor import VisionEngine
from core.database import VectorDB
from ui.components import ResultCard
import os

class MainView:
    def __init__(self, page: ft.Page):
        self.page = page
        self.engine = VisionEngine()
        self.db = VectorDB()
        
        # UI Elements
        self.search_input = ft.TextField(label="Describe what you're looking for...", expand=True)
        self.results_grid = ft.GridView(expand=1, runs_count=5, max_extent=300, spacing=10)
        self.status_text = ft.Text("Ready", color=ft.colors.GREY_400)
        self.progress_bar = ft.ProgressBar(width=400, visible=False)

    def build(self):
        return ft.Column([
            ft.Row([
                ft.Text("CineSearch AI", size=32, weight="bold"),
                ft.Icon(ft.icons.SEARCH_SHARP, size=32)
            ], alignment=ft.MainAxisAlignment.CENTER),
            ft.Divider(),
            ft.Row([
                self.search_input,
                ft.FloatingActionButton(icon=ft.icons.SEARCH, on_click=self.handle_search)
            ]),
            ft.Row([
                ft.ElevatedButton("Index New Video", icon=ft.icons.ADD_TO_DRIVE, on_click=self.handle_indexing),
                self.status_text,
                self.progress_bar
            ]),
            self.results_grid
        ], expand=True)

    async def handle_search(self, e):
        if not self.search_input.value: return
        self.status_text.value = "Searching..."
        self.page.update()
        
        query_vec = self.engine.encode_text(self.search_input.value)
        results = self.db.search(query_vec)
        
        self.results_grid.controls.clear()
        for res in results:
            p = res.payload
            self.results_grid.controls.append(
                ResultCard(p['video_name'], p['timestamp'], p['path'], self.play_video)
            )
        self.status_text.value = f"Found {len(results)} matches"
        self.page.update()

    async def handle_indexing(self, e):
        # File picker logic would go here
        # For this demo, let's assume a hardcoded local file for the flow
        pass 

    def play_video(self, path, timestamp):
        # Use OS command to open video at specific time (VLC example)
        os.system(f'start vlc "{path}" --start-time={int(timestamp)}')