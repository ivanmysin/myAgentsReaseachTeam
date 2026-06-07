---
name: scientific-presentation
description: Create a scientific presentation in Marp format with figures. Use for conference talks, lab meetings, or journal club presentations. Citations and content come from the user's Zotero library.
---

# Purpose

Создать научную презентацию в формате Marp (Markdown-based slides). Структурировать контент по слайдам, подготовить speaker notes. Изображения пользователь добавляет вручную в `output/figures/`.

# When to use

Активируй этот навык когда:
- Пользователь просит «сделать презентацию», «слайды», «presentation»
- Нужна презентация для journal club, lab meeting, конференции
- Требуется визуализировать обзор литературы или результаты исследования
- Задача типа «подготовь слайды по этим статьям»

# Inputs needed

Перед началом уточни у пользователя:
- Тема презентации и целевая аудитория
- Список статей для включения (itemKey из Zotero) или тема для поиска
- Формат выступления (15 минут, 30 минут, 1 час)
- Нужны ли speaker notes
- Предпочитаемая тема Marp (default, gaia, uncover)

# Procedure

**Шаг 1 — Сбор контента:**
1. Если статьи не указаны — проведи поиск как в `literature-review` (этапы 1-3)
2. Определи ключевые сообщения (3-5 главных идей)
3. Составь структуру слайдов

**Шаг 2 — Извлечение рисунков:**
ВНИМАНИЕ: В текущей версии агент НЕ может автоматически извлекать рисунки из PDF-файлов в Zotero.

Действия пользователя для добавления рисунков:
1. Открой нужный PDF в Zotero
2. Скопируй нужные изображения (Page → Save Image As, или внешний инструмент)
3. Положи файлы в `output/figures/<itemKey>/<descriptive_name>.png`
4. Сообщи агенту пути к изображениям для включения в слайды

Альтернативно: пользователь может добавить изображения как attachment к Zotero-элементу (правый клик → Add Attachment → Linked/Imported File), и тогда их можно будет получить через `zotero_get_content` с `include.attachments=true`.

**Шаг 3 — Создание слайдов:**
1. Передай структуру, конспекты статей и пути к рисункам (если есть) субагенту @writer
2. Writer создаёт Marp-презентацию
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

![Figure description](figures/ABCD1234/fig1.png)

<!-- Speaker notes: Explain this figure in detail -->

---

# References
1. (Author et al., Year) Title. Journal. [Zotero: ABCD1234]
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
- [ ] Рисунки имеют корректные относительные пути (в `output/figures/...`)
- [ ] Все рисунки имеют описательные подписи
- [ ] Количество слайдов соответствует времени (~1 слайд/минуту)
- [ ] Speaker notes содержат развёрнутые пояснения
- [ ] Слайд References в формате из `user_profile.md`; Zotero itemKey для каждой
- [ ] Нет слайдов-«простыней» с большими блоками текста
- [ ] Контрастность текста и фона достаточна для проектора

# Anti-patterns

- ❌ Копировать абзацы из статей на слайды (только ключевые bullets)
- ❌ Использовать скриншоты вместо качественных изображений
- ❌ Забывать указывать источник для каждого рисунка
- ❌ Делать больше 30 слайдов для 15-минутного доклада
- ❌ Оставлять рисунки без описания в speaker notes
- ❌ Использовать изображения из интернета (только подготовленные пользователем)

# Examples

**Input:** «Сделай презентацию на 20 минут по статьям о grid cells для lab meeting»
**Output:** Marp-файл с 18-20 слайдами: титул, outline, background (3 слайда), discovery of grid cells (3 слайда с рисунками из оригинальной статьи Hafting et al., 2005 — пользователь положит их в `output/figures/ABCD1234/`), models (4 слайда), open questions (3 слайда), conclusions (1 слайд), references. Все ссылки с Zotero itemKey.
