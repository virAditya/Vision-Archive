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

    # 1. CREATE AND SHOW A LOADING SCREEN FIRST
    loading_text = ft.Text(
        "Downloading & Loading AI Models...\nPlease wait (this takes a few minutes on the first run).", 
        size=20, 
        color=ft.colors.CYAN_400,
        text_align=ft.TextAlign.CENTER
    )
    spinner = ft.ProgressRing(width=50, height=50, stroke_width=5)
    
    loading_view = ft.Column(
        [spinner, loading_text], 
        alignment=ft.MainAxisAlignment.CENTER, 
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )
    
    # Show loading UI
    page.add(ft.Container(content=loading_view, alignment=ft.alignment.center, expand=True))
    page.update()

    # 2. LOAD THE HEAVY AI ENGINE
    app_view = MainView(page)

    # 3. CLEAR LOADING SCREEN AND SHOW THE MAIN APP
    page.controls.clear()
    page.add(app_view.build())
    page.update()

if __name__ == "__main__":
    # Check if DB directory exists locally
    if not os.path.exists("cinesearch_db"):
        os.makedirs("cinesearch_db")
        
    # Start the application using Flet's new standard API
    ft.run(main)