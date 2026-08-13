# Dashboard Polling and Persistence Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace WebSocket dashboard updates with resilient REST polling while fixing UTC timestamps, task-state persistence, request URL visibility, and task-list performance.

**Architecture:** SQLite remains the durable history/configuration store, while the scheduler remains authoritative for live task details. A single lightweight REST snapshot combines SQLite counts with live queue details, and Pinia polls that snapshot with adaptive intervals and bounded backoff.

**Tech Stack:** Python 3.10, FastAPI, aiosqlite, Pydantic 2, pytest, Vue 3, Pinia, Axios, Vite.

## Global Constraints

- Completely remove the WebSocket endpoint and frontend WebSocket client.
- Preserve `data/mineru_center.db` and all existing configuration/history rows.
- Treat legacy timezone-naive timestamps as UTC without shifting their clock value.
- Mark startup `pending` and `running` records as `failed`; do not attempt replay.
- Display the actual target `<instance.url>/file_parse` as the request URL.
- Dashboard responses must not contain Base64 data, full payloads, or parse results.
- Do not add Redis, a separate queue service, or a frontend testing dependency.

---

### Task 1: UTC Utilities and SQLite Migration

**Files:**
- Create: `app/utils/time.py`
- Modify: `app/models/task.py`
- Modify: `app/services/database.py`
- Create: `tests/test_database.py`

**Interfaces:**
- Produces: `utc_now() -> datetime`, `to_utc_iso(value: datetime | str | None) -> str | None`.
- Produces: `database.fail_interrupted_tasks(error: str) -> int`.
- Produces: task rows containing nullable `request_url`.

- [ ] **Step 1: Write failing UTC and migration tests**

```python
@pytest.fixture
def temp_db(tmp_path, monkeypatch):
    path = tmp_path / "mineru_center.db"
    monkeypatch.setattr(database, "DB_PATH", str(path))
    return path

def test_to_utc_iso_treats_legacy_naive_value_as_utc():
    assert to_utc_iso("2026-08-13T06:59:03") == "2026-08-13T06:59:03Z"

@pytest.mark.asyncio
async def test_init_migrates_request_url_and_fails_interrupted_tasks(temp_db):
    await database.init_database()
    await database.save_task("pending-id", "pending", 5, {}, "a.pdf", "2026-08-13T06:00:00")
    count = await database.fail_interrupted_tasks("Service restarted before completion")
    rows, _ = await database.get_tasks_by_status("failed", 1, 50)
    assert count == 1
    assert rows[0]["request_url"] is None
    assert rows[0]["completed_at"].endswith("Z")
```

- [ ] **Step 2: Run the tests and confirm they fail**

Run: `uv run pytest tests/test_database.py -v`

Expected: collection/import failure because the time utilities and migration API do not exist.

- [ ] **Step 3: Implement UTC serialization and database migration**

```python
UTC = timezone.utc

def utc_now() -> datetime:
    return datetime.now(UTC)

def to_utc_iso(value):
    if value is None:
        return None
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00")) if isinstance(value, str) else value
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC).isoformat().replace("+00:00", "Z")
```

Add an idempotent `request_url TEXT` migration, `(status, created_at DESC)` index, explicit list-field selection, `request_url` support in `save_task`/`update_task_status`, and one SQL update for interrupted tasks.

- [ ] **Step 4: Run focused tests**

Run: `uv run pytest tests/test_database.py -v`

Expected: all Task 1 tests pass and the existing database file is untouched because tests use a temporary path.

- [ ] **Step 5: Commit Task 1**

```bash
git add app/utils/time.py app/models/task.py app/services/database.py tests/test_database.py
git commit -m "fix: persist UTC task state and request URLs"
```

### Task 2: Scheduler Persistence and Efficient Task APIs

**Files:**
- Modify: `app/main.py`
- Modify: `app/services/scheduler.py`
- Modify: `app/services/mineru_client.py`
- Modify: `app/api/tasks.py`
- Create: `tests/test_scheduler.py`
- Create: `tests/test_tasks_api.py`

**Interfaces:**
- Consumes: `utc_now`, `to_utc_iso`, `fail_interrupted_tasks`, and `request_url` database fields from Task 1.
- Produces: cancellation and queue-timeout terminal states persisted in SQLite.
- Produces: task-list responses containing `request_url` and explicit UTC timestamps.

