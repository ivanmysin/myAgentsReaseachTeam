---
name: simulation-spec
description: Convert a validated data-mining report into a concrete simulation specification (technical task) for a coding agent to implement a computational neural network model. Produces architectural decisions, parameter tables, and optimization setup grounded in experimental data.
---

# Purpose

Превратить структурированный отчёт `data-mining-for-simulation` в спецификацию (техническое задание) для реализации вычислительной модели. Спецификация содержит все проектные решения: архитектура сети, фиксированные и свободные параметры, входные сигналы, цель оптимизации, критерии валидации. Формат рассчитан на то, чтобы кодинговый агент мог реализовать модель без дополнительных уточнений.

# When to use

Активируй этот навык когда:
- Пользователь завершил `data-mining-for-simulation` и валидировал отчёт
- Нужно принять архитектурные решения на основе собранных данных
- Требуется формализовать «что именно моделируем и оптимизируем»
- Задача: «преврати отчёт в спецификацию для кодинг-агента»
- Пользователь хочет зафиксировать design decisions перед реализацией

# Inputs needed

Перед началом уточни у пользователя:

1. **Путь к отчёту data-mining** — файл `output/drafts/data_mining_<region>_<date>.md` (обязательно)
2. **Феномен для воспроизведения** — что именно модель должна демонстрировать? Примеры:
   - «Theta-modulated place cell activity in CA1»
   - «Gamma oscillation emergence in CA3 recurrent network»
   - «Grid cell pattern formation in MEC LII»
   - «Phase precession of place cells»
3. **Тип модели** (уточни, если не ясно из контекста):
   - `feedforward` — вход → обработка → выход (например, transformation of grid-cell input to place-cell output)
   - `recurrent` — сеть с обратными связями (например, attractor network)
   - `E-I network` — взаимодействие возбуждающих и тормозных популяций
   - `multi-region` — несколько связанных brain regions
4. **Цель оптимизации** (уточни, если не указано):
   - Подогнать firing rates популяций к экспериментальным данным
   - Воспроизвести паттерн разрядов (place field, theta phase precession)
   - Достичь заданной ритмичности (частота oscillations)
   - Минимизировать разницу с эталонным сигналом
5. **Ограничения** (если есть):
   - Максимальное число популяций / n_units (вычислительные ресурсы)
   - Обязательные или исключённые типы нейронов
   - Особые требования к воспроизводимости

# Procedure

**Этап 1 — Загрузка и анализ отчёта:**

1. Прочитай файл отчёта data-mining
2. Извлеки три сводные таблицы параметров из секций 1-3 отчёта
3. Извлеки data gaps из секции 4
4. Составь «инвентаризацию»: какие типы нейронов, какие связи, какие firing patterns задокументированы

**Этап 2 — Архитектурные решения (это ключевой этап — здесь нужен диалог):**

Для каждого решения примени правило: **если данные есть в отчёте → используй их; если данных нет → предложи обоснованный выбор и пометь как «assumption, needs sensitivity analysis».**

2.1 **Выбор популяций:**
   - Какие типы нейронов включаем как отдельные популяции?
   - Какие группируем (например, все PV+ basket cells → одна популяция «fast-spiking IN»)?
   - Для каждой популяции: сколько `n_units` (независимых каналов)?
     - `n_units = 1` если популяция однородна или моделируется как единый пул
     - `n_units > 1` если нужно несколько экземпляров с разными параметрами
   - Покажи таблицу: имя популяции | типы нейронов | n_units | обоснование

2.2 **Выбор входов:**
   - Какие внешние сигналы подаются на сеть?
   - Типы входов из экспериментального контекста:
     - **Theta rhythm** (VonMises-like, 6-10 Hz) — если моделируется hippocampus
     - **Constant background** (ConstantRate-like) — spontaneous activity
     - **Spatial/task input** — если моделируется поведение (place, grid, etc.)
     - **Neuromodulatory** — если важен ACh, DA, etc.
   - Для каждого входа: тип сигнала, параметры (из отчёта, секция 2)

