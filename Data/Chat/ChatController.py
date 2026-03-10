import threading


class ChatController:
    def __init__(self, window, chat_service):
        self._window = window
        self._chat_service = chat_service
        self._is_generating = False

    @property
    def is_generating(self):
        return self._is_generating

    def request_response(self, prompt, on_chunk, on_complete, on_error):
        if self._is_generating:
            return False

        self._is_generating = True
        worker = threading.Thread(
            target=self._run_request,
            args=(prompt, on_chunk, on_complete, on_error),
            daemon=True,
        )
        worker.start()
        return True

    def _run_request(self, prompt, on_chunk, on_complete, on_error):
        full_answer = []
        try:
            for token in self._chat_service.stream_answer(prompt):
                full_answer.append(token)
                self._window.after(0, on_chunk, token)

            answer = "".join(full_answer).strip()
            self._window.after(0, self._complete, answer, on_complete)
        except Exception as exc:
            self._window.after(0, self._fail, str(exc), on_error)

    def _complete(self, answer, callback):
        self._is_generating = False
        callback(answer)

    def _fail(self, error_text, callback):
        self._is_generating = False
        callback(error_text)
