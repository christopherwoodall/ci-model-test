import os
import yaml
import datetime
import openbench
from concurrent.futures import ProcessPoolExecutor, as_completed


def load_config(config_path):
    """
    Loads the configuration from a YAML file.
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found at: {config_path}")

    with open(config_path, "r") as file:
        config = yaml.safe_load(file)
    return config


def run_single_eval(model_name, eval_name, limit):
    """
    Runs a single evaluation task with logging.
    """
    print(
        f"\nRunning evaluation: {eval_name} on model: {model_name} with limit: {limit}"
    )

    # Generate logfile name with timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    sanitized_model_name = (
        model_name.replace("/", "_").replace("-", "_").replace(".", "_")
    )
    logfile_name = f"results_{sanitized_model_name}_{eval_name}_{timestamp}"

    # Run the evaluation
    openbench.run_eval(
        display=openbench._cli.eval_command.DisplayType.NONE,
        benchmarks=["mmlu"],
        model=["openrouter/openai/gpt-oss-20b"],
        # TODO: Fix limit error
        # limit=limit,
        log_format=openbench._cli.eval_command.LogFormat.JSON,
        logfile=logfile_name,
        debug=True,
        # model_base_url = "https://openrouter.ai/api/v1",
        # model_role = "grader_model=openrouter/openai/gpt-4.1-mini",
    )

    return f"Completed {eval_name} on {model_name}"


def run_evaluation(config_path, max_workers=4):
    """
    Runs evaluations based on the provided configuration file.
    """
    config = load_config(config_path)

    tasks = []
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        for run_name, run_config in config["evaluation"]["runs"].items():
            print(f"\n--- Processing Evaluation Run: {run_name} ---")

            model_name = run_config.get("model")
            limit = run_config.get("limit", 0)
            evals_list = run_config.get("evals", [])

            for eval_name in evals_list:
                # Submit each eval to run in parallel
                tasks.append(
                    executor.submit(run_single_eval, model_name, eval_name, limit)
                )

        # Gather results as they complete
        for future in as_completed(tasks):
            try:
                result = future.result()
                print(result)
            except Exception as e:
                print(f"Task failed: {e}")
