/**
 * Name: organize_layers.jsx
 * Purpose: Normalize top-level Illustrator layer names before SVG export.
 * Project: TuPhuongVoLo-ArtPipeline
 * Author: AI-assisted pipeline tooling
 * Date: 2026-05-29
 * Version: 0.2.0
 *
 * Feature 002 tasks: T001, T006, T015
 *
 * Safety:
 *   - Does not delete layers or artwork.
 *   - Does not flatten, move, or alter geometry.
 *   - Only renames top-level layers when the normalized name is safe.
 */

#target illustrator

(function () {
    function showError(message) {
        alert("TuPhuongVoLo-ArtPipeline\n\nLỗi sắp xếp layer:\n" + message);
    }

    function trimText(value) {
        return String(value).replace(/^\s+|\s+$/g, "");
    }

    function pad2(value) {
        return value < 10 ? "0" + value : String(value);
    }

    function normalizeLayerName(name, index) {
        var normalized = trimText(name);
        normalized = normalized.replace(/\s+/g, "_");
        normalized = normalized.replace(/[\\\/:\*\?"<>\|]/g, "");
        normalized = normalized.replace(/_+/g, "_");
        normalized = normalized.replace(/^_+|_+$/g, "");

        // Do not force ASCII conversion: Vietnamese names can be meaningful to the artist.
        // Only unnamed/default Illustrator layer names get a neutral prefix.
        if (!normalized || /^layer_?\d+$/i.test(normalized) || /^Layer\s*\d+$/i.test(name)) {
            normalized = "layer_" + pad2(index + 1);
        }
        return normalized;
    }

    function uniqueName(baseName, usedNames) {
        var candidate = baseName;
        var counter = 2;
        while (usedNames[candidate]) {
            candidate = baseName + "_" + pad2(counter);
            counter += 1;
        }
        usedNames[candidate] = true;
        return candidate;
    }

    try {
        if (app.documents.length === 0) {
            showError("Chưa có tài liệu Illustrator nào đang mở.\nHãy mở file .ai rồi chạy lại script.");
            return;
        }

        var doc = app.activeDocument;
        var usedNames = {};
        var renamed = 0;
        var unchanged = 0;
        var skipped = 0;
        var details = [];

        for (var index = 0; index < doc.layers.length; index += 1) {
            var layer = doc.layers[index];
            var oldName = layer.name;
            var normalized = normalizeLayerName(oldName, index);
            var finalName = uniqueName(normalized, usedNames);

            if (oldName === finalName) {
                unchanged += 1;
                continue;
            }

            try {
                layer.name = finalName;
                renamed += 1;
                details.push("• " + oldName + " → " + finalName);
            } catch (renameError) {
                skipped += 1;
                details.push("• Không đổi được: " + oldName + " (" + renameError + ")");
            }
        }

        var summary =
            "TuPhuongVoLo-ArtPipeline\n\n" +
            "Đã chuẩn hóa tên layer.\n\n" +
            "Đã đổi tên: " + renamed + "\n" +
            "Giữ nguyên: " + unchanged + "\n" +
            "Bỏ qua: " + skipped + "\n\n" +
            "Script chỉ đổi tên top-level layer, không xóa hoặc sửa artwork.";

        if (details.length > 0) {
            summary += "\n\nChi tiết:\n" + details.slice(0, 12).join("\n");
            if (details.length > 12) {
                summary += "\n...";
            }
        }

        alert(summary);
    } catch (error) {
        showError(String(error));
    }
})();
