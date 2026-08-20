# -*- coding: utf-8 -*-
"""
Dung ban web tra cuu du lieu NRO cho GitHub Pages.

Xuat 5 bang: vat pham, ky nang, quai, NPC, ban do.
Icon (item + ky nang + avatar NPC) don vao MOT anh atlas duy nhat kem bang toa do,
thay vi nhung base64 tung anh. Do do trang chi tai 1 anh roi cache, lat trang
sau khong tai them gi.

    python tools/build_site.py              # atlas 255 mau, nho nhat
    python tools/build_site.py --lossless   # atlas giu nguyen mau
"""
import collections
import csv
import hashlib
import io
import json
import os
import subprocess
import sys

from PIL import Image

import mobsprite

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

MYSQL = r"C:/xampp/mysql/bin/mysql.exe"
DB = "tiennghich2d"
ICON_DIR = r"D:/Teamobi2026/SRC/data/icon/x2"
MOB_DIR = r"D:/Teamobi2026/SRC/data/mob/x2"
TEMPLATE = os.path.join(HERE, "site_template.html")
SITE = os.path.join(ROOT, "site")

ATLAS_WIDTH = 2048
PAD = 1
LOSSLESS = "--lossless" in sys.argv

GENDER = {0: "Trái Đất", 1: "Namếc", 2: "Xayda", 3: "Dùng chung"}
PLANET = {0: "Trái Đất", 1: "Namếc", 2: "Xayda"}

# Nhan loai vat pham lay tu comment trong UseItem.java, cho nao code co noi ro.
# Cac loai con lai suy tu ten vat pham (xem labels_from_names).
ITEM_TYPE_LABELS = {
    6: "Đậu thần",
    7: "Sách học kỹ năng",
    11: "Túi đồ",
    12: "Ngọc rồng",
    23: "Thú cưỡi (mới)",
    24: "Thú cưỡi (cũ)",
    33: "Thẻ nạp",
}

# Nhiem vu dung id am lam dia diem tuong trung, tuy hanh tinh nguoi choi ma doi.
# Lay tu hang so MAP_* / NPC_* trong ConstTask.java.
TASK_MAP_SYMBOL = {
    -1: "không chỉ định", -2: "Nhà", -3: "Map 200", -4: "Vách núi",
    -5: "Map 500", -6: "Trung tâm vũ trụ", -7: "Map quái bay 600",
    -8: "Làng", -9: "Map Quy Lão",
}
TASK_NPC_SYMBOL = {
    -1: "không chỉ định", -2: "NPC nhà", -3: "NPC Trung tâm vũ trụ",
    -4: "NPC shop làng", -5: "NPC Quy Lão",
}

# Chuoi nhiem vu chua %1..%14, thay bang ten thuc tuy hanh tinh.
# Lay tu hang so TEN_* trong ConstTask.java.
PLACEHOLDERS = {
    1: "tên làng", 2: "tên NPC nhà", 3: "tên map 200", 4: "tên quái map 200",
    5: "tên vách núi", 6: "tên map 500", 7: "tên NPC trung tâm vũ trụ",
    8: "tên NPC shop làng", 9: "tên quái bay 600", 10: "tên NPC Quy Lão",
    11: "tên map Quy Lão", 12: "tên quái 3000", 13: "tên map 600", 14: "tên quái 1000",
}


# ---------------------------------------------------------------- doc MySQL

def query(sql):
    proc = subprocess.run(
        [MYSQL, "-u", "root", "--default-character-set=utf8mb4",
         "--batch", "--raw", "--skip-column-names", DB, "-e", sql],
        capture_output=True)
    if proc.returncode != 0:
        sys.exit("Loi MySQL: " + proc.stderr.decode("utf-8", "replace"))
    text = proc.stdout.decode("utf-8", "replace")
    return list(csv.reader(io.StringIO(text), delimiter="\t", quoting=csv.QUOTE_NONE))


def rows_of(table, cols, order="id"):
    sql = "SELECT " + ",".join(f"IFNULL(`{c}`,'')" for c in cols) + f" FROM {table} ORDER BY {order};"
    return [r for r in query(sql) if len(r) >= len(cols)]


def num(v, d=0):
    try:
        return int(v)
    except (TypeError, ValueError):
        return d


def clean(v):
    return "" if v in ("NULL", None) else v


