import flet as ft
from ui.views import MainView

def main(page: ft.Page):
    page.title = "CineSearch AI - Desktop"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 20
    page.window_width = 1100
    page.window_height = 850

    # Initialize View
    app_view = MainView(page)
    page.add(app_view.build())

if __name__ == "__main__":
    # Ensure directories exist
    import os
    if not os.path.exists("cinesearch_db"):
        os.makedirs("cinesearch_db")
        
    ft.app(target=main)