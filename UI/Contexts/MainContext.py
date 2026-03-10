from customtkinter import CTkButton, CTkFrame, Y

from .BaseContext import Context



class MainWindowContext(Context):
    def __init__(self, window, data):
        super().__init__(window, data)
        window.title("Main Window")
        self.frame = CTkFrame(window)
        
        self.exitFrame = CTkFrame(self.frame)
        self.buttonExit = CTkButton(self.exitFrame, text="Exit", font=("Arial", 12), command=self._onButtonExit)
        self.buttonExit.pack(padx=10, pady=10)
        self.exitFrame.grid(row=0, column=4, padx=10, pady=10)

        self.frame.pack(fill=Y, padx=10, pady=10)

    def _onButtonExit(self):
        self._window.close()
