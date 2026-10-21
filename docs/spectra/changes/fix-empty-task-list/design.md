## Context

Task groups come from the monthly field research (ScrapedDuck `research.min.json`) and Bahamut 【情報】 posts. Evidence from 2026-10-21 shows Bahamut never yields groups, so the page is effectively empty apart from field research. ScrapedDuck's `events.min.json` has no research tasks, but each event's `link` points to a LeekDuck page with structured research steps.

## Goals / Non-Goals

**Goals:**

- Show timed/special research for active events on 任務待辦.
- Correct Bahamut period parsing for full dates and stop sentence lines from becoming tasks.
- Stable task ids for every task.

**Non-Goals:**

- Scraping LeekDuck pages of events that have not started or have ended.
- Translating every item name; unknown rewards stay in English.

## Decisions

### LeekDuck event pages as the timed research source

`fetch_event_research(events, now)` fetches the `link` of each event with `start <= now < end` (or no start) and type not in `GO_SKIP_TYPES`, at most `LEEKDUCK_MAX_PAGES = 20` pages, one request at a time. `parse_event_research(html)` reads `.special-research-list .step-item`; for each `.task-reward` it takes `.task-text` and the `.reward-label` texts (with their `×N` quantity). A page failure is printed and skipped. Alternative rejected: loosening the Bahamut title filter — the posts contain no task lists.

### Event research group shape

Group `id = "ld-<eventID>"`, `name = "限時調查：<event_name(name)>"`, `url = link`, `start/end` from the event, tasks capped at 40. Each task: `text = research_task(english)`, `reward` = translated reward labels joined with 「、」 (`translate.reward`: Pokémon via `pokemon()`, items via `items` in `translations.json`, `×N` kept), `id = task_id(step, english, n)`.

### Stable task ids by hash

`task_id(*parts)` returns the first 10 hex chars of SHA-1 of the parts joined by `|`. Bahamut tasks use `task_id(text)`, LeekDuck tasks `task_id(step_name, text, n)` where `n` counts repeats of the same text in the same step (LeekDuck lists e.g. four identical "Use a Star Piece" tasks). The page already keys by `t.id || i`, so no page change is needed; existing Bahamut check marks (index-keyed) are lost once, which is acceptable because Bahamut never produced groups.

### Full-date Bahamut periods

`parse_period` first tries `YYYY年M月D日[ HH:MM] ～ [YYYY年]M月D日[ HH:MM]` (also `/` separators); if it matches, those values are used without the 180-day year guess. Otherwise the existing month/day pattern applies. Lines whose text ends with 。 or ！ are not tasks.

## Implementation Contract

- Behaviour: `payload.taskGroups` = Bahamut groups + LeekDuck event research groups + the field research group; every task has `id`, `text`, `reward`.
- Interface: `sources.fetch_event_research(events, now) -> list[tuple[GoEvent, steps]]` (translation into groups happens in `main.build_event_research`), `sources.parse_event_research(html) -> list[tuple[str, str, list[str]]]` (step, task, rewards), `translate.reward(label) -> str`, `sources.task_id(*parts) -> str`; `TaskGroup.tasks` becomes `list[tuple[str, str, str]]` (id, text, reward).
- Failure modes: LeekDuck listing failure for a page → skipped with a log line; whole source failure → error `LeekDuck 限時調查（原因）` like other sources.
- Acceptance: unit tests on fixture pages, `parse_period` full-date test, Bahamut announcement fixture yields `None`; `python -m unittest` passes.
- Scope: in — the items above. Out — dashboard changes, reminder changes.

## Risks / Trade-offs

- [LeekDuck markup changes] → parser returns no tasks and the group is skipped; fixtures make the break visible in tests.
- [Up to 20 extra requests per day to LeekDuck] → sequential, with the existing User-Agent and 30 s timeout; only active events.
- [One-time loss of index-keyed Bahamut check marks] → accepted, see decision above.
