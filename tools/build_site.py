# -*- coding: utf-8 -*-
"""
Dung ban web tra cuu vat pham cho GitHub Pages.

Khac ban artifact mot file: o day icon duoc don vao MOT anh atlas duy nhat
kem bang toa do, thay vi nhung base64 tung anh. Loi:
  - base64 phinh du lieu them 33%, atlas thi khong
  - 1441 file PNG roi = 1441 request; atlas = 1 request
  - trinh duyet cache atlas mot lan, lat trang sau khong tai lai gi

    python tools/build_site.py
"""
import base64
import collections
import csv
import io
import json
import os
import subprocess
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

MYSQL = r"C:/xampp/mysql/bin/mysql.exe"
DB = "tiennghich2d"
ICON_DIR = r"D:/Teamobi2026/SRC/data/icon/x2"
TEMPLATE = os.path.join(HERE, "site_template.html")
SITE = os.path.join(ROOT, "site")

ATLAS_WIDTH = 2048
PAD = 1  # chua 1px cho cac icon canh nhau khong hut mau vao nhau khi scale
LOSSLESS = "--lossless" in sys.argv

COLS = ["id", "TYPE", "gender", "NAME", "description", "level",
        "power_require", "gold", "gem", "icon_id", "part", "head", "body", "leg", "is_up_to_up"]

GENDER = {0: "Trái Đất", 1: "Namếc", 2: "Xayda", 3: "Dùng chung"}


def query(sql):
    proc = subprocess.run(
        [MYSQL, "-u", "root", "--default-character-set=utf8mb4",
         "--batch", "--raw", "--skip-column-names", DB, "-e", sql],
        capture_output=True)
    if proc.returncode != 0:
        sys.exit("Loi MySQL: " + proc.stderr.decode("utf-8", "replace"))
    text = proc.stdout.decode("utf-8", "replace")
    return list(csv.reader(io.StringIO(text), delimiter="\t", quoting=csv.QUOTE_NONE))


def to_int(v, d=0):
    try:
        return int(v)
    except (TypeError, ValueError):
        return d


def load_items():
    sql = "SELECT " + ",".join(f"IFNULL(`{c}`,'')" for c in COLS) + " FROM item_template ORDER BY id;"
    rows = [r for r in query(sql) if len(r) >= len(COLS)]
    return [{
        "id": to_int(r[0]), "type": to_int(r[1]), "gender": to_int(r[2]),
        "name": r[3], "desc": "" if r[4] == "NULL" else r[4],
        "level": to_int(r[5]), "power": to_int(r[6]), "gold": to_int(r[7]), "gem": to_int(r[8]),
        "icon": to_int(r[9], -1), "part": to_int(r[10], -1),
        "head": to_int(r[11], -1), "body": to_int(r[12], -1), "leg": to_int(r[13], -1),
        "upup": to_int(r[14]),
    } for r in rows]


def build_atlas(icon_ids):
    """Xep icon theo kieu ke: sap cao dan roi rai tung hang. Don gian ma kin.

    Tra ve (anh atlas, {icon_id: [x, y, w, h]}).
    """
    loaded = []
    for i in sorted(icon_ids):
        path = os.path.join(ICON_DIR, f"{i}.png")
        if not os.path.exists(path):
            continue
        im = Image.open(path).convert("RGBA")
        loaded.append((i, im))

    loaded.sort(key=lambda t: (-t[1].height, -t[1].width))

    placed = {}
    x = y = row_h = 0
    for i, im in loaded:
        w, h = im.size
        if x + w + PAD > ATLAS_WIDTH:
            x = 0
            y += row_h + PAD
            row_h = 0
        placed[i] = (x, y, w, h, im)
        x += w + PAD
        row_h = max(row_h, h)

    height = y + row_h + PAD
    atlas = Image.new("RGBA", (ATLAS_WIDTH, height), (0, 0, 0, 0))
    coords = {}
    for i, (px, py, w, h, im) in placed.items():
        atlas.paste(im, (px, py))
        coords[i] = [px, py, w, h]
        im.close()

    return atlas, coords


def type_labels(items):
    buckets = collections.defaultdict(collections.Counter)
    for it in items:
        buckets[it["type"]][(it["name"].split() or [""])[0]] += 1
    labels = {}
    for t, c in buckets.items():
        word, n = c.most_common(1)[0]
        labels[t] = word if n * 2 >= sum(c.values()) else f"Loại {t}"
    return labels


def main():
    items = load_items()
    print(f"  {len(items)} vat pham")

    os.makedirs(os.path.join(SITE, "assets"), exist_ok=True)

    atlas, coords = build_atlas({it["icon"] for it in items if it["icon"] >= 0})
    atlas_path = os.path.join(SITE, "assets", "icons.png")

    if LOSSLESS:
        atlas.save(atlas_path, optimize=True)
    else:
        # Ha xuong bang mau 255 mau: 4.25 MB -> 0.72 MB.
        # Sai so chi o vien khu rang cua, o co 40px khong nhan ra.
        # Muon ban khong mat mau thi chay: python tools/build_site.py --lossless
        atlas.quantize(colors=255, method=Image.FASTOCTREE).save(atlas_path, optimize=True)

    print(f"  atlas {atlas.width}x{atlas.height}, {len(coords)} icon, "
          f"{os.path.getsize(atlas_path)/1048576:.2f} MB"
          f"{' (lossless)' if LOSSLESS else ' (255 mau)'}")

    counts = collections.Counter(it["type"] for it in items)
    labels = type_labels(items)

    meta = {
        "items": items,
        "types": [{"t": t, "label": labels[t], "n": counts[t]} for t in sorted(counts)],
        "genders": [{"g": g, "label": l} for g, l in sorted(GENDER.items())],
        "atlas": {"w": atlas.width, "h": atlas.height},
    }

    for name, obj in (("items.json", meta), ("icons.json", coords)):
        path = os.path.join(SITE, "assets", name)
        with io.open(path, "w", encoding="utf-8") as f:
            json.dump(obj, f, ensure_ascii=False, separators=(",", ":"))
        print(f"  {name}: {os.path.getsize(path)/1024:.0f} KB")

    html = io.open(TEMPLATE, encoding="utf-8").read()
    html = html.replace("__COUNT__", f"{len(items):,}".replace(",", "."))
    io.open(os.path.join(SITE, "index.html"), "w", encoding="utf-8").write(html)

    total = sum(os.path.getsize(os.path.join(SITE, "assets", f))
                for f in os.listdir(os.path.join(SITE, "assets")))
    print(f"  -> {SITE} (tong {total/1048576:.2f} MB)")


if __name__ == "__main__":
    main()
