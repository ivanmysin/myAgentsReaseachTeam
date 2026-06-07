# `.opencode/` — конфигурация литературного агента

Универсальный научный ИИ-ассистент, работающий с локальной Zotero-библиотекой пользователя. Не привязан к конкретной дисциплине — специализация задаётся в `user_profile.md`.

## Структура

```
.opencode/
├── user_profile.md            # Специализация, языки, журналы, формат вывода
├── prompts/
│   └── Sophia.txt            # Системный промпт главного агента
├── agents/
│   ├── searcher.md           # Поиск статей в Zotero
│   ├── reader.md             # Глубокое чтение
│   ├── synthesizer.md        # Синтез из конспектов
│   └── writer.md             # Написание финальных текстов
└── skills/                   # Процедуры для типовых задач
    ├── search-strategy/      # Многоканальный поиск в Zotero
    ├── targeted-qa/          # Ответы на конкретные вопросы
    ├── literature-review/    # Полные обзоры литературы
    ├── paper-introduction/   # Введения к статьям
    ├── paper-discussion/     # Обсуждения
    ├── scientific-presentation/  # Marp-презентации
    ├── experiment-protocol/  # Протоколы экспериментов
    └── hypothesis-mining/    # Извлечение гипотез и open questions
```

## Установка и настройка

### 1. Установить Zotero MCP-сервер

Должен быть установлен и настроен пакет `opencode-zotero-mcp` (или эквивалент), предоставляющий инструменты с префиксом `zotero_`. Убедитесь, что он доступен в PATH (либо укажите абсолютный путь в `opencode.json`).

### 2. Настроить специализацию пользователя

Отредактируйте `.opencode/user_profile.md`:
- `primary field` / `subfields` — для подстройки контекста поиска
- `preferred journals` — для калибровки стиля
- `working languages` — язык диалога и выходных текстов
- `citation style` — стиль цитирования
- `output conventions` — формат файлов

Если файла нет или он пуст — агент работает в универсальном режиме.

### 3. Проверить MCP-конфигурацию

В `opencode.json` секция `mcp.zotero` указывает на исполняемый файл MCP-сервера. При необходимости поправьте `command` под вашу установку.

```json
"mcp": {
  "zotero": {
    "type": "local",
    "command": ["opencode-zotero-mcp"],
    "enabled": true
  }
}
```

### 4. Запустить opencode

```bash
opencode
```

Переключитесь на агента `Sophia` (через Tab). В начале сессии агент прочитает `user_profile.md` и подстроит поведение.

## Доступные инструменты (Zotero MCP)

Префикс `zotero_`. Все инструменты доступны агентам без дополнительной настройки.

**Поиск:**
- `zotero_search_library` — по метаданным (q, title, yearRange, tag, fulltext, itemType, sort)
- `zotero_search_fulltext` — по полным текстам PDF
- `zotero_fulltext_database` — кэш full-text (list/search/get/stats)
- `zotero_search_annotations` — по пользовательским аннотациям
- `zotero_search_collections` — поиск коллекций

**Чтение:**
- `zotero_get_item_details` — полные метаданные
- `zotero_get_item_abstract` — только абстракт
- `zotero_get_content` — полный текст (preview/standard/complete)
- `zotero_get_annotations` — аннотации статьи
- `zotero_get_collections` — список коллекций
- `zotero_get_collection_details` / `zotero_get_collection_items` / `zotero_get_subcollections`

**Управление коллекциями** (при необходимости):
- `zotero_create_collection` / `zotero_update_collection` / `zotero_delete_collection`
- `zotero_add_items_to_collection` / `zotero_remove_items_from_collection`

## Чего НЕТ по сравнению со старой версией

Следующие функции были в локальной SQLite+ChromaDB базе, но **отсутствуют в Zotero MCP** и удалены:

| Функция | Старая замена | Текущее поведение |
|---|---|---|
| Семантический поиск (embeddings) | `semantic_search` (SPECTER2 + ChromaDB) | Используйте `zotero_search_fulltext` для контекстного поиска по тексту |
| Извлечение рисунков из PDF | `extract_figures` | Пользователь добавляет вручную в `output/figures/<itemKey>/` или как Zotero attachment |
| Кластерный обзор | `cluster_browse` (CSV кластеры) | Используйте `zotero_get_collections` для навигации по пользовательской иерархии коллекций |
| Чанки текста по 3000 слов | `read_article --chunk` | Используйте `zotero_get_content` с `contentControl.maxContentLength` |

## Совместное использование с коллегами

Эта конфигурация намеренно не привязана к конкретной дисциплине. Чтобы поделиться с коллегой из другой области:

1. Скопируйте всю директорию `.opencode/`.
2. Попросите коллегу отредактировать `user_profile.md` под свою специализацию.
3. Убедитесь, что у коллеги настроен Zotero MCP с его библиотекой.

Узко-доменные навыки (например, data-mining для нейронауки) намеренно удалены. Если нужны — создавайте как отдельные доменные skills в поддиректориях `skills/<domain>/SKILL.md`.
