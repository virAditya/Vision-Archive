import flet as ft
import os
import threading
from core.processor import VisionEngine
from core.database import VectorDB
from ui.components import ResultCard

class MainView:
    def __init__(self, page: ft.Page):
        self.page = page
        self.engine = VisionEngine()
        self.db = VectorDB()
        
        # UI State Elements
        self.search_input = ft.TextField(
            label="Search for scenes (e.g., 'a person drinking coffee')", 
            expand=True,
            on_submit=self.handle_search
        )
        self.results_grid = ft.GridView(expand=1, runs_count=5, max_extent=300, spacing=15)
        self.status_label = ft.Text("System Ready", color=ft.colors.GREEN_400)
        self.loader = ft.ProgressRing(visible=False)

    def build(self):
        """Returns the main UI layout."""
        return ft.Container(
            padding=30,
            content=ft.Column([
                ft.Row([
                    ft.Text("CineSearch", size=40, weight="bold", color=ft.colors.CYAN_400),
                    ft.Text("Desktop AI", size=15, italic=True)
                ], alignment=ft.MainAxisAlignment.CENTER),
                ft.Row([self.search_input, ft.IconButton(ft.icons.SEARCH, on_click=self.handle_search)]),
                ft.Row([
                    ft.ElevatedButton("Index New Video", icon=ft.icons.UPLOAD_FILE, on_click=self.pick_file_dialog),
                    self.loader,
                    self.status_label
                ]),
                ft.Divider(height=20, color=ft.colors.TRANSPARENT),
                self.results_grid
            ], expand=True)
        )

    def pick_file_dialog(self, e):
        # File picker logic for selecting a video
        file_picker = ft.FilePicker(on_result=self.on_file_result)
        self.page.overlay.append(file_picker)
        self.page.update()
        file_picker.pick_files(allow_multiple=False, allowed_extensions=["mp4", "mkv", "avi"])

    def on_file_result(self, e: ft.FilePickerResultEvent):
        if e.files:
            video_path = e.files[0].path
            video_name = e.files[0].name
            # Run indexing in a background thread to prevent UI freezing
            threading.Thread(target=self.index_video, args=(video_path, video_name), daemon=True).start()

    def index_video(self, path, name):
        self.loader.visible = True
        self.status_label.value = f"Processing {name}..."
        self.page.update()
        
        frames, timestamps = self.engine.get_video_frames(path)
        vectors = self.engine.encode_image_batch(frames)
        self.db.add_frames(name, path, vectors, timestamps)
        
        self.loader.visible = False
        self.status_label.value = "Indexing Complete!"
        self.page.update()

    async def handle_search(self, e):
        if not self.search_input.value: return
        self.status_label.value = "Searching vectors..."
        self.page.update()
        
        query_vec = self.engine.encode_text(self.search_input.value)
        results = self.db.search(query_vec)
        
        self.results_grid.controls.clear()
        for res in results:
            p = res.payload
            self.results_grid.controls.append(
                ResultCard(p['video_name'], p['timestamp'], p['path'], self.play_video)
            )
        self.status_label.value = f"Search finished: {len(results)} results"
        self.page.update()

    def play_video(self, path):
        """Opens the video using the default Windows player."""
        # This will trigger the default app associated with .mp4 (usually Media Player)
        os.startfile(path)