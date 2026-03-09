import flet as ft
import threading

from core.processor import VisionProcessor
from core.database import VectorDatabase
from ui.components import ResultCard


class MainView:

    def __init__(self, page: ft.Page):
        self.page = page
        self.page.padding = 20

        self._processor = None
        self._database = None

        # FILE PICKER — must append to overlay AND call page.update() immediately
        self.file_picker = ft.FilePicker()
        self.file_picker.on_result = self.on_file_selected
        self.page.overlay.append(self.file_picker)
        self.page.update()  # <-- critical: registers the FilePicker with the renderer

        # UI ELEMENTS
        self.search_box = ft.TextField(
            hint_text="Describe what you're looking for…",
            expand=True,
            border_color=ft.Colors.CYAN_700,
            focused_border_color=ft.Colors.CYAN_300,
            text_style=ft.TextStyle(color=ft.Colors.WHITE),
            on_submit=self.search,
        )

        self.status = ft.Text(
            "Ready — upload a video to begin.",
            color=ft.Colors.BLUE_GREY_300,
            size=13
        )

        self.results = ft.Column(
            scroll=ft.ScrollMode.AUTO,
            expand=True,
            spacing=0
        )

        self.upload_button = ft.ElevatedButton(
            "Upload Video",
            icon=ft.Icons.VIDEO_FILE,
            on_click=self.open_file_picker,
            bgcolor=ft.Colors.CYAN_700,
            color=ft.Colors.WHITE
        )

        self.search_button = ft.ElevatedButton(
            "Search",
            icon=ft.Icons.SEARCH,
            on_click=self.search,
            bgcolor=ft.Colors.INDIGO_600,
            color=ft.Colors.WHITE
        )

        self.progress = ft.ProgressBar(
            visible=False,
            color=ft.Colors.CYAN_400,
            bgcolor=ft.Colors.BLUE_GREY_700
        )

    # ------------------------------------------------------------------ #
    #  Lazy-load heavy models so the window opens instantly               #
    # ------------------------------------------------------------------ #

    @property
    def processor(self):
        if self._processor is None:
            self._set_status("Loading CLIP model…")
            self._processor = VisionProcessor()
        return self._processor

    @property
    def database(self):
        if self._database is None:
            self._database = VectorDatabase()
        return self._database

    # ------------------------------------------------------------------ #
    #  Layout                                                             #
    # ------------------------------------------------------------------ #

    def build(self):
        header = ft.Text(
            "Vision Archive",
            size=28,
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.CYAN_300
        )

        toolbar = ft.Row(
            controls=[
                self.upload_button,
                self.search_box,
                self.search_button,
            ],
            spacing=10
        )

        return ft.Column(
            controls=[
                header,
                ft.Divider(color=ft.Colors.BLUE_GREY_700),
                toolbar,
                self.progress,
                self.status,
                ft.Divider(color=ft.Colors.BLUE_GREY_800),
                ft.Container(content=self.results, expand=True),
            ],
            expand=True,
            spacing=10
        )

    # ------------------------------------------------------------------ #
    #  Helpers                                                            #
    # ------------------------------------------------------------------ #

    def _set_status(self, msg: str):
        self.status.value = msg
        self.page.update()

    def _set_busy(self, busy: bool):
        self.progress.visible = busy
        self.upload_button.disabled = busy
        self.search_button.disabled = busy
        self.page.update()

    # ------------------------------------------------------------------ #
    #  File picking                                                       #
    # ------------------------------------------------------------------ #

    def open_file_picker(self, e):
        self.file_picker.pick_files(
            allow_multiple=False,
            allowed_extensions=["mp4", "avi", "mov", "mkv", "webm"]
        )

    def on_file_selected(self, e):
        if not e.files:
            return
        video_path = e.files[0].path
        threading.Thread(
            target=self.index_video,
            args=(video_path,),
            daemon=True
        ).start()

    # ------------------------------------------------------------------ #
    #  Indexing                                                           #
    # ------------------------------------------------------------------ #

    def index_video(self, path: str):
        self._set_busy(True)
        try:
            self._set_status("Extracting frames…")
            frames, timestamps = self.processor.extract_frames(path)

            if not frames:
                self._set_status("⚠️  No frames extracted — is the file a valid video?")
                return

            self._set_status(f"Encoding {len(frames)} frames…")
            embeddings = self.processor.encode_images(frames)

            self.database.add_embeddings(embeddings, path, timestamps)
            self._set_status(f"✅  Indexed {len(frames)} frames from \"{path}\"")

        except Exception as exc:
            self._set_status(f"❌  Error: {exc}")
        finally:
            self._set_busy(False)

    # ------------------------------------------------------------------ #
    #  Searching                                                          #
    # ------------------------------------------------------------------ #

    def search(self, e):
        query = self.search_box.value.strip()
        if not query:
            return
        threading.Thread(
            target=self.run_search,
            args=(query,),
            daemon=True
        ).start()

    def run_search(self, query: str):
        self._set_busy(True)
        try:
            self._set_status("Searching…")
            vector = self.processor.encode_text(query)
            results = self.database.search(vector)

            self.results.controls.clear()

            if not results:
                self.results.controls.append(
                    ft.Text("No results found.", color=ft.Colors.BLUE_GREY_400)
                )
            else:
                for r in results:
                    video = r.payload["video"]
                    timestamp = r.payload["timestamp"]
                    score = getattr(r, "score", None)
                    card = ResultCard(video, timestamp, score).build()
                    self.results.controls.append(card)

            self._set_status(f"✅  {len(results)} result(s) for \"{query}\"")

        except Exception as exc:
            self._set_status(f"❌  Search error: {exc}")
        finally:
            self._set_busy(False)