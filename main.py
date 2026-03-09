import flet as ft
from ui.views import MainView


def main(page: ft.Page):
    page.title = "Vision Archive"
    page.window.width = 1400
    page.window.height = 850
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = ft.Colors.BLUE_GREY_900

    app = MainView(page)
    page.add(app.build())


ft.app(main)