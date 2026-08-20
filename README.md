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

## Các cột trong từng bảng

### Vật phẩm — `item_template`

| Cột | Ý nghĩa |
|---|---|
| `id` | khoá chính, cũng là id người chơi thấy trong rương |
| `TYPE` | nhóm vật phẩm (0 áo, 1 quần, 2 găng, 3 giày, 4 nhẫn…) |
| `gender` | 0 Trái Đất · 1 Namếc · 2 Xayda · 3 dùng chung |
| `NAME`, `description` | tên và mô tả |
| `level` | cấp yêu cầu |
| `power_require` | sức mạnh yêu cầu |
| `gold`, `gem` | giá vàng và giá ngọc |
| `icon_id` | trỏ tới `data/icon/x{zoom}/{icon_id}.png` |
| `part` | id phần thân khi mặc lên người, `-1` là không mặc được |
| `head`, `body`, `leg` | id sprite riêng cho đồ thay hình |
| `is_up_to_up` | có nâng cấp được không |

### Kỹ năng — `skill_template`

| Cột | Ý nghĩa |
|---|---|
| `nclass_id` | lớp nhân vật sở hữu kỹ năng |
| `id` | id kỹ năng trong lớp đó |
| `NAME` | tên |
| `max_point` | số điểm tối đa nâng được |
| `mana_use_type` | kiểu tiêu hao mana |
| `TYPE` | kiểu kỹ năng |
| `icon_id` | icon, chung không gian id với vật phẩm |
| `dam_info` | chuỗi mẫu mô tả sát thương, `#` là chỗ thế số |
| `slot` | ô kỹ năng trên thanh |
| `skills` | **từng cấp một, dạng JSON** |

Mỗi phần tử trong `skills` là một cấp:

```json
{"id":7,"point":1,"power_require":10000,"damage":150,"mana_use":30,
 "cool_down":2000,"dx":160,"dy":160,"max_fight":1,"price":500,
 "info":"(Kame joko) Học tại Sư Phụ"}
```

`cool_down` tính bằng mili giây. `dx`/`dy` là tầm đánh. Mô hình "mỗi cấp một bản ghi" nghĩa là server không tính công thức theo cấp mà tra thẳng bảng — đổi cân bằng game là sửa dữ liệu, không sửa code.

### Quái — `mob_template`

| Cột | Ý nghĩa |
|---|---|
| `id`, `TYPE`, `NAME` | id, nhóm quái, tên |
| `hp` | máu |
| `range_move` | tầm đi lại quanh chỗ đứng |
| `speed` | tốc độ |
| `dart_Type` | kiểu phi tiêu bắn ra |
| `percent_dame` | % sát thương |
| `percent_tiem_nang` | % tiềm năng rơi ra |

### NPC — `npc_template`

| Cột | Ý nghĩa |
|---|---|
| `id`, `NAME` | id và tên |
| `head`, `body`, `leg` | ba mảnh sprite dựng hình NPC |
| `avatar` | icon mặt, dùng chung không gian id với vật phẩm |

### Bản đồ — `map_template`

| Cột | Ý nghĩa |
|---|---|
| `id`, `NAME` | id và tên |
| `zones` | số khu trong map |
| `max_player` | số người tối đa mỗi khu |
| `type` | kiểu map |
| `planet_id` | 0 Trái Đất · 1 Namếc · 2 Xayda |
| `tile_id`, `bg_id`, `bg_type` | bộ tile và ảnh nền |
| `is_map_double` | map đôi hay không |
| `waypoints`, `mobs`, `npcs` | **danh sách mảng, xem bên dưới** |

Ba cột cuối là mảng mà mỗi phần tử là một mảng số, không có tên trường:

```
waypoints  [tên, minX, minY, maxX, maxY, isEnter, isOffline, mapTo, xTo, yTo]
mobs       [mobTemplateId, level, hp, x, y]
npcs       [npcTemplateId, x, y]
```

Nhờ ba cột này mà trang tra chéo được: mở một bản đồ ra là thấy tên quái, tên NPC và cửa đi trong đó; mở một con quái là thấy nó đứng ở những bản đồ nào.

Ý nghĩa từng ô trong ba mảng trên là **suy ra từ dữ liệu thật đối chiếu với parser trong client**, không phải từ tài liệu chính thức — dùng thì nên kiểm lại nếu server của bạn khác bản này.

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
