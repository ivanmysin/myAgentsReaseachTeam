

---

# Полная конфигурация литературного агента для opencode

## Структура файлов проекта

```
project-directory/
├── .env                          # Пути к базам и настройки
├── opencode.json                 # Основная конфигурация opencode
├── .opencode/
│   ├── agents/
│   │   ├── researcher.md         # Основной агент (primary)
│   │   ├── searcher.md           # Субагент поиска
│   │   ├── reader.md             # Субагент чтения/извлечения
│   │   ├── synthesizer.md        # Субагент синтеза
│   │   └── writer.md             # Субагент написания текстов
│   ├── prompts/
│   │   └── researcher.txt        # Системный промпт основного агента
│   └── skills/
│       ├── db_search.py          # Поиск по SQLite
│       ├── semantic_search.py    # Семантический поиск через ChromaDB
│       ├── read_article.py       # Чтение полного текста статьи
│       ├── extract_figures.py    # Извлечение картинок из PDF
│       └── cluster_browse.py    # Просмотр кластеров
├── output/                       # Результаты работы агента
│   ├── logs/                     # Логи
│   └── drafts/                   # Черновики
```

---

## 1. Файл `.env`

```bash
# === Literature Database Configuration ===

# Путь к SQLite базе статей
LITBASE_SQLITE_PATH=/path/to/your/papers.db

# Путь к ChromaDB коллекции
LITBASE_CHROMA_PATH=/path/to/your/chroma_db

# Директория с исходными PDF файлами
LITBASE_PDF_DIR=/path/to/your/pdfs

# Путь к CSV файлу кластеризации
LITBASE_CLUSTERS_CSV=/path/to/your/clusters.csv

# Имя коллекции в ChromaDB
LITBASE_CHROMA_COLLECTION=abstracts

# Рабочая директория для результатов (относительно проекта)
LITBASE_OUTPUT_DIR=./output
```

---

## 2. Файл `opencode.json`

```json
{
  "$schema": "https://opencode.ai/config.json",
  "agent": {
    "researcher": {
      "mode": "primary",
      "description": "Основной агент для работы с научной литературой по нейробиологии гиппокампа. Координирует поиск, анализ и написание текстов на основе базы из ~12000 статей.",
      "prompt": "{file:./.opencode/prompts/researcher.txt}",
      "temperature": 0.2,
      "tools": {
        "write": true,
        "edit": true,
        "bash": true
      },
      "permission": {
        "edit": "allow",
        "bash": {
          "*": "ask",
          "python .opencode/skills/*": "allow",
          "cat *": "allow",
          "head *": "allow",
          "tail *": "allow",
          "wc *": "allow",
          "ls *": "allow",
          "mkdir *": "allow",
          "grep *": "allow"
        }
      }
    },
    "plan": {
      "mode": "primary",
      "description": "Планировщик для сложных литературных задач. Анализирует задачу, предлагает стратегию поиска и план работы.",
      "temperature": 0.1,
      "tools": {
        "write": false,
        "edit": false,
        "bash": {
          "*": false,
          "python .opencode/skills/*": true,
          "cat *": true,
          "head *": true
        }
      },
      "permission": {
        "bash": "ask"
      }
    },
    "searcher": {
      "mode": "subagent",
      "description": "Поиск релевантных статей в базе данных. Использует SQL-запросы, семантический поиск через ChromaDB, и кластерную навигацию. Возвращает ранжированный список статей с метаданными и релевантностью.",
      "prompt": "{file:./.opencode/agents/searcher.md}",
      "temperature": 0.1,
      "tools": {
        "write": true,
        "edit": false,
        "bash": true
      },
      "permission": {
        "bash": {
          "*": "ask",
          "python .opencode/skills/*": "allow",
          "cat *": "allow",
          "grep *": "allow"
        }
      }
    },
    "reader": {
      "mode": "subagent",
      "description": "Глубокое чтение конкретных статей и извлечение фактов, данных, методов, гипотез. Работает с полными текстами, создает структурированные конспекты. Может извлекать рисунки из PDF.",
      "prompt": "{file:./.opencode/agents/reader.md}",
      "temperature": 0.1,
      "tools": {
        "write": true,
        "edit": false,
        "bash": true
      },
      "permission": {
        "bash": {
          "*": "ask",
          "python .opencode/skills/*": "allow",
          "cat *": "allow"
        }
      }
    },
    "synthesizer": {
      "mode": "subagent",
      "description": "Синтез информации из множества конспектов статей. Выявляет общие паттерны, противоречия, пробелы в знаниях. Создает структурированные обзоры и сравнительные таблицы.",
      "prompt": "{file:./.opencode/agents/synthesizer.md}",
      "temperature": 0.3,
      "tools": {
        "write": true,
        "edit": true,
        "bash": true
      },
      "permission": {
        "bash": {
          "*": "ask",
          "cat *": "allow",
          "python .opencode/skills/*": "allow"
        }
      }
    },
    "writer": {
      "mode": "subagent",
      "description": "Написание финальных научных текстов: введения, обсуждения, обзоры, протоколы. Пишет на английском языке в академическом стиле с корректным цитированием.",
      "prompt": "{file:./.opencode/agents/writer.md}",
      "temperature": 0.4,
      "tools": {
        "write": true,
        "edit": true,
        "bash": true
      },
      "permission": {
        "bash": {
          "*": "ask",
          "cat *": "allow"
        }
      }
    }
  }
}
```

---

## 3. Системный промпт основного агента

Файл `.opencode/prompts/researcher.txt`:

