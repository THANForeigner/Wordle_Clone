from src.logic import Logic
from src.popup import PopUpWarning, PopUpWindow
from src.board import GridBoard, HINTS_COLORS, MAX_GUESS, WORD_LENGTH
from src.keyboard import Keyboard, KEYBOARD_LAYOUT, DEFAULT_KEY_COLOR
import asyncio
import flet as ft
import os
import sys

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
        self.board = GridBoard()
        self.wordle_logic=Logic(file_path=self.json_file_path)
        self.game_over = False
        self.win = False
        self.guesses = list[list[str]]
        self.guesses = [[""] * WORD_LENGTH for _ in range(MAX_GUESS)]
        self.keyboard = Keyboard(key_press_handler=self.handle_key_press)
        self.keyboard_controls = self.keyboard.keyboard_controls
        self.key_statuses = self.keyboard.key_statuses
        
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
        
        self.main_content_column = self.create_main_content()
        self.page.add(
            ft.Container(height=30),
            self.main_content_column
        )
        self.page.overlay.append(self.game_over_window)
        self.page.overlay.append(self.game_warning_window)
        self.draw_ui()
    
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
                
    def update_ui(self, action: str, key: str = None):
        is_input_key = key in KEYBOARD_LAYOUT[0] + KEYBOARD_LAYOUT[1] + KEYBOARD_LAYOUT[2]
        if is_input_key:
            self.wordle_logic.get_letter(key)
        elif key == "BACKSPACE":
            self.wordle_logic.remove_letter()
        elif key == "ENTER":
            self.submit_answer() 
            return
        self.sync_ui_state_with_logic()
        self.board.update_board_display(self.wordle_logic.history, self.guesses, self.current_guess_row, self.current_guess_col, self.current_letter_col, self.game_over)
        self.keyboard.update_keyboard_display()
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
                    controls=self.board.create_board_controls(self.guesses),
                    spacing=5 
                ),
                ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                ft.Column(
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=self.keyboard.create_keyboard_controls(),
                    spacing=5
                ),
                ft.Container(height=20)
            ]
        )
                   
    def draw_ui(self):
        self.board.update_board_display(self.wordle_logic.history, self.guesses, self.current_guess_row, self.current_guess_col, self.current_letter_col, self.game_over)
        self.keyboard.update_keyboard_display()   
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
        self.board.update_board_display(self.wordle_logic.history, self.guesses, self.current_guess_row, self.current_guess_col, self.current_letter_col, self.game_over)
        self.keyboard.update_keyboard_display()
        
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
        self.keyboard.key_statuses={key: DEFAULT_KEY_COLOR for row in KEYBOARD_LAYOUT for key in row}
        self.key_statuses = self.keyboard.key_statuses
        self.game_over = False
        self.win = False
        self.close_game_over_window(e) 
        self.board.update_board_display(self.wordle_logic.history, self.guesses, self.current_guess_row, self.current_guess_col, self.current_letter_col, self.game_over)
        self.keyboard.update_keyboard_display()
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