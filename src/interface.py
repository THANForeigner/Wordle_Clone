from src.logic import Logic
from src.popup import PopUpWarning, PopUpWindow
import asyncio
import flet as ft
import os
import sys

MAX_GUESS = 6
WORD_LENGTH = 5

KEYBOARD_LAYOUT = [
   "QWERTYUIOP",
    "ASDFGHJKL",
    "ZXCVBNM" 
]

HINTS_COLORS = {
    1: ft.Colors.GREEN_600, 
    2: ft.Colors.YELLOW_600,
    3: ft.Colors.GREY_700 
}

DEFAULT_KEY_COLOR = ft.Colors.BLUE_GREY_600

def get_asset_path(relative_path: str) -> str:
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

  
class Wordle:
    def __init__ (self, page: ft.Page):
        self.page=page
        font_path = get_asset_path(os.path.join("data", "karnakcondensed-normal-700.ttf"))
        page.fonts = {"default" : font_path}
        self.json_file_path = get_asset_path(os.path.join("data", "wordle.json"))
        self.page.title = "Wordle"
        self.page.vertical_alignment = ft.MainAxisAlignment.START
        self.page.scroll = ft.ScrollMode.ADAPTIVE
        self.page.bgcolor = ft.Colors.BLACK
        self.page.on_keyboard_event = self.on_keyboard_event
        self.current_guess_row = 0
        self.current_guess_col = 0
        self.current_letter_col = 0
        self.board_controls = []
        self.keyboard_controls = {}
        self.wordle_logic=Logic(file_path=self.json_file_path)
        self.game_over = False
        self.win = False
        
        self.guesses = list[list[str]]
        self.guesses = [[""] * WORD_LENGTH for _ in range(MAX_GUESS)]
        self.key_statuses = {key: DEFAULT_KEY_COLOR for row in KEYBOARD_LAYOUT for key in row}
        
        self.game_over_window = PopUpWindow(
            title="",
            message="",
            on_restart=self.restart_game_and_close_window,
            on_close=self.close_game_over_window
        )
        
        self.game_warning_window = PopUpWarning (
            title = "Warning",
            message = "",
            on_close=self.close_warning_window
        )
        
        self.main_content = self.create_main_content()
        self.main_content_column = self.create_main_content()
        self.page.add(
            ft.Container(height=30),
            self.main_content_column
        )
        self.page.overlay.append(self.game_over_window)
        self.page.overlay.append(self.game_warning_window)
        self.draw_ui()
    
    def create_board_controls(self):
        self.board_controls = []
        for r in range(MAX_GUESS):
            row_controls = []
            for c in range(WORD_LENGTH):
                text_field = ft.TextField(
                    value = self.guesses[r][c],
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
    
    def update_board_display(self):
        for r in range (MAX_GUESS):
            row_controls = self.board_controls[r].controls
            if r<len(self.wordle_logic.history):
                history_log = self.wordle_logic.history[r]
            else:
                history_log = None
            for c in range(WORD_LENGTH):
                box = row_controls[c]
                text_field_control = box.content 
                text_field_control.value = self.guesses[r][c]
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
                elif r == self.current_guess_row:
                    if c <self.current_guess_col:
                        box.border = ft.border.all(2, ft.Colors.GREY_500)
                    elif c == self.current_letter_col and not self.game_over:
                        box.border = ft.border.all(2, ft.Colors.WHITE)
                
    def create_keyboard_controls(self):
        keyboard_rows = []
        #letter
        for letters in KEYBOARD_LAYOUT:
            row_controls = []
            for letter in letters:
                btn_container = ft.Container(
                    data=letter,
                    width=40,
                    height=50,
                    alignment=ft.alignment.center,
                    bgcolor=self.key_statuses[letter],
                    border_radius=5,
                    content=ft.Text(letter, size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    on_click=self.handle_key_press,
                    ink=True, 
                )
                self.keyboard_controls[letter] = btn_container
                row_controls.append(btn_container)
            keyboard_rows.append(ft.Row(alignment=ft.MainAxisAlignment.CENTER, controls=row_controls, spacing=5))
        
        #Backspace & Enter    
        special_keys_row_controls = []
        special_keys_row_controls.append(self.create_special_key("ENTER", 60, text="ENTER"))
        special_keys_row_controls.extend(keyboard_rows.pop().controls) # Add Z-M keys
        special_keys_row_controls.append(self.create_special_key("BACKSPACE", 60, text="⌫"))
        keyboard_rows.append(ft.Row(alignment=ft.MainAxisAlignment.CENTER, controls=special_keys_row_controls, spacing=5))
        return keyboard_rows
    
    def create_special_key(self, key_name: str, width: int, text: str):
        key_container = ft.Container(
            data=key_name,
            on_click=self.handle_key_press,
            width=width,
            height=50,
            alignment=ft.alignment.center,
            bgcolor=DEFAULT_KEY_COLOR,
            border_radius=5,
            content=ft.Text(text, size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
            ink=True
        )
        return key_container
    
    def on_keyboard_event(self, e: ft.KeyboardEvent):
        if self.game_over or self.game_warning_window.visible or self.game_over_window.visible:
            return
        key = e.key.upper()
        if not self.game_over: 
            if key in KEYBOARD_LAYOUT[0] + KEYBOARD_LAYOUT[1] + KEYBOARD_LAYOUT[2]:
                self.update_ui("key_press", key)
            elif key == "ENTER":
                self.update_ui("key_press", "ENTER")
            elif key == "BACKSPACE":
                self.update_ui("key_press", "BACKSPACE")

    def handle_key_press(self, e: ft.ControlEvent):
        if self.game_over or self.game_warning_window.visible or self.game_over_window.visible:
            return
        key = e.control.data
        if not self.game_over:
            self.update_ui("key_press", key)
    
    def update_keyboard_display(self):
        for letter, color in self.key_statuses.items():
            if letter in self.keyboard_controls:
                self.keyboard_controls[letter].bgcolor = color
                
    def update_ui(self, action: str, key: str = None):
        if self.game_over:
            if self.dialog.open:
                return
        is_input_key = key in KEYBOARD_LAYOUT[0] + KEYBOARD_LAYOUT[1] + KEYBOARD_LAYOUT[2]
        if is_input_key:
            self.wordle_logic.get_letter(key)
        elif key == "BACKSPACE":
            self.wordle_logic.remove_letter()
        elif key == "ENTER":
            self.submit_answer() 
            return
        self.sync_ui_state_with_logic()
        self.update_board_display()
        self.update_keyboard_display()
        self.page.update() 
     
    def sync_ui_state_with_logic(self):
        self.guesses = [[""] * WORD_LENGTH for _ in range(MAX_GUESS)]
        for r, (word, hints) in enumerate(self.wordle_logic.history):
            self.guesses[r] = list(word)
        current_word = self.wordle_logic.get_current_word()
        current_row = len(self.wordle_logic.history)
        if current_row < MAX_GUESS:
            self.guesses[current_row][:len(current_word)] = list(current_word)
            self.current_guess_row = current_row
            self.current_letter_col = len(current_word)
        else:
            self.current_guess_row = MAX_GUESS - 1
            self.current_letter_col = WORD_LENGTH
            self.game_over = True   
    
    def create_main_content(self):
        return ft.Column(
            alignment = ft.MainAxisAlignment.START,
            horizontal_alignment = ft.CrossAxisAlignment.CENTER,
            controls = [
                ft.Text("WORDLE", size=32, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                ft.Column(
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=self.create_board_controls(),
                    spacing=5 
                ),
                ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                ft.Column(
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=self.create_keyboard_controls(),
                    spacing=5
                ),
                ft.Container(height=20)
            ]
        )
                   
    def draw_ui(self):
        self.update_board_display()
        self.update_keyboard_display()   
        self.page.update()
        
    def submit_answer(self):
        hints, is_win, submitted = self.wordle_logic.submit_guess()

        if not submitted:
            current_word = self.wordle_logic.get_current_word()
            if len(current_word) < WORD_LENGTH:
                self.show_warning_dialog("NOT ENOUGH LETTERS!")
            else:
                self.show_warning_dialog("WORD NOT FOUND!")
            return
        else:
            guess_word = self.wordle_logic.history[-1][0]
            for i, (letter, hint) in enumerate( zip ( guess_word, hints ) ):
                flet_color = HINTS_COLORS.get(hint, DEFAULT_KEY_COLOR)
                current_color = self.key_statuses.get(letter)
                if current_color == HINTS_COLORS[1]: 
                    continue
                if flet_color == HINTS_COLORS[1]: 
                    self.key_statuses[letter] = flet_color
                elif flet_color == HINTS_COLORS[2] and current_color != HINTS_COLORS[1]:
                    self.key_statuses[letter] = flet_color
                elif flet_color == HINTS_COLORS[3] and current_color not in (HINTS_COLORS[1], HINTS_COLORS[2]): 
                    self.key_statuses[letter] = flet_color

        self.sync_ui_state_with_logic()
        self.update_board_display()
        self.update_keyboard_display()
        
        if is_win:
            self.game_over = True
            self.win = True
            self.show_game_over_dialog("You Win!", f"Congratulations! You guessed the word in {len(self.wordle_logic.history)}/6 tries.", ft.Colors.GREEN_400)
        elif len(self.wordle_logic.history) >= MAX_GUESS:
            self.game_over = True
            self.show_game_over_dialog("Game Over", f"You ran out of guesses! The word was **{self.wordle_logic.answer}**.", ft.Colors.YELLOW_400)
        else:
            self.page.update()
            
    def restart_game_and_close_window(self, e = None):
        self.wordle_logic = Logic(file_path=self.json_file_path)
        self.current_guess_row = 0
        self.current_guess_col = 0
        self.current_letter_col = 0
        self.guesses = [[""] * WORD_LENGTH for _ in range(MAX_GUESS)]
        self.key_statuses = {key: DEFAULT_KEY_COLOR for row in KEYBOARD_LAYOUT for key in row}
        self.game_over = False
        self.win = False
        self.close_game_over_window(e) 
        self.update_board_display()
        self.update_keyboard_display()
        self.page.update()


    def close_game_over_window(self, e=None):
        self.game_over_window.visible = False
        self.page.update()

    def show_game_over_dialog(self, title: str, message: str, color: ft.Colors):
        self.game_over_window.update_content(title, message, color)
        self.game_over_window.visible = True
        self.page.update()
        async def auto_fade():
            await asyncio.sleep(3)
            if self.game_over_window.visible:
                self.restart_game_and_close_window()
                await self.page.update()
        self.page.run_task(auto_fade)
    
    def close_warning_window(self, e=None):
        self.game_warning_window.visible = False
        self.page.update()

    def show_warning_dialog(self, message: str):
        self.game_warning_window.update_content(message)
        self.game_warning_window.visible = True
        self.page.update()

        async def auto_fade():
            await asyncio.sleep(2)
            if self.game_warning_window.visible:
                self.game_warning_window.visible = False
                await self.page.update()
        self.page.run_task(auto_fade)