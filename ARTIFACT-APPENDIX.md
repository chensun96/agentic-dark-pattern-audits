# Artifact Appendix

Paper title: On the Suitability of LLM-Driven Agents for Dark Pattern Audits

Requested Badge(s): Available, Functional

## Description (Required for all badges)
This artifact contains the implementation code, dataset, and results used to evaluate LLM-driven agents for auditing CCPA right-to-access workflows. It includes: (a) the agent source code with four prompting strategies, (b) a human-annotated ground truth dataset of 100 data brokers, (c) results for all experimental phases, and (d) Jupyter notebooks that reproduce all quantitative results reported in the paper. 

For artifact evaluation, reviewers can verify that analysis pipeline (evaluation notebooks) generates results consistent with those reported in the paper. To reproduce the full experiments (live auditing agent) as described in the paper, please refer to the main README.       

### Security/Privacy Issues and Ethical Concerns (Required for all badges)

The primary evaluation workflow operates on the provided datasets, agent outputs, and evaluation notebooks, and does not interact with live websites. The artifact does not contain malware, exploits, attack code, personally identifiable information, or consumer records. The included annotation data was produced by the authors and does not involve human-subject participants.

The repository also includes the agent implementation used in the study. Re-executing the agent is optional, requires an OpenAI API key, and performs only observational browsing of publicly accessible websites without submitting requests or transmitting personal information.

## Basic Requirements (Required for Functional and Reproduced badges)

### Hardware Requirements (Required for Functional and Reproduced badges)

The artifact can run on a standard laptop or server with a stable Internet connection. No specialized hardware (e.g., GPU, cluster, or accelerator) is required.
The experiments reported in the paper were conducted on a macOS laptop located in California.

### Software Requirements (Required for Functional and Reproduced badges)

We ran all the code in the following software environments:

- OS: macOS 14+. 
- Programming Language: Python 3.13 (required; earlier Python versions are not supported)                                   
- Python packages: See requirements.txt.                                             
- ML Models: GPT-5 via OpenAI API (optional)
- Datasets: All datasets to run the artifacts are included in the repo:                                                   
    - broker_dataset/100_annotated_brokers.csv - ground truth broker URLs (Phase 2)                     
    - broker_dataset/left_test_brokers.csv — deployment broker URLs (Phase 3)                           
    - ground_truth/
        - annotation_guide.pdf
        - annotation_agreement/                                                       
    - results/ — pre-computed agent outputs (prompt_ablation, workflow_execution, deployment)

### Estimated Time and Storage Consumption (Required for Functional and Reproduced badges)

Evaluation notebooks only run a few minutes and require no additional storage.

## Environment (Required for all badges)

### Accessibility (Required for all badges)

Main codebase: https://github.com/chensun96/agentic-dark-pattern-audits

### Set up the environment (Required for Functional and Reproduced badges)

```bash
git clone https://github.com/chensun96/agentic-dark-pattern-audits.git
cd agentic-dark-pattern-audits
python3.13 -m venv env
source env/bin/activate
pip install -r requirements.txt

```

### Testing the Environment (Required for Functional and Reproduced badges)
Run a quick sanity check to verify all notebooks can be opened and key imports work:  

```bash
source env/bin/activate                                                                             
jupyter nbconvert --to notebook --execute evaluation/section3_dataset.ipynb --stdout | grep "Cohen"
```                                                                           
Expected: notebook executes without errors, printing Cohen's Kappa: 0.519 and Cohen's Kappa: 0.737. These values correspond to the inter-annotator agreement scores reported in the paper.

## Artifact Evaluation (Required for Functional and Reproduced badges)


### Main Results and Claims


#### Main Result 1: Prompting strategy ablation (RQ1, Table 2) 

The paper claims that Few-shot + Role + CoT achieves the highest classification accuracy and explanation accuracy across four prompting strategies.  Supported by: Experiment 1 (RQ1.ipynb, Table 2 upper + lower sections)                                
                             

#### Main Result 2: Per-pattern performance (RQ1, Table 3)

The paper claims that under the selected configuration (Few-shot + Role + CoT), agent performs better on detecting the structurally localized patterns than on interaction-dependent patterns.  Supported by: Experiment 1 (RQ1.ipynb, Table 3 section)                                             

####   Main Result 3: Dark pattern prevalence (RQ1, Table 4)

The paper claims that structural barriers are the most prevalent dark pattern in completed CCPA right-to-access workflows, while ambiguity- and fragmentation-based patterns also appear frequently. Supported by: Experiment 1 (RQ1.ipynb, Table 4 sections)

####   Main Result 3: Workflow execution limits (RQ2)  
Our paper claims that a substantial fraction of workflows cannot be completed autonomously.  Supported by: Experiment 2 (RQ2.ipynb)  

### Experiments

In this section, we provide step-by-step instructions to evaluate our artifacts, test code functionality, and reproduce our main results.

#### Experiment 1: Reproduce Tables 2, 3, and 4 (RQ1) 

This experiment reproduces Main Result 1,2,3. The following script outputs the reconstructed version of Table 2, 3, 4 in paper.
- Time: ~5 human-minutes + ~10 compute-minutes

- Open and run evaluation/RQ1.

```bash
source env/bin/activate
jupyter notebook evaluation/RQ1.ipynb
# Run all cells 
```

For Table 2, the upper section reports the performance metrics for each prompting strategy. The lower section reports the difference (Δ) between consecutive strategies. For example, the classification accuracy delta for L1→L2 (+Role) is computed as: 63.6 − 70.8 = −7.1 using the classification accuracies reported in the upper section of the table. The corresponding 95% CI are derived from the `ci_95_lower` and `ci_95_upper` values reported by the notebook. A superscript `*` in Table 2 indicates a statistically significant difference (`p < 0.05`).

#### Experiment 2: Reproduce RQ2 workflow execution statistics

This experiment reproduces Main Result 4. It parses the verification issue fields from the saved agent outputs and recomputes workflow completion rates and failure distributions.
- Time: 5 human-minutes + ~1 compute-minut
- Open and run evaluation/RQ2.ipynb         
```bash
source env/bin/activate
jupyter notebook evaluation/RQ2.ipynb
# Run all cells 
```

## Limitations (Required for Functional and Reproduced badges)

Dynamic websites. Data broker websites and ROA workflows may change over time. As a result, re-running the agent may produce different outputs than those reported in the paper; therefore, we provide the original agent outputs and processed datasets used in our analysis.

Geolocation dependent behavior. Some websites may vary privacy disclosures or rights-request workflows based on the visitor's location. The study was conducted from a California-hosted environment, and executions from other regions may observe different behavior.

External dependencies. Agent execution depends on live websites and LLM services. Changes to website content, anti-bot mechanisms, model updates, or the inherent non-determinism of LLMs may affect future executions and lead to results that differ from those reported in the paper.

## Notes on Reusability (Encouraged for all badges)

- The prompting framework and agent framework (in prompts/) can be adapted to audit dark patterns  beyond CCPA data brokers — e.g., opt-out or deletion portals or subscription cancellation flows.  

- The released annotation guidelines can support future research on dark patterns. It provide examples of how different dark pattern categories manifest in real websites.


