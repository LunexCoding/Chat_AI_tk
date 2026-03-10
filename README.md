# Chat_AI_tk

Приложение на `customtkinter` для локального чата с `llama-cpp-python`.

## Быстрый запуск

1. Создайте и активируйте виртуальное окружение:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Установите зависимости:

```powershell
pip install customtkinter llama-cpp-python windnd
```

3. Запустите приложение:

```powershell
python main.py
```

## Смена модели

По умолчанию модель берется из:

`Data/Models/saiga_yandexgpt_8b.Q8_0.gguf`

### Вариант 1: заменить файл по умолчанию

Положите новый `.gguf` в `Data/Models/` и в `Data/LocalChatModel.py` поменяйте путь в конструкторе `Data/LocalChatModel`.

### Вариант 2: передать путь явно в коде

В `UI/Contexts/MainContext.py` можно создать сервис с нужной моделью так:

```python
from Data.LocalChatModel import LocalChatModel
from Data.Chat import ChatService

model = LocalChatModel(modelPath=r"F:\\Models\\my_model.gguf", nCtx=4096, nGpuLayers=-1)
self.chatService = ChatService(model=model)
```

Где:
- `modelPath` - путь к `.gguf`
- `nCtx` - размер контекста
- `nGpuLayers=-1` - попытка загрузить все слои на GPU (для CPU: `0`)