2.3 **Выбор связей (connectivity):**
   - Какие проекции включаем (из секции 3 отчёта)?
   - Для каждой проекции: pre → post, вероятность связи, сила, тип пластичности
   - Приоритет: известные связи с quantitative данными > qualitative > inferred
   - Решается вопрос о рекуррентных связях (да/нет, какие популяции)

2.4 **Выбор модели популяции:**
   - Если моделируются firing rates и population dynamics →  Izhikevich meanfield или Wison-Cowan
   - Если нужно распределение потенциалов → FokkerPlanck
   - Обоснование выбора

2.5 **Выбор модели синапса:**
   - StaticSynapse — если пластичность не важна
   - TsodyksMarkramSynapse — если важна кратковременная пластичность (депрессия/фасилитация)
   - NMDASynapse — если важен медленный NMDA-компонент
   - Выбор на основе данных из секции 3 отчёта

**Этап 3 — Распределение параметров: fixed vs trainable:**

1. Для каждой популяции — таблица параметров:
   - Параметр | Значение из отчёта | Fixed/Trainable | Диапазон для оптимизации | Обоснование

2. Для каждого синапса — таблица параметров:
   - Параметр | Значение из отчёта | Fixed/Trainable | Диапазон для оптимизации | Обоснование

3. **Правила распределения:**
   - `Fixed`: параметр, надёжно измеренный в 1+ независимых исследованиях (quantitative evidence, малый разброс)
   - `Trainable`: параметр с qualitative-only данными, большим разбросом, или отсутствующий в литературе (из Section 4 отчёта)
   - `Trainable с узким диапазоном`: quantitative данные есть, но разброс высок (можно «докрутить» в пределах измеренного диапазона)

**Этап 4 — Определение цели оптимизации:**

1. Сформулируй, что именно оптимизируется:
   - **Target signal**: какой exactly сигнал модель должна воспроизвести?
     - Firing rate trajectory во времени (если эталон — запись)
     - Статистические характеристики (mean rate, theta modulation index, burst probability)
     - Пространственные паттерны (place field shape, grid spacing)
   - **Loss function**:
     - MSE между firing rate популяции и целевым сигналом
     - Composite loss (основной MSE + stability penalty)
   - **Free parameters**: какие параметры варьируются оптимизатором
   - **Fixed parameters**: какие зафиксированы из литературы

2. Сформулируй критерии успеха:
   - «Firing rate популяции X попадает в диапазон Y-Z Гц»
   - «Theta modulation index > 0.3»
   - «Place field size 20-35 cm (within experimental range)»

**Этап 5 — Выбор технических параметров симуляции:**

1. `dt` (шаг интегрирования): стандартно 0.1-0.5 ms для популяционных моделей
2. `integrator`: RK4 по умолчанию (точность), Euler для быстрого прототипирования
3. `T` (длительность симуляции): достаточная для наблюдения феномена (обычно 1000-5000 ms)
4. `optimizer`: Adam с learning rate 1e-3 → 1e-4
5. `epochs`: 100-500 начально, с возможностью увеличить

**Этап 6 — Сборка спецификации:**

1. Передай все решения субагенту @writer
2. Writer создаёт финальную спецификацию по шаблону из секции Output format
3. Результат: `output/drafts/spec_<region>_<date>.md`

# Output format

Текст на АНГЛИЙСКОМ языке (спецификация для кодинг-агента):

```markdown
# Simulation Specification: [Model Name]

**Based on report:** `[path to data-mining report]`
**Date:** YYYY-MM-DD
**Model type:** [feedforward / recurrent / E-I / multi-region]
**Phenomenon to reproduce:** [brief description]

---

## 1. Network Architecture

### Diagram

```
[Input: theta] ──→ [Pop: Exc (Pyr)] ──→ [Pop: Inh (PV+)]
                         │    ↑               │
                         └────┘               │
                         (recurrent)    (feedback inhibition)
