# DataNRO — Kho Dữ Liệu

Trang tra cứu dữ liệu NRO: vật phẩm, kỹ năng, quái, NPC, bản đồ. Tìm theo tên hoặc id, bấm một cái là chép được id.

**Xem tại:** https://nguyenquocanhz.github.io/DataNRO/

## Có gì

| Bảng | Số dòng | Nguồn |
|---|---|---|
| Vật phẩm | 1.999 | `item_template` |
| Kỹ năng | 27 (198 cấp) | `skill_template` |
| Quái | 119 | `mob_template` |
| NPC | 93 | `npc_template` |
| Bản đồ | 165 | `map_template` |

- **1.515 icon** (vật phẩm, kỹ năng, avatar NPC) gộp trong một ảnh atlas duy nhất
- **Tra chéo**: mở một bản đồ thấy luôn tên quái, tên NPC và cửa đi trong đó; mở một con quái thấy nó xuất hiện ở những bản đồ nào
- Vật phẩm / kỹ năng / NPC hiện dạng thẻ có icon; quái và bản đồ hiện dạng bảng vì dữ liệu thiên về số
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
| Atlas WebP lossless | 3,32 MB | 1 |
| **Atlas PNG 255 màu** | **0,72 MB** | **1** |

*(đo trên 1.440 icon vật phẩm; bản hiện tại thêm icon kỹ năng và avatar NPC, tổng 1.515 icon, atlas 0,92 MB)*

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
  icons.png           atlas 2048×1773, 1.515 icon
  icons.json          icon_id -> [x, y, w, h] trên atlas
  data.json           5 bảng dữ liệu + bảng nhãn loại/phái/hành tinh
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

Script đọc 5 bảng, xếp icon vào atlas theo kiểu kệ (sắp cao dần rồi rải từng hàng), rồi ghi `index.html` + 2 file trong `assets/`.

Một lưu ý khi đọc dữ liệu: cột `skills` của `skill_template` và `waypoints` của `map_template` **không phải JSON hợp lệ** — chúng là mảng mà mỗi phần tử bọc trong nháy kép nhưng nháy kép bên trong lại không escape:

```
["{"power_require":1000,"info":"học tại Sư Phụ"}","{...}"]
```

`json.loads` chết ngay. Script vì thế bỏ qua lớp nháy kép, đếm dấu ngoặc để cắt từng phần tử ra rồi mới parse.

## Ghi chú

Icon và dữ liệu vật phẩm thuộc về TeaMobi. Repo này chỉ là công cụ tra cứu cho việc phát triển máy chủ cá nhân.
