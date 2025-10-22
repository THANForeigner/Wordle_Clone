from src.popup import PopUpWarning, PopUpWindow
from src.board import HINTS_COLORS
import flet as ft

KEYBOARD_LAYOUT = [
   "QWERTYUIOP",
    "ASDFGHJKL",
    "ZXCVBNM" 
]

DEFAULT_KEY_COLOR = ft.Colors.BLUE_GREY_600

class Keyboard:
    def __init__(self, key_press_handler):
        self.key_press_handler = key_press_handler 
        self.keyboard_controls = {}
        #self.key_statuses = {key: DEFAULT_KEY_COLOR for row in KEYBOARD_LAYOUT for key in row}
    
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
                    bgcolor=DEFAULT_KEY_COLOR,
                    border_radius=5,
                    content=ft.Text(letter, size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    on_click=self.key_press_handler,
                    ink=True, 
                )
                self.keyboard_controls[letter] = btn_container
                row_controls.append(btn_container)
            keyboard_rows.append(ft.Row(alignment=ft.MainAxisAlignment.CENTER, controls=row_controls, spacing=5))
        
        #Backspace & Enter    
        special_keys_row_controls = []
        special_keys_row_controls.append(self.create_special_key("ENTER", 60, text="ENTER"))
        special_keys_row_controls.extend(keyboard_rows.pop().controls) # Add Z-M keys
        special_keys_row_controls.append(self.create_special_key("BACKSPACE", 60, text="BACKSPACE"))
        keyboard_rows.append(ft.Row(alignment=ft.MainAxisAlignment.CENTER, controls=special_keys_row_controls, spacing=5))
        return keyboard_rows  
    
    def create_special_key(self, key_name: str, width: int, text: str):
        key_container = ft.Container(
            data=key_name,
            on_click=self.key_press_handler,
            width=width,
            height=50,
            alignment=ft.alignment.center,
            bgcolor=DEFAULT_KEY_COLOR,
            border_radius=5,
            content=ft.Text(text, size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
            ink=True
        )
        self.keyboard_controls[key_name] = key_container
        return key_container
    
    def setAnswerState(self, lst: list[tuple[str, str]]):
        for (boxColor, char) in lst:
            char_upper = char.upper() 
            t = self.keyboard_controls.get(char_upper)
            if not t:
                continue
            if t.bgcolor == HINTS_COLORS[1]:
                continue       
            t.bgcolor = boxColor
            t.update()
            
    def reset(self):
        for key, control in self.keyboard_controls.items():
            control.bgcolor = DEFAULT_KEY_COLOR
            control.update()