#!/usr/bin/env python3
"""Regenerate the single-file corpus reader from current spine CSVs.
Usage: python3 scripts/build_site.py [--out site/pursue_corpus_reader.html]
Every displayed value must trace to a CSV row. No derived or inferred values."""
import argparse, csv, json, os, re
SPINE = os.environ.get("SPINE", "spine")

def year(*s):
    m = re.findall(r"(19[4-9]\d|20[0-2]\d)", " ".join(s))
    return m[0] if m else ""

def family(rid):
    if rid.startswith("video_2605"): return "v2605 edited"
    for k, lab in (("111830","111830 sensor"),("111887","111887 scope"),
                   ("111764","111764 handheld"),("111688","111688 ISR"),("111689","111689 ISR")):
        if k in rid: return lab
    return "other"

def load_aliases(path):
    """Restricted-YAML reader for spine/aliases.yml (flow lists are JSON)."""
    clusters, cur = [], None
    if not os.path.exists(path):
        return clusters
    for line in open(path):
        s = line.rstrip("\n")
        if not s.strip() or s.strip().startswith("#"):
            continue
        if s.startswith("- cluster:"):
            cur = {"cluster": s.split(":", 1)[1].strip()}
            clusters.append(cur)
        elif cur is not None and ":" in s:
            k, v = s.strip().split(":", 1)
            v = v.strip()
            cur[k.strip()] = json.loads(v) if v.startswith("[") else v
    return clusters

def main(out):
    docs = [{"id":r["release_id"], "s":r["subject_meta"][:90], "a":r["release_id"].split("-")[0],
             "p":int(r["pages"]), "q":round(float(r["mean_ocr_quality"] or 0),2),
             "y":year(r["release_id"], r["subject_meta"])}
            for r in csv.DictReader(open(os.path.join(SPINE,"manifest.csv")))]
    media = [{"id":r["release_id"], "d":float(r["duration_s"]), "res":r["resolution"],
              "fps":r["fps"].split("/")[0], "ct":r["creation_time"][:10],
              "b":int(r["file_bytes"]), "fam":family(r["release_id"])}
             for r in csv.DictReader(open(os.path.join(SPINE,"media.csv")))]

    # Layer 3: group mentions by normalized value; verbatim spellings and every
    # page cite ride along. Flags are per-normalized-string, so per-group.
    groups = {}
    n_ment = n_flag = 0
    for r in csv.DictReader(open(os.path.join(SPINE, "entities_normalized.csv"))):
        n_ment += 1
        if r["candidate_flags"] != "CLEAN":
            n_flag += 1
        key = (r["value_normalized"], r["entity_type"])
        g = groups.setdefault(key, {"v": r["value_normalized"], "t": r["entity_type"],
                                    "f": r["candidate_flags"], "vv": [], "c": []})
        if r["value_verbatim"] not in g["vv"]:
            g["vv"].append(r["value_verbatim"])
        g["c"].append(f"{r['release_id']}:{r['pdf_page']}")
    ents = sorted(groups.values(), key=lambda g: -len(g["c"]))
    for g in ents:
        g["n"] = len(g["c"])

    alias = [{"k": c["cluster"], "m": c["members"],
              "conf": c.get("confidence", "unreviewed")}
             for c in load_aliases(os.path.join(SPINE, "aliases.yml"))]

    data = {"docs": docs, "media": media, "ents": ents, "alias": alias,
            "etotal": n_ment, "eflag": n_flag}
    tpl = open(os.path.join(os.path.dirname(__file__), "..", "site", "template.html")).read()
    html = tpl.replace("__DATA__", json.dumps(data, separators=(",",":")))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out,"w").write(html)
    print(f"wrote {out}: {len(docs)} documents, {len(media)} media rows, "
          f"{round(sum(m['d'] for m in media)/3600,2)} hours, "
          f"{n_ment} entity mentions in {len(ents)} groups ({n_flag} flagged), "
          f"{len(alias)} alias clusters")

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--out", default="site/pursue_corpus_reader.html")
    main(ap.parse_args().out)
