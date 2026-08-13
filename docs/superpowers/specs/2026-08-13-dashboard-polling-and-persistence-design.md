# Dashboard Polling and Persistence Design

## Scope

Replace the dashboard WebSocket path with REST polling and fix the related time,
task-state, list-performance, and persistence inconsistencies. Preserve existing
task history and configuration data.

## Current Problems

- Production Nginx does not proxy the WebSocket upgrade, so KPI counts can update
  through REST while queue details remain empty.
- Stored timestamps are timezone-naive UTC values. Browsers interpret them as
  local time, causing an eight-hour error in elapsed-time displays.
- Dashboard counters, task lists, and queue details use different sources.
- Pending-task list generation repeatedly sorts the full queue for every task.
- Interrupted `pending` and `running` records remain active after a restart even
  though their file contents and execution context cannot be recovered.
- Cancelling an in-memory task does not update its SQLite record.
- The task list does not expose the target MinerU request URL.

## Polling Architecture

Add a lightweight dashboard REST endpoint that returns one consistent snapshot:

- queue counts;
- pending task summaries;
- running task summaries;
- task-history counts from SQLite;
- instance summaries.

The response must never contain file Base64 data, complete task payloads, or
parse results. KPI cards and the queue panel consume the same response.

Remove the frontend WebSocket client and the backend WebSocket endpoint. The
frontend polling controller follows these rules:

- poll every two seconds while pending or running tasks exist;
- poll every five seconds while idle;
- poll every fifteen seconds while the page is hidden;
- never start a poll while the previous request remains in flight;
- after failures, back off through 2, 5, 10, and 30 seconds;
- refresh immediately when the page becomes visible again;
- stop timers when the dashboard unmounts.

The existing manual refresh action remains available and uses the same REST
snapshot.

## Time Model

New timestamps are generated as timezone-aware UTC datetimes and serialized with
an explicit UTC offset. API output may normalize `+00:00` to `Z`.

Existing production records contain timezone-naive values that represent UTC.
API serialization treats those legacy values as UTC without shifting their clock
value. No destructive database rewrite is required.

The frontend parses the explicit UTC timestamp and renders it in the browser's
local timezone. Duration values remain backend-calculated elapsed seconds.

## Task State and Persistence

SQLite remains at `data/mineru_center.db` on the host and
`/app/data/mineru_center.db` in the container. The existing Compose bind mount
`./data:/app/data` continues to preserve the file across container replacement.

At application startup, every persisted `pending` or `running` task is changed
to `failed`, with a completion timestamp and an error explaining that service
restart interrupted the task. These tasks cannot be resumed because the database
intentionally does not retain uploaded file contents.

Task cancellation writes `cancelled`, `completed_at`, and an explanatory error to
SQLite after updating in-memory state. Queue timeouts likewise persist their
terminal state.

Configuration updates remain stored in the SQLite `config` table and loaded at
startup. Existing configuration values are preserved.

## Task List and Request URL

Add a nullable `request_url` column to the tasks table through an idempotent
startup migration. Populate it when a task is assigned to an instance, using the
actual target MinerU endpoint:

```text
<instance.url>/file_parse
```

Return this field from history and running-task list endpoints and display it as
"Request URL" / "请求地址" in the task-list dialog. Pending tasks show `-`
because no target instance has been selected yet. Historical rows created before
this migration also show `-`.

## Performance Changes

- Obtain the sorted pending queue once and derive positions by enumeration.
- Add a composite task index for `(status, created_at DESC)`.
- Select only list fields from SQLite; do not load or decode the payload column
  for list responses.
- Query task KPI counts from SQLite so total, completed, failed, cancelled,
  pending, and running figures share the history source.
- Keep live pending/running detail from the in-memory scheduler, because it is the
  authoritative execution state during a process lifetime.
- Remove repeated WebSocket serialization of failed-task payloads.

Large-file Base64 conversion is a separate contributor to event-loop stalls.
Within this change, encoding and decoding should run outside the event-loop
thread where practical, without changing the public upload contract.

## Failure Handling

- A failed dashboard poll retains the last successful snapshot rather than
  clearing the UI.
- Polling resumes automatically using bounded backoff.
- Database migration and interrupted-task cleanup run inside startup initialization
  before scheduling begins.
- Database write failures are logged. API mutations return failure rather than
  reporting success when their required persistence update fails.

## Verification

Automated tests cover:

- UTC serialization for aware and legacy-naive timestamps;
- startup conversion of `pending` and `running` records to `failed`;
- cancellation and queue-timeout persistence;
- request URL migration, storage, and API output;
- queue positions without repeated sorting;
- dashboard snapshot consistency and absence of payload/Base64 data;
- polling interval, visibility, overlap prevention, and retry backoff behavior.

Run backend tests, frontend build/tests available in the repository, Python
compilation, and a local API smoke test. Production verification should confirm
that the dashboard no longer requests `/api/stats/ws`, elapsed times no longer
include eight hours, and KPI counts match their task-list filters.
