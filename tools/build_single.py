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

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SITE = os.path.join(ROOT, "site")
OUT = os.path.join(HERE, "item_search.html")


def read(name):
    with io.open(os.path.join(SITE, "assets", name), encoding="utf-8") as f:
        return f.read()


def main():
    html = io.open(os.path.join(SITE, "index.html"), encoding="utf-8").read()

    with open(os.path.join(SITE, "assets", "icons.png"), "rb") as f:
        atlas_b64 = base64.b64encode(f.read()).decode("ascii")

    html = html.replace('url("assets/icons.png")', f'url("data:image/png;base64,{atlas_b64}")')

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
