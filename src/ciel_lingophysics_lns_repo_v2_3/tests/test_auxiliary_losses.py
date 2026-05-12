from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TASKS = ROOT / "data" / "transformer_features" / "auxiliary_tasks.yaml"


def test_auxiliary_tasks_weights_sum_to_one():
    from src.lingophysics.auxiliary_losses import load_auxiliary_tasks, total_auxiliary_weight
    tasks = load_auxiliary_tasks(TASKS)
    assert total_auxiliary_weight(tasks) == 1.0


def test_weighted_total_loss_is_deterministic():
    from src.lingophysics.auxiliary_losses import load_auxiliary_tasks, weighted_total_loss
    tasks = load_auxiliary_tasks(TASKS)
    losses = {t["id"]: 2.0 for t in tasks["tasks"]}
    assert weighted_total_loss(1.0, losses, tasks) == 3.0


def test_missing_task_losses_are_reported():
    from src.lingophysics.auxiliary_losses import load_auxiliary_tasks, missing_task_losses
    tasks = load_auxiliary_tasks(TASKS)
    missing = missing_task_losses({}, tasks)
    assert "operator_class_prediction" in missing
