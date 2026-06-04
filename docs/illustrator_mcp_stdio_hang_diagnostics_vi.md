# Chẩn đoán Illustrator MCP bị treo ở stdio

Tài liệu này ghi nhận kết quả phase 016A-R2 cho MCP server
`illustrator-sandbox`. Mục tiêu chỉ là chẩn đoán kết nối MCP stdio. Không dùng
MCP để chỉnh artwork, không save/export, không chạy Maya.

## Kết quả 016B

- Antigravity đã thấy tool schema và bắt đầu gọi `illustrator-sandbox / help`.
- Sau khi restart Antigravity, lệnh `help` vẫn đứng ở trạng thái Working.
- Kiểm tra process trước đó không còn `python.exe` chạy
  `D:\Tools\illustrator-mcp\illustrator\server.py`.
- Không có artwork nào bị chỉnh sửa.

## Audit Antigravity settings

File được kiểm tra read-only:

```text
C:\Users\ACER NITRO 16\AppData\Roaming\Antigravity IDE\User\settings.json
```

Kết quả:

- JSON hợp lệ.
- File hiện tại không có `mcpServers`.
- Không thấy entry `illustrator-sandbox` trong active `settings.json`.
- Không thấy `cwd` hoặc `env` trong active settings vì MCP block không có mặt.
- Một bản history của settings có cấu hình cũ:

```json
{
  "mcpServers": {
    "illustrator-sandbox": {
      "command": "D:\\Tools\\illustrator-mcp\\.venv\\Scripts\\python.exe",
      "args": [
        "D:\\Tools\\illustrator-mcp\\illustrator\\server.py"
      ]
    }
  }
}
```

Log Antigravity cũng có dấu hiệu MCP registry đang kẹt:

- `failed to stop mcp instance: illustrator-sandbox: exit status 1`
- `loading already in progress`

Vì vậy operator cần kiểm tra lại Antigravity settings UI trước smoke test tiếp
theo. Không tự sửa settings khi chưa xác nhận.

## Audit server.py

Server ở:

```text
D:\Tools\illustrator-mcp\illustrator\server.py
```

Kết quả audit:

- Entrypoint chạy `asyncio.run(main())`.
- Transport dùng `mcp.server.stdio.stdio_server()`.
- Startup log và config hint ghi vào stderr, không ghi stdout.
- Không thấy stdout pollution trước JSON-RPC.
- Backend Illustrator COM được lazy-init qua `_get_backend()`.
- `help` và `get_system_prompt` chỉ lấy text từ `prompt.py`, không gọi COM.
- Tool `view` và `run` mới có thể gọi Illustrator backend; phase này không gọi
  hai tool đó.

## Controlled diagnostics

Lệnh exact config:

```powershell
& "D:\Tools\illustrator-mcp\.venv\Scripts\python.exe" `
  "D:\Tools\illustrator-mcp\illustrator\server.py"
```

Kết quả startup probe:

- Server vẫn sống sau timeout ngắn: bình thường cho stdio MCP server.
- stdout trước protocol: `0` byte.
- stderr có log startup và config hint.

Kết quả MCP protocol probe:

- `initialize`: OK.
- `tools/list`: OK.
- Tool list có `help` và `get_system_prompt`: OK.
- Gọi `help`: server log báo `Response sent`, nhưng client không nhận được
  JSON-RPC response.
- Stderr ghi lỗi:

```text
UnicodeEncodeError: 'charmap' codec can't encode character '\U0001f3a8'
```

Nguyên nhân trực tiếp: trên Windows, stdout của subprocess đang dùng encoding
`cp1252`. MCP SDK ghi JSON-RPC ra stdout dưới dạng text; response của `help`
có emoji/non-ASCII nên encode fail. Antigravity chờ response mãi và trông như
bị treo.

## Phân loại root cause

Phân loại gần nhất: **E. help tool implementation blocks**.

Chi tiết chính xác hơn: `help` không block Illustrator COM; nó tạo text có emoji
và làm MCP stdout writer crash vì Windows stdout không phải UTF-8. Đây là lỗi
encoding stdio khi trả response tool.

Confidence: cao.

## Diagnostic helper

Repo có helper read-only:

```powershell
& "D:\Tools\illustrator-mcp\.venv\Scripts\python.exe" `
  "D:\TuPhuongVoLo_DCC_Test\TuPhuongVoLo-ArtPipeline\scripts\python\diagnose_illustrator_mcp_stdio.py" `
  --call-readonly-tools
