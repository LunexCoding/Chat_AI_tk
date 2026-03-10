from customtkinter import CTkButton, CTkFrame, CTkLabel, X

from .BaseWidget import BaseWidget


class Ribbon(BaseWidget):
    def __init__(self, master, title="Chat AI", actions=None, **kwargs):
        super().__init__(master)
        self.frame = CTkFrame(master, **kwargs)

        self.leftFrame = CTkFrame(self.frame, fg_color="transparent")
        self.leftFrame.pack(side="left", fill=X, expand=True, padx=10, pady=10)

        self.titleLabel = CTkLabel(self.leftFrame, text=title, font=("Segoe UI", 18, "bold"))
        self.titleLabel.pack(side="left")

        self.rightFrame = CTkFrame(self.frame, fg_color="transparent")
        self.rightFrame.pack(side="right", padx=10, pady=10)

        self._actions = {}
        if actions:
            for text, command in actions:
                self.addAction(text=text, command=command)

    def addAction(self, text, command=None):
        button = CTkButton(self.rightFrame, text=text, command=command, width=120)
        button.pack(side="left", padx=(6, 0))
        self._actions[text] = button
        return button

    def pack(self, **kwargs):
        self.frame.pack(**kwargs)

    def grid(self, **kwargs):
        self.frame.grid(**kwargs)

    def place(self, **kwargs):
        self.frame.place(**kwargs)
