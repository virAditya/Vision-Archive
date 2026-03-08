import flet as ft
from ui.views import MainView
import os

def main(page: ft.Page):
    # App Window Configuration
    page.title = "CineSearch AI"
    page.theme_mode = ft.ThemeMode.DARK
    page.window_width = 1200
    page.window_height = 900
    page.bgcolor = "#121212"

    # Initialize the Main View
    app_view = MainView(page)
    page.add(app_view.build())

if __name__ == "__main__":
    # Check if DB directory exists locally
    if not os.path.exists("cinesearch_db"):
        os.makedirs("cinesearch_db")
        
    # Start the application
    ft.app(target=main)