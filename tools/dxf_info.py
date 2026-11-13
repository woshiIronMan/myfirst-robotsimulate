#!/usr/bin/env python
"""Extract geometry bounding boxes / key features from ASCII DXF files."""
import sys
import re
import io

def parse_dxf(path):
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        lines = [l.rstrip("\n").rstrip("\r") for l in f]
    # pair up (code, value)
    pairs = []
    for i in range(0, len(lines) - 1, 2):
        try:
            code = int(lines[i].strip())
        except ValueError:
            continue
        pairs.append((code, lines[i + 1]))

    header = {}
    cur = None
    in_header = False
    ents = []
    cur_ent = None
    in_entities = False
    layer = "0"

    want_section = False
    for code, val in pairs:
        if code == 0:
            v = val.strip()
            if v == "SECTION":
                want_section = True
                cur = None
                continue
            if v == "ENDSEC":
                if in_entities and cur_ent is not None:
                    ents.append(cur_ent)
                cur_ent = None
                in_header = False
                in_entities = False
                want_section = False
                continue
            if in_entities:
                if cur_ent is not None:
                    ents.append(cur_ent)
                cur_ent = {"type": v, "data": []}
            continue
        if code == 2 and want_section:
            name = val.strip()
            want_section = False
            in_header = (name == "HEADER")
            in_entities = (name == "ENTITIES")
            continue
        if code == 9 and in_header:
            cur = val.strip()
            continue
        if in_header and cur:
            if code == 10:
                header.setdefault(cur, {})["x"] = float(val)
            elif code == 20:
                header.setdefault(cur, {})["y"] = float(val)
            elif code == 30:
                header.setdefault(cur, {})["z"] = float(val)
        if in_entities and cur_ent is not None:
            cur_ent["data"].append((code, val))
    if cur_ent is not None:
        ents.append(cur_ent)
    return header, ents


def summarize(path):
    header, ents = parse_dxf(path)
    print("=" * 70)
    print(path)
    for k in ("$EXTMIN", "$EXTMAX", "$LIMMIN", "$LIMMAX"):
        if k in header:
            h = header[k]
            print("  %s = (%s, %s, %s)" % (k, h.get("x"), h.get("y"), h.get("z")))
    xs, ys = [], []
    kinds = {}
    circles = []
    for e in ents:
        t = e["type"]
        kinds[t] = kinds.get(t, 0) + 1
        if t in ("LINE", "LWPOLYLINE", "POLYLINE", "CIRCLE", "ARC", "SPLINE", "ELLIPSE", "INSERT", "3DFACE", "POINT"):
            x = y = None
            for code, val in e["data"]:
                if code == 10:
                    try:
                        x = float(val)
                    except ValueError:
                        pass
                elif code == 20:
                    try:
                        y = float(val)
                    except ValueError:
                        pass
                if x is not None and y is not None:
                    xs.append(x)
                    ys.append(y)
                    if t == "CIRCLE":
                        r = None
                        for c2, v2 in e["data"]:
                            if c2 == 40:
                                r = float(v2)
                        circles.append((x, y, r))
                    x = y = None
    print("  entity counts:", ", ".join("%s:%d" % (k, v) for k, v in sorted(kinds.items(), key=lambda kv: -kv[1])[:12]))
    if xs:
        print("  geometry X: %.2f .. %.2f  (%.2f mm)" % (min(xs), max(xs), max(xs) - min(xs)))
        print("  geometry Y: %.2f .. %.2f  (%.2f mm)" % (min(ys), max(ys), max(ys) - min(ys)))
    if circles:
        radii = {}
        for (cx, cy, r) in circles:
            if r:
                rr = round(r, 1)
                radii[rr] = radii.get(rr, 0) + 1
        print("  circle radii:", ", ".join("r=%s x%d" % (k, v) for k, v in sorted(radii.items(), key=lambda kv: -kv[1])[:12]))
        print("  circle centers (sample):", circles[:8])
    return header, ents


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    for p in sys.argv[1:]:
        try:
            summarize(p)
        except Exception as exc:  # noqa
            print("FAILED", p, exc)
