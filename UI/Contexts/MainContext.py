import os

from customtkinter import CTkButton, CTkFrame, CTkTextbox, BOTH, LEFT, RIGHT, X
from Data.Chat import ChatController, ChatService

from UI.Widgets.FileDrop import FileDrop
from UI.Widgets.Ribbon import Ribbon

from .BaseContext import Context


class MainWindowContext(Context):
    def __init__(self, window, data):
        super().__init__(window, data)
        self.chatService = ChatService()
        self.chatController = ChatController(window, self.chatService)
        self._streamStart = None
        window.title("Main Window")
        window.geometry("980x680")

        self.frame = CTkFrame(window)
        self.frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

        self.ribbon = Ribbon(
            self.frame,
            title="Chat Workspace",
            actions=[
                ("Clear", self._onClearChat),
                ("Exit", self._onButtonExit),
            ],
        )
        self.ribbon.pack(fill=X, pady=(0, 8))

        self.content = CTkFrame(self.frame)
        self.content.pack(fill=BOTH, expand=True)

        self.chatBox = CTkTextbox(self.content)
        self.chatBox.pack(fill=BOTH, expand=True, padx=10, pady=(10, 8))
        self.chatBox.configure(state="disabled")

        self.inputContainer = CTkFrame(self.content)
        self.inputContainer.pack(fill=X, padx=10, pady=(0, 10))

        self.fileDrop = FileDrop(self.inputContainer, onFilesAdded=self._onFilesAdded)
        self.fileDrop.pack(side=LEFT, fill=X, expand=True)

        self.sendButton = CTkButton(self.inputContainer, text="Send", width=120, command=self._onSend)
        self.sendButton.pack(side=RIGHT, padx=(8, 0), pady=10)

        self._appendChat("System", "UI готов. Введите текст или перетащите файлы в поле ввода.")

    def _appendChat(self, role, message):
        self.chatBox.configure(state="normal")
        self.chatBox.insert("end", f"[{role}] {message}\n\n")
        self.chatBox.see("end")
        self.chatBox.configure(state="disabled")

    def _onFilesAdded(self, files):
        # Изменение списка вложений не логируем в чат.
        # Вложения упоминаются только при отправке сообщения.
        return

    def _onSend(self):
        if self.chatController.is_generating:
            return

        message = self.fileDrop.getText()
        files = self.fileDrop.getFiles()

        if not message and not files:
            return

        if message:
            self._appendChat("You", message)

        if files:
            attached = ", ".join(os.path.basename(path) for path in files)
            self._appendChat("You", f"Attachments: {attached}")

        request = self.chatService.build_request(message, files)
        modelPrompt, skippedFiles = request.prompt, request.skipped_files

        if skippedFiles:
            skipped = ", ".join(skippedFiles)
            self._appendChat("System", f"Пропущены нетекстовые вложения: {skipped}")

        self.fileDrop.clearText()
        self.fileDrop.clearFiles()
        self._requestModelResponse(modelPrompt)

    def _requestModelResponse(self, prompt):
        self.sendButton.configure(state="disabled", text="Ожидание...")

        self.chatBox.configure(state="normal")
        self._streamStart = self.chatBox.index("end-1c")
        self.chatBox.mark_set("assistant_stream_start", self._streamStart)
        self.chatBox.mark_gravity("assistant_stream_start", "left")
        self.chatBox.insert("end", "[Assistant] ")
        self.chatBox.see("end")
        self.chatBox.configure(state="disabled")

        started = self.chatController.request_response(
            prompt=prompt,
            on_chunk=self._onModelChunk,
            on_complete=self._onModelComplete,
            on_error=self._onModelError,
        )
        if not started:
            self.sendButton.configure(state="normal", text="Send")

    def _onModelChunk(self, token):
        if not self.chatController.is_generating:
            return
        self.chatBox.configure(state="normal")
        self.chatBox.insert("end", token)
        self.chatBox.see("end")
        self.chatBox.configure(state="disabled")

    def _onModelComplete(self, answer):
        self.sendButton.configure(state="normal", text="Send")

        cleanedAnswer = self.chatService.clean_answer(answer)

        if not cleanedAnswer:
            self.chatBox.configure(state="normal")
            self.chatBox.insert("end", "Не удалось сгенерировать ответ.")
            self.chatBox.see("end")
            self.chatBox.configure(state="disabled")
        elif cleanedAnswer != answer:
            self.chatBox.configure(state="normal")
            self.chatBox.delete("assistant_stream_start", "end")
            self.chatBox.insert("end", f"[Assistant] {cleanedAnswer}")
            self.chatBox.see("end")
            self.chatBox.configure(state="disabled")

        self.chatBox.configure(state="normal")
        self.chatBox.insert("end", "\n\n")
        self.chatBox.see("end")
        self.chatBox.configure(state="disabled")

    def _onModelError(self, errorText):
        self.sendButton.configure(state="normal", text="Send")

        self.chatBox.configure(state="normal")
        self.chatBox.delete("assistant_stream_start", "end")
        self.chatBox.configure(state="disabled")
        self._appendChat("System", f"Ошибка модели: {errorText}")

    def _onClearChat(self):
        self.chatBox.configure(state="normal")
        self.chatBox.delete("1.0", "end")
        self.chatBox.configure(state="disabled")

    def _onButtonExit(self):
        self._window.close()
