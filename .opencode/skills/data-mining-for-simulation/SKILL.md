---
name: data-mining-for-simulation
description: Extract structured data (neuron types, firing patterns, connectivity) from literature for building computational neural network models. Collects both quantitative parameters and qualitative evidence with explicit source citations.
---

# Purpose

Собрать из литературы структурированные данные для построения вычислительной модели нейронной сети. Три категории данных: (1) типы нейронов и их свойства, (2) параметры паттернов разрядов, (3) информация о связях между нейронами. Результат — сводный отчёт с таблицами параметров, пригодный для непосредственного использования при построении импульсной нейронной сети.

# When to use

Активируй этот навык когда:
- Пользователь строит вычислительную модель (spiking neural network) и нуждается в параметрах из литературы
- Нужно собрать данные о типах нейронов, их электрофизиологии и маркерах для конкретной brain region
- Требуется каталогизировать паттерны разрядов (place fields, grid spacing, phase precession и т.д.)
- Нужны данные о связях: вероятность контакта, сила синапса, long-range projections
- Задача типа «какие нейроны есть в области X и как они взаимодействуют?»
- Нужен machine-usable набор параметров для оптимизационной задачи моделирования

# Inputs needed

Перед началом уточни у пользователя:

- **Brain region(s)**: конкретная область мозга (CA1, CA3, DG, MEC, Subiculum, Septum...) или несколько связанных областей
- **Приоритет категорий**: все три или только некоторые (neuron types / firing patterns / connectivity)
- **Контекст моделирования**: какой тип модели строится, какие аспекты наиболее критичны (это помогает @reader фокусироваться на нужных деталях)
- **Желаемый уровень детализации**: 
  - `comprehensive` — извлечь все доступные параметры, включая разброс (mean ± SD), зависимости от условий
  - `essential` — только ключевые параметры, достаточные для базовой модели
- **Временной диапазон** (если нужен): например, «последние 10 лет»

Если пользователь не указал brain region — ОБЯЗАТЕЛЬНО спроси, без этого поиск невозможен.

# Data categories and what to extract

## Category 1: Neuron Types

Для каждого типа нейронов в интересующей brain region:

| Что извлекать | Примеры |
|---|---|
| **Генетические/биохимические маркеры** | PV+, SST+, VIP+, CCK+, Calbindin+, Calretinin+, Reelin+, nNOS+ |
| **Морфологические свойства** | soma size, dendritic arborization, axonal projection pattern, spine density |
| **Электрофизиологические свойства** | resting membrane potential, input resistance (Rin), membrane time constant (τm), spike threshold, spike half-width, AHP amplitude, firing type (fast-spiking, regular-spiking, burst-spiking, late-spiking, stuttering), adaptation ratio, max firing rate, sag ratio |
| **Нейромодуляторная чувствительность** | response to ACh, 5-HT, DA, NA (если релевантно для модели) |
| **Слой/lamina** | stratum oriens, pyramidale, radiatum, lacunosum-moleculare (для hippocampus); layer II, III, V (для cortex) |

## Category 2: Firing Patterns

Для каждого функционального типа нейронов в поведенческих задачах:

| Что извлекать | Примеры |
|---|---|
| **Spatial tuning** | place field size (cm), grid spacing (cm), grid orientation, head direction tuning width, border field extent |
| **Firing statistics** | mean firing rate (Hz), peak firing rate (Hz), burst frequency, inter-spike interval distribution, coefficient of variation (CV) |
| **Temporal dynamics** | theta phase precession slope, theta modulation strength, phase locking to gamma/SWR, sequence replay properties |
| **State dependence** | firing rate change: running vs stationary, REM vs NREM vs awake, theta vs LIA |
| **Contextual modulation** | rate remapping extent, global remapping probability, novelty response |

## Category 3: Connectivity

Для связей между популяциями нейронов:

