# On the Suitability of LLM-Driven Agents for Dark Pattern Audits

## Overview

This repository contains the code, datasets, and evaluation artifacts for our PETS paper *On the Suitability of LLM-Driven Agents for Dark Pattern Audits*. The agent navigates CCPA right-to-access (ROA) workflows on data broker websites and classifies dark patterns using one of four prompting strategies.

## Repository Structure

```text
prompts/
├── baseline_zero_shot/                     # L1: Zero-shot
├── zero_shot_role_prompting/               # L2: Zero-shot + Role
├── few_shot_scenaiors_only/                # L3: Few-shot + Role
└── few_shot_role_prompting_with_CoT/       # L4: Few-shot + Role + CoT

broker_dataset/
├── 100_annotated_brokers.csv               # 100 ground-truth brokers (Phase 2)
└── left_test_brokers.csv                   # Remaining brokers (Phase 3 deployment)

ground_truth/                               # Human annotation files

results/                                    # Pre-computed outputs used in the paper

evaluation/
├── section3_dataset.ipynb                  # Annotation agreement analysis
├── RQ1.ipynb                               # Prompting strategy evaluation
└── RQ2.ipynb                               # Workflow execution analysis

```

## Requirements

* macOS 14+ or a compatible Linux environment
* Python 3.13
* Google Chrome
* OpenAI API key (required only for agent execution)

## Setup

```bash
git clone https://github.com/chensun96/agentic-dark-pattern-audits.git
cd agentic-dark-pattern-audits

python3.13 -m venv env
source env/bin/activate

pip install -r requirements.txt

# Create a .env file containing your OpenAI API key
echo "OPENAI_API_KEY=your_key_here" > .env
```

## Running the Agent 

The repository includes the agent implementation used in the study. Re-running the agent requires an OpenAI API key and access to live websites.

All scripts should be executed from the project root directory.

By default, the agent processes URLs listed in:

```text
broker_dataset/100_annotated_brokers.csv
```
To run the agent on a different dataset, modify the `df = pd.read_csv(...)` statement in `prompts/<prompting_strategy>/run_openai.py` to point to the desired input CSV.

Outputs are stored under:
```text
agent_output/<domain>/<taxonomy_type>/<model>/<timestamp>/
```


### L1: Zero-shot (Baseline)

No role framing and no examples.

```bash
source env/bin/activate
python prompts/baseline_zero_shot/run_openai.py
```

### L2: Zero-shot + Role

Adds regulatory expert role framing.

```bash
source env/bin/activate
python prompts/zero_shot_role_prompting/run_openai.py
```

### L3: Few-shot + Role

Adds few-shot examples together with role framing.

```bash
source env/bin/activate
python prompts/few_shot_scenaiors_only/run_openai.py
```

### L4: Few-shot + Role + CoT

Adds chain-of-thought reasoning on top of few-shot examples and role framing. This is the best-performing configuration and the one used for Phase 3 deployment.

```bash
source env/bin/activate
python prompts/few_shot_role_prompting_with_CoT/run_openai.py
```
## Reproducing Paper Results

The `results/` directory contains the pre-computed outputs used in the paper. All reported tables and statistics can be reproduced directly from these artifacts without re-running the agent.

```bash
source env/bin/activate

jupyter notebook evaluation/section3_dataset.ipynb
jupyter notebook evaluation/RQ1.ipynb
jupyter notebook evaluation/RQ2.ipynb
```

### Notebook Outputs

| Notebook                 | Paper Content                              |
| ------------------------ | ------------------------------------------ |
| `section3_dataset.ipynb` | Annotation agreement (Cohen's κ)           |
| `RQ1.ipynb`              | Prompting strategy evaluation (Tables 2–4) |
| `RQ2.ipynb`              | Workflow execution and failure analysis    |

### Environment Sanity Check

Run the following command:

```bash
jupyter nbconvert --to notebook --execute evaluation/section3_dataset.ipynb --stdout | grep "Cohen"
```

Expected output:

```text
Cohen's Kappa: 0.519
Cohen's Kappa: 0.737
```

These values correspond to the inter-annotator agreement scores reported in the paper for the initial 20-broker calibration set and the second 20-broker calibration set, respectively.