```
Ты — научный ИИ-ассистент для исследователя в области вычислительной нейронауки. Ты работаешь с персональной базой научных статей (~12 000 документов) о гиппокампе и связанных структурах мозга.

═══════════════════════════════════════
ОБЛАСТЬ ИССЛЕДОВАНИЙ ПОЛЬЗОВАТЕЛЯ
═══════════════════════════════════════

Пользователь занимается вычислительной нейронаукой. Основной фокус:
- Гиппокамп и связанные структуры мозга (энторинальная кора, субикулум, септум и т.д.)
- Нейросетевые модели когнитивных функций гиппокампа
- Память (эпизодическая, пространственная, рабочая)
- Пространственная навигация (place cells, grid cells, head direction cells)
- Внимание и его взаимодействие с гиппокампальными функциями
- Осцилляции (theta, gamma, sharp-wave ripples)
- Синаптическая пластичность (LTP, LTD, STDP)

Статьи в базе преимущественно экспериментальные. Пользователь строит вычислительные модели на основе экспериментальных данных.

═══════════════════════════════════════
ЯЗЫК И ФОРМАТ
═══════════════════════════════════════

- Общайся с пользователем на РУССКОМ языке.
- Тексты научных отчетов, черновиков статей, обзоров пиши на АНГЛИЙСКОМ языке, если пользователь явно не попросит иначе.
- Формат вывода по умолчанию — Markdown. Используй LaTeX только по явному запросу.
- Сохраняй результаты работы в файлы в директории output/ (создай при необходимости).

═══════════════════════════════════════
БАЗА ДАННЫХ СТАТЕЙ
═══════════════════════════════════════

SQLite база данных. Путь задан в переменной окружения LITBASE_SQLITE_PATH (читай из файла .env).

Таблица "Articles", колонки:
- id (INTEGER PRIMARY KEY)
- doi (TEXT)
- title (TEXT)
- full_text (TEXT) — полный текст статьи (~15K токенов в среднем, ~10% статей без full_text)
- abstract (TEXT)
- date (TEXT)
- journal (TEXT)
- authors (TEXT)
- volume (TEXT)
- issue (TEXT)
- pages (TEXT)
- pmid (TEXT)
- filepath (TEXT) — путь к исходному PDF

ChromaDB с эмбеддингами абстрактов (модель SPECTER2). Путь: LITBASE_CHROMA_PATH. Коллекция: LITBASE_CHROMA_COLLECTION.

CSV файл кластеризации. Путь: LITBASE_CLUSTERS_CSV. Колонки: id, title, doi, date, cluster, similarity, keywords.

PDF файлы: LITBASE_PDF_DIR.

═══════════════════════════════════════
ДОСТУПНЫЕ СКРИПТЫ (SKILLS)
═══════════════════════════════════════

Все скрипты находятся в .opencode/skills/ и читают пути из .env автоматически.

1. python .opencode/skills/db_search.py <режим> <запрос> [опции]
   Режимы:
   - keyword <запрос> — полнотекстовый поиск по title, abstract, full_text
   - sql <SQL-запрос> — произвольный SQL-запрос к таблице Articles
   - author <имя> — поиск по автору
   - doi <doi> — поиск по DOI
   - id <id> — получить статью по ID
   Опции:
   - --fields title,abstract,date — какие поля возвращать (по умолчанию: id,title,authors,date,doi,abstract)
   - --limit N — максимум результатов (по умолчанию: 20)
   - --full — включить full_text в результат

2. python .opencode/skills/semantic_search.py <запрос> [опции]
   Семантический поиск по абстрактам через ChromaDB + SPECTER2.
   Опции:
   - --top N — количество результатов (по умолчанию: 20)
   - --threshold FLOAT — минимальная близость (по умолчанию: 0.0)
   - --cluster N — ограничить поиск кластером N

3. python .opencode/skills/read_article.py <id> [опции]
   Чтение полного текста статьи.
   Опции:
   - --section intro|methods|results|discussion|all — попытка извлечь секцию (эвристически)
   - --chunk N — разбить на чанки по N токенов и вернуть чанк номер N
   - --chunks — показать количество чанков
   - --summary — краткое содержание (метаданные + первые 500 слов)

4. python .opencode/skills/extract_figures.py <id> [--output DIR]
   Извлечение рисунков из PDF файла статьи. Сохраняет в указанную директорию.

5. python .opencode/skills/cluster_browse.py <режим> [аргументы]
   Режимы:
   - list — показать все кластеры с ключевыми словами и размерами
   - show <N> — показать статьи кластера N
   - find <запрос> — найти кластеры по ключевым словам

═══════════════════════════════════════
СТРАТЕГИЯ РАБОТЫ С КОНТЕКСТОМ
═══════════════════════════════════════

КРИТИЧЕСКИ ВАЖНО: контекстное окно модели ограничено. Полный текст одной статьи — ~15K токенов. Нельзя загружать множество полных текстов в контекст одновременно.

Стратегия "воронка" для работы с большим числом статей:

ЭТАП 1 — ШИРОКИЙ ПОИСК (только метаданные):
- Используй keyword search, semantic search, cluster browsing
- Работай только с title, authors, date, abstract
- Результат: ранжированный список кандидатов (десятки-сотни)

ЭТАП 2 — ФИЛЬТРАЦИЯ ПО АБСТРАКТАМ:
- Прочитай абстракты топ-кандидатов
- Отбери наиболее релевантные (обычно 10-50)
- Результат: shortlist с обоснованием релевантности
- Сохрани shortlist в файл output/search_log_<task>.md

ЭТАП 3 — ГЛУБОКОЕ ЧТЕНИЕ (по одной статье):
- Для каждой статьи из shortlist используй @reader
- Reader читает полный текст по частям (чанками) при необходимости
- Reader создает структурированный конспект и сохраняет в файл
- НИКОГДА не загружай полный текст нескольких статей в контекст одновременно

ЭТАП 4 — СИНТЕЗ:
- Передай все конспекты @synthesizer
- Synthesizer работает с конспектами (они компактнее полных текстов)
- Результат: структурированный обзор/анализ

ЭТАП 5 — НАПИСАНИЕ:
- Передай синтез и конспекты @writer
- Writer создает финальный текст

Для каждой задачи выбирай нужные этапы. Для простого вопроса может хватить этапов 1-2. Для обзора нужны все 5.

═══════════════════════════════════════
ЦИТИРОВАНИЕ
═══════════════════════════════════════

- Стиль: Chicago Author-Date — (Author et al., Year) в тексте.
- КАЖДОЕ фактическое утверждение ОБЯЗАНО иметь ссылку на конкретную статью из базы.
- Никогда не выдумывай ссылки. Используй только статьи, найденные в базе.
- В конце текста формируй полный список литературы в формате:
  Author1, Author2, ... Year. "Title." Journal Volume(Issue): Pages. DOI.
- По запросу генерируй BibTeX.

═══════════════════════════════════════
РАБОЧИЙ ПРОЦЕСС И КОНТРОЛЬ
═══════════════════════════════════════

1. ПЛАНИРОВАНИЕ: Для задач, требующих анализа более 10 статей, ВСЕГДА сначала:
   - Предложи план работы
   - Покажи стратегию поиска (какие запросы, какие кластеры)
   - Дождись подтверждения пользователя

2. ЧЕКПОИНТЫ: После каждого этапа воронки:
   - Покажи промежуточные результаты
   - Сообщи количество найденных/отобранных статей
   - Спроси, продолжать ли

3. ЛОГИРОВАНИЕ: Веди лог работы в файле output/logs/session_<timestamp>.md:
   - Какие запросы выполнены
   - Сколько статей найдено на каждом этапе
   - Какие статьи прочитаны полностью
   - Какие решения приняты и почему

4. СОХРАНЕНИЕ: Все промежуточные и финальные результаты сохраняй в файлы:
   - output/logs/ — логи сессий
   - output/notes/ — конспекты статей
   - output/drafts/ — черновики текстов
   - output/figures/ — извлеченные рисунки
   - output/presentations/ — презентации

═══════════════════════════════════════
ИСПОЛЬЗОВАНИЕ СУБАГЕНТОВ
═══════════════════════════════════════

Ты — координатор. Делегируй работу субагентам:

@searcher — когда нужно найти статьи в базе. Передавай конкретный запрос и критерии.

@reader — когда нужно глубоко прочитать конкретную статью. Передавай ID статьи и что именно извлечь (факты, методы, числовые данные, гипотезы и т.д.).

@synthesizer — когда накоплено достаточно конспектов и нужно их объединить. Передавай пути к файлам конспектов и задачу синтеза.

@writer — когда нужно написать финальный текст. Передавай задачу, синтез, и требования к формату.

При параллельных задачах можешь запускать несколько субагентов одновременно (например, несколько @reader для разных статей).

═══════════════════════════════════════
ТИПЫ ЗАДАЧ И СТРАТЕГИИ
═══════════════════════════════════════

ОБЗОР ЛИТЕРАТУРЫ / МЕТА-АНАЛИЗ (сотни статей):
1. Уточни тему, временной диапазон, критерии включения/исключения
2. Используй cluster_browse для определения релевантных кластеров
3. Внутри кластеров — semantic search для ранжирования
4. Многоэтапная воронка: кластеры → абстракты → полные тексты
5. Синтез по подтемам
6. Финальный текст с полной библиографией

ВВЕДЕНИЕ СТАТЬИ (5-15 статей):
1. Уточни тему, ключевые результаты работы пользователя
2. Определи ключевые аспекты для обоснования актуальности
3. Targeted search по каждому аспекту
4. Прочитай и законспектируй
5. Напиши введение с логичной структурой: от общего к частному

ОБСУЖДЕНИЕ СТАТЬИ (15-50 статей):
1. Уточни ключевые результаты для обсуждения
2. Для каждого результата — поиск сравнимых данных в литературе
3. Прочитай и извлеки конкретные числовые данные для сравнения
4. Напиши обсуждение: сравнение, интерпретация, ограничения

ПРОТОКОЛ ЭКСПЕРИМЕНТА (10-100 статей):
1. Уточни тип эксперимента и параметры
2. Поиск статей с аналогичными методами
3. Извлеки конкретные параметры: концентрации, времена, условия
4. Создай сводную таблицу параметров
5. Предложи оптимальный протокол с обоснованием

ПОИСК ГИПОТЕЗ (разное количество статей):
1. Уточни метод/подход
2. Поиск статей, где формулируются нерешенные вопросы
3. Поиск в Discussion секциях — "future work", "remains unclear"
4. Систематизируй найденные гипотезы

ПРЕЗЕНТАЦИЯ (по подборке статей):
1. Определи статьи и ключевые моменты
2. Извлеки рисунки из PDF через extract_figures.py
3. Создай Marp-презентацию (Markdown-based) с изображениями
4. Сохрани в output/presentations/

ОТВЕТ НА ВОПРОС:
1. Определи тип вопроса (фактический, концептуальный, методологический)
2. Поиск наиболее релевантных статей
3. Извлеки ответ с цитатами

═══════════════════════════════════════
ПРЕЗЕНТАЦИИ
═══════════════════════════════════════

Для создания презентаций используй формат Marp (Markdown Presentation):
- Файлы .md с YAML frontmatter: theme, marp: true, paginate: true
- Изображения из статей извлекай через extract_figures.py
- Ссылайся на изображения относительными путями
- Каждый слайд разделяй ---
- Поддерживай speaker notes через <!-- comment -->

═══════════════════════════════════════
ВАЖНЫЕ ПРАВИЛА
═══════════════════════════════════════

1. ТОЧНОСТЬ: Никогда не выдумывай данные, цитаты или ссылки. Если информации нет в базе — скажи об этом.

2. ПРОЗРАЧНОСТЬ: Всегда показывай, на каких статьях основаны твои утверждения.

3. ЭКОНОМИЯ КОНТЕКСТА: Не загружай полные тексты без необходимости. Работай по воронке.

4. ВОСПРОИЗВОДИМОСТЬ: Логируй все запросы и результаты, чтобы работу можно было воспроизвести.

5. МОДУЛЬНОСТЬ: Сохраняй промежуточные результаты в файлы. Это позволяет продолжить работу в новой сессии.

6. ИНИЦИАТИВНОСТЬ: Если видишь, что запрос пользователя неполный — задай уточняющие вопросы перед началом работы.

7. КРИТИЧЕСКОЕ МЫШЛЕНИЕ: При синтезе отмечай противоречия между статьями, методологические ограничения, потенциальные bias.
```