| Что извлекать | Примеры |
|---|---|
| **Local connectivity** | connection probability (Pconn), synaptic strength (EPSP/CPSP amplitude, pA or mV), short-term plasticity (paired-pulse ratio), contact multiplicity (number of synapses per connected pair), synapse type (glutamatergic/GABAergic, receptor composition) |
| **Long-range projections** | source → target regions, projection density, topographic organization, conduction delay |
| **Plasticity parameters** | LTP/LTD induction protocols, STDP time constants (τ+, τ−), magnitude of weight change, dependence on pre/postsynaptic firing rate |
| **Neuromodulatory inputs** | Cholinergic, dopaminergic, serotonergic, noradrenergic projections to region; receptor types and effects |

# Procedure

**Этап 1 — Уточнение scope:**

1. Запроси у пользователя обязательные inputs (brain region — обязательно, остальное опционально)
2. Определи, какие из трёх категорий данных наиболее критичны для модели
3. Сформулируй 3-5 поисковых концепций для каждой категории

**Этап 2 — Поиск литературы:**

1. Делегируй поиск навыку `search-strategy` для каждой категории данных отдельно
2. Для Category 1 (Neuron Types) — акцент на review articles + articles with electrophysiological characterization. Ключевые слова: названия brain region + "interneuron", "pyramidal", "electrophysiology", "patch clamp", "immunohistochemistry", маркеры (PV, SST, VIP), firing pattern terms ("fast-spiking", "regular-spiking")
3. Для Category 2 (Firing Patterns) — акцент на in vivo recordings, calcium imaging, behavior. Ключевые слова: "place cell", "grid cell", "head direction", "phase precession", "theta modulation", "firing rate" + название brain region
4. Для Category 3 (Connectivity) — акцент на paired recordings, optogenetics, rabies tracing. Ключевые слова: "connection probability", "synaptic", "projection", "circuit", connectome", "paired recording" + названия brain regions
5. Объедини результаты, удали дубликаты
6. Сохрани лог поиска в `output/logs/search_log_<region>_data_mining.md`

**Этап 3 — Фильтрация по абстрактам:**

1. Прочитай абстракты топ-кандидатов через `read_article` (id, summary: true)
2. Для каждой категории отбери 10-30 наиболее релевантных статей
3. Критерии включения:
   - Статья содержит КОНКРЕТНЫЕ данные (числа или чёткие качественные описания) по одной из трёх категорий
   - Экспериментальная работа (не purely computational/modeling без данных)
   - Тот же вид животного/препарат, что интересует пользователя (если уточнено)
4. Критерии исключения:
   - Review без новых данных (использовать только если не хватает первичных источников)
   - Purely computational без экспериментальной валидации
   - Статьи по другим brain regions без сравнительных данных
5. Покажи shortlist пользователю: количество статей по каждой категории, обоснование — дождись подтверждения

**Этап 4 — Глубокое чтение и извлечение данных:**

1. Для каждой статьи из shortlist используй субагента @reader
2. Инструкция для @reader:
   - Извлекай ВСЕ численные параметры по релевантным категориям (even from Methods)
   - Для каждого параметра указывай: название, значение, единицы измерения, разброс (SD/SEM), условия получения (температура, anesthesia, behavioral state, age...)
   - Если чисел нет, но есть качественные оценки («larger than...», «increased...», «fast-spiking») — извлекай и пометь как qualitative
   - Если информация по какой-либо из трёх категорий в статье отсутствует — явно сообщи об этом
   - Цитируй источник: Author (Year), страница/секция
3. Сохраняй конспекты в `output/notes/<id>_<short_title>.md`
4. Запускай несколько @reader параллельно для ускорения
5. НИКОГДА не загружай полные тексты статей в контекст координатора

**Этап 5 — Синтез данных:**

1. Передай все конспекты субагенту @synthesizer
2. Режим: «comparative parameter table» + «cross-validation»
3. Задачи synthesizer:
   - Сгруппировать все извлечённые параметры по трём категориям
   - Для каждого параметра собрать значения из разных статей в единую таблицу
   - Отметить согласие/противоречия между источниками
   - Выделить диапазоны значений (min, max, typical)
   - Пометить evidence type для каждой записи: `quantitative` (число), `qualitative` (описание), `inferred` (косвенно)
   - Выявить пробелы: какие параметры не найдены ни в одной статье
4. Результат сохранить в `output/drafts/synthesis_data_mining_<region>.md`

