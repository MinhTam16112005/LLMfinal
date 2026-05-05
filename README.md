# LLMfinal

Code and reproduction artifacts for the Intro to LLM final report on R2-Guard.

This repository is based on the official R2-Guard code release and adds a controlled reproducibility workflow, environment files, execution scripts, cached scores, and result reports.

Start here:

- `REPRODUCIBILITY.md`: detailed setup, execution status, blockers, and exact reproduction notes.
- `REPRODUCTION.md`: shorter reproduction summary.
- `results/advisor_reproduction_status.md`: report-ready progress summary.
- `results/table2_local_full_deviation.md`: local full-result comparison.
- `results/table2_official_style_balanced_n64_deviation.md`: official-style balanced n64 subset result.

Original R2-Guard notes:

### Evaluations on standard safety benchmark

```bash
bash scripts.sh
```

### Evaluations against jailbreaks

For GCG attack:

```bash
bash scripts.sh
```

In `scripts.sh`, specify the corresponding adversarial string:

- `adv_string_1`: GCG-U1
- `adv_string_2`: GCG-U2
- `adv_string_3`: GCG-V
- `adv_string_4`: GCG-L
- `adv_string_5`: GCG-R

For AutoDAN, TAP, and PAIR attacks:

```bash
bash jailbreak.sh
```

Note: the original released scripts are extensive command banks and require selecting/commenting the experiment to run.