def chunks(raw, oc, cc, depth_wanted):
    """Cat cac doan can bang dau ngoac o dung mot do sau.

    Cac cot skills/waypoints trong DB KHONG phai JSON hop le: chung la mang ma
    moi phan tu boc trong nhay kep nhung nhay kep BEN TRONG lai khong escape:

        ["{"power_require":1000,"info":"hoc tai Su Phu"}","{...}"]

    json.loads chet ngay. Nhung ban than tung phan tu lai la JSON hop le, nen
    cach chac an la bo qua lop nhay kep, dem dau ngoac de cat tung phan tu ra.
    Ten trong du lieu khong chua dau ngoac nen dem the la du.
    """
    out = []
    depth = 0
    start = None
    for i, ch in enumerate(raw):
        if ch == oc:
            depth += 1
            if depth == depth_wanted:
                start = i
        elif ch == cc:
            if depth == depth_wanted and start is not None:
                out.append(raw[start:i + 1])
                start = None
            depth -= 1
    return out


def parse_objects(raw):
    """Lay cac object {...} nam trong mang boc ngoai."""
    if not raw:
        return []
    res = []
    for c in chunks(raw, "{", "}", 1):
        try:
            res.append(json.loads(c))
        except ValueError:
            pass
    return res


def parse_arrays(raw):
    """Lay cac mang [...] nam trong mang boc ngoai."""
    if not raw:
        return []
    res = []
    for c in chunks(raw, "[", "]", 2):
        try:
            res.append(json.loads(c))
        except ValueError:
            pass
    return res


# ---------------------------------------------------------------- tung bang

def load_items():
    cols = ["id", "TYPE", "gender", "NAME", "description", "level",
            "power_require", "gold", "gem", "icon_id", "part", "head", "body", "leg", "is_up_to_up"]
    return [{
        "id": num(r[0]), "type": num(r[1]), "gender": num(r[2]),
        "name": r[3], "desc": clean(r[4]),
        "level": num(r[5]), "power": num(r[6]), "gold": num(r[7]), "gem": num(r[8]),
        "icon": num(r[9], -1), "part": num(r[10], -1),
        "head": num(r[11], -1), "body": num(r[12], -1), "leg": num(r[13], -1),
        "upup": num(r[14]),
    } for r in rows_of("item_template", cols)]


def load_skills():
    cols = ["nclass_id", "id", "NAME", "max_point", "mana_use_type", "TYPE", "icon_id", "dam_info", "slot", "skills"]
    out = []
    for r in rows_of("skill_template", cols, order="nclass_id, id"):
        levels = parse_objects(r[9])
        out.append({
            "nclass": num(r[0]), "id": num(r[1]), "name": r[2],
            "maxPoint": num(r[3]), "manaType": num(r[4]), "type": num(r[5]),
            "icon": num(r[6], -1), "damInfo": clean(r[7]), "slot": num(r[8]),
            "levels": [{
                "id": num(lv.get("id"), -1), "point": num(lv.get("point")),
                "power": num(lv.get("power_require")), "damage": num(lv.get("damage")),
                "mana": num(lv.get("mana_use")), "cd": num(lv.get("cool_down")),
                "dx": num(lv.get("dx")), "dy": num(lv.get("dy")),
                "maxFight": num(lv.get("max_fight")), "price": num(lv.get("price")),
                "info": lv.get("info") or "",
            } for lv in levels],
        })
    return out


def load_mobs():
    cols = ["id", "TYPE", "NAME", "hp", "range_move", "speed", "dart_Type", "percent_dame", "percent_tiem_nang"]
    return [{
        "id": num(r[0]), "type": num(r[1]), "name": r[2], "hp": num(r[3]),
        "rangeMove": num(r[4]), "speed": num(r[5]), "dart": num(r[6]),
        "pctDame": num(r[7]), "pctTiemNang": num(r[8]),
    } for r in rows_of("mob_template", cols)]


def load_npcs():
    cols = ["id", "NAME", "head", "body", "leg", "avatar"]
    return [{
        "id": num(r[0]), "name": r[1],
        "head": num(r[2], -1), "body": num(r[3], -1), "leg": num(r[4], -1),
        "icon": num(r[5], -1),
    } for r in rows_of("npc_template", cols)]


