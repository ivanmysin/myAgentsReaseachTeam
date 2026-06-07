---
name: hypothesis-mining
description: Mine the user's Zotero library for hypotheses, open questions, and knowledge gaps. Extract unanswered questions from Discussion sections and systematize them into structured hypothesis lists.
---

# Purpose

Систематически извлечь из литературы в Zotero нерешённые вопросы, гипотезы и пробелы в знаниях по заданной теме. Создать структурированный список гипотез с указанием их источника и уровня обоснованности.

# When to use

Активируй этот навык когда:
- Пользователь просит «найти гипотезы», «open questions», «future directions»
- Нужно определить направления для нового исследования
- Требуется gap analysis в конкретной области
- Задача типа «что мы не знаем о X?», «какие гипотезы существуют о Y?»
- Нужен список идей для моделирования или эксперимента

# Inputs needed

Перед началом уточни у пользователя:
- Конкретная тема/область поиска гипотез
- Тип гипотез (механистические, функциональные, вычислительные, экспериментальные)
- Временной диапазон (последние N лет или без ограничений)
- Нужны ли только непроверенные гипотезы или любые

# Procedure

**Шаг 1 — Поиск статей с гипотезами в Zotero:**
1. `zotero_search_library` (q=<тема>) — для обзорных статей и оригинальных работ
2. `zotero_search_fulltext` с маркерами неопределённости:
   - "remains unclear"
   - "open question"
   - "future work" / "future studies" / "future directions"
   - "further investigation" / "remains to be determined"
   - "poorly understood" / "not well understood"
   - "it is unknown whether" / "whether ... remains"
3. `zotero_search_annotations` — пользователь мог выделять такие фразы
4. Фокус на Discussion секциях

**Шаг 2 — Глубокое чтение Discussion:**
1. Для топ-кандидатов используй @reader
2. Извлекай конкретные формулировки гипотез и нерешённых вопросов (с цитатой и номером страницы, если есть)
3. Запроси `zotero_get_annotations` — пользователь мог уже делать пометки на этих формулировках

**Шаг 3 — Систематизация:**
1. Передай конспекты @synthesizer
2. Режим: gap analysis + тематическая группировка
3. Сгруппируй гипотезы по темам и уровню обоснованности

**Шаг 4 — Оценка гипотез:**
1. Для каждой гипотезы определи:
   - Уровень обоснованности (solid evidence / suggestive / speculative)
   - Количество статей, поддерживающих гипотезу
   - Проверяемость (testable / currently untestable)
   - Конкурирующие гипотезы (если есть)

# Output format

Текст на языке выходных текстов (см. `user_profile.md`, по умолчанию — английский):

```markdown
# Hypothesis Mining: [Topic]

## Summary
Total hypotheses found: N
Categories: M

## Category 1: [Theme]

### Hypothesis 1: [Concise statement]
- **Source**: (Author et al., Year, itemKey: ABCD1234)
- **Evidence level**: Solid / Suggestive / Speculative
- **Supporting studies**: N
- **Testability**: How this could be tested
- **Competing hypotheses**: (if any)
- **Direct quote**: "..." (Author et al., Year, p.XX)

### Hypothesis 2: ...

## Category 2: [Theme]
...

## Cross-cutting Open Questions
[Questions that span multiple categories]

## Prioritized Research Directions
1. Most impactful + testable hypothesis
2. ...
```

# Quality bar (self-check)

- [ ] Использованы специальные поисковые запросы для Discussion секций
- [ ] Каждая гипотеза имеет точную ссылку на источник (Author, Year, itemKey)
- [ ] Указан уровень обоснованности для каждой гипотезы
- [ ] Гипотезы сгруппированы тематически
- [ ] Отмечены случаи, когда гипотезы противоречат друг другу
- [ ] Нет выдуманных гипотез — все из конкретных статей
- [ ] Для проверяемых гипотез предложены подходы к проверке
- [ ] Учтены пользовательские аннотации (если есть)

# Anti-patterns

- ❌ Выдавать список тем вместо конкретных гипотез
- ❌ Приписывать автору гипотезу, которую он не формулировал
- ❌ Смешивать гипотезы и established facts
- ❌ Игнорировать опровергнутые гипотезы (они важны для контекста!)
- ❌ Пропускать поиск по полному тексту — многие гипотезы только в Discussion

# Examples

**Input:** «Какие гипотезы существуют о роли sharp-wave ripples в консолидации памяти?»
**Output:** 15-25 гипотез, сгруппированных в 4 категории: (1) reactivation of memory traces, (2) synaptic plasticity during SWRs, (3) cortico-hippocampal dialogue, (4) computational theories. Для каждой — источник (Author, Year, itemKey), уровень обоснованности, проверяемость. Cross-cutting: contradiction between "reactivation" and "interference" theories.
