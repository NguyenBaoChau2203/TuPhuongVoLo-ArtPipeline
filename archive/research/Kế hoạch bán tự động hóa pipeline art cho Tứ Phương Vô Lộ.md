# Kế hoạch bán tự động hóa pipeline art cho Tứ Phương Vô Lộ

## Tóm tắt điều hành

Báo cáo này xây một phương án **semi-automated, ưu tiên độ chắc chắn và khả năng tái lập** cho pipeline art của *Tứ Phương Vô Lộ*, bám theo nhu cầu sản xuất asset từ bản vẽ/line art 2D sang cảnh isometric có thể render hàng loạt, với trọng tâm là: vector hóa sạch, dọn SVG, đưa vào DCC, extrude tường, dựng camera isometric, render hàng loạt, và giảm thao tác tay trong Illustrator bằng Actions/JSX. Phạm vi này phù hợp với bài toán pipeline bạn đã mô tả trong các tệp đã dán. fileciteturn0file0 fileciteturn0file1

Kết luận cốt lõi của nghiên cứu là: **tuyến an toàn nhất** không phải “AI tạo tất cả”, mà là pipeline lai gồm **Illustrator + Potrace/Vectorizer.AI + vpype + svgpathtools + Blender**, còn **Maya** nên đóng vai trò nhánh nâng cao hoặc nhánh studio khi bạn thực sự cần tiếp tục trong hệ Autodesk. Lý do là Illustrator hiện có Image Trace, Auto-Simplify, Export for Screens, Actions và Script menu rất rõ ràng; Potrace cho tracing trắng đen ổn định và lâu năm; vpype mạnh ở tối ưu đường vector theo pipeline CLI; svgpathtools mạnh ở phân tích/chuẩn hóa SVG bằng Python; Blender có đường đi SVG→curve→mesh rất phù hợp cho extrude và render batch; trong khi với Maya, tôi xác minh chắc tài liệu Python/mayapy/USD rất tốt, nhưng **không xác minh được một “SVG import” first-party chính thức tương đương Blender** trong trang product help mà tôi truy cập được, nên nếu vào Maya thì đường đi chắc chắn hơn là **tự parse SVG bằng Python** hoặc **đi qua Blender/USD**. citeturn50view0turn50view4turn54view0turn55view0turn33view0turn63view0turn36view0turn16view0turn16view2turn61view0

Nếu mục tiêu của bạn là triển khai trong 7–30 ngày với rủi ro thấp, tôi khuyến nghị chốt **workflow “Semi-Automated”** như sau:  
**Illustrator 29.8.7 LTS** cho thao tác sản xuất ổn định; dùng **Illustrator 30.4** chỉ ở nhánh R&D nếu bạn muốn thử thêm Text to Vector/Turntable; **Potrace 1.16** cho line art trắng đen; **vpype 1.15.0** cho clean-up batch; **svgpathtools 1.7.2** cho rule-based cleanup; **Vectorizer.AI** khi cần tracing màu/shape fitting tốt hơn; **Blender LTS 4.x** làm đầu ra isometric mặc định; **Maya 2026 + mayapy** chỉ khi cần bám pipeline Autodesk hoặc USD; **IfcOpenShell/Bonsai** và **Sweet Home 3D 7.5** chỉ nên dùng như công cụ phụ cho blockout tỷ lệ/phòng, không nên là lõi của pipeline game art stylized. citeturn47view2turn47view1turn33view0turn63view0turn37view1turn34view0turn35view0turn61view0turn38view0turn38view2turn40view1turn40view2

Điểm quan trọng nhất để tránh “tự động hóa nửa vời” là **chuẩn hóa đầu vào**: SVG phải có lớp rõ ràng, quy ước đặt tên rõ, đường tường là closed path, không dùng hiệu ứng Illustrator sống ở nhánh geometry, và tất cả asset đi qua một **naming/organizing agent** viết bằng Python để gắn version, trạng thái và loại asset ngay từ đầu. Nếu không làm phần chuẩn hóa này, mọi nỗ lực import/extrude/render batch về sau sẽ bị gãy. Đây là kết luận mang tính thực hành, suy ra từ khả năng batch hóa của Illustrator Actions/Scripts, vpype pipelines và batch processing bằng mayapy/Python. citeturn54view0turn55view0turn63view0turn16view2turn16view3

## Kiến trúc đề xuất

Tôi khuyến nghị chia pipeline thành **ba lớp** thay vì gom tất cả vào một DCC:

**Lớp authoring 2D**: Illustrator là nơi bạn hoặc artist vẽ/clean thủ công, dùng Image Trace khi cần, Auto-Simplify, Actions, Scripts, và Export for Screens. Illustrator hiện hỗ trợ chạy script qua `File > Scripts`, cài script vào thư mục `Scripting`, và chạy actions trên batch file. Export for Screens cho phép xuất nhiều artboard/asset cùng lúc sang PNG, JPEG, SVG, PDF, WebP và TIFF. citeturn50view0turn50view4turn55view0turn54view0turn54view2

**Lớp cleanup/vector-processing tự động**: Potrace/mkbitmap dùng cho line art hoặc mask đen trắng; Vectorizer.AI dùng cho input màu, logo, line art có transparency hoặc khi cần shape fitting tốt hơn; vpype dùng để hợp nhất đường, sắp xếp đường, giản lược node và đóng gói SVG; svgpathtools dùng để viết rule riêng như bỏ path nhỏ, đo bbox, phát hiện path discontinuous, tính area/length, hoặc tách layer trước khi vào DCC. Đây là lớp đem lại ROI lớn nhất vì chi phí triển khai thấp nhưng giúp giảm nhiều thao tác lặp. citeturn33view0turn34view0turn59view2turn60view0turn63view0turn36view0turn37view2

