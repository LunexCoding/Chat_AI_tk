from dataclasses import dataclass

from Data.LocalChatModel import LocalChatModel

from .PromptBuilder import ChatPromptBuilder


@dataclass
class ChatRequest:
    prompt: str
    skipped_files: list[str]


class ChatService:
    def __init__(self, model=None, prompt_builder=None):
        self._model = model or LocalChatModel()
        self._prompt_builder = prompt_builder or ChatPromptBuilder()

    def build_request(self, message: str, files: list[str]) -> ChatRequest:
        prompt_result = self._prompt_builder.build_model_prompt(message, files)
        return ChatRequest(prompt=prompt_result.prompt, skipped_files=prompt_result.skipped_files)

    def stream_answer(self, prompt: str):
        return self._model.stream_ask(prompt)

    def clean_answer(self, answer: str | None) -> str:
        return self._prompt_builder.clean_model_answer(answer)
