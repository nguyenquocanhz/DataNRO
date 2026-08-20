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
    """Doc mot file quai.

    Byte dau la 'kieu', quyet dinh client doc bang ham nao:
      0        -> readData
      1        -> readMobNew voi typeread = 1
      khac     -> readMobNew, va khi do x0/y0 cua manh anh la SHORT chu khong
                  phai byte. Day la khac biet duy nhat giua hai ham; boss to
                  hon 255px nen mot byte khong du de chi toa do trong sheet.
    """
    raw = open(path, "rb").read()

    # Phan lon file co header 1 byte (kieu). Vai file lai co 2 byte: [id][kieu].
    # Nhan ra bang cach thu doc int do dai phan khung: chi mot trong hai vi tri
    # cho ra do dai nam gon trong file.
    head = None
    for h in (1, 2):
        try:
            v = struct.unpack_from(">i", raw, h)[0]
            if 0 < v < len(raw) - h - 8:
                head = h
                break
        except struct.error:
            pass
    if head is None:
        raise ValueError("khong doc duoc do dai phan khung")

    kind = raw[head - 1]
    wide = kind not in (0, 1)

    pos = head
    flen = struct.unpack_from(">i", raw, pos)[0]; pos += 4
    frame_data = raw[pos:pos + flen]; pos += flen
    plen = struct.unpack_from(">i", raw, pos)[0]; pos += 4
    png = raw[pos:pos + plen]

    u8, i8, i16 = _reader(frame_data)
    coord = i16 if wide else u8

    infos = {}
    for _ in range(i8()):
        iid = i8()
        x0, y0 = coord(), coord()
        infos[iid] = [x0, y0, u8(), u8()]          # x0, y0, w, h

    frames = []
    for _ in range(i16()):
        frames.append([[i16(), i16(), i8()] for _ in range(i8())])

    # Sau danh sach khung con mot bang nua: thu tu phat hoat anh.
    # Game khong phat khung theo thu tu 0,1,2... ma theo bang nay.
    seq = []
    try:
        for _ in range(i16()):
            seq.append(i16())
    except (IndexError, struct.error):
        seq = []

    return {"kind": kind, "infos": infos, "frames": frames, "seq": seq, "png": png}


def load_all(mob_dir):
    sprites, skipped = {}, []
    if not os.path.isdir(mob_dir):
        return sprites, skipped

    dropped = 0
    for name in sorted(os.listdir(mob_dir)):
        path = os.path.join(mob_dir, name)
        if not os.path.isfile(path) or not name.isdigit():
            continue
        try:
            sp = parse_file(path)

            # Vai manh khai bao vung cat nam ngoai sheet (vi du y0 = 255 nhu mot
            # gia tri danh dau). Trong atlas gop, cat ra ngoai la an nham sang
            # sheet cua con ben canh, nen bo han cac manh do.
            with Image.open(io.BytesIO(sp["png"])) as im:
                W, H = im.size
            bad = [i for i, r in sp["infos"].items()
                   if r[0] + r[2] > W or r[1] + r[3] > H or r[2] <= 0 or r[3] <= 0]
            for i in bad:
                del sp["infos"][i]
            dropped += len(bad)

            sprites[int(name)] = sp
        except Exception as e:
            skipped.append((name, str(e)[:40]))

    if dropped:
        print(f"  (bo {dropped} manh anh khai bao vuot ra ngoai sheet)")
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