def load_maps():
    cols = ["id", "NAME", "zones", "max_player", "type", "planet_id",
            "bg_type", "tile_id", "bg_id", "is_map_double", "waypoints", "mobs", "npcs"]
    out = []
    for r in rows_of("map_template", cols):
        wps = parse_arrays(r[10])
        mobs = parse_arrays(r[11])
        npcs = parse_arrays(r[12])
        out.append({
            "id": num(r[0]), "name": r[1], "zones": num(r[2]), "maxPlayer": num(r[3]),
            "type": num(r[4]), "planet": num(r[5]), "bgType": num(r[6]),
            "tile": num(r[7]), "bg": num(r[8]), "double": num(r[9]),
            # waypoint: [ten, minX, minY, maxX, maxY, isEnter, isOffline, mapTo, xTo, yTo]
            "waypoints": [{"name": w[0] if w else "", "to": num(w[7], -1) if len(w) > 7 else -1}
                          for w in wps if isinstance(w, list)],
            # mob trong map: [mobTemplateId, level, hp, x, y]
            "mobs": [{"t": num(m[0], -1), "lv": num(m[1]) if len(m) > 1 else 0,
                      "hp": num(m[2]) if len(m) > 2 else 0}
                     for m in mobs if isinstance(m, list) and m],
            # npc trong map: [npcTemplateId, x, y]
            "npcs": [num(n[0], -1) for n in npcs if isinstance(n, list) and n],
        })
    return out


def load_tasks():
    mains = rows_of("task_main_template", ["id", "NAME", "detail"])
    subs = rows_of("task_sub_template",
                   ["task_main_id", "NAME", "max_count", "notify", "npc_id", "map", "ducvupro"],
                   order="ducvupro")

    by_main = collections.defaultdict(list)
    for s in subs:
        by_main[num(s[0])].append({
            "name": s[1], "maxCount": num(s[2], -1), "notify": clean(s[3]),
            "npc": num(s[4], -1), "map": num(s[5], -1), "order": num(s[6]),
        })

    return [{
        "id": num(m[0]), "name": m[1], "detail": clean(m[2]),
        "subs": by_main.get(num(m[0]), []),
    } for m in mains]


def load_parts(part_ids):
    """Doc bang part cho cac id can dung.

    Moi part la mot bo khung hinh: DATA = [[imgId, dx, dy], ...].
    So khung tuy TYPE, dung nhu lop Part trong client:
    type 0 dau = 3 khung, type 1 than = 17 khung, type 2 chan = 14 khung.
    """
    out = {}
    for r in rows_of("part", ["id", "TYPE", "DATA"]):
        pid = num(r[0])
        if pid not in part_ids:
            continue
        try:
            frames = [[num(f[0], -1), num(f[1]), num(f[2])] for f in json.loads(r[2])]
        except (ValueError, TypeError, IndexError):
            continue
        out[pid] = {"type": num(r[1]), "frames": frames}
    return out


def load_char_info():
    """Bang hoat anh nhan vat, 33 khung x 4 bo phan x [chi so khung, dx, dy].

    Trich tu Char.CharInfo trong client da decompile. Day la bang quyet dinh
    o khung thu i thi dau/chan/than lay khung nao va dat lech bao nhieu -
    khong co no thi khong the ghep ba manh cho dung vi tri.
    """
    path = os.path.join(HERE, "charinfo.json")
    if not os.path.exists(path):
        print("  (thieu charinfo.json, bo qua phan hoat anh)")
        return []
    with io.open(path, encoding="utf-8") as f:
        return json.load(f)


def load_power_marks(items, skills):
    """Cac moc suc manh: gom tat ca power_require cua vat pham va tung cap ky nang.

    Day khong phai bang co san trong DB. No la thu duoc rut ra tu du lieu -
    tra loi cau hoi 'toi moc suc manh nay thi mo khoa duoc nhung gi'.
    """
    marks = {}

    def slot(p):
        return marks.setdefault(p, {"id": p, "power": p, "items": [], "skills": []})

    for it in items:
        if it["power"] > 0:
            slot(it["power"])["items"].append({"id": it["id"], "name": it["name"], "icon": it["icon"]})

    for s in skills:
        for lv in s["levels"]:
            if lv["power"] > 0:
                slot(lv["power"])["skills"].append({
                    "id": s["id"], "name": s["name"], "point": lv["point"], "icon": s["icon"],
                })

    out = sorted(marks.values(), key=lambda m: m["power"])
    for m in out:
        m["nItems"] = len(m["items"])
        m["nSkills"] = len(m["skills"])
        m["name"] = f"{m['power']:,}".replace(",", ".") + " sức mạnh"
    return out


