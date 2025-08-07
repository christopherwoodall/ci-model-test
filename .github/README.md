# CI Model Test
Benchmark models using OpenRouter and [OpenBench](https://github.com/groq/openbench) from a Github Workflow.


![Results](https://raw.githubusercontent.com/christopherwoodall/ci-model-test/main/.github/docs/results.png)

![Charts](https://raw.githubusercontent.com/christopherwoodall/ci-model-test/main/.github/docs/chart.png)


## Installation
1. Add your OpenRouter API key to your GitHub secrets as `OPENROUTER_API_KEY`.
2. Enable Github Pages for the repository.
3. Edit the `config.yaml` file to specify the models and benchmarks you want to evaluate.
4. Run the action manually or on a schedule.
