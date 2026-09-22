# Threats to Validity & Limitations Disclosure

A rigorous empirical study requires an open and transparent evaluation of threats to validity. This document details seven key limitations and threats affecting SpecForge AI's experimental findings, categorizing them across Internal, External, Construct, and Statistical Conclusion validity (*Wohlin et al., 2012*).

---

## 1. Threats to Internal Validity

### 1.1 Non-Deterministic LLM Behavior & Temperature Sensitivity
Multi-agent LLM executions inherently exhibit non-deterministic behavior due to token sampling variance ($T > 0$), floating-point non-determinism in parallel GPU execution, and background API updates. While SpecForge sets default temperature parameters ($T=0.2$) and seeds random state variables where supported, slight variance in generated trace outputs across repeated runs remains possible.

### 1.2 Reimplementation Validity of the MARE Framework
The official MARE paper (*Jin et al., 2024*, arXiv:2405.03256) does not provide a publicly available open-source code repository. To conduct head-to-head specification quality comparisons, SpecForge relies on a faithful **reimplementation** of MARE's 5-agent, 4-stage pipeline based on the architecture described in the paper. Although the reimplementation matches the described agent roles, prompts, and stage transitions, minor implementation disparities between our reimplementation and the authors' proprietary baseline may exist.

---

## 2. Threats to External Validity

### 2.1 Benchmark Task Suite Sample Size ($N = 15$)
The empirical evaluation suite comprises $N = 15$ diverse software task descriptions spanning small-to-medium enterprise domains (e.g., API services, lending systems, inventory trackers). While this sample size provides strong exploratory signal, statistical inferences must be interpreted as **directional evidence** rather than generalizable population facts. Enterprise codebases with hundreds of interconnected microservices or legacy domain rules may introduce emergent failure modes not captured in 15 benchmark tasks.

### 2.2 Foundation Model Lock-In (Anthropic Claude API)
SpecForge's RIT classification, LLM ambiguity scoring, and MAST trace judging currently utilize Anthropic's Claude Sonnet API. While the architecture is model-agnostic, empirical performance metrics (such as classification accuracy and ambiguity correlation) may vary when using alternative foundation models (e.g., OpenAI GPT-4o, Llama-3-70B, or DeepSeek-R1).

---

## 3. Threats to Construct Validity

### 3.1 Heuristic Ambiguity Smell Coverage Boundaries
SpecForge's heuristic ambiguity detector scans for five established natural language requirement smells: vague quantifiers, passive voice, weak directives, subjective adjectives, and un-anchored open conditionals. While these cover major syntactic ambiguity types (*Femmer et al., 2017*), subtle semantic ambiguities—such as domain-specific jargon conflicts, circular business logic, or implicit environmental constraints—may bypass rule-based heuristic detection.

### 3.2 Construct Validity of LLM-as-a-Judge Trace Evaluation
Using an LLM (Claude Sonnet) as an automated judge to tag MAST failure modes in execution logs introduces potential evaluator bias or mis-classification. To mitigate this threat, SpecForge implements defensive JSON schema validation, strict 14-mode system prompt definitions, and a rule-based fallback keyword parser for unconfigured environments. Nonetheless, automated LLM judging remains an approximation of human expert annotation.

---

## 4. Threats to Statistical Conclusion Validity

### 4.1 Contingency Table Low Expected Cell Counts
In the Chi-Square ($\chi^2$) Test of Independence between RIT requirement labels and MAST failure categories, certain sparse combinations (e.g., *Actor Permission* vs. *Task Verification*) yield low cell counts ($< 5$). To preserve statistical validity, SpecForge automatically filters zero-sum matrix dimensions and reports degrees of freedom explicitly. However, Fisher's Exact Test or Monte Carlo Chi-Square approximations should be employed in future larger-scale evaluations.

---

## 5. Summary Matrix of Validity Threats

| Threat Category | Specific Limitation | Primary Mitigation Strategy | Impact Level |
|---|---|---|---|
| **Internal** | Non-deterministic LLM behavior | Standardized low-temperature settings ($T=0.2$) | Moderate |
| **Internal** | MARE reimplementation disparity | Explicit architectural matching & docstring disclaimers | Moderate |
| **External** | Benchmark sample size ($N=15$) | 10,000-iteration Bootstrap CI reporting & explicit caveats | High |
| **External** | Dependence on Claude Sonnet API | Decoupled model provider interface for future LLMs | Low |
| **Construct** | Heuristic smell rule boundaries | Hybrid architecture combining heuristics with LLM scoring | Moderate |
| **Construct** | LLM-as-a-Judge evaluation bias | Defensive schema parsing & dual-mode fallback judge | Moderate |
| **Statistical** | Low expected counts in Chi-Square | Matrix dimension pruning & 95% Bootstrap interval estimation | Low |