**Lớp 3D/isometric**: Blender là tuyến mặc định để import SVG, extrude tường, đặt camera orthographic isometric, render hàng loạt và xuất PNG. Maya được dùng khi bạn cần tiếp tục sang pipeline Autodesk/USD; khi đó nhánh an toàn là **Python tự parse SVG thành polygon/curve** hoặc **Blender → USD → Maya** qua plugin maya-usd chính thức. Plugin Maya USD là repo chính thức của Autodesk, hỗ trợ Maya 2023–2027 và cung cấp API import/export. citeturn23search0turn23search4turn61view0turn16view0turn20view1

Về nguyên tắc, pipeline nên xem **SVG là source of truth cho geometry 2D sạch**, còn `.blend` hoặc `.ma/.mb` là scene build artifact. Khi artist sửa tường/các contour trong Illustrator hay bằng Python cleanup, scene 3D phải có thể **rebuild từ SVG** thay vì chỉnh tay trong DCC. Điều này mới làm cho pipeline “bán tự động” thực sự, vì nó tạo được vòng lặp “sửa nguồn → rebuild scene → render lại”. Khả năng này phù hợp với mayapy cho batch processing và với mô hình pipeline CLI trong vpype. citeturn16view2turn16view3turn63view0

```mermaid
flowchart LR
    A[Sketch / floorplan / line art] --> B[Illustrator authoring]
    B --> C{Vectorization path}
    C -->|Black-white mask| D[mkbitmap + Potrace]
    C -->|Color or noisy art| E[Vectorizer.AI or Image Trace]
    D --> F[SVG clean]
    E --> F[SVG clean]
    F --> G[vpype optimize]
    G --> H[svgpathtools rules]
    H --> I{3D branch}
    I -->|Default| J[Blender import SVG]
    I -->|Autodesk branch| K[Maya Python parser or Maya USD bridge]
    J --> L[Extrude walls]
    K --> L[Extrude walls]
    L --> M[Isometric camera preset]
    M --> N[Batch render PNG]
    N --> O[Game-ready exports / review sheets]
```

Ở cấp tổ chức folder, bạn nên dùng một cấu trúc nhất quán, vì chính folder layout quyết định batch của Illustrator, Python và DCC có chạy thẳng được hay không.

| Thư mục | Vai trò | Đầu vào điển hình | Đầu ra điển hình |
|---|---|---|---|
| `assets/refs/` | Ảnh tham chiếu, moodboard, blueprint | PNG/JPG/PDF | Không build trực tiếp |
| `assets/2d/ai_src/` | File Illustrator gốc | `.ai` | SVG sạch, PNG preview |
| `assets/2d/svg_raw/` | SVG từ tracing ban đầu | `.svg` | Dùng cho cleanup |
| `assets/2d/svg_clean/` | SVG chuẩn hóa để build 3D | `.svg` | Source of truth cho scene |
| `assets/3d/blender/` | Scene Blender build từ SVG | `.blend` | PNG render, USD/FBX nếu cần |
| `assets/3d/maya/` | Scene Maya build từ SVG/USD | `.ma/.mb` | Render/scene downstream |
| `renders/iso/` | Render cuối | `.png/.webp` | Game review / content |
| `scripts/illustrator/` | JSX/JS/Actions | `.jsx/.aia` | Tự động hóa Illustrator |
| `scripts/python/` | Potrace/vpype/svgpathtools/naming agent | `.py/.yaml` | CLI batch |
| `tests/in/` | Test fixtures | motel room, island map | Dùng CI cục bộ |
| `tests/out_expected/` | Kỳ vọng hình học/render | SVG/PNG chuẩn | So QA |

Quy ước tên file nên có tối thiểu: `project_asset_variant_stage_v###`. Ví dụ: `tu_phuong_vo_lo_motel_room_a_svgclean_v003.svg`, `tu_phuong_vo_lo_island_small_blockout_v001.blend`, `tu_phuong_vo_lo_motel_room_iso_final_v007.png`. Việc này rất phù hợp để triển khai bằng Python `pathlib`, `re`, `csv` hoặc `yaml` và chạy như một “file naming/organizing agent”. Cách tiếp cận này không đến từ một phần mềm riêng, mà là mô-đun hạ tầng bạn nên tự viết vì nó mới khớp với dự án. citeturn54view0turn55view0turn16view2

## Bộ công cụ và tương thích

Bảng dưới đây chốt bộ công cụ mà tôi cho là **đủ cụ thể để bắt đầu ngay**, đồng thời chỉ ra **nên dùng ở đâu** và **khi nào nên tránh**.