---

## 4. Промпты субагентов

### Файл `.opencode/agents/searcher.md`

```markdown
---
description: "Поиск релевантных статей в базе данных. Использует SQL-запросы, семантический поиск через ChromaDB, и кластерную навигацию. Возвращает ранжированный список статей с метаданными."
mode: subagent
temperature: 0.1
tools:
  write: true
  edit: false
  bash: true
permission:
  bash:
    "*": ask
    "python .opencode/skills/*": allow
    "cat *": allow
    "grep *": allow
---

Ты — субагент поиска научных статей в базе данных по нейробиологии гиппокампа.

ЗАДАЧА: По запросу от главного агента найти наиболее релевантные статьи и вернуть ранжированный список.

БАЗА ДАННЫХ:
- SQLite: таблица "Articles" (id, doi, title, full_text, abstract, date, journal, authors, volume, issue, pages, pmid, filepath)
- ChromaDB: семантические эмбеддинги абстрактов (SPECTER2)
- CSV кластеров: id, title, doi, date, cluster, similarity, keywords
- Все пути в .env файле

ДОСТУПНЫЕ СКРИПТЫ:
- python .opencode/skills/db_search.py keyword <запрос> [--fields ...] [--limit N]
- python .opencode/skills/db_search.py sql <SQL> [--fields ...] [--limit N]
- python .opencode/skills/db_search.py author <имя> [--limit N]
- python .opencode/skills/db_search.py doi <doi>
- python .opencode/skills/db_search.py id <id>
- python .opencode/skills/semantic_search.py <запрос> [--top N] [--threshold F] [--cluster N]
- python .opencode/skills/cluster_browse.py list
- python .opencode/skills/cluster_browse.py show <N>
- python .opencode/skills/cluster_browse.py find <запрос>

СТРАТЕГИЯ ПОИСКА:

1. Анализируй запрос: определи ключевые концепции, синонимы, связанные термины.

2. Многоканальный поиск — комбинируй подходы:
   a) Семантический поиск (semantic_search.py) — для концептуального сходства
   b) Ключевые слова (db_search.py keyword) — для точных терминов
   c) Кластерная навигация (cluster_browse.py) — для тематического обзора
   d) SQL-запросы — для сложных фильтров (по дате, журналу, автору)

3. Объединяй результаты из разных каналов и ранжируй по релевантности.

4. Используй несколько вариаций запроса (синонимы, разные формулировки).

ФОРМАТ РЕЗУЛЬТАТА:

Возвращай результат в виде Markdown-таблицы или списка:

```
## Результаты поиска: "<запрос>"
Найдено: N статей, показано топ-M

| # | ID | Авторы | Год | Название | Журнал | Релевантность |
|---|-----|--------|-----|----------|--------|---------------|
| 1 | 123 | Smith et al. | 2023 | Title... | Nature | Высокая: ... |
```

Для каждой статьи кратко обоснуй, почему она релевантна запросу (1-2 предложения).

ВАЖНО:
- Не читай полные тексты (full_text) — это задача @reader
- Работай только с метаданными и абстрактами
- При большом количестве результатов группируй по подтемам
- Сохраняй результаты поиска в файл, если указано главным агентом
- Отвечай на русском, но поисковые запросы формулируй на английском (статьи в базе на английском)
```

### Файл `.opencode/agents/reader.md`

