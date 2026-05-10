# -*- coding: utf-8 -*-
"""
remote_gui.py Beispiel
Diese Datei gehört ins GitHub-Repo.

Sie muss enthalten:
    def create_app_screen(context):
        return Screen(...)
"""

from kivy.core.window import Window
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.image import Image


def create_app_screen(context):
    Window.clearcolor = (0.01, 0.02, 0.04, 1)

    screen = Screen()
    box = BoxLayout(orientation="vertical", padding=30, spacing=20)

    png_path = context.get("paths", {}).get("png")

    if png_path:
        box.add_widget(Image(
            source=png_path,
            size_hint_y=None,
            height=300,
            allow_stretch=True,
            keep_ratio=True
        ))

    box.add_widget(Label(
        text="[color=00E6FF][b]MAC ULTRA[/b][/color]\n\nRemote-GUI wurde erfolgreich geladen.",
        markup=True,
        font_size="24sp",
        halign="center"
    ))

    screen.add_widget(box)
    return screen
