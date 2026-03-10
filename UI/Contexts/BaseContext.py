class ContextTypes:
    INPUT = 0
    EDIT = 1
    INFO = 2


class Context:
    def __init__(self, window, data):
        self._window = window
        self._data = data

    def clear(self):
        for widget in self._window.winfo_children():
            widget.destroy()
        self._window = None