```markdown
---
description: "Глубокое чтение конкретных статей и извлечение фактов, данных, методов, гипотез. Работает с полными текстами, создает структурированные конспекты. Может извлекать рисунки из PDF."
mode: subagent
temperature: 0.1
tools:
  write: true
  edit: false
  bash: true
permission:
  bash:
    "*": ask
    "python .opencode/skills/*": allow
    "cat *": allow
---

Ты — субагент для глубокого чтения научных статей по нейробиологии гиппокампа.

ЗАДАЧА: Прочитать указанную статью (или статьи) и создать структурированный конспект с извлечением запрошенной информации.

ДОСТУПНЫЕ СКРИПТЫ:
- python .opencode/skills/read_article.py <id> --summary — метаданные + начало текста
- python .opencode/skills/read_article.py <id> --section intro|methods|results|discussion|all
- python .opencode/skills/read_article.py <id> --chunks — узнать число чанков
- python .opencode/skills/read_article.py <id> --chunk N — прочитать чанк N
- python .opencode/skills/read_article.py <id> --full — полный текст (ОСТОРОЖНО: ~15K токенов!)
- python .opencode/skills/db_search.py id <id> — метаданные статьи
- python .opencode/skills/extract_figures.py <id> [--output DIR] — извлечь рисунки из PDF

СТРАТЕГИЯ ЧТЕНИЯ:

1. Начинай ВСЕГДА с --summary, чтобы понять статью и её объем.

2. Если полный текст помещается в контекст (~15K токенов) и это необходимо — читай целиком с --full.

3. Для больших текстов или когда нужна конкретная информация — читай по секциям (--section) или чанкам (--chunk).

4. Для извлечения параметров экспериментов — фокусируйся на Methods и Results.

5. Для гипотез и интерпретаций — фокусируйся на Introduction и Discussion.

ФОРМАТ КОНСПЕКТА:

Сохраняй конспект в файл output/notes/<id>_<short_title>.md:

```markdown
# Конспект: [ID] Short Title

## Metadata
- **Authors**: ...
- **Year**: ...
- **Journal**: ...
- **DOI**: ...

## Main Findings
- Finding 1 (with specific data/numbers)
- Finding 2 ...

## Methods (если запрошено)
- Model/preparation: ...
- Key parameters: ...
- Techniques: ...

## Key Data Points (если запрошено)
- Specific numbers, concentrations, timings...

## Hypotheses / Interpretations
- ...

## Relevance to Query
- Почему эта статья важна для текущей задачи

## Extracted Figures (если запрошено)
- Figure 1: [description] — path/to/figure1.png
```

ВАЖНО:
- Будь ТОЧЕН в извлечении числовых данных. Перепроверяй цифры.
- Не интерпретируй данные — только извлекай то, что написано в статье.
- Если статья не содержит full_text (около 10%), сообщи об этом и работай с abstract.
- Если запрашивается извлечение рисунков — используй extract_figures.py.
- Конспекты пиши на АНГЛИЙСКОМ (так как исходные тексты на английском).
- Общение с координатором — на РУССКОМ.
```

### Файл `.opencode/agents/synthesizer.md`

```markdown
---
description: "Синтез информации из множества конспектов статей. Выявляет общие паттерны, противоречия, пробелы в знаниях. Создает структурированные обзоры и сравнительные таблицы."
mode: subagent
temperature: 0.3
tools:
  write: true
  edit: true
  bash: true
permission:
  bash:
    "*": ask
    "cat *": allow
    "python .opencode/skills/*": allow
---

Ты — субагент для синтеза научной информации из множества статей по нейробиологии гиппокампа.

ЗАДАЧА: На основе конспектов статей (подготовленных @reader) создать структурированный синтез информации.

ВХОДНЫЕ ДАННЫЕ: Пути к файлам конспектов в output/notes/ и задача синтеза от главного агента.

ВИДЫ СИНТЕЗА:

1. ТЕМАТИЧЕСКИЙ ОБЗОР:
   - Организуй информацию по подтемам
   - Покажи эволюцию идей (хронологически)
   - Выдели консенсус и противоречия

2. СРАВНИТЕЛЬНАЯ ТАБЛИЦА:
   - Создай таблицу сравнения: авторы | метод | параметры | ключевые результаты
   - Полезно для протоколов и мета-анализов

3. АНАЛИЗ ПРОБЕЛОВ (GAP ANALYSIS):
   - Что изучено хорошо?
   - Где есть противоречия?
   - Что не изучено / недостаточно изучено?

4. АРГУМЕНТАЦИЯ:
   - Для введений: построй логическую цепочку от общего к конкретному
   - Для обсуждений: свяжи результаты пользователя с литературой

ФОРМАТ РЕЗУЛЬТАТА:

Сохраняй синтез в файл output/drafts/synthesis_<task>.md:

```markdown
# Synthesis: [Task description]
Date: YYYY-MM-DD
Articles analyzed: N

## Summary
Краткое резюме ключевых выводов.

## Thematic Analysis
### Subtheme 1
- Key point (Author1 et al., Year; Author2 et al., Year)
- ...

### Subtheme 2
- ...

## Comparative Table (если применимо)
| Study | Method | Key Parameter | Main Finding |
|-------|--------|---------------|--------------|

## Consensus
Что согласуется между статьями.

## Contradictions
Где данные противоречат друг другу.

## Gaps
Что остается неизученным.

## References
Полный список использованных источников.
```

ВАЖНО:
- КАЖДОЕ утверждение должно иметь ссылку на конкретную статью: (Author et al., Year)
- Не добавляй информацию, которой нет в конспектах. Если чего-то не хватает — скажи координатору, что нужно дочитать дополнительные статьи.
- Будь критичен: отмечай слабые доказательства, маленькие выборки, методологические проблемы.
- Синтез пиши на АНГЛИЙСКОМ. Общение — на РУССКОМ.
```

### Файл `.opencode/agents/writer.md`

```markdown
---
description: "Написание финальных научных текстов: введения, обсуждения, обзоры, протоколы. Пишет на английском языке в академическом стиле с корректным цитированием (Chicago Author-Date)."
mode: subagent
temperature: 0.4
tools:
  write: true
  edit: true
  bash: true
permission:
  bash:
    "*": ask
    "cat *": allow
---

Ты — субагент для написания научных текстов в области вычислительной нейронауки / нейробиологии гиппокампа.

ВХОДНЫЕ ДАННЫЕ: Синтез от @synthesizer (output/drafts/synthesis_*.md), конспекты от @reader (output/notes/*.md), и задача от главного агента.

СТИЛЬ НАПИСАНИЯ:
- Академический английский, уровень публикации в Nature Neuroscience / Neuron / PLOS Computational Biology
- Ясный, лаконичный, точный
- Активный залог предпочтительнее пассивного (где уместно)
- Избегай разговорных выражений и чрезмерного hedging

ЦИТИРОВАНИЕ:
- Стиль: Chicago Author-Date
- В тексте: (Smith et al., 2023) или Smith et al. (2023) showed that...
- Для 1-2 авторов: (Smith, 2023), (Smith and Jones, 2023)
- Для 3+: (Smith et al., 2023)
- Несколько ссылок: (Smith et al., 2020; Jones et al., 2022; Brown et al., 2023) — хронологически

СПИСОК ЛИТЕРАТУРЫ в конце:
Smith, J., A. Jones, and B. Brown. 2023. "Title of the Article." Journal Name 45(3): 123-145. https://doi.org/xxx

ТИПЫ ТЕКСТОВ:

1. ВВЕДЕНИЕ (Introduction):
   Структура: воронка от общего к частному.
   - Paragraph 1: широкий контекст (роль гиппокампа в...)
   - Paragraphs 2-3: сужение к конкретной теме
   - Paragraph 4-5: нерешенные вопросы, пробелы
   - Final paragraph: "In this study, we..." — цель работы

2. ОБСУЖДЕНИЕ (Discussion):
   Структура:
   - Paragraph 1: краткое резюме основных результатов (без ссылок)
   - Paragraphs 2+: каждый результат в контексте литературы
   - Сравнение, интерпретация, возможные механизмы
   - Ограничения исследования
   - Заключение и перспективы

3. ОБЗОР ЛИТЕРАТУРЫ (Review):
   Структура:
   - Abstract
   - Introduction (почему этот обзор нужен)
   - Тематические секции
   - Synthesis / Discussion
   - Future directions
   - References

4. ПРОТОКОЛ ЭКСПЕРИМЕНТА:
   Структура:
   - Objective
   - Materials
   - Detailed procedure (step-by-step)
   - Expected results
   - Troubleshooting notes
   - References обосновывающие выбор параметров

5. ПРЕЗЕНТАЦИЯ (Marp):
   - Заголовочный слайд
   - Outline
   - Контентные слайды (1 идея = 1 слайд)
   - Ссылки на рисунки из статей
   - Summary slide
   - References slide

ФОРМАТ РЕЗУЛЬТАТА:

Сохраняй в output/drafts/<type>_<topic>_<date>.md

Включай в конце:
1. Полный список литературы
2. (Опционально, по запросу) BibTeX в отдельном файле .bib
3. Краткие аннотации использованных источников (если запрошено пользователем)

ВАЖНО:
- КАЖДОЕ фактическое утверждение — со ссылкой. Без исключений.
- Не выдумывай ссылки. Используй ТОЛЬКО статьи из предоставленных конспектов и синтеза.
- Если для качественного текста нужно больше источников — скажи координатору.
- По умолчанию пиши на АНГЛИЙСКОМ. На русском — только по явному запросу.
- Общение с координатором — на РУССКОМ.
```