# ------------------------------------------------------------------- atlas

def build_atlas(icon_ids):
    """Xep icon theo kieu ke: sap cao dan roi rai tung hang."""
    loaded = []
    for i in sorted(icon_ids):
        path = os.path.join(ICON_DIR, f"{i}.png")
        if os.path.exists(path):
            loaded.append((i, Image.open(path).convert("RGBA")))

    loaded.sort(key=lambda t: (-t[1].height, -t[1].width))

    placed = {}
    x = y = row_h = 0
    for i, im in loaded:
        w, h = im.size
        if x + w + PAD > ATLAS_WIDTH:
            x, y, row_h = 0, y + row_h + PAD, 0
        placed[i] = (x, y, w, h, im)
        x += w + PAD
        row_h = max(row_h, h)

    atlas = Image.new("RGBA", (ATLAS_WIDTH, y + row_h + PAD), (0, 0, 0, 0))
    coords = {}
    for i, (px, py, w, h, im) in placed.items():
        atlas.paste(im, (px, py))
        coords[i] = [px, py, w, h]
        im.close()
    return atlas, coords


def labels_from_names(rows, key="type"):
    """Suy nhan cho tung gia tri type bang tu dau pho bien nhat trong ten."""
    buckets = collections.defaultdict(collections.Counter)
    for r in rows:
        buckets[r[key]][(r["name"].split() or [""])[0]] += 1
    out = {}
    for t, c in buckets.items():
        word, n = c.most_common(1)[0]
        out[t] = word if n * 2 >= sum(c.values()) else f"Loại {t}"
    return out


# -------------------------------------------------------------------- main