```

### Populations

| Name | Neuron types | n_units | Model | Rationale |
|------|-------------|---------|-------|-----------|
| Pyr | CA1 pyramidal cells | 4 | IzhikevichMeanField | Place cells with diverse field locations |
| PV | PV+ basket cells | 2 | IzhikevichMeanField | Fast-spiking, perisomatic inhibition |
| SST | SST+ O-LM cells | 1 | IzhikevichMeanField | Dendritic inhibition |

### Inputs

| Name | Type | Signal | Rationale |
|------|------|--------|-----------|
| theta | VonMises | 8 Hz, R=0.5, mean_rate=20 Hz | Theta rhythmic drive from medial septum |
| bg | ConstantRate | 5 Hz | Background spontaneous activity |

### Connections

| Name | Pre → Post | Type | Pconn | Rationale |
|------|-----------|------|-------|-----------|
| theta→Pyr | theta → Pyr | TsodyksMarkram | 1-to-all | Theta-modulated excitatory drive |
| Pyr→PV | Pyr → PV | StaticSynapse | 1-to-all | Feedforward excitation of interneurons |
| PV→Pyr | PV → Pyr | StaticSynapse | all-to-all | Perisomatic feedback inhibition |
| Pyr→Pyr | Pyr → Pyr | TsodyksMarkram | sparse (0.1) | Recurrent excitation |

---

## 2. Population Parameters

### Pyr (CA1 pyramidal cells)

Based on data-mining report Section 1, Type: Pyramidal cells.

| Parameter | Value from literature | Fixed/Trainable | Range | Rationale |
|-----------|----------------------|-----------------|-------|-----------|
| tau_pop | 1.0 | Fixed | — | Dimensionless, standard value |
| alpha | 0.5 | Fixed | — | Dimensionless, standard value |
| a (adaptation) | 0.02 | Fixed | — | Corresponds to regular-spiking |
| b | 0.2 | Fixed | — | Corresponds to regular-spiking |
| w_jump | 0.1 | Fixed | — | Standard value |
| Delta_I | 0.5 ± 0.2 | Trainable | [0.3, 0.9] | Controls heterogeneity; qualitative evidence |
| I_ext | 0.5 ± 0.3 | Trainable | [0.0, 1.5] | Sets baseline excitability; diverse across cells |

### PV (PV+ basket cells)

Based on data-mining report Section 1, Type: PV+ basket cells.

| Parameter | Value from literature | Fixed/Trainable | Range | Rationale |
|-----------|----------------------|-----------------|-------|-----------|
| tau_pop | 1.0 | Fixed | — | Standard |
| alpha | 0.5 | Fixed | — | Standard |
| a (adaptation) | 0.01 | Fixed | — | Lower adaptation — fast-spiking phenotype |
| b | 0.15 | Fixed | — | Lower adaptation |
| w_jump | 0.05 | Fixed | — | Lower adaptation |
| Delta_I | 0.4 ± 0.15 | Trainable | [0.2, 0.7] | Qualitative range |
| I_ext | 0.3 ± 0.2 | Trainable | [0.0, 0.8] | Interneurons receive less external drive |

### SST (SST+ O-LM cells)

Based on data-mining report Section 1, Type: SST+ O-LM cells.

| Parameter | Value from literature | Fixed/Trainable | Range | Rationale |
|-----------|----------------------|-----------------|-------|-----------|
| ... | ... | ... | ... | ... |

---

## 3. Synapse Parameters

### theta→Pyr (VonMises input to pyramidal cells)

| Parameter | Value from literature | Fixed/Trainable | Range | Rationale |
|-----------|----------------------|-----------------|-------|-----------|
| gsyn_max | — | Trainable | [0.0, 0.5] | Not quantified in literature (data gap) |
| tau_f | — | Trainable | [6, 240] | Short-term facilitation possible |
| tau_d | — | Trainable | [2, 15] | — |
| tau_r | — | Trainable | [91, 1300] | — |
| Uinc | — | Trainable | [0.04, 0.7] | — |
| e_r | 0.0 | Fixed | — | Excitatory reversal |

### PV→Pyr (feedback inhibition)

| Parameter | Value from literature | Fixed/Trainable | Range | Rationale |
|-----------|----------------------|-----------------|-------|-----------|
| gsyn_max | IPSC 80-150 pA (quantitative) | Trainable | [-1.0, -0.2] | Converted from pA to dimensionless |
| e_r | −70 mV | Fixed | — | GABA-A reversal |
| pconn | 0.6-0.8 | Fixed | — | Connection probability from literature |

### Pyr→Pyr (recurrent excitation)

| Parameter | Value from literature | Fixed/Trainable | Range | Rationale |
|-----------|----------------------|-----------------|-------|-----------|
| gsyn_max | — | Trainable | [0.0, 0.3] | Not quantified (data gap) |
| pconn | 0.01-0.02 (MEC) | Trainable | [0.0, 0.1] | Qualitative estimate from MEC; CA1 may differ |
| ... | ... | ... | ... | ... |

---

## 4. Optimization Setup

### Target

- **Target signal**: Firing rates extracted from [reference / experimental trace / desired pattern]
- **Target description**: Place-cell-like activity: each Pyr unit should show elevated firing rate (~10-20 Hz) at a specific theta phase, lower rate otherwise. Target signal TBD based on experimental data.
- **Target format**: tf.Tensor [1, T_steps, n_units] — firing rate time series in Hz

### Loss function

| Component | Weight | Description |
|-----------|--------|-------------|
| MSELoss (target) | 1.0 | Match firing rates to target pattern |
| StabilityPenalty | 1e-3 | Penalize NaN / Inf / divergence |

### Free parameters (optimized)

| Parameter group | Count | Description |
|-----------------|-------|-------------|
| Pop Delta_I × 3 populations | 7 | Heterogeneity parameter |
| Pop I_ext × 3 populations | 7 | Baseline excitability |
| Synaptic gsyn_max × 4 connections | 27 | Synaptic weights |
| Synaptic STP params × 2 connections | 16 | Short-term plasticity |

**Total free parameters: ~57**

### Fixed parameters (from literature)

- Neuronal time constants (tau_pop, alpha, a, b, w_jump)
- Reversal potentials (e_r)
- Connection probabilities (pconn)

---

## 5. Simulation Parameters

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| dt | 0.1 ms | Fine enough for RK4, captures sub-ms dynamics |
| Integrator | RK4 | High accuracy for long simulations |
| Simulation duration | 2000 ms | Sufficient for multiple theta cycles (~16 cycles at 8 Hz) |
| Optimizer | Adam | Standard for neural ODE training |
| Learning rate | 1e-3 initial, decay 0.9/100epochs | Standard schedule |
| Epochs | 200-500 | Empirically sufficient for convergence |
| Gradient method | BPTT (or adjoint if T > 500 steps) | Standard; switch to adjoint for memory constraints |

---

## 6. Evaluation & Validation

### Quantitative criteria

| Metric | Target | How to measure |
|--------|--------|----------------|
| Pyr mean firing rate | 1-3 Hz (experimental range) | `tf.reduce_mean(rates['Pyr'])` |
| Pyr peak firing rate | 10-20 Hz | `tf.reduce_max(rates['Pyr'])` |
| Theta modulation index | > 0.3 | FFT at 8 Hz / total power |
| PV firing rate | 10-30 Hz (FS phenotype) | `tf.reduce_mean(rates['PV'])` |
| Stability | No NaN, no divergence | Check `stability_loss < 1.0` |

### Qualitative validation

- Place-cell-like pattern: each Pyr unit should have a preferred theta phase
- Phase precession: firing phase should advance across the field (if spatial input provided)
- PV should fire at theta trough (experimental observation)
- SST should fire at theta peak (experimental observation)

---

## 7. Implementation Notes

### Data gaps that affect the model

- [List from report Section 4, with impact on model design]
- Example: «SST→Pyr synapse strength — only qualitative. Will be treated as free parameter and requires sensitivity analysis.»
- Example: «CCK+ connectivity — not found. CCK+ cells excluded from this model version.»

### Assumptions made

- [List assumptions not directly supported by literature]
- Example: «Recurrent Pyr→Pyr connection assumed sparse (pconn ~0.02) based on MEC data; CA1 data not available.»
- Example: «All PV+ subtypes (basket, axo-axonic, bistratified) grouped into one population — fast-spiking phenotype.»

### Recommended sensitivity analyses

- Vary gsyn_max of PV→Pyr ±50% — check stability of Pyr firing rate
- Vary I_ext of Pyr ±30% — check place field emergence
- Compare Static vs TsodyksMarkram synapses for theta→Pyr (is STP critical?)

### Future extensions

- [Optional: what could be added in next model version]

---

## 8. References

[Chicago Author-Date format; subset from data-mining report that directly informs parameter choices]
```

