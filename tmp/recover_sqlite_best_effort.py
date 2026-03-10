import sqlite3
from pathlib import Path
from datetime import datetime

ROOT = Path(r"C:\Users\Winsock\Documents\GitHub\ordl-aether")
SRC = ROOT / "aether-system" / "data" / "aether.db"
DST = ROOT / "aether-system" / "data" / "aether_salvaged.db"
LOG = ROOT / "tmp" / "enrichment" / f"sqlite_salvage_{datetime.now().strftime('%Y%m%dT%H%M%S')}.log"


def log(msg: str):
    print(msg)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(msg + "\n")


def get_tables(conn):
    rows = conn.execute(
        "SELECT name, sql FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
    ).fetchall()
    return [(r[0], r[1]) for r in rows if r[1]]


def get_indexes(conn):
    rows = conn.execute(
        "SELECT name, sql FROM sqlite_master WHERE type='index' AND sql IS NOT NULL AND name NOT LIKE 'sqlite_%' ORDER BY name"
    ).fetchall()
    return [r[1] for r in rows]


def get_triggers(conn):
    rows = conn.execute(
        "SELECT sql FROM sqlite_master WHERE type='trigger' AND sql IS NOT NULL ORDER BY name"
    ).fetchall()
    return [r[0] for r in rows]


def copy_rows_range(src, dst, table, cols, lo, hi, pk, skipped, depth=0):
    if lo > hi:
        return 0
    query = f"SELECT {','.join(cols)} FROM {table} WHERE {pk} BETWEEN ? AND ? ORDER BY {pk}"
    try:
        rows = src.execute(query, (lo, hi)).fetchall()
        if rows:
            ph = ",".join(["?"] * len(cols))
            dst.executemany(f"INSERT INTO {table} ({','.join(cols)}) VALUES ({ph})", rows)
        return len(rows)
    except sqlite3.DatabaseError as e:
        if lo == hi:
            skipped.append((table, lo, str(e)))
            return 0
        mid = (lo + hi) // 2
        a = copy_rows_range(src, dst, table, cols, lo, mid, pk, skipped, depth + 1)
        b = copy_rows_range(src, dst, table, cols, mid + 1, hi, pk, skipped, depth + 1)
        return a + b


def copy_table(src, dst, table):
    cols = [r[1] for r in src.execute(f"PRAGMA table_info({table})").fetchall()]
    pk_cols = [r[1] for r in src.execute(f"PRAGMA table_info({table})").fetchall() if int(r[5]) > 0]
    pk = pk_cols[0] if pk_cols else None

    skipped = []
    copied = 0

    if pk:
        try:
            min_id, max_id = src.execute(f"SELECT MIN({pk}), MAX({pk}) FROM {table}").fetchone()
        except sqlite3.DatabaseError as e:
            log(f"[{table}] failed to read min/max on pk {pk}: {e}")
            min_id, max_id = None, None

        if min_id is not None and max_id is not None:
            # chunk copy to avoid scanning corrupted pages in one large read
            step = 2000
            start = int(min_id)
            end = int(max_id)
            ph = ",".join(["?"] * len(cols))
            for lo in range(start, end + 1, step):
                hi = min(lo + step - 1, end)
                copied += copy_rows_range(src, dst, table, cols, lo, hi, pk, skipped)
                dst.commit()
            return copied, skipped

    # fallback full scan for tables without readable PK range
    try:
        rows = src.execute(f"SELECT {','.join(cols)} FROM {table}").fetchall()
        if rows:
            ph = ",".join(["?"] * len(cols))
            dst.executemany(f"INSERT INTO {table} ({','.join(cols)}) VALUES ({ph})", rows)
        copied = len(rows)
    except sqlite3.DatabaseError as e:
        skipped.append((table, None, str(e)))
    dst.commit()
    return copied, skipped


def main():
    if DST.exists():
        DST.unlink()

    if LOG.exists():
        LOG.unlink()

    log(f"source={SRC}")
    log(f"dest={DST}")

    src = sqlite3.connect(str(SRC))
    dst = sqlite3.connect(str(DST))

    src.execute("PRAGMA query_only=ON")
    dst.execute("PRAGMA journal_mode=WAL")
    dst.execute("PRAGMA synchronous=NORMAL")

    tables = get_tables(src)
    for name, create_sql in tables:
        log(f"create table {name}")
        dst.execute(create_sql)
    dst.commit()

    total_skipped = []
    for name, _ in tables:
        log(f"copy table {name} ...")
        copied, skipped = copy_table(src, dst, name)
        total_skipped.extend(skipped)
        log(f"copied {name}: {copied} rows; skipped fragments: {len(skipped)}")

    for idx_sql in get_indexes(src):
        try:
            dst.execute(idx_sql)
        except Exception as e:
            log(f"index create skipped due to error: {e}")

    for trig_sql in get_triggers(src):
        try:
            dst.execute(trig_sql)
        except Exception as e:
            log(f"trigger create skipped due to error: {e}")
    dst.commit()

    ok = dst.execute("PRAGMA integrity_check").fetchone()[0]
    log(f"integrity_check={ok}")

    for name, _ in tables:
        try:
            cnt = dst.execute(f"SELECT COUNT(*) FROM {name}").fetchone()[0]
            log(f"dest_count[{name}]={cnt}")
        except Exception as e:
            log(f"dest_count[{name}] failed: {e}")

    if total_skipped:
        log("skipped details:")
        for t, k, e in total_skipped[:500]:
            log(f"  table={t} key={k} err={e}")

    src.close()
    dst.close()
    log("done")


if __name__ == "__main__":
    main()
