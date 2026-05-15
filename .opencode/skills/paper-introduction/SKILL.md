---
name: paper-introduction
description: Write an Introduction section for a computational neuroscience paper. Narrow-down structure from broad context to specific research question, grounded in 5-15 key citations from the database.
---

# Purpose

Написать секцию Introduction для научной статьи в области вычислительной нейронауки. Структура «воронка»: от широкого контекста к конкретному исследовательскому вопросу. Все утверждения подкреплены ссылками из базы.

# When to use

Активируй этот навык когда:
- Пользователь просит написать «введение», «introduction» к статье
- Нужно обосновать актуальность исследования
- Требуется сформулировать исследовательский вопрос и гипотезу

# Inputs needed

Перед началом уточни у пользователя:
- Тема статьи и ключевые результаты работы
- Целевой журнал (влияет на объем и стиль)
- Есть ли конкретные статьи, которые обязательно процитировать
- Ожидаемый объем (обычно 3-6 параграфов, 800-1500 слов)

# Procedure

**Шаг 1 — Определи структуру:**
1. Paragraph 1: широкий контекст (роль гиппокампа в исследуемой функции)
2. Paragraphs 2-3: сужение к конкретной теме, текущее состояние знаний
3. Paragraphs 4-5: нерешенные вопросы, пробелы, противоречия
4. Final paragraph: цель работы, гипотеза, подход

**Шаг 2 — Целевой поиск под каждый параграф:**
1. Для каждого аспекта используй `semantic_search` + `db_search` (keyword)
2. Найди 2-4 ключевые статьи на каждый параграф
3. Отбери только наиболее авторитетные и релевантные источники

**Шаг 3 — Чтение и конспектирование:**
1. Для отобранных статей (5-15) используй @reader
2. Фокус: ключевые findings, методы, интерпретации
3. Конспекты в `output/notes/`

**Шаг 4 — Написание:**
1. Передай конспекты и структуру субагенту @writer
2. Writer создает текст Introduction с цитированием
3. Результат: `output/drafts/introduction_<topic>_<date>.md`

# Output format

Текст на АНГЛИЙСКОМ языке в академическом стиле:

```markdown
# Introduction

[Paragraph 1: Broad context — hippocampus and the cognitive function]

[Paragraph 2: What is known about the specific mechanism]

[Paragraph 3: Current models and their limitations]

[Paragraph 4: Open questions and contradictions]

[Paragraph 5: "In this study, we..." — aim, hypothesis, approach]

## References
[Chicago Author-Date format]
```

Стиль: активный залог, без разговорных выражений, уровень Nature Neuroscience / Neuron.

# Quality bar (self-check)

- [ ] Структура «воронка»: от общего к частному прослеживается
- [ ] Каждое утверждение имеет ссылку на конкретную статью
- [ ] Использовано 5-15 источников (не больше, не меньше)
- [ ] Последний параграф четко формулирует цель и гипотезу
- [ ] Текст на английском, академический стиль
- [ ] Нет выдуманных ссылок — все статьи из базы
- [ ] Нет избыточного цитирования (5+ ссылок на одно утверждение)
- [ ] Все BibTeX-записи валидны (если запрошены)

# Anti-patterns

- ❌ Писать «с середины» без широкого контекста в первом параграфе
- ❌ Использовать статьи без предварительного чтения через @reader
- ❌ Цитировать больше 15 статей во введении (перегрузка)
- ❌ Забывать сформулировать конкретную гипотезу в последнем параграфе
- ❌ Использовать пассивный залог где можно активный
- ❌ Писать общими фразами без конкретных данных из статей

# Examples

**Input:** «Напиши введение для статьи о роли grid cells в энторинальной коре для пространственной навигации»
**Output:** 5 параграфов: (1) spatial navigation overview, (2) discovery of grid cells, (3) grid cell models, (4) open questions about grid-hippocampus interaction, (5) "Here we investigate how grid cell input shapes hippocampal place field formation using a computational model...". 12 ссылок.