**Этап 6 — Финальный отчёт:**

1. Передай синтез субагенту @writer или собери отчёт самостоятельно
2. Writer создаёт финальный документ по шаблону из секции Output format
3. Результат: `output/drafts/data_mining_<region>_<date>.md`

# Output format

Текст на АНГЛИЙСКОМ языке. Структура:

```markdown
# Data Mining for Simulation: [Brain Region]

**Modeling context:** [краткое описание целевой модели]
**Date:** YYYY-MM-DD
**Articles analyzed:** N (full list in References)

---

## Section 1 — Neuron Types in [Region]

### Type 1: [Neuron type name]
- **Markers:** [genetic/biochemical profile]
- **Location:** [layer/lamina]
- **Morphology:** [key morphological features]

#### Electrophysiological Properties

| Parameter | Value | Range (min–max) | N (articles) | Evidence | Sources |
|-----------|-------|-----------------|--------------|----------|---------|
| Resting potential (mV) | −65 | −70 to −60 | 4 | quantitative | Author1, Author2... |
| Input resistance (MΩ) | 120 | 80–200 | 3 | quantitative | Author3, Author4... |
| Spike half-width (ms) | 0.35 | 0.25–0.45 | 5 | quantitative | ... |
| Firing type | fast-spiking | — | 7 | qualitative | ... |
| Adaptation ratio | 0.9 | 0.7–1.1 | 2 | quantitative | ... |

#### Functional Properties (if available)

| Property | Description | Evidence | Sources |
|----------|------------|----------|---------|
| Theta modulation | Strong, phase-locked to trough | qualitative | Author1 |
| Behavioral correlate | Active during running | qualitative | Author2 |

#### Neuromodulation (if available)

| Modulator | Effect | Evidence | Sources |
|-----------|--------|----------|---------|

### Type 2: [Neuron type name]
...

---

## Section 2 — Firing Patterns in [Region]

### Cell population: [e.g., CA1 place cells]

| Parameter | Value | Range | N (articles) | Evidence | Sources |
|-----------|-------|-------|--------------|----------|---------|
| Place field size (cm) | 25 | 15–40 | 8 | quantitative | ... |
| Peak firing rate (Hz) | 12 | 5–25 | 6 | quantitative | ... |
| Mean firing rate (Hz) | 1.5 | 0.5–3.0 | 6 | quantitative | ... |
| Theta phase precession (°/cm) | −5.2 | −3 to −8 | 3 | quantitative | ... |

### Cell population: [e.g., MEC grid cells]
...

---

## Section 3 — Connectivity

### Local connections within [Region]

| Pre → Post | Pconn | EPSP/C/IPSP/C (amplitude) | Short-term plasticity | N (articles) | Evidence | Sources |
|------------|-------|--------------------------|-----------------------|--------------|----------|---------|
| PV+ IN → Pyr | 0.65 | IPSC 120 pA | Depression (PPR 0.7) | 3 | quantitative | ... |
| Pyr → SST+ IN | 0.4 | EPSC 45 pA | Facilitation (PPR 1.4) | 2 | quantitative | ... |

### Long-range projections

| Source → Target | Type | Density/Strength | Evidence | Sources |
|-----------------|------|------------------|----------|---------|
| MEC LII → CA1 (SLM) | Glutamatergic (TA) | Moderate | qualitative | ... |
| CA1 → Subiculum | Glutamatergic | Dense | qualitative | ... |

### Synaptic plasticity parameters

| Synapse type | Plasticity type | Induction protocol | Change magnitude | Evidence | Sources |
|--------------|-----------------|--------------------|------------------|----------|---------|

---

## Section 4 — Data Gaps & Recommendations

### Missing quantitative data:
- [List parameters that were searched but not found numerically]

### Parameters with only qualitative evidence:
- [List parameters where only descriptive data exists]

### Conflicting data:
- [Cases where different studies report contradictory values]

### Recommendations for model:
- Which parameters are solid enough to use directly
- Which require sensitivity analysis due to uncertain values
- Which must be treated as free parameters in optimization

---

## References

[Chicago Author-Date format, all articles cited in tables above]
```

