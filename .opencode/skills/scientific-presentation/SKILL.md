---
name: scientific-presentation
description: Create a scientific presentation in Marp format with figures extracted from article PDFs. Use for conference talks, lab meetings, or journal club presentations.
---

# Purpose

Создать научную презентацию в формате Marp (Markdown-based slides). Извлечь рисунки из PDF статей, структурировать контент по слайдам, подготовить speaker notes.

# When to use

Активируй этот навык когда:
- Пользователь просит «сделать презентацию», «слайды», «presentation»
- Нужна презентация для journal club, lab meeting, конференции
- Требуется визуализировать обзор литературы или результаты исследования
- Задача типа «подготовь слайды по этим статьям»

# Inputs needed

Перед началом уточни у пользователя:
- Тема презентации и целевая аудитория
- Список статей для включения (или тема для поиска)
- Формат выступления (15 минут, 30 минут, 1 час)
- Нужны ли speaker notes
- Предпочитаемая тема Marp (default, gaia, uncover)

# Procedure

**Шаг 1 — Сбор контента:**
1. Если статьи не указаны — проведи поиск как в `literature-review` (этапы 1-3)
2. Определи ключевые сообщения (3-5 главных идей)
3. Составь структуру слайдов

**Шаг 2 — Извлечение рисунков:**
1. Для каждой статьи используй `extract_figures` (id)
2. Рисунки сохраняются в `output/figures/<id>/`
3. Выбери 1-3 наиболее информативных рисунка на статью

**Шаг 3 — Создание слайдов:**
1. Передай структуру, конспекты статей и пути к рисункам субагенту @writer
2. Writer создает Marp-презентацию
3. Результат: `output/presentations/<topic>_<date>.md`

**Шаг 4 — Дополнительно (по запросу):**
1. Конвертация Marp → PDF: `npx @marp-team/marp-cli output/presentations/<file>.md -o output/presentations/<file>.pdf`
2. Проверка: все ли изображения отображаются корректно

# Output format

Marp Markdown с YAML frontmatter:

```markdown
---
marp: true
theme: default
paginate: true
size: 16:9
---

# Title Slide
## Subtitle
### Author / Date

---

# Outline
1. Background
2. Key Findings
3. Discussion
4. Conclusions

---

# Slide Title
- Bullet point 1
- Bullet point 2

![Figure description](figures/123/page1_img1.png)

<!-- Speaker notes: Explain this figure in detail -->

---

# References
1. (Author et al., Year) Title. Journal.
...
```

Правила слайдов:
- 1 идея = 1 слайд
- Минимум текста (bullets, не абзацы)
- Каждый рисунок с подписью
- Speaker notes через `<!-- comment -->`
- Разделитель слайдов: `---`

# Quality bar (self-check)

- [ ] YAML frontmatter корректный: `marp: true`, `paginate: true`, `theme`
- [ ] Рисунки извлечены и пути относительные
- [ ] Все рисунки имеют описательные подписи
- [ ] Количество слайдов соответствует времени (~1 слайд/минуту)
- [ ] Speaker notes содержат развернутые пояснения
- [ ] Слайд References в формате Chicago Author-Date
- [ ] Нет слайдов-«простыней» с большими блоками текста
- [ ] Контрастность текста и фона достаточна для проектора

# Anti-patterns

- ❌ Копировать абзацы из статей на слайды (только ключевые bullets)
- ❌ Использовать скриншоты вместо извлеченных из PDF рисунков
- ❌ Забывать указывать источник для каждого рисунка
- ❌ Делать больше 30 слайдов для 15-минутного доклада
- ❌ Оставлять рисунки без описания в speaker notes
- ❌ Использовать изображения из интернета (только из базы статей)

# Examples

**Input:** «Сделай презентацию на 20 минут по статьям о grid cells для lab meeting»
**Output:** Marp-файл с 18-20 слайдами: титул, outline, background (3 слайда), discovery of grid cells (3 слайда с рисунками из оригинальной статьи Hafting et al., 2005), models (4 слайда), open questions (3 слайда), conclusions (1 слайд), references.
