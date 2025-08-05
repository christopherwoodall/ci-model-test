import argparse
import yaml
import os
import subprocess
import datetime


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


def run_evaluation(model_name, eval_name, limit, json_output):
    """
    Constructs and executes the bench eval command.
    """
    # Construct the base command
    command = [
        "bench",
        "eval", eval_name,
        "--model", model_name,
        "--limit", str(limit),
        "--log-level", "debug"
    ]

    # Add JSON flag and logfile if required
    if json_output:
        # Generate a logfile name using Python's datetime for portability
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        # Sanitize model_name for filename (replace problematic characters)
        sanitized_model_name = (
            model_name.replace("/", "_").replace("-", "_").replace(".", "_")
        )
        logfile_name = f"results_{sanitized_model_name}_{eval_name}_{timestamp}"

        command.extend(["--logfile", logfile_name])
        command.append("--json")

    print(f"Executing command: {' '.join(command)}")

    try:
        # Execute the command. `check=True` will raise a CalledProcessError for non-zero exit codes.
        # `capture_output=True` captures stdout and stderr.
        # `text=True` decodes stdout/stderr as text.
        # `env=os.environ` passes the current environment variables, including OPENROUTER_API_KEY.
        result = subprocess.run(
            command, check=True, capture_output=True, text=True, env=os.environ
        )

        if result.stdout:
            print("STDOUT:\n", result.stdout)
        if result.stderr:
            print("STDERR:\n", result.stderr)
        print(f"Evaluation for {model_name} on {eval_name} completed successfully.")

    except subprocess.CalledProcessError as e:
        print(f"Error running evaluation for {model_name} on {eval_name}:")
        print(f"  Command: {' '.join(e.cmd)}")
        print(f"  Return Code: {e.returncode}")
        if e.stdout:
            print(f"  Output (stdout):\n{e.stdout}")
        if e.stderr:
            print(f"  Output (stderr):\n{e.stderr}")
        raise
    except FileNotFoundError:
        print(
            "Error: 'bench' command not found. Make sure OpenBench is installed and in your PATH."
        )
        raise
    except Exception as e:
        print(f"An unexpected error occurred during command execution: {e}")
        raise


def main():
    """
    Main function to parse arguments and run evaluations based on config.
    """
    parser = argparse.ArgumentParser(
        description="Run model evaluations based on a configuration file."
    )
    parser.add_argument(
        "--config",
        type=str,
        default="config.yaml",
        help="Path to the YAML configuration file (default: config.yaml)",
    )

    args = parser.parse_args()
    config_file_path = args.config

    print(f"Loading configuration from: {config_file_path}")

    try:
        config = load_config(config_file_path)

        if "evaluation_runs" in config and isinstance(config["evaluation_runs"], dict):
            print("\n--- Starting Evaluation Runs ---")
            for run_name, run_config in config["evaluation_runs"].items():
                print(f"\n--- Processing Evaluation Run: {run_name} ---")

                model_name = run_config.get("model")
                limit = run_config.get("limit")
                json_output = run_config.get("json", False)
                evals_list = run_config.get("evals")

                if not all([model_name, limit, evals_list]):
                    print(
                        f"  Skipping run '{run_name}' due to missing 'model', 'limit', or 'evals' configuration."
                    )
                    continue

                if not isinstance(evals_list, list):
                    print(f"  Skipping run '{run_name}': 'evals' must be a list.")
                    continue

                for eval_name in evals_list:
                    run_evaluation(model_name, eval_name, limit, json_output)
        else:
            print(
                "  No 'evaluation_runs' section found or it is malformed in config.yaml."
            )

    except FileNotFoundError as e:
        print(f"Fatal Error: {e}")
        exit(1)
    except yaml.YAMLError as e:
        print(f"Fatal Error parsing YAML file: {e}")
        exit(1)
    except Exception as e:
        print(f"An unexpected fatal error occurred: {e}")
        exit(1)


if __name__ == "__main__":
    main()
