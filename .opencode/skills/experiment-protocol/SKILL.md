---
name: experiment-protocol
description: Design an experimental protocol grounded in literature from the user's Zotero library. Extract specific parameters (concentrations, timings, conditions) from published studies and create a step-by-step protocol with justification for each parameter choice.
---

# Purpose

Создать протокол эксперимента, обоснованный литературой. Извлечь конкретные параметры (концентрации, время, условия) из опубликованных исследований в Zotero-библиотеке и предложить оптимальный протокол с обоснованием каждого выбора.

# When to use

Активируй этот навык когда:
- Пользователь просит «протокол», «protocol» для эксперимента
- Нужно спроектировать экспериментальную процедуру (in vitro, in vivo, in silico, behavioral, и т.д.)
- Требуется обосновать выбор параметров ссылками на литературу
- Задача типа «как правильно провести эксперимент X?»

# Inputs needed

Перед началом уточни у пользователя:
- Тип эксперимента (электрофизиология, оптогенетика, имиджинг, поведение, моделирование...)
- Биологический препарат/модель (срезы, культура, in vivo, вид/линия животного)
- Целевой вопрос эксперимента
- Особые требования (good laboratory practice, воспроизводимость и т.д.)

# Procedure

**Шаг 1 — Поиск методических статей в Zotero:**
1. `zotero_search_library` + `zotero_search_fulltext` по методике и препарату
2. `zotero_get_collections` + `zotero_search_collections` — посмотри, есть ли в библиотеке пользователя тематические подборки (например, «Methods», «Protocols»)
3. `zotero_search_annotations` — пользователь мог оставлять заметки по методикам
4. Цель: 10-100 статей с аналогичными методами

**Шаг 2 — Извлечение параметров:**
1. Для каждой статьи из shortlist — @reader с фокусом на Methods
2. Извлекай КОНКРЕТНЫЕ числа: концентрации, время инкубации, температура, напряжение, частота...

**Шаг 3 — Создание сводной таблицы:**
1. Передай конспекты @synthesizer
2. Режим: сравнительная таблица параметров
3. Колонки: параметр | значения из статей | частота использования | обоснование

**Шаг 4 — Написание протокола:**
1. Передай таблицу @writer
2. Writer создаёт протокол: Objective → Materials → Procedure → Expected Results → Troubleshooting → References

# Output format

Текст на языке выходных текстов (см. `user_profile.md`, по умолчанию — английский):

```markdown
# Protocol: [Experiment Title]

## Objective
[1-2 предложения о цели]

## Materials
- Equipment: ...
- Reagents: ... (с концентрациями)
- Animals/Preparation: ...

## Detailed Procedure
### Step 1: Preparation
[Подробно, с параметрами]

### Step 2: ...
[Каждый шаг с конкретными числами и ссылкой на обоснование]

## Parameter Summary Table
| Parameter | Value | Justification | Reference |
|-----------|-------|---------------|-----------|
| ... | ... | ... | (Author et al., Year, itemKey: ABCD1234) |

## Expected Results

## Troubleshooting
| Problem | Possible Cause | Solution | Reference |
|---------|---------------|----------|-----------|
| ... | ... | ... | (Author et al., Year, itemKey: XYZ5678) |

## References
[Стиль из user_profile.md; Zotero itemKey для каждой]
```

# Quality bar (self-check)

- [ ] Каждый параметр имеет ссылку на литературу или обоснование
- [ ] Числовые значения точны и перепроверены
- [ ] Протокол воспроизводим: достаточно деталей для повторения
- [ ] Указаны типичные проблемы и их решения
- [ ] Сравнительная таблица показывает разброс параметров в литературе
- [ ] Opt-in: для противоречивых параметров предложен компромисс с обоснованием
- [ ] Все ссылки в формате из `user_profile.md`; itemKey для каждой

# Anti-patterns

- ❌ Давать параметры без ссылок («стандартные значения»)
- ❌ Копировать протокол из одной статьи без сравнения с другими
- ❌ Игнорировать разброс параметров в литературе (показать диапазон!)
- ❌ Пропускать шаги, которые «очевидны» для специалиста
- ❌ Использовать нестандартные единицы измерения

# Examples

**Input:** «Составь протокол для whole-cell patch clamp записи с пирамидальных нейронов в срезах мыши»
**Output:** Протокол с: состав extracellular solution (с концентрациями ионов из 5+ статей), состав intracellular solution, resistance pipettes (3-5 MΩ), протокол стимуляции, temperature (32-34°C), критерии качества записи (Ra < 20 MΩ). Каждый параметр со ссылкой на Zotero itemKey. Сравнительная таблица составов растворов из 10 статей.