- [ ] **Step 1: Write failing scheduler and API tests**

```python
@pytest.mark.asyncio
async def test_cancel_pending_task_persists_cancelled(monkeypatch, scheduler, queued_task):
    await scheduler.cancel_task(queued_task.id)
    assert updates[-1][1] == "cancelled"
    assert updates[-1][2]["completed_at"].endswith("Z")

def test_pending_list_uses_sorted_queue_once(client, queue_with_three_tasks, monkeypatch):
    response = client.get("/api/tasks?status=pending")
    assert [task["position"] for task in response.json()["tasks"]] == [1, 2, 3]
    assert get_position_call_count == 0
```

Also test that assigning an instance writes `<instance.url>/file_parse`, queue timeout writes `timeout`, and legacy timestamps return with `Z`.

- [ ] **Step 2: Run focused tests and confirm failure**

Run: `uv run pytest tests/test_scheduler.py tests/test_tasks_api.py -v`

Expected: assertions fail because cancellation/timeouts are not persisted and task-list timestamps/request URLs are incomplete.

- [ ] **Step 3: Implement scheduler and task API changes**

Use `utc_now()` for task lifecycle timestamps. During dispatch, compute:

```python
request_url = f"{instance.url.rstrip('/')}/file_parse"
```

Persist it with the running status. Make cancellation asynchronous persistence part of the success condition. Enumerate `queue.get_all()` once for pending positions. Serialize every API timestamp through `to_utc_iso()`.

In startup initialization, run `fail_interrupted_tasks(...)` after database migration and before scheduler start. Move Base64 encode/decode CPU work to `asyncio.to_thread` without changing request or response schemas.

- [ ] **Step 4: Run focused tests**

Run: `uv run pytest tests/test_scheduler.py tests/test_tasks_api.py -v`

Expected: all Task 2 tests pass.

- [ ] **Step 5: Commit Task 2**

```bash
git add app/main.py app/services/scheduler.py app/services/mineru_client.py app/api/tasks.py tests/test_scheduler.py tests/test_tasks_api.py
git commit -m "fix: keep task lifecycle and history consistent"
```

### Task 3: Unified REST Dashboard Snapshot

**Files:**
- Modify: `app/api/stats.py`
- Modify: `app/services/database.py`
- Modify: `pyproject.toml`
- Create: `tests/test_dashboard_api.py`

**Interfaces:**
- Consumes: `database.get_task_stats()` and UTC serialization from Tasks 1-2.
- Produces: `GET /api/stats` as the unified dashboard snapshot with `queue`, `tasks`, `instances`, `queued_tasks`, and `running_tasks`.

- [ ] **Step 1: Write a failing snapshot test**

```python
def test_stats_snapshot_has_consistent_counts_and_no_payload(client):
    body = client.get("/api/stats").json()
    assert set(body) == {"queue", "tasks", "instances", "queued_tasks", "running_tasks"}
    assert body["queue"]["running"] == len(body["running_tasks"])
    assert "payload" not in json.dumps(body)
```

Test that task counts come from SQLite, pending tasks include stable positions, running tasks include `request_url`, and no `/api/stats/ws` route exists.

- [ ] **Step 2: Run the test and confirm failure**

Run: `uv run pytest tests/test_dashboard_api.py -v`

Expected: response-shape and route-removal assertions fail.

- [ ] **Step 3: Replace the stats module with one REST snapshot**

Remove `WebSocket`, `WebSocketDisconnect`, `ConnectionManager`, and the websocket route. Build one response using SQLite counts and live scheduler details. Keep summaries bounded to `max_queue_size` and omit all payload fields.

Remove the direct `websockets` dependency from `pyproject.toml` and refresh the lock file with the repository package manager.

- [ ] **Step 4: Run focused and full backend tests**

Run: `uv run pytest tests/test_dashboard_api.py -v`

Run: `uv run pytest -v`

Expected: all backend tests pass.

- [ ] **Step 5: Commit Task 3**

```bash
git add app/api/stats.py app/services/database.py pyproject.toml uv.lock tests/test_dashboard_api.py
git commit -m "feat: serve a unified REST dashboard snapshot"
```

