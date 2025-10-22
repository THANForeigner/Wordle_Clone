import flet as ft
import asyncio

MAX_GUESS = 6
WORD_LENGTH = 5

HINTS_COLORS = {
    1: ft.Colors.GREEN_600, 
    2: ft.Colors.YELLOW_600,
    3: ft.Colors.GREY_700 
}

class GridBoard:

    def __init__(self):
        self.board_controls = []
        
    def create_board_controls(self, guesses: list[list[str]]):
            for r in range(MAX_GUESS):
                row_controls = []
                for c in range(WORD_LENGTH):
                    text_field = ft.TextField(
                        value = guesses[r][c],
                        text_align = ft.TextAlign.CENTER,
                        read_only = True,
                        border=ft.InputBorder.NONE, 
                        bgcolor=ft.Colors.BLACK,
                        content_padding=0,
                        text_size=32,
                        text_style=ft.TextStyle(weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                        max_length=1, 
                        cursor_height=0, 
                        cursor_color=ft.Colors.TRANSPARENT,
                    )
                    box_container = ft.Container(
                        width=60, 
                        height=60,
                        content=text_field,
                        alignment=ft.alignment.center,
                        border_radius=3, 
                        border=ft.border.all(2, ft.Colors.GREY_700), 
                        data={"row": r, "col": c}
                    )
                    row_controls.append(box_container)
                self.board_controls.append(ft.Row(alignment=ft.MainAxisAlignment.CENTER, controls=row_controls, spacing=5))
            return self.board_controls
        
    def update_board_display(self, history: list, guesses: list[list[str]], row: int, col: int, letter_col: int, game_over: bool):
        for r in range (MAX_GUESS):
            row_controls = self.board_controls[r].controls
            if r<len(history):
                history_log = history[r]
            else:
                history_log = None
            for c in range(WORD_LENGTH):
                box = row_controls[c]
                text_field_control = box.content 
                text_field_control.value = guesses[r][c]
                box.bgcolor = ft.Colors.BLACK
                box.border = ft.border.all(2, ft.Colors.GREY_700)
                text_field_control.text_style.color = ft.Colors.WHITE
                text_field_control.bgcolor = ft.Colors.BLACK
                if history_log:
                    word, hints = history_log
                    hint = hints[c]
                    color = HINTS_COLORS.get(hint, ft.Colors.BLACK)
                    box.bgcolor = color
                    box.border = ft.border.all(2,color)                 
                    text_field_control.bgcolor = color
                    
                    if color == ft.Colors.YELLOW_600:
                        text_field_control.text_style.color = ft.Colors.BLACK
                    else:
                        text_field_control.text_style.color = ft.Colors.WHITE
                elif r == row:
                    if c < col:
                        box.border = ft.border.all(2, ft.Colors.GREY_500)
                    elif c == letter_col and not game_over:
                        box.border = ft.border.all(2, ft.Colors.WHITE)