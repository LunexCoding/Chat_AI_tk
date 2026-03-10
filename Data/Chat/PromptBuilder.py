import os
from dataclasses import dataclass


@dataclass
class PromptBuildResult:
    prompt: str
    skipped_files: list[str]


class ChatPromptBuilder:
    _MAX_FILE_CHARS = 12000
    _TEXT_EXTENSIONS = {
        ".txt", ".md", ".csv", ".json", ".yaml", ".yml", ".xml", ".html", ".htm",
        ".py", ".js", ".ts", ".tsx", ".jsx", ".java", ".c", ".cpp", ".h", ".hpp",
        ".cs", ".go", ".rs", ".php", ".rb", ".sql", ".ini", ".cfg", ".log",
    }

    @staticmethod
    def _is_text_candidate(file_path: str) -> bool:
        _, ext = os.path.splitext(file_path)
        return ext.lower() in ChatPromptBuilder._TEXT_EXTENSIONS

    @staticmethod
    def _looks_binary(file_path: str) -> bool:
        try:
            with open(file_path, "rb") as file_obj:
                sample = file_obj.read(2048)
        except Exception:
            return False

        if not sample:
            return False
        if b"\x00" in sample:
            return True

        non_text = sum(1 for byte in sample if byte < 9 or (13 < byte < 32))
        return (non_text / len(sample)) > 0.2

    @staticmethod
    def _try_read_text_file(file_path: str) -> tuple[str | None, str | None]:
        for encoding in ("utf-8", "cp1251"):
            try:
                with open(file_path, "r", encoding=encoding) as file_obj:
                    return file_obj.read(ChatPromptBuilder._MAX_FILE_CHARS), None
            except UnicodeDecodeError:
                continue
            except Exception as exc:
                return None, str(exc)

        return None, "Файл не удалось прочитать как текст (utf-8/cp1251)"

    def _read_attached_files(self, files: list[str]) -> dict:
        contents = []
        skipped = []

        for file_path in files:
            file_name = os.path.basename(file_path)
            if not self._is_text_candidate(file_path) or self._looks_binary(file_path):
                skipped.append(file_name)
                continue

            text, error = self._try_read_text_file(file_path)
            if error is not None:
                contents.append(f"[Файл: {file_name}] Ошибка чтения: {error}")
                continue

            if not text.strip():
                contents.append(f"[Файл: {file_name}] Пустой файл")
                continue

            contents.append(f"[Файл: {file_name}]\n{text}")

        return {
            "text": "\n\n".join(contents),
            "skipped": skipped,
            "has_text": bool(contents),
        }

    def build_model_prompt(self, message: str, files: list[str]) -> PromptBuildResult:
        if not files:
            return PromptBuildResult(prompt=message, skipped_files=[])

        read_result = self._read_attached_files(files)
        files_text = read_result["text"]
        skipped_files = read_result["skipped"]

        if message and read_result["has_text"]:
            prompt = (
                "Ответь строго на вопрос пользователя по данным из файлов. "
                "Не придумывай новые вопросы и не продолжай диалог от имени пользователя.\n\n"
                f"Вопрос пользователя:\n{message}\n\n"
                f"Текст из файлов:\n{files_text}"
            )
            return PromptBuildResult(prompt=prompt, skipped_files=skipped_files)

        if message and not read_result["has_text"]:
            prompt = (
                f"{message}\n\n"
                "Примечание: вложения не являются текстовыми, отвечай только по вопросу пользователя."
            )
            return PromptBuildResult(prompt=prompt, skipped_files=skipped_files)

        if read_result["has_text"]:
            prompt = (
                "Ниже дан текст из файлов пользователя. "
                "Сделай краткий ответ по содержимому.\n\n"
                f"{files_text}"
            )
            return PromptBuildResult(prompt=prompt, skipped_files=skipped_files)

        prompt = (
            "Пользователь отправил только нетекстовые вложения без вопроса. "
            "Кратко попроси текстовый вопрос или текстовый файл."
        )
        return PromptBuildResult(prompt=prompt, skipped_files=skipped_files)

    @staticmethod
    def clean_model_answer(answer: str | None) -> str:
        if not answer:
            return ""

        text = answer.replace("\r\n", "\n").strip()

        for prefix in ("Ассистент:", "assistant:", "Ответ ассистента:"):
            if text.startswith(prefix):
                text = text[len(prefix):].strip()

        cut_markers = (
            "\n[Файл:",
            "\nВопрос пользователя:",
            "\nОтвет ассистента:",
            "\nassistant:",
            "\nАссистент:",
        )
        cut_at = -1
        for marker in cut_markers:
            idx = text.find(marker)
            if idx != -1 and (cut_at == -1 or idx < cut_at):
                cut_at = idx

        if cut_at != -1:
            text = text[:cut_at].strip()

        return text
