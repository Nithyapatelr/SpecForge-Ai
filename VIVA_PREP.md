# Master Viva Defense Preparation & Defense Guide

This question bank prepares the candidate for technical, methodological, and statistical examination during their Master Thesis Viva Defense. Questions are structured into five core defense domains, accompanied by clear, authoritative model answers.

---

## Domain 1: System Architecture & Technical Design

### Q1.1: Why introduce a pre-analysis annotation layer rather than embedding requirement analysis directly inside multi-agent frameworks like MetaGPT or ChatDev?
**Model Answer:**
> "Embedding pre-analysis inside existing framework SOPs requires intrusive code modifications, creates tight coupling to specific framework releases, and increases execution overhead during agent collaboration loops. SpecForge AI adopts a **Shift-Left, Non-Invasive Adapter Design Pattern**. By intercepting raw requirement prompts at the ingress boundary, classifying intent into RIT categories, and injecting structured pre-analysis annotations, SpecForge remains framework-agnostic. Both MetaGPT and ChatDev execute their standard SOPs without internal modifications, while benefiting from reduced ambiguity and clear architectural constraints."

### Q1.2: How does SpecForge handle compound requirement sentences that contain multiple conflicting modal directives?
**Model Answer:**
> "SpecForge utilizes an atomic preprocessing pipeline (`specforge.preprocessing.segmenter`). The pipeline first performs sentence tokenization using spaCy (`en_core_web_sm`). When a sentence contains compound structures (e.g., coordinating conjunctions 'and', 'but' joining clauses with modal verbs 'shall', 'must', 'should'), the segmenter splits the compound sentence into sibling atomic requirements. Each atomic requirement inherits parent metadata while receiving independent RIT intent classification and ambiguity smell scoring."

---

## Domain 2: Empirical Methodology & MAST Failure Taxonomy

### Q2.1: Why did you adopt the MAST Taxonomy (Cemri et al., 2025) rather than creating a custom failure classification?
**Model Answer:**
> "Creating an ad-hoc failure classification risks introducing subject-matter bias and lacks external validity. The Multi-Agent System Failure Taxonomy (MAST), published by UC Berkeley researchers in 2025, provides a standardized, peer-reviewed 14-mode classification across Specification Issues, Inter-Agent Misalignment, and Task Verification. Leveraging MAST allows SpecForge to evaluate failure reduction against an independently established benchmark, ensuring direct comparability with contemporary multi-agent research."

### Q2.2: How does the LLM-as-a-Judge trace evaluator ensure reliable tagging without hallucinating failures?
**Model Answer:**
> "The MAST judge (`specforge.failure_logging.mast_judge`) employs three safeguards:
> 1. **Structured System Prompting**: The system prompt embeds all 14 MAST definitions with explicit confidence scoring instructions and requires output formatted strictly as a JSON array.
> 2. **Defensive Parsing & Fallbacks**: If parsing fails or the API is unavailable, the judge falls back to heuristic pattern matching against known failure trace keywords.
> 3. **Trace Chunking**: Long execution traces are split into overlapping 10,000-character chunks with a 1,000-character overlap to prevent context truncation."

---

## Domain 3: Statistical Rigor & Empirical Analysis

### Q3.1: Why did you use Bootstrap Confidence Intervals rather than standard parametric t-tests for failure reduction?
**Model Answer:**
> "Parametric t-tests assume a normal distribution of paired differences. Multi-agent execution failure counts across software tasks are typically non-normal, skewed, and bounded at zero. Non-parametric **10,000-iteration Bootstrap resampling with replacement** constructs empirical 95% confidence intervals ([2.5%, 97.5%]) without relying on Gaussian distribution assumptions, providing a robust statistical estimate of mean failure reduction."

### Q3.2: What does the Point-Biserial correlation measure in your evaluation engine?
**Model Answer:**
> "Point-biserial correlation ($r_{pb}$) measures the strength and direction of association between a continuous variable (SpecForge's requirement ambiguity score from 0.0 to 1.0) and a binary indicator (whether downstream execution produced a failure: 1, or succeeded cleanly: 0). A statistically significant positive correlation ($r_{pb} > 0, p < 0.05$) demonstrates that higher requirement ambiguity scores directly predict downstream multi-agent execution failures."

---

## Domain 4: Related Work & Comparative Frameworks

### Q4.1: How does SpecForge AI differ from the MARE framework (Jin et al., 2024)?
**Model Answer:**
> "MARE is a generative 5-agent pipeline designed to draft formal requirements specifications from scratch. SpecForge AI is a **diagnostic pre-analysis and annotation framework** designed to optimize downstream multi-agent code generation engines (MetaGPT and ChatDev). In our head-to-head evaluation, SpecForge's annotated specifications achieved superior completeness against ground-truth checklists, higher machine-parseable structure scores, and lower ambiguity smell rates compared to MARE's multi-agent outputs."

### Q4.2: How did you handle the absence of an open-source code release for MARE?
**Model Answer:**
> "For complete intellectual honesty, we explicitly documented in our literature review and limitations disclosure that MARE does not have a public open-source code repository. SpecForge includes a faithful **Reimplementation** of MARE's 5-agent, 4-stage pipeline based strictly on the architecture described by Jin et al. (2024). Every function in `specforge.comparison.mare_runner` is documented with explicit reimplementation disclaimers."

---

## Domain 5: Technical Trade-offs & Future Directions

### Q5.1: What are the primary limitations of your current evaluation?
**Model Answer:**
> "We explicitly disclose three main threats to validity in `LIMITATIONS_DRAFT.md`:
> 1. **Sample Size ($N=15$)**: The evaluation batch comprises 15 paired tasks, so results represent directional evidence rather than population scale.
> 2. **LLM Temperature Sensitivity**: LLM non-determinism introduces trace output variance.
> 3. **Foundation Model Lock-in**: Current scoring relies on Anthropic Claude Sonnet API; future work will benchmark offline open-weights models like Llama-3-70B."

### Q5.2: What are the immediate next steps for scaling SpecForge AI?
**Model Answer:**
> "Future work includes:
> 1. Fine-tuning a local BERT transformer for zero-latency, offline RIT intent classification.
> 2. Expanding the evaluation benchmark to 100+ open-source GitHub repositories.
> 3. Integrating interactive human-in-the-loop clarification modals directly into the FastAPI service for unresolved ambiguity smells."