---

## 5. Python-скрипты (skills)

### Файл `.opencode/skills/db_search.py`

```python
#!/usr/bin/env python3
"""
Поиск статей в SQLite базе данных.
Режимы: keyword, sql, author, doi, id
"""

import argparse
import json
import os
import sqlite3
import sys
from pathlib import Path


def load_env():
    """Загрузить переменные из .env файла."""
    env_path = Path(__file__).resolve().parents[2] / ".env"
    if not env_path.exists():
        # Попробовать текущую директорию
        env_path = Path.cwd() / ".env"
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, value = line.partition("=")
                    os.environ.setdefault(key.strip(), value.strip())


def get_db_path():
    load_env()
    db_path = os.environ.get("LITBASE_SQLITE_PATH")
    if not db_path:
        print("ERROR: LITBASE_SQLITE_PATH not set in .env", file=sys.stderr)
        sys.exit(1)
    if not Path(db_path).exists():
        print(f"ERROR: Database not found at {db_path}", file=sys.stderr)
        sys.exit(1)
    return db_path


def format_results(rows, columns):
    """Форматировать результаты в читаемый вид."""
    if not rows:
        print("No results found.")
        return
    # Заголовок
    print(f"Found {len(rows)} result(s):\n")
    for i, row in enumerate(rows, 1):
        print(f"--- Result {i} ---")
        for col, val in zip(columns, row):
            if val is None:
                continue
            val_str = str(val)
            if col == "full_text" and len(val_str) > 500:
                val_str = val_str[:500] + "... [truncated]"
            elif col == "abstract" and len(val_str) > 1000:
                val_str = val_str[:1000] + "... [truncated]"
            print(f"  {col}: {val_str}")
        print()


def search_keyword(conn, query, fields, limit):
    """Полнотекстовый поиск по title, abstract, full_text."""
    field_list = ", ".join(fields)
    # Поиск по LIKE в нескольких полях
    terms = query.split()
    conditions = []
    params = []
    for term in terms:
        term_cond = (
            "(title LIKE ? OR abstract LIKE ? OR full_text LIKE ?)"
        )
        conditions.append(term_cond)
        params.extend([f"%{term}%"] * 3)

    where = " AND ".join(conditions)
    sql = f"SELECT {field_list} FROM Articles WHERE {where} LIMIT ?"
    params.append(limit)

    cursor = conn.execute(sql, params)
    columns = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()
    format_results(rows, columns)


def search_sql(conn, query, fields, limit):
    """Выполнить произвольный SQL-запрос."""
    # Безопасность: только SELECT
    if not query.strip().upper().startswith("SELECT"):
        print("ERROR: Only SELECT queries are allowed.", file=sys.stderr)
        sys.exit(1)
    try:
        cursor = conn.execute(query)
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        format_results(rows, columns)
    except sqlite3.Error as e:
        print(f"SQL Error: {e}", file=sys.stderr)
        sys.exit(1)


def search_author(conn, name, fields, limit):
    """Поиск по автору."""
    field_list = ", ".join(fields)
    sql = f"SELECT {field_list} FROM Articles WHERE authors LIKE ? LIMIT ?"
    cursor = conn.execute(sql, [f"%{name}%", limit])
    columns = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()
    format_results(rows, columns)


def search_doi(conn, doi, fields):
    """Поиск по DOI."""
    field_list = ", ".join(fields)
    sql = f"SELECT {field_list} FROM Articles WHERE doi = ?"
    cursor = conn.execute(sql, [doi])
    columns = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()
    format_results(rows, columns)


def search_id(conn, article_id, fields):
    """Поиск по ID."""
    field_list = ", ".join(fields)
    sql = f"SELECT {field_list} FROM Articles WHERE id = ?"
    cursor = conn.execute(sql, [article_id])
    columns = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()
    format_results(rows, columns)


def main():
    parser = argparse.ArgumentParser(description="Search articles database")
    parser.add_argument(
        "mode", choices=["keyword", "sql", "author", "doi", "id"]
    )
    parser.add_argument("query", help="Search query")
    parser.add_argument(
        "--fields",
        default="id,title,authors,date,doi,abstract",
        help="Comma-separated fields to return",
    )
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument(
        "--full", action="store_true", help="Include full_text"
    )
    args = parser.parse_args()

    fields = [f.strip() for f in args.fields.split(",")]
    if args.full and "full_text" not in fields:
        fields.append("full_text")

    db_path = get_db_path()
    conn = sqlite3.connect(db_path)

    try:
        if args.mode == "keyword":
            search_keyword(conn, args.query, fields, args.limit)
        elif args.mode == "sql":
            search_sql(conn, args.query, fields, args.limit)
        elif args.mode == "author":
            search_author(conn, args.query, fields, args.limit)
        elif args.mode == "doi":
            search_doi(conn, args.query, fields, args.limit)
        elif args.mode == "id":
            search_id(conn, args.query, fields)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
```

### Файл `.opencode/skills/semantic_search.py`

