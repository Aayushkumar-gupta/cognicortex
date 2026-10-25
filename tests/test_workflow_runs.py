import pytest

from app.db.models.task_run import TaskRun
from app.db.models.workflow_run import WorkflowRun
from app.db.session import SessionLocal
from app.workers import workflow_executor
from app.workflows.models import WorkflowStep


def create_workflow(client, headers, step_names, edges=()):
    """Create a workflow through the API, then link its steps in the database.

    The API needs step ids in next_steps before the steps exist, so the
    dependencies are added directly once the ids are known.
    """
    response = client.post(
        "/api/v1/workflows",
        headers=headers,
        json={
            "name": "Test workflow",
            "steps": [
                {"name": name, "step_type": "action", "config": {}}
                for name in step_names
            ],
        },
    )
    workflow = response.json()
    ids = {step["name"]: step["id"] for step in workflow["steps"]}
    with SessionLocal() as db:
        for parent, child in edges:
            step = db.get(WorkflowStep, ids[parent])
            step.next_steps = [*(step.next_steps or []), ids[child]]
        db.commit()
    return workflow["id"]


def start_run(client, headers, workflow_id):
    client.post(f"/api/v1/workflow_runs?workflow_id={workflow_id}", headers=headers)
    with SessionLocal() as db:
        return db.query(WorkflowRun).order_by(WorkflowRun.id.desc()).first().id


def load_run(run_id):
    with SessionLocal() as db:
        run = db.get(WorkflowRun, run_id)
        tasks = {
            task.task_name: {
                "id": task.id,
                "status": task.status,
                "started_at": task.started_at,
                "finished_at": task.finished_at,
                "error_message": task.error_message,
            }
            for task in db.query(TaskRun).filter(TaskRun.workflow_run_id == run_id)
        }
        return run.status, tasks


def test_run_executes_steps_in_dependency_order(client, auth_headers):
    workflow_id = create_workflow(client, auth_headers, ["A", "B"], [("A", "B")])

    status, tasks = load_run(start_run(client, auth_headers, workflow_id))

    assert status == "FINISHED"
    assert {name: task["status"] for name, task in tasks.items()} == {
        "A": "SUCCESS",
        "B": "SUCCESS",
    }
    assert tasks["A"]["id"] < tasks["B"]["id"]


def test_step_waits_for_all_parents_and_runs_once(client, auth_headers):
    workflow_id = create_workflow(
        client, auth_headers, ["A", "B", "C"], [("A", "C"), ("B", "C")]
    )

    status, tasks = load_run(start_run(client, auth_headers, workflow_id))

    assert status == "FINISHED"
    assert sorted(tasks) == ["A", "B", "C"]
    assert tasks["C"]["id"] > max(tasks["A"]["id"], tasks["B"]["id"])


def test_failed_step_stops_downstream_and_fails_run(
    client, auth_headers, monkeypatch
):
    def fail_on_a(step):
        if step.name == "A":
            raise RuntimeError("step A exploded")

    monkeypatch.setattr(workflow_executor, "execute_step_logic", fail_on_a)
    workflow_id = create_workflow(client, auth_headers, ["A", "B"], [("A", "B")])

    status, tasks = load_run(start_run(client, auth_headers, workflow_id))

    assert status == "FAILED"
    assert tasks["A"]["status"] == "FAILED"
    assert "B" not in tasks


def test_monitor_reports_summary(client, auth_headers):
    workflow_id = create_workflow(client, auth_headers, ["A", "B"], [("A", "B")])
    run_id = start_run(client, auth_headers, workflow_id)

    response = client.get(f"/api/v1/workflow_runs/{run_id}", headers=auth_headers)

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "FINISHED"
    assert body["summary"]["total_tasks"] == 2
    assert body["summary"]["completed_tasks"] == 2


@pytest.mark.xfail(reason="Known bug: starting a run does not return its id")
def test_start_run_returns_run_id(client, auth_headers):
    workflow_id = create_workflow(client, auth_headers, ["A"])

    response = client.post(
        f"/api/v1/workflow_runs?workflow_id={workflow_id}", headers=auth_headers
    )

    assert "workflow_run_id" in response.json()


@pytest.mark.xfail(reason="Known bug: run details need no login")
def test_run_details_require_login(client, auth_headers):
    workflow_id = create_workflow(client, auth_headers, ["A"])
    run_id = start_run(client, auth_headers, workflow_id)

    response = client.get(f"/api/v1/workflow_runs/{run_id}")

    assert response.status_code == 401


@pytest.mark.xfail(reason="Known bug: any user can start any workflow")
def test_other_user_cannot_start_workflow(client, register_and_login):
    owner = register_and_login(email="owner@example.com")
    other = register_and_login(email="other@example.com")
    workflow_id = create_workflow(client, owner, ["A"])

    response = client.post(
        f"/api/v1/workflow_runs?workflow_id={workflow_id}", headers=other
    )

    assert response.status_code == 404


@pytest.mark.xfail(reason="Known bug: steps never record start and finish times")
def test_step_durations_are_recorded(client, auth_headers):
    workflow_id = create_workflow(client, auth_headers, ["A"])

    _, tasks = load_run(start_run(client, auth_headers, workflow_id))

    assert tasks["A"]["started_at"] is not None
    assert tasks["A"]["finished_at"] is not None


@pytest.mark.xfail(reason="Known bug: a failed step does not store its error")
def test_failed_step_records_error_message(client, auth_headers, monkeypatch):
    def always_fail(step):
        raise RuntimeError("step exploded")

    monkeypatch.setattr(workflow_executor, "execute_step_logic", always_fail)
    workflow_id = create_workflow(client, auth_headers, ["A"])

    _, tasks = load_run(start_run(client, auth_headers, workflow_id))

    assert tasks["A"]["error_message"] == "step exploded"
