import pytest
import time
from app.tasks import progress_store


def test_get_tasks_empty(client):
    response = client.get("/tasks")
    assert response.status_code == 200
    assert response.json() == []


def test_create_task(client):
    payload = {
        "title": "Название тестовой задачи",
        "description": "Описание тестовой задачи"
    }
    response = client.post("/tasks", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == payload["title"]
    assert data["description"] == payload["description"]
    assert "id" in data


def test_update_task_success(client):
    create_resp = client.post(
        "/tasks",
        json={
            "title": "Название старой задачи",
            "description": "Описание старой задачи"
        }
    )
    task_id = create_resp.json()["id"]

    update_data = {
        "title": "Новой название задачи",
        "completed": False
    }
    update_resp = client.put(f"/tasks/{task_id}", json=update_data)
    assert update_resp.status_code == 200
    updated_task = update_resp.json()
    assert updated_task["title"] == "Новой название задачи"
    assert updated_task["description"] == "Описание старой задачи"
    assert updated_task["completed"] is False


def test_update_task_not_found(client):
    response = client.put(
        "/tasks/9999",
        json={
            "title": "Задача, которой нет",
            "completed": True
        }
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"


def test_delete_task_success(client):
    # Создаём задачу
    create_resp = client.post(
        "/tasks",
        json={
            "title": "Задача на удаление",
            "description": ""
        }
    )
    task_id = create_resp.json()["id"]

    # Удаляем
    delete_resp = client.delete(f"/tasks/{task_id}")
    assert delete_resp.status_code == 200
    assert delete_resp.json() == {"ok": True}

    # Проверяем, что задачи больше нет
    get_resp = client.get("/tasks")
    tasks = get_resp.json()
    assert all(t["id"] != task_id for t in tasks)


def test_delete_task_not_found(client):
    response = client.delete("/tasks/9999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"


# --- Тесты долгой асинхронной задачи ---

@pytest.mark.asyncio
async def test_long_task_start_and_progress(client):
    # Запускаем задачу
    start_resp = client.post("/long-task/")
    assert start_resp.status_code == 200
    task_id = start_resp.json()["task_id"]
    assert task_id in progress_store

    # В начале прогресс 0
    progress_resp = client.get(f"/long-task/{task_id}")
    assert progress_resp.status_code == 200

    progress_store[task_id] = 42

    progress_resp = client.get(f"/long-task/{task_id}")
    assert progress_resp.status_code == 200
    assert progress_resp.json()["progress"] == 42


@pytest.mark.asyncio
async def test_long_task_progress_not_found(client):
    response = client.get("/long-task/invalid-task-id")
    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"