| Công cụ | Version / mốc xác minh | Vai trò khuyến nghị | Ghi chú tương thích và caveat |
|---|---|---|---|
| **Adobe Illustrator** | **29.8.7 LTS** và **30.4** là hai mốc chính thức gần nhất tôi xác minh được | 2D authoring, Image Trace, Auto-Simplify, Scripts, Actions, Export for Screens | **29.8.7 LTS** hợp cho production ổn định; **30.4** hợp cho R&D nếu bạn muốn Turntable/Text to Vector và các cải tiến export gần đây. citeturn47view2turn47view1turn49view0 |
| **Illustrator scripting** | Không có “version” riêng; dùng cùng version Illustrator | JSX/ExtendScript làm trục chính cho automation trong Illustrator | Script chạy qua `File > Scripts`; cài vào thư mục `Scripting`; Illustrator hỗ trợ Visual Basic, AppleScript, JavaScript và ExtendScript. citeturn55view0 |
| **Maya** | **2026** là mốc tài liệu Autodesk tôi xác minh sâu nhất | Nhánh Autodesk, build scene, batch bằng mayapy, render / USD | Dùng `mayapy` để cài package và batch; Python API 2.0 là lựa chọn nên ưu tiên. citeturn16view0turn16view1turn16view2turn16view3 |
| **Maya USD** | Repo chính thức Autodesk, hỗ trợ Maya **2023–2027** | Cầu nối Blender/Maya hoặc pipeline USD về sau | Hợp khi scene cần sống lâu và qua nhiều DCC; chưa cần ở tuần đầu. citeturn61view0 |
| **Blender** | Khuyến nghị **Blender LTS 4.x**; nếu muốn chốt ngay thì dùng LTS hiện hành trong đội | SVG→curve→mesh, extrude, camera isometric, render batch | Trong phiên duyệt này tôi không lấy được manual chính thức của Blender một cách ổn định, nên khuyến nghị theo hướng **LTS 4.x** thay vì ép một build duy nhất; các snapshot công khai vẫn cho thấy Blender hỗ trợ nhập SVG và USD. citeturn23search0turn23search4 |
| **Potrace** | **1.16** | Tracing đen-trắng sạch, ổn định, deterministic | Cực mạnh cho mask/ink/line art; không phải lựa chọn tối ưu cho ảnh màu phức tạp. mkbitmap đi kèm Potrace. citeturn33view0 |
| **vpype** | **1.15.0**, Python `>=3.11,<3.14` | CLI clean-up SVG, merge/sort/simplify/layout, batch | Rất hợp để tối ưu path sau Potrace hoặc trước khi import DCC; là package production/stable trên PyPI. citeturn63view0turn32view0 |
| **svgpathtools** | **1.7.2**, Python `>=3.8` | Rule-based cleanup và phân tích hình học SVG | Hợp để viết script “bỏ path rác, tách layer, đo bbox, lọc area/length”; tránh dùng như bộ dựng CAD hoàn chỉnh. citeturn37view1turn37view2turn37view3turn36view0 |
| **Vectorizer.AI** | Web app + API, pricing xác minh tháng 5/2026 | Tracing màu / transparency / shape fitting tốt hơn Potrace | Phù hợp khi ảnh có màu hoặc artist muốn preview trước khi mua; API có test mode và quickstart rõ. citeturn34view0turn59view2turn60view0turn35view0 |
| **IfcOpenShell / Bonsai** | Docs **0.8.5**; repo IfcOpenShell active lớn | Phụ trợ nếu bạn cần blockout kiến trúc/to-scale/BIM | Với game indie stylized, đây thường là **overkill**. Chỉ dùng khi tỷ lệ kiến trúc là trọng tâm. citeturn38view0turn38view2 |
| **Sweet Home 3D** | **7.5**, cập nhật 2025-05-05 | Blockout layout phòng nhanh, tỷ lệ nội thất, tham chiếu bố trí | Có thể vẽ tường có kích thước và xuất PDF / ảnh vector / file 3D; mạnh ở bố cục phòng, không phải tool cleanup hay final DCC. Có hỗ trợ tiếng Việt trong giao diện. citeturn40view1turn40view2 |
| **Recraft / Kittl** | Dịch vụ web hiện hành | Tạo concept vector nhanh, icon set, typography variation | Chỉ nên dùng cho **ideation**; không nên coi là geometry production source. Recraft nhấn mạnh vector generation; Kittl có AI Vector Generator và Vectorizer. citeturn43view0turn43view3turn42view0turn42view1 |

Về chọn bộ version, tôi khuyến nghị thực dụng như sau: nếu đội nhỏ và mục tiêu là ra asset nhanh, hãy khóa **Illustrator 29.8.7 LTS + Potrace 1.16 + vpype 1.15.0 + svgpathtools 1.7.2 + Blender LTS 4.x**. Khi nào nhánh này ổn định, mới thêm **Illustrator 30.4** cho Turntable/Text to Vector hoặc **Maya USD** cho exchange sâu hơn. Cách khóa version như vậy có độ chắc chắn cao hơn việc nâng tất cả lên “latest” một lần. citeturn47view2turn47view1turn33view0turn63view0turn37view1turn61view0

## Tác vụ tự động hóa

### Vector hóa SVG và dọn hình

Đây là cụm việc nên làm đầu tiên vì hiệu quả cao nhất. Illustrator hiện cho phép vector hóa raster bằng Image Trace, với Enhanced Presets hỗ trợ gradients, shapes, transparency và auto grouping; sau đó bạn có thể Auto-Simplify để giảm anchor points. Song song, Potrace cho đường đi deterministic hơn với line art đen trắng, còn Vectorizer.AI mạnh hơn với ảnh màu hoặc asset cần shape fitting đẹp. citeturn50view0turn50view1turn50view4turn33view0turn34view0turn59view2

**Khuyến nghị triển khai cụ thể**:

- **Raster đen-trắng, bản đồ nét mực, contour tường/phòng**: dùng `mkbitmap + Potrace`, sau đó `vpype`.
- **Raster màu, icon, concept có vùng transparency**: dùng **Vectorizer.AI** hoặc **Illustrator Image Trace** rồi mới qua `vpype/svgpathtools`.
- **SVG artist làm tay nhưng bị rác node/path**: bỏ Image Trace, đi thẳng `vpype + svgpathtools + Auto-Simplify`.

Đầu ra đạt chuẩn để vào DCC nên có các đặc tính sau: đường kín cho tường/floor, không self-intersection rõ ràng, không còn path dài bằng 0, không còn các path tí hon do trace lỗi, và layer/tên object mô tả đúng phần tử. Những tiêu chí này là rule QA nội bộ bạn nên code hóa bằng Python, không nên chỉ kiểm bằng mắt.

### Illustrator JSX và Actions

