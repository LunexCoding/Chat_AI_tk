import os
from pathlib import Path


class LocalChatModel:
    _STOP_MARKERS = (
        "Пользователь:",
        "User:",
        "Вопрос пользователя:",
        "[Файл:",
        "\n[Файл:",
        "Ответ ассистента:",
        "assistant:",
        "</s>",
    )
    _SYSTEM_INSTRUCTION = "Ты полезный ассистент. Дай один короткий ответ и остановись."

    def __init__(self, modelPath=None, nCtx=2048, nGpuLayers=-1):
        baseDir = Path(__file__).resolve().parent
        self.modelPath = str(modelPath or (baseDir / "Models" / "saiga_yandexgpt_8b.Q8_0.gguf"))
        self.nCtx = nCtx
        self.nGpuLayers = nGpuLayers
        self._llm = None

    def _ensureLoaded(self):
        if self._llm is not None:
            return self._llm

        if not os.path.isfile(self.modelPath):
            raise RuntimeError(f"Модель не найдена: {self.modelPath}")

        try:
            from llama_cpp import Llama
        except ImportError as exc:
            raise RuntimeError(
                "Пакет llama-cpp-python не установлен. Установите: pip install llama-cpp-python"
            ) from exc

        self._llm = Llama(model_path=self.modelPath, n_ctx=self.nCtx, n_gpu_layers=self.nGpuLayers, verbose=False)
        return self._llm

    def _buildPrompt(self, userMessage):
        return (
            f"{self._SYSTEM_INSTRUCTION}\n"
            f"Пользователь: {userMessage}\n"
            "Ассистент:"
        )

    def _generationKwargs(self):
        return {
            "max_tokens": 320,
            "temperature": 0.3,
            "top_p": 0.9,
            "top_k": 40,
            "repeat_penalty": 1.2,
            "stop": list(self._STOP_MARKERS),
        }

    def ask(self, userMessage):
        llm = self._ensureLoaded()
        prompt = self._buildPrompt(userMessage)
        result = llm(prompt, **self._generationKwargs())

        text = result["choices"][0]["text"].strip()
        return text or "Не удалось сгенерировать ответ."

    def stream_ask(self, userMessage):
        llm = self._ensureLoaded()
        prompt = self._buildPrompt(userMessage)
        stream = llm(prompt, stream=True, **self._generationKwargs())

        max_marker_len = max(len(marker) for marker in self._STOP_MARKERS)
        pending = ""
        for chunk in stream:
            text = chunk.get("choices", [{}])[0].get("text", "")
            if text:
                pending += text

                cut_at = -1
                for marker in self._STOP_MARKERS:
                    idx = pending.find(marker)
                    if idx != -1 and (cut_at == -1 or idx < cut_at):
                        cut_at = idx

                if cut_at != -1:
                    final_chunk = pending[:cut_at]
                    if final_chunk:
                        yield final_chunk
                    return

                safe_len = len(pending) - max_marker_len
                if safe_len > 0:
                    yield pending[:safe_len]
                    pending = pending[safe_len:]

        if pending:
            yield pending
