import os
from importlib import import_module
from tkinter import filedialog

from customtkinter import CTkButton, CTkFrame, CTkLabel, CTkTextbox, X

from .BaseWidget import BaseWidget


class FileDrop(BaseWidget):
    def __init__(self, master, onFilesAdded=None, **kwargs):
        super().__init__(master)
        self.frame = CTkFrame(master, **kwargs)
        self._onFilesAdded = onFilesAdded
        self._files = []

        self.textbox = CTkTextbox(self.frame, height=110)
        self.textbox.pack(fill=X, padx=10, pady=(10, 6))

        self.filesList = CTkFrame(self.frame)
        self.filesList.pack(fill=X, padx=10, pady=(0, 6))

        self.footer = CTkFrame(self.frame, fg_color="transparent")
        self.footer.pack(fill=X, padx=10, pady=(0, 10))

        self.infoLabel = CTkLabel(self.footer, text="Перетащите файлы в поле ввода", anchor="w")
        self.infoLabel.pack(side="left", fill=X, expand=True)

        self.clearButton = CTkButton(self.footer, text="Clear Files", width=110, command=self.clearFiles)
        self.clearButton.pack(side="right", padx=(8, 0))

        self.detachButton = CTkButton(self.footer, text="Detach Last", width=110, command=self.removeLastFile)
        self.detachButton.pack(side="right", padx=(8, 0))

        self.attachButton = CTkButton(self.footer, text="Attach", width=110, command=self.pickFiles)
        self.attachButton.pack(side="right")

        self._initDropSupport()
        self._refreshLabel()

    def _initDropSupport(self):
        try:
            windnd = import_module("windnd")
        except ImportError:
            self.infoLabel.configure(text="Drop не активен: установите пакет windnd")
            return

        windnd.hook_dropfiles(self.textbox, func=self._onDropFiles)
        windnd.hook_dropfiles(self.frame, func=self._onDropFiles)

    def _onDropFiles(self, files):
        normalized = []
        for filePath in files:
            if isinstance(filePath, bytes):
                try:
                    filePath = filePath.decode("utf-8")
                except UnicodeDecodeError:
                    filePath = filePath.decode("mbcs", errors="ignore")
            normalized.append(filePath)
        self._addFiles(normalized)

    def _addFiles(self, files):
        added = []
        for filePath in files:
            if os.path.isfile(filePath) and filePath not in self._files:
                self._files.append(filePath)
                added.append(filePath)

        if added and self._onFilesAdded is not None:
            self._onFilesAdded(added)

        self._refreshLabel()

    def _refreshLabel(self):
        if not self._files:
            self.infoLabel.configure(text="Перетащите файлы в поле ввода")
            self.detachButton.configure(state="disabled")
            self.clearButton.configure(state="disabled")
            self._refreshFilesList()
            return

        preview = ", ".join(os.path.basename(path) for path in self._files[:2])
        if len(self._files) > 2:
            preview = f"{preview} +{len(self._files) - 2}"
        self.infoLabel.configure(text=f"Файлы: {preview}")
        self.detachButton.configure(state="normal")
        self.clearButton.configure(state="normal")
        self._refreshFilesList()

    def _refreshFilesList(self):
        for child in self.filesList.winfo_children():
            child.destroy()

        if not self._files:
            return

        for index, filePath in enumerate(self._files):
            row = CTkFrame(self.filesList, fg_color="transparent")
            row.pack(fill=X, pady=2)

            fileName = os.path.basename(filePath)
            fileLabel = CTkLabel(row, text=fileName, anchor="w")
            fileLabel.pack(side="left", fill=X, expand=True)

            removeButton = CTkButton(
                row,
                text="x",
                width=28,
                command=lambda idx=index: self.removeFileAt(idx),
            )
            removeButton.pack(side="right")

    def pickFiles(self):
        filePaths = filedialog.askopenfilenames(parent=self.frame, title="Выберите файлы")
        self._addFiles(list(filePaths))

    def getText(self):
        return self.textbox.get("1.0", "end-1c").strip()

    def clearText(self):
        self.textbox.delete("1.0", "end")

    def getFiles(self):
        return list(self._files)

    def removeLastFile(self):
        if not self._files:
            return
        self._files.pop()
        self._refreshLabel()

    def removeFileAt(self, index):
        if 0 <= index < len(self._files):
            self._files.pop(index)
            self._refreshLabel()

    def clearFiles(self):
        self._files.clear()
        self._refreshLabel()

    def pack(self, **kwargs):
        self.frame.pack(**kwargs)

    def grid(self, **kwargs):
        self.frame.grid(**kwargs)

    def place(self, **kwargs):
        self.frame.place(**kwargs)