```

Để test repair bằng UTF-8 env:

```powershell
& "D:\Tools\illustrator-mcp\.venv\Scripts\python.exe" `
  "D:\TuPhuongVoLo_DCC_Test\TuPhuongVoLo-ArtPipeline\scripts\python\diagnose_illustrator_mcp_stdio.py" `
  --utf8-env `
  --call-readonly-tools
```

Helper này chỉ gọi:

- startup probe
- `initialize`
- `tools/list`
- nếu bật flag: `help`, `get_system_prompt`

Nó không gọi `view`, không gọi `run`, không save/export.

## Repair an toàn được khuyến nghị

Tạo wrapper ngoài repo:

```bat
@echo off
cd /d D:\Tools\illustrator-mcp
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
".venv\Scripts\python.exe" "illustrator\server.py"
```

Đường dẫn đề xuất:

```text
D:\Tools\illustrator-mcp\run_illustrator_mcp_stdio.bat
```

Sau đó operator cập nhật Antigravity settings thủ công:

```json
{
  "mcpServers": {
    "illustrator-sandbox": {
      "command": "D:\\Tools\\illustrator-mcp\\run_illustrator_mcp_stdio.bat",
      "args": []
    }
  }
}
```

Wrapper này:

- ép Python stdio sang UTF-8;
- đặt cwd đúng `D:\Tools\illustrator-mcp`;
- không in gì ra stdout trước server;
- không sửa artwork;
- không cần reinstall package.

Nếu Antigravity hỗ trợ `env` và `cwd` trực tiếp, có thể dùng cách tương đương,
nhưng wrapper `.bat` là cách Windows rõ ràng nhất.

## Thứ tự retry an toàn

1. Operator hủy run Antigravity đang stuck nếu còn.
2. Đóng/restart Antigravity để clear trạng thái `loading already in progress`.
3. Kiểm tra active `settings.json` hoặc settings UI có đúng MCP block mới.
4. Chạy helper với `--utf8-env --call-readonly-tools` nếu muốn smoke test độc lập.
5. Chỉ sau đó smoke test Antigravity bằng prompt 016B-R2 bên dưới.

## Prompt smoke test 016B-R2

```text
Bạn là Antigravity + Claude Sonnet 4.6 đang smoke test Illustrator MCP
`illustrator-sandbox` cho dự án Tứ Phương Vô Lộ.

Mục tiêu: chỉ xác nhận MCP stdio phản hồi sau khi đổi sang UTF-8 wrapper.
Không edit, không save, không export, không tạo file, không sửa artwork.

Quy tắc an toàn:
- Không mở hoặc sửa file .ai gốc.
- Không sửa Illustrator sandbox hiện có.
- Không chạy ExtendScript có side effect.
- Không gọi tool `run`.
- Không gọi tool `view` trong smoke test này.
- Chỉ gọi tool text/read-only.
- Nếu tool đứng quá 30 giây hoặc báo EOF/error, dừng và báo kết quả.

Hãy thực hiện theo thứ tự:
1. Gọi tool `help` của `illustrator-sandbox`.
2. Gọi tool `get_system_prompt` của `illustrator-sandbox`.
3. Gọi `get_prompting_tips` nếu có.
4. Báo kết quả ngắn gọn:
   - MCP responsive: YES/NO
   - help returned: YES/NO
   - get_system_prompt returned: YES/NO
   - stdout/encoding error còn xuất hiện không nếu thấy log
   - Không có edit/save/export đã thực hiện
```