# Quality bar (self-check)

- [ ] Отчёт data-mining прочитан и все три секции учтены
- [ ] Архитектурные решения явно обоснованы ссылками на отчёт или помечены как «assumption»
- [ ] Для КАЖДОГО параметра указано: Fixed или Trainable, с обоснованием
- [ ] Trainable параметры имеют диапазон для оптимизации
- [ ] Явно указаны параметры, взятые из quantitative данных vs qualitative vs data gaps
- [ ] Цель оптимизации сформулирована конкретно (не «сделать хорошо», а «MSE между rate и target»)
- [ ] Критерии валидации количественные (числа, диапазоны) где возможно
- [ ] Data gaps из отчёта перенесены в секцию Implementation Notes с указанием влияния на модель
- [ ] Все assumptions явно перечислены
- [ ] Спецификация самодостаточна — кодинг-агент может реализовать без дополнительных вопросов
- [ ] Спецификация НЕ содержит код на Python и НЕ ссылается на конкретные API NeuralTide (только концептуально: «модель популяции Izhikevich mean-field», «синапс с кратковременной пластичностью»)
- [ ] Все ссылки на литературу из отчёта сохранены

# Anti-patterns

- ❌ Пропускать этап диалога с пользователем по архитектурным решениям (Этап 2) — это ключевые design decisions
- ❌ Делать все параметры trainable «на всякий случай» — fixed параметры из литературы экономят ресурсы оптимизации
- ❌ Игнорировать data gaps из отчёта — их нужно явно перенести в секцию Implementation Notes
- ❌ Давать необоснованные ranges для trainable параметров — каждый range должен быть мотивирован (из литературы, из физических ограничений, или ±X% от typical value)
- ❌ Смешивать dimensionless и dimensional параметры — выбрать одну систему и придерживаться её
- ❌ Пропускать quantitative validation criteria — «модель должна работать» не является спецификацией
- ❌ Забывать про stability penalty в loss function — для популяционных моделей это критично
- ❌ Не указывать n_units явно (кодинг-агент не знает, сколько каналов создавать)

