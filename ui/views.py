import flet as ft
import os
import asyncio
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

    async def pick_file_dialog(self, e):
        """Opens the system file picker asynchronously (Flet 0.80+ standard)."""
        # Await the new async FilePicker directly
        files = await ft.FilePicker().pick_files(allow_multiple=False, allowed_extensions=["mp4", "mkv", "avi"])
        
        if files:
            video_path = files[0].path
            video_name = files[0].name
            
            # Run the heavy indexing function in a background thread to prevent UI lockup
            asyncio.create_task(asyncio.to_thread(self.index_video, video_path, video_name))

    def index_video(self, path, name):
        """Extracts frames, gets embeddings, and saves to database."""
        self.loader.visible = True
        self.status_label.value = f"Processing {name}..."
        self.status_label.color = ft.colors.YELLOW_400
        self.page.update()
        
        try:
            # 1. Extract frames
            frames, timestamps = self.engine.get_video_frames(path)
            # 2. Convert frames to vector embeddings
            vectors = self.engine.encode_image_batch(frames)
            # 3. Save to Qdrant DB
            self.db.add_frames(name, path, vectors, timestamps)
            
            self.status_label.value = "Indexing Complete!"
            self.status_label.color = ft.colors.GREEN_400
        except Exception as ex:
            self.status_label.value = f"Error: {ex}"
            self.status_label.color = ft.colors.RED_400
            
        self.loader.visible = False
        self.page.update()

    async def handle_search(self, e):
        """Handles the text search query."""
        if not self.search_input.value: 
            return
            
        self.status_label.value = "Searching vectors..."
        self.status_label.color = ft.colors.YELLOW_400
        self.page.update()
        
        try:
            # Run the AI encoding in a background thread
            query_vec = await asyncio.to_thread(self.engine.encode_text, self.search_input.value)
            
            # Search DB
            results = await asyncio.to_thread(self.db.search, query_vec)
            
            # Update UI
            self.results_grid.controls.clear()
            for res in results:
                p = res.payload
                self.results_grid.controls.append(
                    ResultCard(p['video_name'], p['timestamp'], p['path'], self.play_video)
                )
                
            self.status_label.value = f"Search finished: {len(results)} results"
            self.status_label.color = ft.colors.GREEN_400
        except Exception as ex:
            self.status_label.value = f"Search Error: {ex}"
            self.status_label.color = ft.colors.RED_400
            
        self.page.update()

    def play_video(self, path):
        """Opens the video using the default Windows player."""
        try:
            os.startfile(path)
        except Exception as ex:
            self.status_label.value = f"Error playing video: {ex}"
            self.status_label.color = ft.colors.RED_400
            self.page.update()