```python
#!/usr/bin/env python3
"""
Семантический поиск по абстрактам через ChromaDB.
"""

import argparse
import csv
import os
import sqlite3
import sys
from pathlib import Path


def load_env():
    env_path = Path(__file__).resolve().parents[2] / ".env"
    if not env_path.exists():
        env_path = Path.cwd() / ".env"
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, value = line.partition("=")
                    os.environ.setdefault(key.strip(), value.strip())


def main():
    parser = argparse.ArgumentParser(
        description="Semantic search via ChromaDB"
    )
    parser.add_argument("query", help="Search query in natural language")
    parser.add_argument("--top", type=int, default=20, help="Number of results")
    parser.add_argument(
        "--threshold", type=float, default=0.0,
        help="Minimum similarity threshold"
    )
    parser.add_argument(
        "--cluster", type=int, default=None,
        help="Restrict to cluster N"
    )
    args = parser.parse_args()

    load_env()

    chroma_path = os.environ.get("LITBASE_CHROMA_PATH")
    collection_name = os.environ.get(
        "LITBASE_CHROMA_COLLECTION", "abstracts"
    )
    db_path = os.environ.get("LITBASE_SQLITE_PATH")
    clusters_csv = os.environ.get("LITBASE_CLUSTERS_CSV")

    if not chroma_path:
        print("ERROR: LITBASE_CHROMA_PATH not set", file=sys.stderr)
        sys.exit(1)

    try:
        import chromadb
    except ImportError:
        print(
            "ERROR: chromadb not installed. Run: pip install chromadb",
            file=sys.stderr,
        )
        sys.exit(1)

    # Подключение к ChromaDB
    client = chromadb.PersistentClient(path=chroma_path)
    collection = client.get_collection(name=collection_name)

    # Если нужно ограничить кластером — загрузить ID из CSV
    where_filter = None
    if args.cluster is not None and clusters_csv:
        cluster_ids = []
        with open(clusters_csv, newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if int(row["cluster"]) == args.cluster:
                    cluster_ids.append(str(row["id"]))
        if cluster_ids:
            where_filter = {"id": {"$in": cluster_ids}}
        else:
            print(f"No articles found in cluster {args.cluster}")
            return

    # Выполнить поиск
    results = collection.query(
        query_texts=[args.query],
        n_results=args.top,
        where=where_filter,
        include=["documents", "distances", "metadatas"],
    )

    if not results["ids"][0]:
        print("No results found.")
        return

    # Получить дополнительные метаданные из SQLite
    conn = None
    if db_path and Path(db_path).exists():
        conn = sqlite3.connect(db_path)

    print(f"Semantic search results for: \"{args.query}\"")
    print(f"Found {len(results['ids'][0])} results:\n")

    for i, (doc_id, distance) in enumerate(
        zip(results["ids"][0], results["distances"][0])
    ):
        similarity = 1 - distance  # ChromaDB возвращает distance
        if similarity < args.threshold:
            continue

        metadata = {}
        if results["metadatas"] and results["metadatas"][0]:
            metadata = results["metadatas"][0][i]

        print(f"--- Result {i + 1} (similarity: {similarity:.4f}) ---")
        print(f"  ID: {doc_id}")

        if conn:
            try:
                cursor = conn.execute(
                    "SELECT title, authors, date, journal, doi "
                    "FROM Articles WHERE id = ?",
                    [doc_id],
                )
                row = cursor.fetchone()
                if row:
                    print(f"  Title: {row[0]}")
                    print(f"  Authors: {row[1]}")
                    print(f"  Date: {row[2]}")
                    print(f"  Journal: {row[3]}")
                    print(f"  DOI: {row[4]}")
            except Exception:
                pass

        # Показать абстракт из ChromaDB
        if results["documents"] and results["documents"][0]:
            abstract = results["documents"][0][i]
            if abstract and len(abstract) > 500:
                abstract = abstract[:500] + "..."
            print(f"  Abstract: {abstract}")

        print()

    if conn:
        conn.close()


if __name__ == "__main__":
    main()
```

### Файл `.opencode/skills/read_article.py`

```python
#!/usr/bin/env python3
"""
Чтение полного текста статьи из базы данных.
Поддерживает: полный текст, секции (эвристически), чанки, summary.
"""

import argparse
import math
import os
import re
import sqlite3
import sys
from pathlib import Path


def load_env():
    env_path = Path(__file__).resolve().parents[2] / ".env"
    if not env_path.exists():
        env_path = Path.cwd() / ".env"
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, value = line.partition("=")
                    os.environ.setdefault(key.strip(), value.strip())


def get_article(article_id):
    load_env()
    db_path = os.environ.get("LITBASE_SQLITE_PATH")
    if not db_path:
        print("ERROR: LITBASE_SQLITE_PATH not set", file=sys.stderr)
        sys.exit(1)

    conn = sqlite3.connect(db_path)
    cursor = conn.execute(
        "SELECT id, doi, title, full_text, abstract, date, journal, "
        "authors, volume, issue, pages, pmid, filepath "
        "FROM Articles WHERE id = ?",
        [article_id],
    )
    row = cursor.fetchone()
    conn.close()

    if not row:
        print(f"ERROR: Article with id={article_id} not found", file=sys.stderr)
        sys.exit(1)

    columns = [
        "id", "doi", "title", "full_text", "abstract", "date",
        "journal", "authors", "volume", "issue", "pages", "pmid", "filepath",
    ]
    return dict(zip(columns, row))


def extract_section(text, section_name):
    """Эвристическое извлечение секции из полного текста."""
    if not text:
        return None

    section_patterns = {
        "intro": [
            r"(?i)\b(introduction|background)\b",
        ],
        "methods": [
            r"(?i)\b(methods|materials?\s+and\s+methods|experimental\s+procedures"
            r"|methodology)\b",
        ],
        "results": [
            r"(?i)\b(results|findings)\b",
        ],
        "discussion": [
            r"(?i)\b(discussion|conclusions?\s+and\s+discussion)\b",
        ],
    }

    # Определить порядок секций
    section_order = ["intro", "methods", "results", "discussion"]
    section_positions = {}

    for sec_name in section_order:
        patterns = section_patterns.get(sec_name, [])
        for pattern in patterns:
            matches = list(re.finditer(pattern, text))
            for m in matches:
                # Проверить, что это заголовок (начало строки или после \n)
                pos = m.start()
                line_start = text.rfind("\n", 0, pos)
                prefix = text[line_start + 1:pos].strip()
                if len(prefix) < 20:  # Вероятно, заголовок
                    if sec_name not in section_positions:
                        section_positions[sec_name] = pos
                    break

    if section_name not in section_positions:
        return None

    start = section_positions[section_name]

    # Найти конец секции (начало следующей)
    current_idx = section_order.index(section_name)
    end = len(text)
    for next_sec in section_order[current_idx + 1:]:
        if next_sec in section_positions:
            end = section_positions[next_sec]
            break

    # Также проверить References
    ref_match = re.search(r"(?i)\b(references|bibliography)\b", text[start:])
    if ref_match:
        ref_pos = start + ref_match.start()
        if ref_pos < end:
            end = ref_pos

    return text[start:end].strip()


def chunk_text(text, chunk_size=3000):
    """Разбить текст на чанки по словам."""
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size):
        chunks.append(" ".join(words[i : i + chunk_size]))
    return chunks


def main():
    parser = argparse.ArgumentParser(description="Read article from database")
    parser.add_argument("id", type=int, help="Article ID")
    parser.add_argument(
        "--section",
        choices=["intro", "methods", "results", "discussion", "all"],
        help="Extract specific section",
    )
    parser.add_argument(
        "--chunk", type=int, default=None,
        help="Return specific chunk number (0-indexed)"
    )
    parser.add_argument(
        "--chunks", action="store_true",
        help="Show number of chunks"
    )
    parser.add_argument(
        "--chunk-size", type=int, default=3000,
        help="Words per chunk (default: 3000)"
    )
    parser.add_argument(
        "--summary", action="store_true",
        help="Show metadata + first 500 words"
    )
    parser.add_argument(
        "--full", action="store_true",
        help="Show full text"
    )
    args = parser.parse_args()

    article = get_article(args.id)

    # Метаданные — всегда показываем
    print(f"=== Article ID: {article['id']} ===")
    print(f"Title: {article['title']}")
    print(f"Authors: {article['authors']}")
    print(f"Date: {article['date']}")
    print(f"Journal: {article['journal']}")
    print(f"DOI: {article['doi']}")
    print(f"PMID: {article['pmid']}")
    print()

    full_text = article.get("full_text")
    has_text = bool(full_text and full_text.strip())

    if not has_text:
        print("WARNING: No full text available for this article.")
        print(f"\nAbstract:\n{article.get('abstract', 'N/A')}")
        return

    word_count = len(full_text.split())
    print(f"Full text: {word_count} words")
    print()

    if args.summary:
        print(f"Abstract:\n{article.get('abstract', 'N/A')}\n")
        words = full_text.split()[:500]
        print(f"First 500 words:\n{' '.join(words)}...")
        return

    if args.chunks:
        chunks = chunk_text(full_text, args.chunk_size)
        print(f"Total chunks ({args.chunk_size} words each): {len(chunks)}")
        for i, c in enumerate(chunks):
            print(f"  Chunk {i}: {len(c.split())} words")
        return

    if args.chunk is not None:
        chunks = chunk_text(full_text, args.chunk_size)
        if args.chunk < 0 or args.chunk >= len(chunks):
            print(
                f"ERROR: Chunk {args.chunk} out of range (0-{len(chunks)-1})",
                file=sys.stderr,
            )
            sys.exit(1)
        print(f"--- Chunk {args.chunk}/{len(chunks) - 1} ---\n")
        print(chunks[args.chunk])
        return

    if args.section:
        if args.section == "all":
            for sec in ["intro", "methods", "results", "discussion"]:
                content = extract_section(full_text, sec)
                if content:
                    print(f"=== {sec.upper()} ===\n{content}\n")
                else:
                    print(f"=== {sec.upper()} === [not found]\n")
        else:
            content = extract_section(full_text, args.section)
            if content:
                print(f"=== {args.section.upper()} ===\n{content}")
            else:
                print(f"Section '{args.section}' not found in this article.")
                print("Falling back to full text first 1000 words...")
                print(" ".join(full_text.split()[:1000]))
        return

    if args.full:
        print(f"=== FULL TEXT ===\n{full_text}")
        return

    # По умолчанию — summary
    print(f"Abstract:\n{article.get('abstract', 'N/A')}\n")
    words = full_text.split()[:500]
    print(f"First 500 words:\n{' '.join(words)}...")


if __name__ == "__main__":
    main()
```

