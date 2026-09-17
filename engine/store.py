"""DevRadar store — history, velocity state, snapshots.
Owns: data/history.json (90d star time-series) + data/snapshots/prev.json (last run).
Stdlib only. Atomic writes so Pages never serves a half-written file.
"""
import json, os, time, datetime as dt

DATA    = os.path.join(os.path.dirname(__file__), "..", "data")
HISTORY = os.path.join(DATA, "history.json")
PREV    = os.path.join(DATA, "snapshots", "prev.json")
MAX_DAYS, PRUNE_AFTER = 90, 30


def _read(path, default):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def _write(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, separators=(",", ":"))
    os.replace(tmp, path)


def load_prev():
    """Previous run's state: {full_name: [unix_ts, stars]}"""
    return _read(PREV, {})


def velocity(full_name, stars, prev, min_h=4, max_h=48):
    """24h velocity vs previous snapshot. 0 if no valid 4–48h-old reference."""
    ref = prev.get(full_name)
    if not ref:
        return 0
    ts, pstars = ref
    hours = (time.time() - ts) / 3600
    if not (min_h <= hours <= max_h):
        return 0
    return round(max(0, stars - pstars) * 24 / hours)


def update(records, now=None):
    """Call ONCE at end of pipeline run. Appends today's stars to history,
    prunes stale repos, writes fresh prev snapshot."""
    now     = now or dt.datetime.now(dt.timezone.utc)
    today   = f"{now:%Y-%m-%d}"
    history = _read(HISTORY, {})

    for r in records:
        fn = r["full_name"]
        history.setdefault(fn, {})[today] = r["stars"]
        dates = sorted(history[fn])
        if len(dates) > MAX_DAYS:
            history[fn] = {d: history[fn][d] for d in dates[-MAX_DAYS:]}

    # Repos unseen for 30 days leave history (keeps file small)
    live   = {r["full_name"] for r in records}
    cutoff = f"{now - dt.timedelta(days=PRUNE_AFTER):%Y-%m-%d}"
    history = {fn: h for fn, h in history.items()
               if fn in live or max(h) >= cutoff}

    _write(HISTORY, history)
    _write(PREV, {r["full_name"]: [now.timestamp(), r["stars"]] for r in records})