# Examples

**Input:** «Вот отчёт `data_mining_ca1_2026-05-06.md`. Нужна модель, которая воспроизводит theta-modulated firing CA1 place cells с участием PV+ и SST+ интернейронов.»

**Output (ход работы):**
1. Этап 1 — загрузка отчёта: 3 популяции нейронов (Pyr, PV+, SST+), данные по connectivity, place field параметры
2. Этап 2 — диалог с пользователем:
   - Популяции: Pyr (n=4, place cells), PV (n=2, FS), SST (n=1, dendritic inh)
   - Входы: theta (VonMises, 8 Hz), background (ConstantRate)
   - Связи: theta→Pyr, theta→PV, theta→SST, Pyr→PV, PV→Pyr, SST→Pyr, Pyr→Pyr (recurrent)
   - Модели: IzhikevichMeanField для всех, StaticSynapse для fast connections, TsodyksMarkram для theta→Pyr
3. Этап 3 — распределение параметров: tau_pop/a/b/w_jump fixed, Delta_I/I_ext trainable, gsyn_max trainable
4. Этап 4 — цель: MSE между firing rate и целевым place-cell паттерном
5. Этап 5 — dt=0.1, RK4, Adam(1e-3), 300 epochs
6. Финальная спецификация → `output/drafts/spec_ca1_theta_2026-05-06.md`
