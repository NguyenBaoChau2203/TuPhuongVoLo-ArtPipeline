# Khắc phục lỗi Illustrator MCP EOF

Tài liệu này dùng cho phase 016A khi Antigravity MCP server
`illustrator-sandbox` trả EOF ở các lệnh inspect như `view`, `help`, hoặc
`get_system_prompt`.

Mục tiêu chỉ là sửa kết nối MCP. Không dùng tài liệu này để chỉnh sửa artwork,
không test trên file `.ai` gốc, và không export/save bằng Illustrator MCP.

## Triệu chứng

- Antigravity gọi tool `illustrator-sandbox` và nhận EOF ngay.
- `view`, `help`, và `get_system_prompt` đều EOF.
- Illustrator có thể vẫn đang mở bình thường.
- Không có thay đổi nào trên file `.ai`, `.svg`, `.ma`, `.json`, `.png`.

## Nguyên nhân thường gặp

- MCP server Python cũ còn sống nhưng Antigravity đang giữ stdio đã chết.
- Antigravity/Sonnet session cũ vẫn đang kết nối vào process MCP bị lỗi.
- Illustrator COM bridge chưa sẵn sàng hoặc Illustrator chưa khởi tạo xong.
- Active document trong Illustrator không đúng trạng thái test an toàn.
- Đường dẫn MCP config trỏ sai Python venv hoặc sai `server.py`.
- Python venv/server path đúng nhưng chỉ fail trong sandbox của tool khác; cần
  kiểm tra bằng process/launch context thực tế của Antigravity.

## Đường dẫn MCP kỳ vọng

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

## Lệnh kiểm tra an toàn

Chạy trong PowerShell. Các lệnh này chỉ đọc thông tin.

```powershell
Test-Path -LiteralPath "D:\Tools\illustrator-mcp"
Test-Path -LiteralPath "D:\Tools\illustrator-mcp\.venv\Scripts\python.exe"
Test-Path -LiteralPath "D:\Tools\illustrator-mcp\illustrator\server.py"

& "D:\Tools\illustrator-mcp\.venv\Scripts\python.exe" --version
& "D:\Tools\illustrator-mcp\.venv\Scripts\python.exe" -m py_compile "D:\Tools\illustrator-mcp\illustrator\server.py"
```

Nếu `server.py` không có argparse/`--help`, không chạy `server.py --help` vì nó
có thể khởi động stdio MCP server và chờ client.

## Kiểm tra process

```powershell
Get-CimInstance Win32_Process |
  Where-Object {
    $_.Name -match "python|node|Illustrator|Antigravity" -or
    $_.CommandLine -match "illustrator-mcp|server.py|Antigravity|Illustrator"
  } |
  Select-Object ProcessId, ParentProcessId, Name, ExecutablePath, CreationDate, CommandLine |
  Format-List
```

Process MCP cần xóa chỉ được coi là an toàn khi:

- `Name` là `python.exe`.
- `CommandLine` trỏ rõ vào
  `D:\Tools\illustrator-mcp\illustrator\server.py`.
- Process không phải Codex hiện tại.
- Có thể để Antigravity restart lại sau khi đóng session cũ.

Không kill các process sau nếu chưa có xác nhận của operator:

- `Illustrator.exe`.
- `Antigravity IDE.exe`.
- process Python/Node không có command line rõ ràng liên quan
  `D:\Tools\illustrator-mcp`.

## Thứ tự sửa an toàn

1. Nếu Antigravity/Sonnet đang stuck, operator cancel run đó trước.
2. Kiểm tra MCP folder, venv Python, và `server.py`.
3. Kiểm tra syntax/import của `server.py` bằng Python venv.
4. Tìm process Python MCP cũ có command line trỏ vào `D:\Tools\illustrator-mcp`.
5. Chỉ stop đúng các PID Python MCP cũ đã xác định rõ.
6. Không kill Illustrator nếu operator chưa xác nhận.
7. Khởi động lại Antigravity để nó tạo stdio session mới.
8. Giữ Illustrator 2020 mở, nhưng không mở file `.ai` gốc để smoke test.
9. Chạy prompt smoke test 016B bên dưới. Chỉ inspect, không edit/save/export.

Ví dụ stop process sau khi đã xác định PID rõ:

```powershell
Stop-Process -Id <MCP_PYTHON_PID> -Force
```

## Prompt smoke test 016B cho Antigravity

```text
Bạn là Antigravity + Claude Sonnet 4.6 đang smoke test Illustrator MCP
`illustrator-sandbox` cho dự án Tứ Phương Vô Lộ.

Mục tiêu: chỉ xác nhận MCP có phản hồi. Không edit, không save, không export,
không tạo file, không sửa bất kỳ artwork nào.

Quy tắc an toàn:
- Không mở hoặc sửa file .ai gốc.
- Không sửa Illustrator sandbox hiện có.
- Không chạy ExtendScript có side effect.
- Chỉ gọi các lệnh inspect/read-only.
- Nếu bất kỳ tool nào trả EOF, dừng ngay và báo EOF vẫn chưa resolved.

Hãy thực hiện theo thứ tự:
1. Gọi tool `help` của `illustrator-sandbox`.
2. Gọi tool `get_system_prompt` của `illustrator-sandbox`.
3. Nếu có tool inspect an toàn, kiểm tra Illustrator document count.
4. Nếu có active document, chỉ đọc và báo active document path/name; không save.
5. Báo kết quả ngắn gọn:
   - MCP responsive: YES/NO
   - EOF resolved: YES/NO
   - Illustrator document count nếu đọc được
   - Active document path/name nếu đọc được
   - Không có edit/save/export đã thực hiện
```

## Điều kiện dừng ngay

- MCP vẫn trả EOF ở `help`, `view`, hoặc `get_system_prompt`.
- `D:\Tools\illustrator-mcp` bị thiếu.
- Python venv không launch được trong context Antigravity.
- `server.py` syntax/import fail và cần reinstall package.
- Phải sửa file `.ai` gốc mới test được.
- Không xác định rõ process nào an toàn để kill.
- Cần dùng Maya hoặc Maya commandPort.

Khi gặp stop condition, dừng Illustrator Prompt Loop và quay về manual SVG export.
