import os
import yaml
import openbench


# import datetime
# import subprocess


def load_config(config_path):
    """
    Loads the configuration from a YAML file.

    Args:
        config_path (str): The path to the YAML configuration file.

    Returns:
        dict: The loaded configuration as a dictionary.

    Raises:
        FileNotFoundError: If the config file does not exist.
        yaml.YAMLError: If there's an error parsing the YAML file.
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found at: {config_path}")

    with open(config_path, "r") as file:
        config = yaml.safe_load(file)
    return config


def run_evaluation(config_path):
    config = load_config(config_path)

    # model_name = config.get("model_name", "default_model")
    # eval_name = config.get("eval_name", "default_eval")
    # limit = config.get("limit", 5)
    # json_output = config.get("json_output", False)

    # # Add JSON flag and logfile if required
    # if json_output:
    #     # Generate a logfile name using Python's datetime for portability
    #     timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    #     # Sanitize model_name for filename (replace problematic characters)
    #     sanitized_model_name = (
    #         model_name.replace("/", "_").replace("-", "_").replace(".", "_")
    #     )
    #     logfile_name = f"results_{sanitized_model_name}_{eval_name}_{timestamp}"

    openbench.run_eval(
        benchmarks=["mmlu"],
        model=["openrouter/openai/gpt-oss-20b"],
        limit=5,
        log_format="json",
        # logfile = logfile_name,
        # model_base_url = "https://openrouter.ai/api/v1",
        # model_role = "grader_model=openrouter/openai/gpt-4.1-mini",
    )