### Task 4: Adaptive Frontend Polling and Request URL UI

**Files:**
- Modify: `ui/src/api/index.js`
- Modify: `ui/src/stores/index.js`
- Modify: `ui/src/views/Dashboard.vue`
- Modify: `ui/src/components/TaskListDialog.vue`
- Modify: `ui/src/components/FailedTasksDialog.vue`
- Modify: `ui/src/components/TaskCard.vue`
- Modify: `ui/src/i18n/zh.js`
- Modify: `ui/src/i18n/en.js`
- Create: `tests/test_frontend_contract.py`

**Interfaces:**
- Consumes: unified `/api/stats` response and `request_url` fields from Tasks 2-3.
- Produces: `startPolling()`, `stopPolling()`, and `refreshDashboard()` Pinia actions.

- [ ] **Step 1: Write failing frontend contract tests**

```python
def test_frontend_has_no_websocket_code():
    source = "\n".join(
        path.read_text(encoding="utf-8")
        for path in Path("ui/src").rglob("*")
        if path.is_file()
    )
    assert "new WebSocket" not in source
    assert "connectWebSocket" not in source

def test_store_uses_adaptive_polling():
    source = Path("ui/src/stores/index.js").read_text()
    for interval in ("2000", "5000", "15000", "30000"):
        assert interval in source
    assert "pollInFlight" in source
```

The actual test helper reads the named source files explicitly rather than adding a new dependency.

- [ ] **Step 2: Run the contract tests and confirm failure**

Run: `uv run pytest tests/test_frontend_contract.py -v`

Expected: WebSocket symbols remain and polling symbols are absent.

- [ ] **Step 3: Implement polling and UI changes**

Remove `createWebSocket` and all `wsConnected` state. Add one timeout-based polling loop:

```javascript
const delay = document.hidden
  ? 15000
  : activeTaskCount.value > 0 ? 2000 : 5000
```

Track `pollInFlight`, retain the last successful snapshot on errors, use bounded failure delays `[2000, 5000, 10000, 30000]`, and refresh immediately on `visibilitychange` when visible.

Replace the connection pill with a REST freshness state. Render `task.request_url || '-'` in the task list using new `requestUrl` translations. Normalize any legacy timestamp lacking a suffix by appending `Z` before `new Date(...)` so old and new API versions display correctly during rollout.

- [ ] **Step 4: Run frontend verification**

Run: `uv run pytest tests/test_frontend_contract.py -v`

Run: `npm run build` from `ui`

Expected: contract tests pass and Vite completes without errors.

- [ ] **Step 5: Commit Task 4**

```bash
git add ui/src tests/test_frontend_contract.py
git commit -m "feat: poll dashboard state over REST"
```

### Task 5: End-to-End Verification and Deployment Notes

**Files:**
- Modify: `README.md`
- Modify: `docker-compose.yml` only if documentation needs an explicit absolute data-path example; do not change the bind mount.

**Interfaces:**
- Consumes: all previous task behavior.
- Produces: operator guidance for SQLite preservation and post-deploy validation.

- [ ] **Step 1: Document persistence and deployment behavior**

Document these exact paths and constraints:

```text
Host:      <project>/data/mineru_center.db
Container: /app/data/mineru_center.db
Bind mount: ./data:/app/data
```

State that code/image updates preserve data when the same host directory is used, while deleting/moving `data` or deploying from a different directory without copying it loses access to history/configuration.

- [ ] **Step 2: Run complete verification**

Run: `uv run pytest -v`

Run: `python -m compileall app tests`

Run: `npm run build` from `ui`

Run: `rg -n "WebSocket|websocket|stats/ws|connectWebSocket" app ui/src pyproject.toml`

Expected: tests and builds pass; the final search returns no application WebSocket code.

- [ ] **Step 3: Run a local smoke test**

Start the application on an unused port, then verify:

```text
GET /health                    -> 200
GET /api/stats                 -> unified snapshot
GET /api/tasks?page=1          -> timestamps with Z and request_url
GET /api/config                -> existing persisted values
```

Expected: all endpoints return promptly and no response contains `file_base64`.

- [ ] **Step 4: Commit documentation and final verification fixes**

```bash
git add README.md docker-compose.yml
git commit -m "docs: explain SQLite data preservation"
```
