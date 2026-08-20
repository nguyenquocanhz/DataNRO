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
| Loại đồ | 33 | suy từ `item_template` |
| Nhiệm vụ | 30 (125 bước) | `task_main_template` + `task_sub_template` |
| Mốc sức mạnh | 88 | rút từ `power_require` |

- **2.415 icon** (vật phẩm, kỹ năng, avatar NPC, mảnh sprite nhân vật) gộp trong một ảnh atlas duy nhất
- **Tra chéo**: mở một bản đồ thấy bảng quái và bảng NPC trong đó kèm đầy đủ cột; mở một con quái thấy nó xuất hiện ở những bản đồ nào
- **Preview hoạt ảnh**: mở một NPC thấy nhân vật ghép từ ba mảnh đầu / thân / chân; mở một con quái thấy nó cử động qua từng khung
- **Địa điểm nhiệm vụ**: mỗi bước nhiệm vụ kèm NPC và bản đồ; id âm là địa điểm tượng trưng (Nhà, Làng, Trung tâm vũ trụ…) đã giải nghĩa
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

## Preview hoạt ảnh nhân vật

Nhân vật trong NRO không phải một ảnh, mà là **ba mảnh ghép lại**: đầu, thân, chân. Mỗi mảnh nằm trong bảng `part`, cột `DATA` là danh sách khung hình dạng `[imgId, dx, dy]`. Số khung tuỳ loại: đầu 3, thân 17, chân 14.

Nhưng biết ba mảnh thôi thì chưa ghép được — còn cần biết **ở khung hình thứ i thì lấy khung nào của từng mảnh và đặt lệch bao nhiêu**. Bảng đó tên `CharInfo`, nằm trong client chứ không nằm trong DB: 33 khung × 4 mảnh × `[chỉ số khung, dx, dy]`. File `tools/charinfo.json` là bảng đó trích từ client đã decompile.

Công thức vẽ lấy nguyên từ `Char.paint` của client:

```
x = cx + (CharInfo[cf][k].dx + part.frames[pi].dx) − chiều_rộng_ảnh
y = cy − CharInfo[cf][k].dy + part.frames[pi].dy
```

Phần `− chiều_rộng_ảnh` là do client neo ảnh theo góc trên-phải (anchor 24 = `TOP | RIGHT`).

Một điểm đáng lưu ý: **phần lớn NPC chỉ có đúng một tư thế**. Bảng part của họ có đủ 3/14/17 ô nhưng chỉ một ô trỏ tới ảnh thật, còn lại trỏ tới ảnh id 0 (2×2 rỗng). Trang vì thế chỉ chạy qua những khung có ảnh thật, NPC đứng yên thì ghi rõ "chỉ có 1 tư thế".

Atlas chỉ gom mảnh của **NPC** (914 ảnh). Gom cả 2.111 part thì thành 12.819 ảnh / 31,7 MB, quá nặng cho một trang tĩnh.

### Quái thì khác hẳn

Quái không ghép từ ba mảnh. Mỗi con có **một sprite sheet riêng** nằm trong `data/mob/x2/<id>` — file đó là một gói trọn:

```
[byte kiểu][int độ dài][dữ liệu khung][int độ dài][PNG]
```

Phần dữ liệu khung dùng format `EffectData.readData` của client:

```
byte  soMảnhẢnh
  byte ID, ubyte x0, ubyte y0, ubyte w, ubyte h
short soKhung
  byte soMiếng
    short dx, short dy, byte idẢnh
```

Vẽ một khung = vẽ lần lượt từng miếng: cắt vùng `(x0,y0,w,h)` của mảnh ảnh có `ID` tương ứng rồi đặt tại `(dx, dy)`. Neo `TOP|LEFT`, không trừ chiều rộng như nhân vật.

Sprite sheet của **101 con** được gom vào atlas thứ hai `assets/mobs.png` (0,81 MB). 8 con bị bỏ qua vì dùng format boss (`readDataNewBoss`) hoặc file lỗi: 70, 76, 77, 85, 88, 89, 92, 93.

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

Đường dẫn tài nguyên có gắn dấu bản build (`?v=…`, băm từ nội dung). Không có nó thì trình duyệt có thể giữ `data.json` cũ — GitHub Pages đặt `Cache-Control: max-age=600` — rồi ghép với `index.html` mới, và trang sẽ báo lỗi thiếu trường.

Muốn bản không mất màu:

```bash
python tools/build_site.py --lossless
```

## Cấu trúc

```
index.html            trang tra cứu, không phụ thuộc thư viện ngoài
assets/
  icons.png           atlas 2048×2532, 2.415 icon (kèm mảnh sprite NPC)
  mobs.png            atlas sprite sheet của 101 quái
  icons.json          icon_id -> [x, y, w, h] trên atlas
  data.json           8 bảng dữ liệu + bảng part + bảng CharInfo
tools/
  build_site.py       sinh lại toàn bộ từ MySQL + thư mục icon
  build_single.py     gộp thành một file HTML chạy offline
  site_template.html  khuôn của index.html
  charinfo.json       bảng hoạt ảnh 33 khung trích từ client
  mobsprite.py        đọc và đóng gói sprite quái
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

Script đọc 8 bảng, xếp icon vào atlas theo kiểu kệ (sắp cao dần rồi rải từng hàng), rồi ghi `index.html` + 2 file trong `assets/`.

Một lưu ý khi đọc dữ liệu: cột `skills` của `skill_template` và `waypoints` của `map_template` **không phải JSON hợp lệ** — chúng là mảng mà mỗi phần tử bọc trong nháy kép nhưng nháy kép bên trong lại không escape:

```
["{"power_require":1000,"info":"học tại Sư Phụ"}","{...}"]
```

`json.loads` chết ngay. Script vì thế bỏ qua lớp nháy kép, đếm dấu ngoặc để cắt từng phần tử ra rồi mới parse.

## Ghi chú

Icon và dữ liệu vật phẩm thuộc về TeaMobi. Repo này chỉ là công cụ tra cứu cho việc phát triển máy chủ cá nhân.
