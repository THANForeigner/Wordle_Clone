from src.interface import Wordle
import flet as ft

def main(page: ft.Page):
    Wordle(page)

if __name__ == "__main__":
    ft.app(target=main)