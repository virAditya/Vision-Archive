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
        
        # Initialize FilePicker once and add it to the page overlay
        self.file_picker = ft.FilePicker(on_result=self.on_file_result)
        self.page.overlay.append(self.file_picker)
        
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
                ft.Row([
                    self.search_input, 
                    ft.IconButton(ft.icons.SEARCH, on_click=self.handle_search)
                ]),
                ft.Row([
                    ft.ElevatedButton(
                        "Index New Video", 
                        icon=ft.icons.UPLOAD_FILE, 
                        on_click=self.pick_file_dialog
                    ),
                    self.loader,
                    self.status_label
                ]),
                ft.Divider(height=20, color=ft.colors.TRANSPARENT),
                self.results_grid
            ], expand=True)
        )

    def pick_file_dialog(self, e):
        """Opens the system file picker dialog."""
        self.file_picker.pick_files(allow_multiple=False, allowed_extensions=["mp4", "mkv", "avi"])

    def on_file_result(self, e):
        """Handles the result from the file picker. 
        Note: Removed strict type hinting (ft.FilePickerResultEvent) to prevent version conflicts.
        """
        if e.files:
            video_path = e.files[0].path
            video_name = e.files[0].name
            # Run indexing in a background thread to prevent UI freezing
            threading.Thread(
                target=self.index_video, 
                args=(video_path, video_name), 
                daemon=True
            ).start()

    def index_video(self, path, name):
        """Extracts frames, gets embeddings, and saves to database."""
        self.loader.visible = True
        self.status_label.value = f"Processing {name}..."
        self.status_label.color = ft.colors.YELLOW_400
        self.page.update()
        
        # 1. Extract frames
        frames, timestamps = self.engine.get_video_frames(path)
        # 2. Convert frames to vector embeddings
        vectors = self.engine.encode_image_batch(frames)
        # 3. Save to Qdrant DB
        self.db.add_frames(name, path, vectors, timestamps)
        
        self.loader.visible = False
        self.status_label.value = "Indexing Complete!"
        self.status_label.color = ft.colors.GREEN_400
        self.page.update()

    async def handle_search(self, e):
        """Handles the text search query."""
        if not self.search_input.value: 
            return
            
        self.status_label.value = "Searching vectors..."
        self.status_label.color = ft.colors.YELLOW_400
        self.page.update()
        
        # 1. Convert text to vector
        query_vec = self.engine.encode_text(self.search_input.value)
        # 2. Search DB
        results = self.db.search(query_vec)
        
        # 3. Update UI
        self.results_grid.controls.clear()
        for res in results:
            p = res.payload
            self.results_grid.controls.append(
                ResultCard(p['video_name'], p['timestamp'], p['path'], self.play_video)
            )
            
        self.status_label.value = f"Search finished: {len(results)} results"
        self.status_label.color = ft.colors.GREEN_400
        self.page.update()

    def play_video(self, path):
        """Opens the video using the default Windows player."""
        try:
            os.startfile(path)
        except Exception as ex:
            self.status_label.value = f"Error playing video: {ex}"
            self.status_label.color = ft.colors.RED_400
            self.page.update()