Illustrator có hai lớp tự động hóa đáng dùng ngay: **Actions** cho chuỗi thao tác lặp và **JSX scripts** cho logic có điều kiện. Actions có thể chạy trên batch file hoặc data sets và cho phép chọn `Folder`, `Save and Close`, `None` làm destination. Scripts có thể được đặt trong thư mục `Scripting` để xuất hiện ngay trong `File > Scripts`. Đây là trục automation chủ đạo của Illustrator cho đội indie vì chi phí thay đổi thấp và artist dễ dùng. citeturn54view0turn55view0

Các tác vụ Illustrator nên triển khai sớm:

- Mở file `.ai` theo folder, chuẩn hóa artboard name.
- Expand appearance nếu asset nằm trong nhánh geometry.
- Chạy `Object > Path > Simplify` hoặc preset Image Trace đã lưu.
- Tách từng artboard thành từng SVG qua Export for Screens.
- Thu asset theo naming pattern và ghi log CSV sau mỗi batch.
- Tự thêm prefix/suffix theo stage như `raw`, `trace`, `svgclean`, `iso`.

### SVG vào Blender hoặc Maya và extrude tường

Với Blender, hướng ít rủi ro nhất là import SVG làm curve, đặt `dimensions='2D'`, `fill_mode='BOTH'`, gán `extrude`, rồi chuyển mesh nếu cần boolean hoặc export tiếp. Với Maya, do tôi **không xác minh được một tuyến “SVG import” first-party rõ ràng tương đương** trong tài liệu sản phẩm hiện truy cập được, tôi khuyến nghị **đừng phụ thuộc vào “Maya tự đọc SVG”**; hãy dùng **Python parser** đọc SVG rồi dựng polygon/curve trong Maya, hoặc dùng **Blender → USD → Maya** nếu scene sẽ đi sâu vào Autodesk. Maya USD của Autodesk hỗ trợ import/export USD và có API extensible. citeturn61view0turn16view0turn20view3

Nếu asset của bạn chỉ là **phòng trọ, đảo nhỏ, mặt bằng cửa hàng, mái nhà, tường phân room**, Blender gần như luôn là điểm vào hợp lý hơn Maya trong giai đoạn đầu. Maya chỉ thắng khi pipeline sau đó còn kéo dài sang animation/lookdev/render pipe riêng.

### Camera isometric và batch render

Illustrator Turntable có thể tạo nhiều góc nhìn mới cho object 2D và xuất GIF, nhưng nó là công cụ **tham khảo/gợi ý góc nhìn**, không phải chạy geometry production. Nó hữu ích cho moodboard hoặc exploration, không thay thế một camera orthographic thực trong Blender/Maya. citeturn49view0

Cho production, camera nên là:

- **Orthographic**.
- **Strict isometric** nếu bạn muốn ba trục foreshortening bằng nhau.
- Hoặc **2:1 dimetric game look** nếu muốn gần phong cách game hơn là hình chiếu kỹ thuật.

Render batch nên được chuẩn hóa theo tên camera, output folder, format PNG, alpha background, và độ phân giải cố định. Với Illustrator, Export for Screens đã hỗ trợ xuất hàng loạt artboards/assets ở nhiều format. Với Maya, `cmds.render(batch=True)` có batch mode trong command docs; với mayapy, bạn có thể mở scene và gọi render từ script. citeturn54view2turn20view1turn16view2

### Naming và organizing agent

Đây là automation dễ làm nhưng giá trị rất lớn. Dùng **Python 3.11+**, `pathlib`, `csv`, `json` hoặc `yaml`; tùy nhu cầu thêm `pydantic` và `python-slugify`. Agent này nên làm tối thiểu bốn việc:

1. ingest file mới từ `drops/`,
2. chuẩn hóa tên,
3. chuyển file vào đúng stage folder,
4. ghi manifest `assets_manifest.csv` hoặc `assets_manifest.json`.

Một lệnh CLI đủ tốt để bắt đầu:

```bash
python scripts/python/asset_agent.py ingest ^
  --src drops/motel_room/*.png ^
  --project tu_phuong_vo_lo ^
  --asset motel_room ^
  --stage traced ^
  --out assets/2d/svg_raw
```

Đầu ra mong muốn là tên file và folder không còn phụ thuộc vào artist. Một khi manifest đã ổn, bạn mới dễ gọi batch script trong Illustrator, vpype, Blender hay Maya.

## Mã mẫu và lệnh chạy

Các snippet dưới đây là **mẫu tối thiểu, chạy được với giả định hợp lý**, nhưng chúng không thay thế việc smoke-test trên 2 case thật của bạn: **motel room** và **island map**. Cách cài package và các command được dựa trên tài liệu chính thức của Potrace, vpype, svgpathtools, Illustrator scripts và mayapy. citeturn33view0turn63view0turn37view1turn55view0turn16view2turn16view3

### Cài đặt tối thiểu

```bash
# Python tools
python -m pip install "svgpathtools==1.7.2"
python -m pip install "vpype[all]==1.15.0"

# Kiểm tra
vpype --help
python -c "import svgpathtools; print(svgpathtools.__version__)"
```

`vpype 1.15.0` trên PyPI yêu cầu Python `>=3.11,<3.14`; `svgpathtools 1.7.2` yêu cầu Python `>=3.8`. citeturn63view0turn37view1

Cài package vào Maya nên dùng `mayapy`, không dùng Script Editor. Autodesk ghi rõ `pip` được gọi từ command line bằng `mayapy`, và cho phép cài vào thư mục site-packages theo version người dùng. citeturn16view2turn16view3

```bash
# Windows
"C:\Program Files\Autodesk\Maya2026\bin\mayapy.exe" -m pip install svgpathtools==1.7.2 --target "%USERPROFILE%\Documents\maya\2026\scripts\site-packages"

# macOS/Linux
./mayapy -m pip install svgpathtools==1.7.2 --target "$HOME/maya/2026/scripts/site-packages"
```

Potrace 1.16 có binary chính thức cho Windows/macOS/Linux, đồng thời kèm `mkbitmap`. citeturn33view0

