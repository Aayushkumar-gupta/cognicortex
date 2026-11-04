WORKFLOW = {
    "name": "Onboarding",
    "description": "New hire setup",
    "steps": [
        {"name": "Create account", "step_type": "action", "config": {}},
        {"name": "Send welcome email", "step_type": "action", "config": {}},
    ],
}


def test_create_workflow_with_steps(client, auth_headers):
    response = client.post("/api/v1/workflows", headers=auth_headers, json=WORKFLOW)

    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Onboarding"
    assert [step["name"] for step in body["steps"]] == [
        "Create account",
        "Send welcome email",
    ]


def test_list_shows_only_own_workflows(client, register_and_login):
    owner = register_and_login(email="owner@example.com")
    other = register_and_login(email="other@example.com")
    client.post("/api/v1/workflows", headers=owner, json=WORKFLOW)

    assert len(client.get("/api/v1/workflows", headers=owner).json()) == 1
    assert client.get("/api/v1/workflows", headers=other).json() == []


def test_other_users_workflow_is_not_found(client, register_and_login):
    owner = register_and_login(email="owner@example.com")
    other = register_and_login(email="other@example.com")
    workflow_id = client.post("/api/v1/workflows", headers=owner, json=WORKFLOW).json()[
        "id"
    ]

    response = client.get(f"/api/v1/workflows/{workflow_id}", headers=other)

    assert response.status_code == 404


def test_update_renames_workflow(client, auth_headers):
    workflow_id = client.post(
        "/api/v1/workflows", headers=auth_headers, json=WORKFLOW
    ).json()["id"]

    response = client.put(
        f"/api/v1/workflows/{workflow_id}",
        headers=auth_headers,
        json={"name": "Offboarding"},
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Offboarding"
    assert response.json()["description"] == "New hire setup"


def test_delete_removes_workflow(client, auth_headers):
    workflow_id = client.post(
        "/api/v1/workflows", headers=auth_headers, json=WORKFLOW
    ).json()["id"]

    delete_response = client.delete(
        f"/api/v1/workflows/{workflow_id}", headers=auth_headers
    )
    get_response = client.get(f"/api/v1/workflows/{workflow_id}", headers=auth_headers)

    assert delete_response.status_code == 200
    assert get_response.status_code == 404
