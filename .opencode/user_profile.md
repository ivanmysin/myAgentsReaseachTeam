# User Profile

Этот файл задаёт специализацию пользователя и предпочтения, которые подгружает агент `Sophia` в начале сессии. Отредактируйте под себя. Если файл пустой или отсутствует — агент работает в универсальном режиме без специализации.

---

## Specialization

**Primary field:** Computational neuroscience
**Subfields:** Hippocampus, memory, spatial navigation, synaptic plasticity

## Research focus

- Hippocampus and related structures (entorhinal cortex, subiculum, septum)
- Neural network models of cognitive function
- Memory (episodic, spatial, working)
- Spatial navigation (place cells, grid cells, head direction cells)
- Attention and its interaction with hippocampal function
- Oscillations (theta, gamma, sharp-wave ripples)
- Synaptic plasticity (LTP, LTD, STDP)

## Typical article types

Primarily experimental papers. User builds computational models based on experimental data.

## Preferred journals (for style calibration)

- Nature Neuroscience
- Neuron
- PLOS Computational Biology
- eLife
- Hippocampus

## Working languages

- **Dialog with agent:** Russian
- **Output texts (drafts, reviews, papers):** English (default). Russian — only on explicit request.
- **Search queries:** English (articles in the library are typically in English)

## Citation style

Chicago Author-Date: `(Smith et al., 2023)` / `Smith et al. (2023) showed that...`

## Output conventions

- Default format: Markdown
- LaTeX: only on explicit request
- Intermediate results saved to `output/`
  - `output/logs/` — session logs
  - `output/notes/` — per-article notes
  - `output/drafts/` — draft texts
  - `output/figures/` — figures (user provides manually)
  - `output/presentations/` — Marp slides
