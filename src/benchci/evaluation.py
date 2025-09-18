import datetime
import openbench
from concurrent.futures import ProcessPoolExecutor, as_completed


def run_single_eval(model_name, eval_name, limit):
    """
    Runs a single evaluation task with logging.
    """
    print(
        f"\nRunning evaluation: {eval_name} on model: {model_name} with limit: {limit}"
    )

    # Generate logfile name with timestamp
    sanitized_model_name = model_name
    for char in ["/", "-", ".", ":"]:
        sanitized_model_name = sanitized_model_name.replace(char, "_")
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    logfile_name = f"results_{sanitized_model_name}_{eval_name}_{timestamp}"

    # Run the evaluation
    openbench.run_eval(
        display=openbench._cli.eval_command.DisplayType.NONE,
        benchmarks=[eval_name],
        model=[model_name],
        # TODO: Fix limit error
        # limit=limit,
        log_format=openbench._cli.eval_command.LogFormat.JSON,
        logfile=logfile_name,
        debug=True,
        # model_base_url = "https://openrouter.ai/api/v1",
        # model_role = "grader_model=openrouter/openai/gpt-4.1-mini",
    )

    return f"Completed {eval_name} on {model_name}"


def run_evaluation(config, max_workers=4):
    """
    Runs evaluations based on the provided configuration file.
    """
    tasks = []
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        for run_name, run_config in config["evaluation"]["runs"].items():
            print(f"\n--- Processing Evaluation Run: {run_name} ---")

            model_name = run_config.get("model")
            limit = run_config.get("limit", 0)
            evals_list = run_config.get("evals", [])

            for eval_name in evals_list:
                run_single_eval(model_name, eval_name, limit)

        #     for eval_name in evals_list:
        #         # Submit each eval to run in parallel
        #         tasks.append(
        #             executor.submit(run_single_eval, model_name, eval_name, limit)
        #         )

        # # Gather results as they complete
        # for future in as_completed(tasks):
        #     try:
        #         result = future.result()
        #         print(result)
        #     except Exception as e:
        #         print(f"Task failed: {e}")