### Pipeline Potrace và vpype

Potrace nhận đầu vào bitmap và xuất được SVG, PDF, EPS, DXF, GeoJSON; tài liệu usage chính thức ghi rõ các option như `-s/--svg`, `-t/--turdsize`, `-a/--alphamax`, `-O/--opttolerance`, `--group`, `--flat`, `--tight`. vpype vận hành theo mô hình pipeline CLI với các command như `read`, `linemerge`, `linesort`, `reloop`, `linesimplify`, `write`. citeturn33view0turn63view0

```bash
# Bước 1: Chuẩn hóa ảnh line art sang PBM bằng mkbitmap
mkbitmap -f 2 -s 2 -t 0.45 tests/in/motel_room_mask.png -o tests/tmp/motel_room_mask.pbm

# Bước 2: Trace bằng Potrace
potrace tests/tmp/motel_room_mask.pbm \
  -s --group --flat --tight \
  -t 3 -a 1 -O 0.2 \
  -o tests/tmp/motel_room_trace.svg

# Bước 3: Tối ưu SVG bằng vpype
vpype \
  read tests/tmp/motel_room_trace.svg \
  linemerge --tolerance 0.2mm \
  linesort \
  reloop \
  linesimplify \
  write tests/out/motel_room_clean.svg
```

**Test input**: `tests/in/motel_room_mask.png` là ảnh đen-trắng, tường/phân vùng rõ.  
**Expected output**: `tests/out/motel_room_clean.svg` mở được trong Illustrator hoặc Blender, số path rác giảm rõ, contour tường đi liền mạch hơn so với SVG trace thô. Đây là test case đầu tiên nên khóa để benchmark các thay đổi sau.

### Ví dụ svgpathtools để lọc path rác

`svgpathtools` có các khả năng hữu ích trực tiếp cho pipeline này: đọc/ghi SVG, lấy bbox, tính chiều dài, area của path kín, tách subpath liên tục, cắt/tách path, kiểm tra intersection. citeturn36view0turn37view2

```python
# scripts/python/clean_svg_paths.py
from pathlib import Path
from svgpathtools import svg2paths2, wsvg

SRC = Path("tests/tmp/motel_room_trace.svg")
DST = Path("tests/out/motel_room_clean_rules.svg")

MIN_LENGTH = 8.0      # px
MIN_BBOX_SIDE = 2.0   # px

paths, attributes, svg_attributes = svg2paths2(str(SRC))

kept_paths = []
kept_attrs = []

for path, attr in zip(paths, attributes):
    xmin, xmax, ymin, ymax = path.bbox()
    width = xmax - xmin
    height = ymax - ymin
    length = path.length(error=1e-4)

    # Bỏ path quá ngắn hoặc bbox quá nhỏ
    if length < MIN_LENGTH:
        continue
    if width < MIN_BBOX_SIDE and height < MIN_BBOX_SIDE:
        continue

    kept_paths.append(path)
    kept_attrs.append(attr)

wsvg(
    kept_paths,
    attributes=kept_attrs,
    svg_attributes=svg_attributes,
    filename=str(DST)
)

print(f"Kept {len(kept_paths)} / {len(paths)} paths -> {DST}")
```

Chạy:

```bash
python scripts/python/clean_svg_paths.py
```

**Expected output**: giảm số path nhỏ do trace sai ở mép tường, góc giường, bóng bụi, texture ảnh đầu vào. Với **island map**, bạn có thể thay rule này bằng bỏ path có area nhỏ hơn ngưỡng để dọn các “đảo bụi” không mong muốn.

### Maya Python để dựng polygon từ SVG và extrude tường

Autodesk khuyến nghị dùng Python API 2.0, có `mayapy` cho batch và cho phép cài package bằng pip. Maya command docs xác minh `file` cho import/open/save/export và `render(batch=True)` cho batch render. Mẫu dưới đây chọn con đường chắc chắn hơn: **tự parse SVG bằng svgpathtools rồi dựng mesh trong Maya**, thay vì trông chờ một importer SVG first-party mà tôi không xác minh được một tài liệu product-help rõ ràng cho bản Maya hiện tại. citeturn16view0turn16view2turn16view3turn20view1turn20view3

```python
# scripts/python/maya_import_svg_walls.py
import math
from pathlib import Path

import maya.cmds as cmds
from svgpathtools import svg2paths2

SVG_PATH = Path(r"assets/2d/svg_clean/tu_phuong_vo_lo_motel_room_a_svgclean_v001.svg")
GROUP_NAME = "svg_walls_grp"
WALL_HEIGHT = 2.8
SCALE = 0.01  # 1 SVG px -> 1 cm nếu scene làm việc theo mét thì chỉnh theo chuẩn đội
SAMPLES_PER_SEGMENT = 8

def sample_path(path, samples_per_segment=8):
    pts = []
    for seg in path:
        for i in range(samples_per_segment):
            t = i / float(samples_per_segment)
            p = seg.point(t)
            pts.append((p.real, p.imag))
    # thêm điểm cuối
    p_end = path[-1].point(1.0)
    pts.append((p_end.real, p_end.imag))
    return pts

def dedupe_points(points, eps=1e-6):
    out = []
    for p in points:
        if not out:
            out.append(p)
            continue
        if abs(p[0] - out[-1][0]) > eps or abs(p[1] - out[-1][1]) > eps:
            out.append(p)
    if len(out) > 2:
        if abs(out[0][0] - out[-1][0]) < eps and abs(out[0][1] - out[-1][1]) < eps:
            out.pop()
    return out

def make_wall_face(points_2d, name):
    # Maya Y-up: map SVG x -> X, SVG y -> -Z, extrude theo Y
    pts3d = [(x * SCALE, 0.0, -y * SCALE) for x, y in points_2d]
    if len(pts3d) < 3:
        return None
    mesh = cmds.polyCreateFacet(p=pts3d, n=name)[0]
    cmds.polyExtrudeFacet(f"{mesh}.f[0]", localTranslateY=WALL_HEIGHT)
    return mesh

def main():
    if cmds.objExists(GROUP_NAME):
        cmds.delete(GROUP_NAME)
    grp = cmds.group(em=True, n=GROUP_NAME)

    paths, attrs, svg_attrs = svg2paths2(str(SVG_PATH))
    created = 0

    for idx, path in enumerate(paths):
        subpaths = path.continuous_subpaths()
        for sidx, sub in enumerate(subpaths):
            pts = dedupe_points(sample_path(sub, SAMPLES_PER_SEGMENT))
            if len(pts) < 3:
                continue
            name = f"wall_{idx:03d}_{sidx:02d}"
            obj = make_wall_face(pts, name)
            if obj:
                cmds.parent(obj, grp)
                created += 1

    print(f"Created {created} wall objects under {GROUP_NAME}")

if __name__ == "__main__":
    main()
```

