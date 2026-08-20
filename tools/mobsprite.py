# -*- coding: utf-8 -*-
"""
Doc sprite quai tu data/mob/x<zoom>/<id> va don vao mot atlas rieng.

Moi file quai la mot goi tron:

    [byte kieu][int do dai][du lieu khung][int do dai][PNG]

Phan du lieu khung dung format EffectData.readData cua client:

    byte  soManhAnh
      byte ID, ubyte x0, ubyte y0, ubyte w, ubyte h
    short soKhung
      byte soMieng
        short dx, short dy, byte idAnh

Ve mot khung = ve lan luot tung mieng: cat vung (x0,y0,w,h) cua manh anh co ID
tuong ung roi dat tai (dx, dy). Dung y het EffectData.paintFrame.

Quai co 'kieu' khac 0 la boss, client doc bang readDataNewBoss - format khac han,
o day bo qua.
"""
import io
import os
import struct

from PIL import Image


def _reader(data):
    pos = [0]

    def u8():
        v = data[pos[0]]; pos[0] += 1
        return v

    def i8():
        v = u8()
        return v - 256 if v > 127 else v

    def i16():
        v = struct.unpack_from(">h", data, pos[0])[0]; pos[0] += 2
        return v

    return u8, i8, i16


def parse_file(path):
    raw = open(path, "rb").read()
    kind = raw[0]
    if kind != 0:
        raise ValueError(f"kieu {kind} (boss, format khac)")

    pos = 1
    flen = struct.unpack_from(">i", raw, pos)[0]; pos += 4
    frame_data = raw[pos:pos + flen]; pos += flen
    plen = struct.unpack_from(">i", raw, pos)[0]; pos += 4
    png = raw[pos:pos + plen]

    u8, i8, i16 = _reader(frame_data)

    infos = {}
    for _ in range(i8()):
        iid = i8()
        infos[iid] = [u8(), u8(), u8(), u8()]      # x0, y0, w, h

    frames = []
    for _ in range(i16()):
        frames.append([[i16(), i16(), i8()] for _ in range(i8())])

    return {"infos": infos, "frames": frames, "png": png}


def load_all(mob_dir):
    sprites, skipped = {}, []
    if not os.path.isdir(mob_dir):
        return sprites, skipped

    for name in sorted(os.listdir(mob_dir)):
        path = os.path.join(mob_dir, name)
        if not os.path.isfile(path) or not name.isdigit():
            continue
        try:
            sprites[int(name)] = parse_file(path)
        except Exception as e:
            skipped.append((name, str(e)[:40]))
    return sprites, skipped


def pack(sprites, width, pad=1):
    """Don sprite sheet cua tung quai vao mot anh atlas, xep theo kieu ke."""
    loaded = [(mid, Image.open(io.BytesIO(s["png"])).convert("RGBA"))
              for mid, s in sprites.items()]
    loaded.sort(key=lambda t: (-t[1].height, -t[1].width))

    placed = {}
    x = y = row_h = 0
    for mid, im in loaded:
        w, h = im.size
        if x + w + pad > width:
            x, y, row_h = 0, y + row_h + pad, 0
        placed[mid] = (x, y, w, h, im)
        x += w + pad
        row_h = max(row_h, h)

    atlas = Image.new("RGBA", (width, y + row_h + pad), (0, 0, 0, 0))
    coords = {}
    for mid, (px, py, w, h, im) in placed.items():
        atlas.paste(im, (px, py))
        coords[mid] = [px, py, w, h]
        im.close()
    return atlas, coords
