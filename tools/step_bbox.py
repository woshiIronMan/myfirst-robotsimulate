#!/usr/bin/env python
"""Rough bounding box of a STEP file from its CARTESIAN_POINT records (mm)."""
import sys
import re

PT = re.compile(r"CARTESIAN_POINT\s*\(\s*'[^']*'\s*,\s*\(\s*([-0-9.eE+]+)\s*,\s*([-0-9.eE+]+)\s*,\s*([-0-9.eE+]+)\s*\)")


def bbox(path):
    xs = ys = zs = None
    n = 0
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            if "CARTESIAN_POINT" not in line:
                continue
            for m in PT.finditer(line):
                x, y, z = (float(m.group(1)), float(m.group(2)), float(m.group(3)))
                if xs is None:
                    xs = [x, x]
                    ys = [y, y]
                    zs = [z, z]
                else:
                    xs[0] = min(xs[0], x); xs[1] = max(xs[1], x)
                    ys[0] = min(ys[0], y); ys[1] = max(ys[1], y)
                    zs[0] = min(zs[0], z); zs[1] = max(zs[1], z)
                n += 1
    return xs, ys, zs, n


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    for p in sys.argv[1:]:
        xs, ys, zs, n = bbox(p)
        if xs is None:
            print(p, ": no points")
            continue
        print("%s" % p)
        print("  points=%d" % n)
        print("  X: %10.2f .. %10.2f   size=%8.2f" % (xs[0], xs[1], xs[1] - xs[0]))
        print("  Y: %10.2f .. %10.2f   size=%8.2f" % (ys[0], ys[1], ys[1] - ys[0]))
        print("  Z: %10.2f .. %10.2f   size=%8.2f" % (zs[0], zs[1], zs[1] - zs[0]))