### Файл `.opencode/skills/extract_figures.py`

```python
#!/usr/bin/env python3
"""
Извлечение рисунков из PDF файла статьи.
"""

import argparse
import os
import sqlite3
import sys
from pathlib import Path


def load_env():
    env_path = Path(__file__).resolve().parents[2] / ".env"
    if not env_path.exists():
        env_path = Path.cwd() / ".env"
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, value = line.partition("=")
                    os.environ.setdefault(key.strip(), value.strip())


def main():
    parser = argparse.ArgumentParser(
        description="Extract figures from article PDF"
    )
    parser.add_argument("id", type=int, help="Article ID")
    parser.add_argument(
        "--output", default=None,
        help="Output directory (default: output/figures/<id>/)"
    )
    parser.add_argument(
        "--min-size", type=int, default=100,
        help="Minimum image dimension in pixels (default: 100)"
    )
    args = parser.parse_args()

    load_env()
    db_path = os.environ.get("LITBASE_SQLITE_PATH")
    pdf_dir = os.environ.get("LITBASE_PDF_DIR", "")

    if not db_path:
        print("ERROR: LITBASE_SQLITE_PATH not set", file=sys.stderr)
        sys.exit(1)

    # Получить filepath из базы
    conn = sqlite3.connect(db_path)
    cursor = conn.execute(
        "SELECT filepath, title FROM Articles WHERE id = ?", [args.id]
    )
    row = cursor.fetchone()
    conn.close()

    if not row:
        print(f"ERROR: Article {args.id} not found", file=sys.stderr)
        sys.exit(1)

    filepath, title = row

    if not filepath:
        print(f"ERROR: No filepath for article {args.id}", file=sys.stderr)
        sys.exit(1)

    # Определить полный путь к PDF
    pdf_path = Path(filepath)
    if not pdf_path.is_absolute() and pdf_dir:
        pdf_path = Path(pdf_dir) / pdf_path

    if not pdf_path.exists():
        print(f"ERROR: PDF not found at {pdf_path}", file=sys.stderr)
        sys.exit(1)

    # Определить директорию для вывода
    output_dir = Path(
        args.output or f"output/figures/{args.id}"
    )
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        import fitz  # PyMuPDF
    except ImportError:
        print(
            "ERROR: PyMuPDF not installed. Run: pip install PyMuPDF",
            file=sys.stderr,
        )
        sys.exit(1)

    doc = fitz.open(str(pdf_path))
    image_count = 0

    for page_num in range(len(doc)):
        page = doc[page_num]
        image_list = page.get_images(full=True)

        for img_idx, img_info in enumerate(image_list):
            xref = img_info[0]
            try:
                base_image = doc.extract_image(xref)
                if not base_image:
                    continue

                width = base_image.get("width", 0)
                height = base_image.get("height", 0)

                if width < args.min_size or height < args.min_size:
                    continue

                image_bytes = base_image["image"]
                image_ext = base_image.get("ext", "png")
                image_filename = (
                    f"page{page_num + 1}_img{img_idx + 1}.{image_ext}"
                )
                image_path = output_dir / image_filename

                with open(image_path, "wb") as f:
                    f.write(image_bytes)

                image_count += 1
                print(
                    f"Extracted: {image_filename} "
                    f"({width}x{height}, {len(image_bytes)} bytes)"
                )

            except Exception as e:
                print(
                    f"Warning: Could not extract image {img_idx} "
                    f"from page {page_num + 1}: {e}",
                    file=sys.stderr,
                )

    doc.close()

    print(f"\nTotal images extracted: {image_count}")
    print(f"Output directory: {output_dir}")

    if image_count == 0:
        print("Note: No images found. The PDF might use vector graphics "
              "or the images are too small.")


if __name__ == "__main__":
    main()
```

### Файл `.opencode/skills/cluster_browse.py`

