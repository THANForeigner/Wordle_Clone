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
                        data={"row": r, "col": c},
                        scale=ft.Scale(scale=1),
                        animate_scale=ft.Animation(100, ft.AnimationCurve.EASE_OUT),
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
                box.scale.scale = 1.0
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
                    if c < letter_col: 
                        box.border = ft.border.all(2, ft.Colors.GREY_500)
                        if c == letter_col - 1 and not game_over:
                            box.scale.scale = 1.1
                    elif c == letter_col and not game_over: 
                        box.border = ft.border.all(2, ft.Colors.WHITE)
                        
    async def animate_row_flip(self, row_index: int, hints: list, word: list):
        row_controls = self.board_controls[row_index].controls
        for c in range(WORD_LENGTH):
            box = row_controls[c]
            
            # 1. "Pop" animation (Scale up)
            box.scale.scale = 1.1
            box.update()
            await asyncio.sleep(0.1) 

            # 2. Change color and text mid-animation
            color = HINTS_COLORS.get(hints[c], ft.Colors.BLACK)
            box.bgcolor = color
            box.border = ft.border.all(2, color)
            text_field = box.content
            text_field.value = word[c]
            text_field.bgcolor = color
            if color == HINTS_COLORS[2]: # Yellow
                text_field.text_style.color = ft.Colors.BLACK
            else:
                text_field.text_style.color = ft.Colors.WHITE
            
            # 3. "Pop" animation (Scale down)
            box.scale.scale = 1.0
            box.update()
            
            # Stagger the reveal of the next letter
            await asyncio.sleep(0.2)

    def reset(self):
        for r in range(MAX_GUESS):
            row_controls = self.board_controls[r].controls
            for c in range(WORD_LENGTH):
                box = row_controls[c]
                text_field = box.content
                text_field.value = ""
                box.bgcolor = ft.Colors.BLACK
                box.border = ft.border.all(2, ft.Colors.GREY_700)
                text_field.bgcolor = ft.Colors.BLACK
                text_field.text_style.color = ft.Colors.WHITE
                box.scale.scale = 1
                box.update()