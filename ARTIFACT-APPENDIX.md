# Artifact Appendix

Paper title: On the Suitability of LLM-Driven Agents for Dark Pattern Audits

Requested Badge(s): Available, Functional, Reproduced

## Description (Required for all badges)
This artifact contains the implementation of an LLM-driven browser agent that audits CCPA data rights request portals for dark patterns. It includes: (a) the agent source code with four prompting strategies, (b) a human-annotated ground truth dataset of 100 data brokers, (c) results for all experimental phases, and (d) Jupyter notebooks that reproduce all quantitative results reported in the paper. 

For artifact evaluation, we provide steps to reproduce our experiments on a small sample of websites so that evaluation can be completed in a reasonable amount of time and cost. Reviewers can verify that the agent produces outputs in the correct format and that the analysis pipeline (evaluation notebooks) generates results consistent with those reported in the paper. The pre-computed full results — generated through the identical process — are also included, allowing reviewers to run all evaluation notebooks (Tables 2–4, RQ2 statistics) directly against the full dataset without re-running the agent.

To reproduce the full experiments as described in the paper, please refer to the main README.       

### Security/Privacy Issues and Ethical Concerns (Required for all badges)

The artifact navigates live public websites using an LLM-driven browser agent and interacts with live websites using Playwright. The agent performs only pre-defined interactions and does not submit requests, transmit personal information, create accounts, or retrieve consumer records. Interaction rates were kept low to
avoid imposing operational burden.

The agent_output directory contains screenshots and interaction logs from real data broker websites these are publicly accessible pages.   

Human annotation data (ground_truth) was produced by the authors; no user study participants are involved.

An OpenAI API key is required to re-run the agent (not needed for the evaluation notebooks).  

## Basic Requirements (Required for Functional and Reproduced badges)

### Hardware Requirements (Required for Functional and Reproduced badges)

The artifact can run on a standard laptop or server with a stable Internet connection. No specialized hardware (e.g., GPU, cluster, or accelerator) is required.
The experiments reported in the paper were conducted on a macOS laptop located in California.

### Software Requirements (Required for Functional and Reproduced badges)

We runned all the code in the following software environments:

- OS: macOS 14+ (Sonoma). 
- Programming Language: Python 3.13                                      
- Python packages: See requirements.txt.                                             
- ML Models: GPT-5 via OpenAI API 
- Datasets: All datasets to run the artifacts are included in the repo:                                                   
    - broker_dataset/100_annotated_brokers.csv - ground truth broker URLs (Phase 2)                     
    - broker_dataset/left_test_brokers.csv — deployment broker URLs (Phase 3)                           
    - ground_truth/ — annotation_agreement.CSVs                                                         
    - results/ — pre-computed agent outputs (prompt_ablation, workflow_execution, deployment)

### Estimated Time and Storage Consumption (Required for Functional and Reproduced badges)

Evaluation notebooks only run a few minutes and require no additional storage
Full agent re-run (all 456 brokers): estimate 100+ hours and need around 40G disk space
Sample data brokers re-run: XXX time and XXX disk space


## Environment (Required for all badges)

### Accessibility (Required for all badges)

Main codebase: https://github.com/chensun96/CCPA_dark_pattern


### Set up the environment (Required for Functional and Reproduced badges)

```bash
git clone https://github.com/chensun96/CCPA_dark_pattern.git
cd CCPA_dark_pattern
python3.13 -m venv env
source env/bin/activate
pip install -r requirements.txt

#### Create a .env file with your OpenAI API key
echo "OPENAI_API_KEY=your_key_here" > .env
```bash

### Testing the Environment (Required for Functional and Reproduced badges)

Replace the following by a description of the basic functionality tests to check
if the environment is set up correctly. These tests could be unit tests,
training an ML model on very low training data, etc. If these tests succeed, all
required software should be functioning correctly. Use code segments to simplify
the workflow, e.g.,

Launch the Docker container, attach the current working directory (i.e., run
from the root of the cloned git repository) as a volume, set the context to be
that volume, and provide an interactive bash terminal:

