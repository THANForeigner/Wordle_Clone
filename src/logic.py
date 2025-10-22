import random
import json
from collections import Counter

CORRECT = 1
PRESENT = 2
ABSENT = 3

class Logic:
    def load_data(self,file_path: str):
        file = open(file_path,"r")
        data=json.load(file)
        return data
    
    @staticmethod
    def get_hidden_word(word_list: list) -> str:
        word=random.choice(word_list).upper()
        print(f"{word}")
        return word
    
    def __init__ (self, file_path: str):
        self.word_list = self.load_data(file_path)
        self.answer=self.get_hidden_word(self.word_list)
        self.max_guesses=6
        self.current_guess=""
        self.history = []
        
    def get_current_word(self) -> str:
        return self.current_guess
    
    def get_remaining_guess(self) -> int:
        return self.max_guesses - len(self.history)
    
    def get_letter(self, letter: str):
        if not letter.isalpha():
            return
        if len(self.current_guess) < len(self.answer):
            self.current_guess += letter.upper()
    
    def remove_letter(self):
        if len(self.current_guess)>0:
            self.current_guess=self.current_guess[:-1]
            
    def compare_word(self) -> list[int]:
        hints = [ABSENT] * len(self.answer)
        guess = self.current_guess
        ans= self.answer
        times_letter_appear = Counter(ans)
        for i in range(len(guess)):
            if guess[i] == ans[i]:
                hints[i] = CORRECT
                times_letter_appear[guess[i]]-=1
        for i in range(len(guess)):
            if(hints[i]!=CORRECT):
                if times_letter_appear.get(guess[i],0)>0:
                    hints[i]=PRESENT
                    times_letter_appear[guess[i]]-=1
        return hints
    
    def submit_guess(self) -> tuple[list[int], bool, bool]: #return hints, win game, accept submit
        if len(self.current_guess) != len(self.answer) or self.current_guess.lower() not in self.word_list:
            return [], False, False
        hints=self.compare_word()
        win = False
        if all(h == CORRECT for h in hints):
            win=True
        self.history.append((self.current_guess, hints))
        self.current_guess=""
        return hints, win, True
    
    def get_max_guess(self) -> int: return self.max_guesses
    def get_ans_length(self) -> int: return len(self.answer)