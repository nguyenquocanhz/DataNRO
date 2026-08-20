# DataNRO — Kho Vật Phẩm

Trang tra cứu vật phẩm NRO: tìm theo tên hoặc id, xem icon, bấm một cái là chép được id.

**Xem tại:** https://nguyenquocanhz.github.io/DataNRO/

## Có gì

- **1.999 vật phẩm** từ bảng `item_template`
- **1.440 icon** gộp trong một ảnh atlas duy nhất
- Tìm kiếm **không dấu vẫn ra** — gõ `ao vai` ra `Áo vải 3 lỗ`
- Lọc theo loại và phái, sắp xếp theo id / tên / cấp / sức mạnh / giá
- Phân trang 60 · 120 · 240 mỗi trang, phím `←` `→` lật trang
- Chạy hoàn toàn tĩnh, không cần server, không cần API

## Vì sao gộp icon thành atlas

| Cách | Dung lượng | Số request |
|---|---|---|
| 1.441 file PNG rời | 3,84 MB | 1.441 |
| Nhúng base64 vào HTML | 5,12 MB | 1 |
| Atlas PNG RGBA | 4,25 MB | 1 |
| **Atlas PNG 255 màu** | **0,72 MB** | **1** |

Base64 phình dữ liệu thêm 33% nên là lựa chọn tệ nhất. Atlas RGBA thì một ảnh lớn nén kém hơn nhiều ảnh nhỏ rời rạc. Hạ bảng màu xuống 255 màu mới là chỗ ăn tiền: **nhỏ đi 6 lần**, sai số chỉ nằm ở viền khử răng cưa, ở cỡ 40px không nhận ra.

Tải một lần rồi trình duyệt cache, lật trang sau không tải thêm gì.

Muốn bản không mất màu:

```bash
python tools/build_site.py --lossless
```

## Cấu trúc

```
index.html            trang tra cứu, không phụ thuộc thư viện ngoài
assets/
  icons.png           atlas 2048×1233, 1.440 icon
  icons.json          icon_id -> [x, y, w, h] trên atlas
  items.json          1.999 vật phẩm + bảng loại + bảng phái
tools/
  build_site.py       sinh lại toàn bộ từ MySQL + thư mục icon
  site_template.html  khuôn của index.html
```

## Dựng lại

Cần MySQL có bảng `item_template` và thư mục icon của server.

```bash
pip install pillow
python tools/build_site.py
```

Sửa đường dẫn ở đầu `tools/build_site.py` cho khớp máy bạn:

```python
MYSQL    = r"C:/xampp/mysql/bin/mysql.exe"
DB       = "tiennghich2d"
ICON_DIR = r"D:/.../data/icon/x2"
```

Script sẽ đọc `item_template`, xếp icon vào atlas theo kiểu kệ (sắp cao dần rồi rải từng hàng), rồi ghi `index.html` + 3 file trong `assets/`.

## Ghi chú

Icon và dữ liệu vật phẩm thuộc về TeaMobi. Repo này chỉ là công cụ tra cứu cho việc phát triển máy chủ cá nhân.