Chạy bằng mayapy sau khi đã đặt `svgpathtools` vào site-packages của Maya:

```bash
"C:\Program Files\Autodesk\Maya2026\bin\mayapy.exe" scripts/python/maya_import_svg_walls.py
```

**Caveat quan trọng**: cách này hoạt động tốt nhất với **closed path đơn giản, không lỗ, không self-intersection**. Nếu phòng có lỗ phức tạp, bạn nên tách outer/inner contours trước trong Illustrator hoặc bằng `svgpathtools`, hoặc chuyển qua Blender để boolean ổn định hơn.

### Blender Python thay thế

Trong thực hành studio nhỏ, đây là tuyến tôi khuyến nghị hơn cho tuần đầu vì đơn giản hơn cho bài toán phòng/tường/isometric. Các snapshot công khai cho thấy Blender hỗ trợ SVG và USD trong hệ manual/file-format hiện hành. citeturn23search0turn23search4

```python
# scripts/python/blender_build_iso.py
import bpy
import math
from pathlib import Path

SVG_PATH = str(Path("assets/2d/svg_clean/tu_phuong_vo_lo_motel_room_a_svgclean_v001.svg").resolve())
OUT_PATH = str(Path("renders/iso/motel_room_iso_v001.png").resolve())

# Reset scene
bpy.ops.wm.read_factory_settings(use_empty=True)

# Import SVG as curves
bpy.ops.import_curve.svg(filepath=SVG_PATH)

# Select imported objects
imported = [obj for obj in bpy.context.scene.objects if obj.type == 'CURVE']
for obj in imported:
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    # Chuẩn hóa curve để fill/extrude
    if obj.data.dimensions != '2D':
        obj.data.dimensions = '2D'
    obj.data.fill_mode = 'BOTH'
    obj.data.extrude = 0.28  # theo scene scale
    obj.scale = (0.01, 0.01, 0.01)

# Gom vào collection riêng
col = bpy.data.collections.new("SVG_BUILD")
bpy.context.scene.collection.children.link(col)
for obj in imported:
    for old_col in obj.users_collection:
        old_col.objects.unlink(obj)
    col.objects.link(obj)

# Camera isometric orthographic
cam_data = bpy.data.cameras.new("iso_cam")
cam_data.type = 'ORTHO'
cam_data.ortho_scale = 12.0
cam = bpy.data.objects.new("iso_cam", cam_data)
bpy.context.scene.collection.objects.link(cam)
bpy.context.scene.camera = cam

# Strict isometric gần chuẩn
cam.location = (10.0, -10.0, 10.0)
cam.rotation_euler = (
    math.radians(54.7356),  # tilt
    0.0,
    math.radians(45.0)
)

# Sun light
light_data = bpy.data.lights.new(name="sun", type='SUN')
light = bpy.data.objects.new(name="sun", object_data=light_data)
bpy.context.scene.collection.objects.link(light)
light.rotation_euler = (math.radians(45), 0, math.radians(35))

# Render settings
scene = bpy.context.scene
scene.render.engine = 'BLENDER_EEVEE'
scene.render.film_transparent = True
scene.render.image_settings.file_format = 'PNG'
scene.render.filepath = OUT_PATH
scene.render.resolution_x = 2048
scene.render.resolution_y = 2048

bpy.ops.render.render(write_still=True)
print(f"Rendered to {OUT_PATH}")
```

Chạy:

```bash
blender -b -P scripts/python/blender_build_iso.py
```

**Test input**: `motel_room` và `island_map`.  
**Expected output**: PNG alpha, orthographic, all wall extrusions đứng, không perspective skew.  
**Kiểm thử bắt buộc**: đặt một cube chuẩn vào scene và xác nhận ba trục có foreshortening đều trước khi khóa preset camera.

### Batch render Maya bằng mayapy

```python
# scripts/python/maya_batch_render.py
import maya.standalone
maya.standalone.initialize()

import maya.cmds as cmds

SCENE = r"assets/3d/maya/tu_phuong_vo_lo_motel_room_v001.ma"

cmds.file(SCENE, open=True, force=True)
cmds.setAttr("defaultRenderGlobals.imageFormat", 32)  # png
cmds.render(batch=True)
print("Batch render triggered.")
```

Chạy:

```bash
"C:\Program Files\Autodesk\Maya2026\bin\mayapy.exe" scripts/python/maya_batch_render.py
```

Tài liệu Autodesk xác nhận `render(batch=True)` là batch mode và `mayapy` là interpreter dành cho batch processing/cài package. citeturn20view1turn16view2

## So sánh workflow và repo khuyến nghị

### Ba tầng workflow

