# LLM Tree

**Документация:** [🇺🇸 English](../README.md) | [🇷🇺 Русский](RU.md) | [🇩🇪 Deutsch](DE.md) | [🇯🇵 日本語](JA.md) | [🇨🇳 中文](CH.md)

CLI инструмент для подготовки данных проекта для контекста LLM. Генерирует markdown файл с структурой проекта и содержимым исходников.

## Установка

```bash
pip install -e .
```

Или для глобальной установки:
```bash
pip install llmtree
```

## Быстрый старт

```bash
# Обработать текущую директорию
llmtree .

# Обработать конкретную папку
llmtree /path/to/project

# Использовать конкретный профиль
llmtree . -p python

# Настроить профили
llmtree --config
```

## Основные возможности

### Профили
- **default** - универсальный профиль для большинства проектов
- **python** - оптимизирован для Python проектов
- Создание кастомных профилей через интерактивное меню

### Интерактивное использование
При запуске `llmtree .`:
- **Enter** - генерирует файл `4llm.md`
- **Space** - открывает меню настроек

### Настройки профиля
- Паттерны включаемых файлов
- Паттерны исключений
- Включение структуры дерева
- Максимальный размер файла
- Нумерация строк
- Кастомные заголовок и подвал

## Структура конфигурации

Настройки хранятся в `~/.llmtree/config.json`:

```json
{
  "default": {
    "name": "default",
    "include_patterns": ["*.py", "*.js", "*.md"],
    "exclude_patterns": ["node_modules/*", ".git/*"],
    "include_tree": true,
    "max_file_size": 100000,
    "encoding": "utf-8",
    "add_line_numbers": false,
    "include_hidden": false,
    "tree_depth": 3,
    "custom_header": "",
    "custom_footer": ""
  }
}
```

## Примеры использования

### Создание профиля для фронтенда
```bash
llmtree --config
# Выберите "Create new profile"
# Имя: frontend
# Include patterns: *.js,*.jsx,*.ts,*.tsx,*.vue,*.css,*.scss,package.json
# Exclude patterns: node_modules/*,dist/*,build/*
```

### Профиль для документации
```bash
llmtree --config
# Создайте профиль "docs"
# Include patterns: *.md,*.rst,*.txt
# Tree: Yes
# Add line numbers: No
```

## Командная строка

```
usage: llmtree [-h] [-p PROFILE] [-o OUTPUT] [--config] [path]

positional arguments:
  path                  Target directory path (default: current directory)

optional arguments:
  -h, --help           show this help message and exit
  -p, --profile PROFILE Profile to use (default: default)
  -o, --output OUTPUT  Output file name (default: 4llm.md)
  --config             Run interactive configuration
```

## Выходной формат

Генерируемый `4llm.md` включает:
1. Кастомный заголовок (если указан)
2. Структуру проекта (tree)
3. Содержимое исходных файлов с подсветкой синтаксиса
4. Кастомный подвал (если указан)

Пример выхода:
```markdown
## Project Structure

```
.
├── src/
│   ├── main.py
│   └── utils.py
├── tests/
│   └── test_main.py
└── README.md
```

## Source Files

### src/main.py
```python
def main():
    print("Hello, World!")
```

### README.md
```markdown
# My Project
```

## Лицензия

MIT License