```bash
docker run --rm -it -v ${PWD}:/workspaces/example-docker-python-pip \
    -w /workspaces/example-docker-python-pip \
    --entrypoint bash example-docker-python-pip:main
```

Then within the Docker container, run:

```bash
./test.sh
```

Include the expected output.

## Artifact Evaluation (Required for Functional and Reproduced badges)


### Main Results and Claims


#### Main Result 1: Prompting strategy ablation (RQ1, Table 2) 

The paper claims that Few-shot + Role + CoT achieves the highest classification accuracy and explanation accuracy across four prompting strategies.  Supported by: Experiment 1 (RQ1.ipynb, Table 2 upper + lower sections)                                
                             

#### Main Result 2: Per-pattern performance (RQ1, Table 3)

The paper claims that under the selected configuration (Few-shot + Role + CoT), agent performs better on detecting the structurally localized patterns than on interaction-dependent patterns.  Supported by: Experiment 1 (RQ1.ipynb, Table 3 section)                                             

####   Main Result 3: Dark pattern prevalence (Table 4)

The paper claims that structural barriers are the most prevalent dark pattern in completed CCPA right-to-access workflows, while ambiguity- and fragmentation-based patterns also appear frequently. Supported by: Experiment 1 (RQ1.ipynb, Table 4 sections)

####   Main Result 3: Workflow execution limits (RQ2)  
Our paper claims that a substantial fraction of workflows cannot be completed autonomously.  Supported by: Experiment 2 (RQ2.ipynb)  

### Experiments

In this section, we provide step-by-step instructions to evaluate our artifacts, test code functionality, and reproduce our main results.



List each experiment to execute to reproduce your results. Describe:
 - How to execute it in detailed steps.
 - What the expected result is.
 - How long it takes to execute in human and compute times (approximately).
 - How much space it consumes on disk (approximately) (omit if <10GB).
 - Which claim and results does it support, and how.

#### Experiment 1: Reproduce Tables 2, 3, and 4 (RQ1) 

This experiment reproduces Main Result 1,2,3. The following script outputs the reconstructed version of Table 2, 3, 4 in paper.
- Time: ~5 human-minutes + ~10 compute-minutes

- Open and run evaluation/RQ1.

```bash
source env/bin/activate
jupyter notebook evaluation/RQ1.ipynb
# Run all cells (Kernel → Restart & Run All)
```

#### Experiment 2: Reproduce RQ2 workflow execution statistics

This experiment reproduces Main Result 4. It parses the verification issue fields from the saved agent outputs and recomputes workflow completion rates and failure distributions.
- Time: 5 human-minutes + ~1 compute-minut
- Open and run evaluation/RQ2.ipynb         
```bash
source env/bin/activate
jupyter notebook evaluation/RQ2.ipynb
# Run all cells (Kernel → Restart & Run All)
```

## Limitations (Required for Functional and Reproduced badges)

Dynamic websites. Data broker websites and ROA workflows may change over time. As a result, re-running the agent may produce different outputs than those reported in the paper; therefore, we provide the original agent outputs and processed datasets used in our analysis.

Geolocation dependent behavior. Some websites may vary privacy disclosures or rights-request workflows based on the visitor's location. The study was conducted from a California-hosted environment, and executions from other regions may observe different behavior.

External dependencies. Agent execution depends on live websites and LLM services. Changes to website content, anti-bot mechanisms, model updates, or the inherent non-determinism of LLMs may affect future executions and lead to results that differ from those reported in the paper.

## Notes on Reusability (Encouraged for all badges)

- The prompting framework and agent framework (in prompts/) can be adapted to audit dark patterns  beyond CCPA data brokers — e.g., opt-out or deletion portals or subscription cancellation flows.  

- The released annotation guidelines, ground-truth dataset (in ground_truth/), and agent outputs (in agent_output/) can support future research on dark patterns. In particular, it provide concrete examples of how different dark pattern categories manifest in real websites.