# Quality bar (self-check)

- [ ] Brain region уточнён у пользователя до начала поиска
- [ ] Поиск выполнен через `search-strategy` для каждой из трёх категорий
- [ ] Каждый параметр в таблицах имеет ссылку на конкретный источник
- [ ] Для quantitative данных указаны: значение, единицы измерения, разброс (если доступен)
- [ ] Для qualitative данных явно указано «qualitative» в колонке Evidence
- [ ] Параметры, которые искались но не найдены, перечислены в Section 4
- [ ] Противоречия между источниками явно отмечены
- [ ] Полный текст НИ ОДНОЙ статьи не загружался в контекст координатора (только через @reader)
- [ ] Все поисковые запросы сохранены в лог
- [ ] Каждый этап воронки показан пользователю с чекпоинтом
- [ ] Текст отчёта на английском языке
- [ ] Нет выдуманных данных — если в литературе нет цифр, честно сказано об этом

# Anti-patterns

- ❌ Заменять отсутствие численных данных выдуманными значениями — если нет цифр, отметить как «qualitative» или «not found»
- ❌ Начинать чтение полных текстов до фильтрации по абстрактам
- ❌ Загружать несколько полных текстов в контекст координатора (всегда через @reader)
- ❌ Пропускать чекпоинты и не спрашивать подтверждения пользователя
- ❌ Игнорировать разброс значений в литературе — всегда показывать диапазон (min–max) при наличии нескольких источников
- ❌ Смешивать данные из разных видов животных или препаратов без явной пометки
- ❌ Отбрасывать качественные данные только потому, что они не количественные
- ❌ Искать данные только по одной категории, если пользователь запросил все три
- ❌ Пропускать поиск по полным текстам (через `semantic_search` + `chunks`) — многие параметры спрятаны глубоко в Methods/Results
- ❌ Считать отсутствие данных в абстрактах отсутствием в статье — проверять через @reader

# Examples

**Input:** «Мне нужны данные для модели CA1 hippocampus: какие там типы интернейронов, их электрофизиология, как они связаны с пирамидными клетками, и параметры place fields для пирамид.»

**Output (ход работы):**
1. Уточнение: mouse, all three categories, essential detail
2. Поиск по трём направлениям → ~120 статей найдено
3. Фильтрация по абстрактам → 45 статей в shortlist
4. Глубокое чтение через @reader → 45 конспектов в `output/notes/`
5. Синтез → сводные таблицы:
   - Section 1: PV+ basket cells, SST+ O-LM cells, CCK+ basket cells, VIP+ IS cells, Axo-axonic cells, Bistratified cells — для каждого: RMP, Rin, spike width, firing type, маркеры
   - Section 2: CA1 place cells — field size 20–35 cm, peak firing rate 10–20 Hz, theta phase precession −4 to −8°/cm
   - Section 3: PV→Pyr Pconn ≈ 0.6, IPSC 80–150 pA; SST→Pyr distal dendrites; CA3→CA1 Schaffer collateral synapse — LTP with STDP τ+ ≈ 16 ms, τ− ≈ 34 ms
   - Section 4: Quantitative gap — CCK+ connectivity probability not found numerically; SST→Pyr synapse strength — only qualitative
6. Финальный отчёт → `output/drafts/data_mining_ca1_2026-05-06.md`

**Input:** «Построй модель grid cell network в MEC LII. Какие там нейроны и как они связаны?»

**Output:**
1. Поиск → 80 статей → shortlist 35
2. Секция 1: Stellate cells (reelin+, calbindin−), Pyramidal cells (calbindin+, reelin−), PV+ interneurons (fast-spiking), SST+ interneurons. Для каждого — электрофизиология.
3. Секция 2: Grid spacing 30–80 cm (increases along dorsoventral axis), grid orientation, theta modulation of grid cells.
4. Секция 3: Stellate↔Stellate recurrent connections (Pconn ≈ 0.01–0.02), PV+ IN→Stellate (Pconn ≈ 0.4–0.6), SST+ IN→Stellate distal dendrites.
5. Секция 4: Quantitative gap — exact synaptic weights for recurrent MEC connections not found; only qualitative data.