Các tỷ lệ tiết kiệm thời gian dưới đây là **ước tính bảo thủ**, suy ra từ mức tự động hóa đã được tài liệu hóa ở các khâu tracing, clean-up, export, batch action, script menu, mayapy và pipeline CLI. Chúng không phải benchmark chính thức. citeturn54view0turn55view0turn63view0turn16view2

| Tầng | Mô tả | Tiết kiệm thời gian ước tính | Rủi ro | Kỹ năng cần | Chi phí |
|---|---|---:|---|---|---|
| **Beginner** | Illustrator thủ công + Image Trace + Export for Screens + sửa tay trong Blender | **15–30%** | Thấp | Illustrator, Blender cơ bản | Thấp đến trung bình |
| **Semi-Automated** | Illustrator + Actions/JSX + Potrace/Vectorizer.AI + vpype + svgpathtools + Blender batch | **40–65%** | Thấp đến trung bình | Illustrator, Python cơ bản, Blender cơ bản | Trung bình |
| **Advanced** | Thêm Maya branch, mayapy, USD bridge, manifest agent, CI cục bộ, rebuild scene tự động | **55–75%** | Trung bình đến cao | Python khá, Maya/Blender pipeline, quản lý version | Trung bình đến cao |

**Khuyến nghị chính thức cho Tứ Phương Vô Lộ** là tầng **Semi-Automated**. Nó giải quyết phần lớn công việc lặp mà không buộc bạn đầu tư quá sớm vào một hạ tầng DCC phức tạp. Khi nào asset volume tăng hoặc cần chia việc qua nhiều DCC, mới nâng lên Advanced.

### Repo GitHub nên lưu vào bookmark

Bảng này ưu tiên repo có tính hữu dụng trực tiếp cho pipeline. Ở một vài repo GitHub, snapshot HTML không luôn trả về “last commit date” ổn định; vì vậy tôi dùng **bằng chứng hoạt động gần nhất xác minh được** thay cho cột “last commit” tuyệt đối, và ghi rõ chỗ nào thiếu. Đây là cách an toàn hơn là bịa một ngày commit. 

| Repo | License | Bằng chứng hoạt động gần nhất xác minh được | Độ phù hợp |
|---|---|---|---|
| `abey79/vpype` | MIT | Tag **1.15.0** ngày **2025-08-04**; PyPI xác minh `1.15.0`, trạng thái `Production/Stable`, 519 commits trong snapshot repo | **Rất phù hợp** cho clean-up batch SVG. citeturn32view0turn63view0turn31view0 |
| `mathandy/svgpathtools` | MIT | PyPI **1.7.2** ngày **2025-11-30**; repo snapshot có 358 commits | **Rất phù hợp** cho custom cleanup/QA hình học. citeturn37view1turn36view0 |
| `Autodesk/maya-usd` | Theo repo chính thức Autodesk | Repo chính thức, 16,842 commits trong snapshot; hỗ trợ Maya **2023–2027** | **Phù hợp có điều kiện** nếu bạn cần USD bridge và nhánh Autodesk bền vững. citeturn61view0 |
| `IfcOpenShell/IfcOpenShell` | LGPL-3.0 và GPL-3.0 | Repo 20,672 commits; docs hiện **0.8.5**; có Bonsai cho Blender | **Phù hợp mức vừa**; mạnh cho kiến trúc/to-scale, nhưng thường overkill cho indie stylized game. citeturn38view0turn38view2 |
| `creold/illustrator-scripts` | MIT | Repo snapshot 202 commits; README nêu môi trường test **Illustrator CS6, CC 2019–2026** trên Windows/Mac | **Phù hợp cao** làm nguồn tham khảo JSX thực dụng cho Illustrator. Không phải repo chính thức Adobe. citeturn62view0turn62view1 |

Đáng lưu ý là **Potrace không phải repo GitHub cốt lõi** trong đề xuất này, vì nguồn chính thức mạnh nhất của nó là website SourceForge/official site chứ không phải GitHub. Vì bạn yêu cầu danh sách repo GitHub riêng, tôi không cố nhét một mirror không chính thức vào danh sách lõi.

## Lộ trình triển khai và kiểm thử

### Kế hoạch bảy ngày

| Ngày | Mục tiêu | Deliverable | Test case |
|---|---|---|---|
| **Ngày một** | Khóa version, tạo folder, naming convention, manifest CSV | Repo cấu trúc thư mục + `README_pipeline.md` + mẫu tên file | Tạo 5 file giả lập và chạy naming agent |
| **Ngày hai** | Thiết lập Illustrator Actions + 1 JSX export script | 1 action batch + 1 script xuất SVG/artboards | `motel_room.ai` xuất đúng `svg_raw` |
| **Ngày ba** | Thiết lập Potrace/vpype/svgpathtools pipeline | CLI chạy được từ raster → `svg_clean` | `motel_room_mask.png` và `island_map_ink.png` |
| **Ngày bốn** | Dựng Blender importer + extrude tường + camera preset | `blender_build_iso.py` | `motel_room_clean.svg` render PNG được |
| **Ngày năm** | Chạy batch render 2 cảnh mẫu | 2 PNG isometric + checklist QA | motel room, island map |
| **Ngày sáu** | Nhánh Maya tối thiểu bằng mayapy | `maya_import_svg_walls.py` smoke-test | `motel_room_clean.svg` sinh wall mesh |
| **Ngày bảy** | Viết guideline artist + fix edge case | Tài liệu 1–2 trang + preset đã khóa | Artist khác dùng được không cần hỏi lại |

**Milestone chấp nhận sau 7 ngày** nên là:  
`raster/map -> svg_clean -> blend scene -> iso render` chạy được trên **2 case thật**, không chỉ demo toy. Nếu đến ngày bảy mà Maya branch chưa ổn, vẫn có thể coi sprint thành công nếu tuyến Blender đã chạy ổn định, vì đó mới là tuyến lõi đề xuất.