def main():
    items, skills, mobs, npcs, maps = load_items(), load_skills(), load_mobs(), load_npcs(), load_maps()
    tasks = load_tasks()
    powers = load_power_marks(items, skills)
    print(f"  {len(items)} vat pham | {len(skills)} ky nang "
          f"({sum(len(s['levels']) for s in skills)} cap) | {len(mobs)} quai | "
          f"{len(npcs)} npc | {len(maps)} map | {len(tasks)} nhiem vu "
          f"({sum(len(t['subs']) for t in tasks)} buoc) | {len(powers)} moc suc manh")

    os.makedirs(os.path.join(SITE, "assets"), exist_ok=True)

    mobSprites, mobSkipped = mobsprite.load_all(MOB_DIR)
    if mobSprites:
        mobAtlas, mobCoords = mobsprite.pack(mobSprites, ATLAS_WIDTH, PAD)
        mob_path = os.path.join(SITE, "assets", "mobs.png")
        if LOSSLESS:
            mobAtlas.save(mob_path, optimize=True)
        else:
            mobAtlas.quantize(colors=255, method=Image.FASTOCTREE).save(mob_path, optimize=True)
        print(f"  atlas quai {mobAtlas.width}x{mobAtlas.height}, {len(mobCoords)} sprite, "
              f"{os.path.getsize(mob_path)/1048576:.2f} MB"
              + (f" (bo qua {len(mobSkipped)}: {', '.join(n for n, _ in mobSkipped)})" if mobSkipped else ""))
    else:
        mobCoords = {}

    # bo khung hinh cua NPC: chi lay part ma NPC dung, khong lay het 2111 part
    # (het bang thi 12.819 anh / 31,7 MB, qua nang cho mot trang web tinh)
    npc_part_ids = set()
    for n in npcs:
        npc_part_ids.update(p for p in (n["head"], n["body"], n["leg"]) if p >= 0)
    parts = load_parts(npc_part_ids)
    charInfo = load_char_info()
    print(f"  {len(parts)} bo phan NPC, {len(charInfo)} khung hoat anh")

    wanted = {it["icon"] for it in items if it["icon"] >= 0}
    wanted |= {s["icon"] for s in skills if s["icon"] >= 0}
    wanted |= {n["icon"] for n in npcs if n["icon"] >= 0}
    for p in parts.values():
        wanted |= {f[0] for f in p["frames"] if f[0] >= 0}

    atlas, coords = build_atlas(wanted)
    atlas_path = os.path.join(SITE, "assets", "icons.png")
    if LOSSLESS:
        atlas.save(atlas_path, optimize=True)
    else:
        # Ha xuong 255 mau: 4,25 MB -> 0,72 MB. Sai so chi o vien khu rang cua.
        atlas.quantize(colors=255, method=Image.FASTOCTREE).save(atlas_path, optimize=True)

    print(f"  atlas {atlas.width}x{atlas.height}, {len(coords)}/{len(wanted)} icon, "
          f"{os.path.getsize(atlas_path)/1048576:.2f} MB{' (lossless)' if LOSSLESS else ' (255 mau)'}")

    auto = labels_from_names(items)
    mobTypes = labels_from_names(mobs)

    # nhan tu code duoc uu tien, con lai lay nhan suy tu ten
    itemTypes = []
    examples = collections.defaultdict(list)
    for it in items:
        if len(examples[it["type"]]) < 3:
            examples[it["type"]].append(it["name"])

    for t, n in sorted(collections.Counter(i["type"] for i in items).items()):
        itemTypes.append({
            "id": t, "v": t,
            "label": ITEM_TYPE_LABELS.get(t, auto[t]),
            "fromCode": t in ITEM_TYPE_LABELS,
            "n": n,
            "examples": examples[t],
            "name": ITEM_TYPE_LABELS.get(t, auto[t]),
        })

    data = {
        "items": items,
        "skills": skills,
        "mobs": mobs,
        "npcs": npcs,
        "maps": maps,
        "tasks": tasks,
        "powers": powers,
        "parts": parts,
        "charInfo": charInfo,
        "mobSprites": {str(mid): {"infos": sp["infos"], "frames": sp["frames"],
                                  "seq": sp["seq"], "sheet": mobCoords[mid]}
                       for mid, sp in mobSprites.items() if mid in mobCoords},
        "itemTypes": itemTypes,
        "taskMapSymbol": TASK_MAP_SYMBOL,
        "taskNpcSymbol": TASK_NPC_SYMBOL,
        "placeholders": PLACEHOLDERS,
        "mobTypes": [{"v": t, "label": mobTypes[t], "n": n}
                     for t, n in sorted(collections.Counter(m["type"] for m in mobs).items())],
        "classes": [{"v": c, "n": n}
                    for c, n in sorted(collections.Counter(s["nclass"] for s in skills).items())],
        "planets": [{"v": p, "label": PLANET.get(p, f"Hành tinh {p}"), "n": n}
                    for p, n in sorted(collections.Counter(m["planet"] for m in maps).items())],
        "genders": [{"v": g, "label": l} for g, l in sorted(GENDER.items())],
    }

    for name, obj in (("data.json", data), ("icons.json", coords)):
        path = os.path.join(SITE, "assets", name)
        with io.open(path, "w", encoding="utf-8") as f:
            json.dump(obj, f, ensure_ascii=False, separators=(",", ":"))
        print(f"  {name}: {os.path.getsize(path)/1024:.0f} KB")

    old = os.path.join(SITE, "assets", "items.json")
    if os.path.exists(old):
        os.remove(old)

    # Dau ban build gan vao duong dan tai nguyen. Khong co no thi trinh duyet
    # co the giu data.json cu (GitHub Pages dat max-age=600) ghep voi index.html
    # moi -> trang bao loi vi thieu truong.
    stamp = hashlib.sha1()
    for name in ("data.json", "icons.json", "icons.png", "mobs.png"):
        with open(os.path.join(SITE, "assets", name), "rb") as f:
            stamp.update(f.read())
    build = stamp.hexdigest()[:10]

    html = io.open(TEMPLATE, encoding="utf-8").read().replace("__BUILD__", build)
    io.open(os.path.join(SITE, "index.html"), "w", encoding="utf-8").write(html)
    print(f"  ban build: {build}")

    total = sum(os.path.getsize(os.path.join(SITE, "assets", f))
                for f in os.listdir(os.path.join(SITE, "assets")))
    print(f"  -> {SITE} (assets {total/1048576:.2f} MB)")


if __name__ == "__main__":
    main()
