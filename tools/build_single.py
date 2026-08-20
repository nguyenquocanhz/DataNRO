# -*- coding: utf-8 -*-
"""
Gop ban web thanh MOT file HTML duy nhat, chay bang cach mo file, khong can server.

Chay sau build_site.py. Lay nguyen site/ roi nhung du lieu vao the script
va nhung atlas vao CSS duoi dang data URI.

    python tools/build_site.py && python tools/build_single.py
"""
import base64
import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SITE = os.path.join(ROOT, "site")
OUT = os.path.join(HERE, "item_search.html")


def read(name):
    with io.open(os.path.join(SITE, "assets", name), encoding="utf-8") as f:
        return f.read()


def main():
    html = io.open(os.path.join(SITE, "index.html"), encoding="utf-8").read()

    # Nhung ca hai atlas: icon va sprite quai.
    # Duong dan co gan dau ban build (?v=...) nen phai thay bang regex.
    for name in ("icons.png", "mobs.png"):
        path = os.path.join(SITE, "assets", name)
        if not os.path.exists(path):
            print(f"  (khong co {name}, bo qua)")
            continue

        with open(path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("ascii")

        pattern = r'url\("assets/' + name.replace(".", r"\.") + r'[^"]*"\)'
        html, n = re.subn(pattern, lambda _: f'url("data:image/png;base64,{b64}")', html)
        if n != 1:
            sys.exit(f"Khong thay duong dan {name} trong index.html (tim thay {n} cho)")

    data = read("data.json").replace("</", "<\\/")
    icons = read("icons.json").replace("</", "<\\/")
    inline = (f'<script id="inline-data" type="application/json">{data}</script>\n'
              f'<script id="inline-icons" type="application/json">{icons}</script>\n')

    # phai nam TRUOC script chinh, vi script chinh doc hai the nay ngay khi chay
    html = html.replace("<script>\n(function(){", inline + "<script>\n(function(){", 1)

    # Artifact tu boc <head>/<body>, nen bo lop the tai lieu ngoai di
    # keo long nhau thanh hai tang.
    for tag in ("<!DOCTYPE html>", '<html lang="vi">', "</html>",
                "<head>", "</head>", "<body>", "</body>"):
        html = html.replace(tag + "\n", "").replace(tag, "")

    io.open(OUT, "w", encoding="utf-8").write(html)
    print(f"  -> {OUT} ({os.path.getsize(OUT)/1048576:.2f} MB)")


if __name__ == "__main__":
    main()
