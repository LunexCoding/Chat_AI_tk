from customtkinter import CTkLabel, TOP

from Markup import MARCUP, TypesUiMarkups
from .BaseWidget import BaseWidget


class ErrorLabel(BaseWidget):
    def __init__(self, master, **kwargs):
        super().__init__(master)
        self._visibility = False
        self.label = CTkLabel(master, **kwargs)
        self._uiElements.append(MARCUP(element=self.label, type=TypesUiMarkups.PACK, pady=10, padx=10, side=TOP))

    def setText(self, text):
        self.label.configure(text=text)