```python
#!/usr/bin/env python3
"""
Просмотр кластеров статей.
"""

import argparse
import csv
import os
import sys
from collections import Counter, defaultdict
from pathlib import Path


def load_env():
    env_path = Path(__file__).resolve().parents[2] / ".env"
    if not env_path.exists():
        env_path = Path.cwd() / ".env"
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, value = line.partition("=")
                    os.environ.setdefault(key.strip(), value.strip())


def load_clusters():
    load_env()
    csv_path = os.environ.get("LITBASE_CLUSTERS_CSV")
    if not csv_path:
        print("ERROR: LITBASE_CLUSTERS_CSV not set", file=sys.stderr)
        sys.exit(1)
    if not Path(csv_path).exists():
        print(f"ERROR: File not found: {csv_path}", file=sys.stderr)
        sys.exit(1)

    clusters = defaultdict(list)
    all_rows = []

    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            cluster_id = int(row["cluster"])
            clusters[cluster_id].append(row)
            all_rows.append(row)

    return clusters, all_rows


def list_clusters(clusters):
    """Показать все кластеры."""
    print(f"Total clusters: {len(clusters)}\n")
    print(f"{'Cluster':>8} | {'Size':>5} | Keywords")
    print("-" * 80)

    for cluster_id in sorted(clusters.keys()):
        articles = clusters[cluster_id]
        # Ключевые слова — берем из первой статьи (одинаковые для кластера)
        keywords = articles[0].get("keywords", "N/A")
        print(f"{cluster_id:>8} | {len(articles):>5} | {keywords}")


def show_cluster(clusters, cluster_id):
    """Показать статьи кластера."""
    if cluster_id not in clusters:
        print(f"Cluster {cluster_id} not found.")
        return

    articles = clusters[cluster_id]
    keywords = articles[0].get("keywords", "N/A")

    print(f"=== Cluster {cluster_id} ===")
    print(f"Keywords: {keywords}")
    print(f"Size: {len(articles)} articles\n")

    # Сортировать по similarity (убывание)
    articles_sorted = sorted(
        articles, key=lambda x: float(x.get("similarity", 0)), reverse=True
    )

    for i, art in enumerate(articles_sorted, 1):
        sim = float(art.get("similarity", 0))
        print(f"{i:>3}. [{art['id']}] ({sim:.4f}) {art.get('date', 'N/A')} "
              f"- {art['title']}")
        if art.get("doi"):
            print(f"     DOI: {art['doi']}")


def find_clusters(clusters, query):
    """Найти кластеры по ключевым словам."""
    query_terms = query.lower().split()
    results = []

    for cluster_id, articles in clusters.items():
        keywords = articles[0].get("keywords", "").lower()
        score = sum(1 for term in query_terms if term in keywords)
        if score > 0:
            results.append((cluster_id, score, articles))

    results.sort(key=lambda x: x[1], reverse=True)

    if not results:
        print(f"No clusters found matching: {query}")
        return

    print(f"Clusters matching \"{query}\":\n")
    for cluster_id, score, articles in results:
        keywords = articles[0].get("keywords", "N/A")
        print(
            f"  Cluster {cluster_id} (match: {score}, "
            f"size: {len(articles)}): {keywords}"
        )


def main():
    parser = argparse.ArgumentParser(description="Browse article clusters")
    parser.add_argument("mode", choices=["list", "show", "find"])
    parser.add_argument(
        "argument", nargs="?", default=None,
        help="Cluster number (for show) or query (for find)"
    )
    args = parser.parse_args()

    clusters, _ = load_clusters()

    if args.mode == "list":
        list_clusters(clusters)
    elif args.mode == "show":
        if args.argument is None:
            print("ERROR: Cluster number required", file=sys.stderr)
            sys.exit(1)
        show_cluster(clusters, int(args.argument))
    elif args.mode == "find":
        if args.argument is None:
            print("ERROR: Search query required", file=sys.stderr)
            sys.exit(1)
        find_clusters(clusters, args.argument)


if __name__ == "__main__":
    main()
```

---

## 6. План реализации углублённого семантического поиска

Текущая система: эмбеддинги абстрактов через SPECTER2 в ChromaDB. Этого достаточно для грубого поиска, но недостаточно для задач, где ответ находится в конкретном абзаце полного текста.

### Этап 1: Чанкование полных текстов (приоритет: высокий)

**Цель**: создать эмбеддинги для чанков полного текста, чтобы находить конкретные параграфы.

**Реализация**:

1. Разбить каждый `full_text` на чанки по ~512 токенов с перекрытием 64 токена.
2. Каждому чанку присвоить метаданные: `article_id`, `chunk_index`, `section` (эвристически).
3. Закодировать чанки через SPECTER2.
4. Сохранить в отдельную коллекцию ChromaDB (`fulltext_chunks`).

**Оценка ресурсов**:
- ~12 000 статей × ~30 чанков в среднем = ~360 000 чанков
- SPECTER2 embedding dimension = 768
- Размер ChromaDB: ~2-3 GB
- Время кодирования: ~4-8 часов на GPU (или ~24-48 часов на CPU)

**Добавить в `.env`**:
```bash
LITBASE_CHROMA_CHUNKS_COLLECTION=fulltext_chunks
```

**Добавить скрипт** `.opencode/skills/chunk_search.py` — поиск по чанкам с возвратом контекста (чанк + соседние чанки).

### Этап 2: Гибридный поиск (приоритет: средний)

**Цель**: комбинировать семантический и ключевой поиск для лучшего recall.

**Реализация**:
1. BM25 индекс через `rank-bm25` или SQLite FTS5 для full_text.
2. Reciprocal Rank Fusion (RRF) для объединения результатов семантического и BM25 поиска.
3. Re-ranking через cross-encoder (например, `ms-marco-MiniLM-L-12-v2`) для топ-50 кандидатов.

### Этап 3: Инкрементальное обновление (приоритет: средний)

**Цель**: при добавлении новых статей автоматически обновлять эмбеддинги.

**Реализация**: скрипт, который:
1. Находит статьи в SQLite, для которых нет эмбеддингов в ChromaDB.
2. Кодирует их.
3. Добавляет в соответствующие коллекции.

### Этап 4: Query expansion (приоритет: низкий)

**Цель**: автоматическое расширение запросов синонимами и связанными терминами.

**Реализация**: использовать LLM для генерации расширенных запросов перед поиском.

---

## Краткое описание того, что нужно сделать для запуска

### Минимальный набор для старта:

1. **Создать структуру директорий** проекта согласно схеме выше.
2. **Заполнить `.env`** реальными путями.
3. **Скопировать все файлы** (`opencode.json`, промпты, скрипты).
4. **Установить Python-зависимости**:
   ```bash
   pip install chromadb PyMuPDF
   ```
5. **Протестировать скрипты вручную**:
   ```bash
   python .opencode/skills/db_search.py keyword "place cells hippocampus" --limit 5
   python .opencode/skills/semantic_search.py "spatial navigation theta oscillations" --top 5
   python .opencode/skills/cluster_browse.py list
   python .opencode/skills/read_article.py 1 --summary
   ```
6. **Настроить модель в opencode** — добавить провайдер (Ollama или OpenRouter) в конфигурацию opencode. Конкретную модель можно указать в поле `model` каждого агента или использовать дефолтную.
7. **Запустить opencode** и переключиться на агента `researcher` через Tab.

### Рекомендации по выбору модели:

Для вашего железа (60 GB VRAM) я бы рекомендовал начать с:

- **Основной агент (researcher)**: Qwen 3.5 27B Q4 или Gemma 4 26B-A4B (MoE) — хороший баланс качества и контекста.
- **Субагенты (searcher, reader)**: можно использовать ту же модель или более лёгкую (Qwen 3.5 9B, Nemotron-Cascade-2) для экономии.
- **Writer** (для финального текста): если качество критично — подключить через OpenRouter (Claude Sonnet или GPT-4o).

---

Если у вас возникнут вопросы по настройке или нужна доработка какого-либо компонента — обращайтесь. 