### Kế hoạch ba mươi ngày

Tuần đầu khóa pipeline lõi như trên.  
Tuần hai thêm rule-based QA cho SVG: bỏ path rác, kiểm số node, kiểm layer naming, so sánh bbox với threshold.  
Tuần ba thêm preset style render, template scene, light rig, background alpha, export sizes 1x/2x/game size.  
Tuần bốn mới thêm một trong hai hướng: **Maya/USD** hoặc **AI ideation branch** như Recraft/Kittl/Illustrator Text to Vector. Việc thêm quá sớm thường làm phân tán, vì đội nhỏ dễ bị “tool shopping” thay vì chốt quy ước. citeturn61view0turn43view0turn43view3turn47view1

**Deliverables cuối 30 ngày** nên gồm:

- 1 repo scripts đầy đủ.
- 1 folder preset cho project.
- 2 scene mẫu production-grade: **motel room** và **island map**.
- 1 checklist QA cho artist.
- 1 manifest asset.
- 1 preset camera isometric đã khóa.
- 1 report so sánh “trước/sau” về thời gian làm asset.

### Test cases xác minh bắt buộc

**Motel room**  
Mục đích: kiểm bố cục trong nhà, tường kín, đồ nội thất ít nhưng rõ, render orthographic rõ layer.  
Pass nếu: SVG clean mở đúng; extrude tường không lật mặt; furniture silhouettes không đè sai thứ tự; render alpha sạch.

**Island map**  
Mục đích: kiểm đường bờ biển phức tạp, đảo con/path nhỏ, cleanup rule giữ được silhouette chính nhưng bỏ path rác.  
Pass nếu: không còn “mụn path”; contour chính còn nguyên; khi đặt camera isometric vẫn đọc được cao thấp.

**Regression test nhỏ**  
Mỗi khi sửa script cleanup, chạy lại 2 case trên và so số lượng path, bbox tổng, thời gian chạy và số file render thành công. Không cần CI cloud; một script cục bộ là đủ ở giai đoạn đầu.

### Prompt mẫu cho AI vectorizer và render ideation

**Lưu ý quan trọng**: **Vectorizer.AI không phải công cụ prompt-based**; nó là bitmap-to-vector web/API. Với nó, “prompt” thực chất là **cách chuẩn bị input**: nền trong suốt, tương phản mạnh, ít texture nền, crop sát vùng cần vector hóa. citeturn34view0turn59view2turn60view0

Với các công cụ prompt-based như **Illustrator Text to Vector**, **Recraft**, **Kittl**, bạn có thể dùng các prompt sau để tạo asset concept hoặc icon set rồi mới đưa qua cleanup:

```text
staged isometric motel room, orthographic look, clean vector shapes, muted worn tropical palette,
separate readable objects for bed, fan, desk, sink, window, thin outlines, transparent background,
game-ready silhouette, no perspective distortion, no text, minimal clutter
```

```text
stylized island map for an indie mystery game, flat vector illustration, readable coastline,
small pier, shrine ruins, 5-7 color palette, strong negative space, transparent background,
clean closed shapes, suitable for SVG cleanup
```

```text
top-down to isometric interior props pack, bed, chair, cabinet, lamp, window, fan,
consistent line weight, edit-friendly vector artwork, grouped objects, no gradients unless necessary,
transparent background
```

Nếu bạn muốn khai thác chiều “gợi ý góc nhìn”, Illustrator Turntable có thể tạo nhiều góc cho object 2D, xoay ngang tới 180 độ, nghiêng trên/dưới 30 độ, place tất cả views lên canvas hoặc export GIF. Dùng nó như nguồn **tham khảo pose/angle**, không dùng làm source geometry cuối. citeturn49view0

## Giới hạn và ba yêu cầu tiếp theo

Có ba giới hạn tôi muốn ghi rõ để báo cáo này giữ mức **high-confidence**:

Thứ nhất, trong phiên duyệt này tôi **không lấy được manual chính thức của Blender một cách ổn định**, nên phần Blender được khuyến nghị theo hướng **LTS 4.x** và theo bằng chứng hỗ trợ SVG/USD ở các snapshot công khai, thay vì khẳng định một URL manual cụ thể như với Adobe hay Autodesk. Việc đó không làm hỏng đề xuất, nhưng có nghĩa là khi bạn chốt build sản xuất, nên smoke-test đúng version Blender của đội trước khi đóng băng. citeturn23search0turn23search4

Thứ hai, tôi **không xác minh được một importer SVG first-party chính thức cho Maya** trong product help đã truy cập. Vì vậy, tôi cố tình không đẩy bạn vào một workflow “Maya import SVG trực tiếp” có rủi ro tài liệu hóa thấp. Thay vào đó, tôi đề xuất nhánh **Python parser** hoặc **Blender/USD bridge**, vì hai tuyến này có chứng cứ kỹ thuật rõ hơn và dễ kiểm soát hơn. citeturn16view0turn16view2turn61view0

Thứ ba, các con số **tiết kiệm thời gian** là ước tính vận hành, không phải benchmark nhà cung cấp. Chúng hữu ích để ra quyết định, nhưng bạn vẫn nên đo lại bằng đúng 2 case của dự án sau tuần đầu.

Ba yêu cầu cụ thể tiếp theo bạn có thể giao cho tôi là:

- **“Viết hoàn chỉnh script Maya Python để import SVG, tạo mesh, extrude tường, đặt camera iso và lưu scene.”**
- **“Thiết kế bộ folder structure + file naming agent bằng Python cho Tứ Phương Vô Lộ, có manifest CSV và CLI ingest.”**
- **“Tạo bộ Illustrator JSX và Actions cho export artboards, rename asset, simplify path và xuất SVG hàng loạt.”**