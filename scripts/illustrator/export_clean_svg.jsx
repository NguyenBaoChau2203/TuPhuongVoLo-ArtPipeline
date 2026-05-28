/**
 * Name: export_clean_svg.jsx
 * Purpose: Export the active Illustrator document to versioned SVG raw files.
 * Project: TuPhuongVoLo-ArtPipeline
 * Author: AI-assisted pipeline tooling
 * Date: 2026-05-29
 * Version: 0.2.0
 *
 * Feature 002 tasks: T001, T003, T004, T005, T015
 *
 * Output:
 *   assets/2d/svg_raw/tu_phuong_vo_lo_{asset_name}_main_svgraw_v001.svg
 *   assets/2d/svg_raw/tu_phuong_vo_lo_{asset_name}_ab01_svgraw_v001.svg for multi-artboard docs
 *
 * Safety:
 *   - Does not save or modify the source .ai file.
 *   - Exports a copy to the project raw SVG folder.
 */

#target illustrator

(function () {
    function showError(message) {
        alert("TuPhuongVoLo-ArtPipeline\n\nLỗi xuất SVG:\n" + message);
    }

    function trimText(value) {
        return String(value).replace(/^\s+|\s+$/g, "");
    }

    function stripExtension(fileName) {
        return String(fileName).replace(/\.[^\.]+$/, "");
    }

    function normalizeAssetName(name) {
        var stem = trimText(stripExtension(name)).toLowerCase();
        stem = stem.replace(/[^a-z0-9_]+/g, "_");
        stem = stem.replace(/_+/g, "_");
        stem = stem.replace(/^_+|_+$/g, "");
        if (!stem || !/^[a-z]/.test(stem)) {
            stem = stem ? "asset_" + stem : "asset";
        }
        if (stem.length > 40) {
            stem = stem.substring(0, 40).replace(/_+$/g, "");
        }
        return stem || "asset";
    }

    function parseDocumentName(fileName) {
        var stem = normalizeAssetName(fileName);
        var match = stem.match(
            /^tu_phuong_vo_lo_(.+)_([a-z][a-z0-9_]*)_(raw|traced|svgraw|svgclean|blockout|iso|preview|final_candidate)_v(\d{3})$/
        );
        if (match) {
            return {
                assetName: match[1],
                variant: match[2],
                version: parseInt(match[4], 10)
            };
        }
        return {
            assetName: stem,
            variant: "main",
            version: 1
        };
    }

    function formatOutputStem(assetName, variant, version) {
        return "tu_phuong_vo_lo_" + assetName + "_" + variant + "_svgraw_v" + pad3(version);
    }

    function ensureFolder(folder) {
        if (!folder.exists && !folder.create()) {
            throw new Error("Không tạo được thư mục output: " + folder.fsName);
        }
    }

    function versionedFile(folder, assetName, variant, startVersion) {
        var version = startVersion || 1;
        var candidate;
        do {
            candidate = new File(
                folder.fsName + "/" + formatOutputStem(assetName, variant, version) + ".svg"
            );
            version += 1;
        } while (candidate.exists && version < 1000);
        if (candidate.exists) {
            throw new Error("Không tạo được tên phiên bản mới cho: " + assetName);
        }
        return candidate;
    }

    function hasFile(folder, relativePath) {
        return new File(folder.fsName + "/" + relativePath).exists;
    }

    function isValidProjectRoot(folder) {
        return folder && folder.exists && (
            hasFile(folder, "AGENTS.md") ||
            hasFile(folder, "config/pipeline.yaml") ||
            hasFile(folder, ".specify/constitution.md")
        );
    }

    function discoverProjectRoot() {
        var scriptFile = new File($.fileName);
        var folder = scriptFile.parent;
        var guard = 0;
        while (folder && folder.exists && guard < 20) {
            if (isValidProjectRoot(folder)) {
                return folder;
            }
            folder = folder.parent;
            guard += 1;
        }

        var selected = Folder.selectDialog(
            "Chọn thư mục TuPhuongVoLo-ArtPipeline để xuất SVG vào assets/2d/svg_raw/"
        );
        if (isValidProjectRoot(selected)) {
            return selected;
        }
        throw new Error(
            "Không tìm thấy thư mục project hợp lệ.\n" +
            "Hãy chọn thư mục có AGENTS.md hoặc config/pipeline.yaml."
        );
    }

    function pad2(value) {
        return value < 10 ? "0" + value : String(value);
    }

    function pad3(value) {
        if (value < 10) {
            return "00" + value;
        }
        if (value < 100) {
            return "0" + value;
        }
        return String(value);
    }

    function buildExportOptions(artboardNumber) {
        var options = new ExportOptionsSVG();

        // SVG 1.1 is the pipeline interchange target. Illustrator exposes this as SVGDTDVersion.SVG1_1
        // in modern CC builds; the guarded assignment keeps older ExtendScript engines from failing hard.
        try {
            options.DTD = SVGDTDVersion.SVG1_1;
        } catch (error) {
            $.writeln("SVGDTDVersion.SVG1_1 unavailable in this Illustrator version: " + error);
        }

        // UTF-8 keeps Vietnamese layer/group names readable in the exported SVG.
        try {
            options.documentEncoding = SVGDocumentEncoding.UTF8;
        } catch (encodingError) {
            $.writeln("SVG UTF8 option unavailable: " + encodingError);
        }

        // Preserve layer names/editability as much as Illustrator's SVG exporter allows.
        // Some Illustrator versions still rewrite duplicate IDs; cleanup/validation handles the result.
        options.preserveEditability = true;
        options.coordinatePrecision = 3;
        options.cssProperties = SVGCSSPropertyLocation.STYLEATTRIBUTES;
        options.embedRasterImages = false;
        options.includeFileInfo = false;
        options.includeVariablesAndDatasets = false;
        options.includeUnusedStyles = false;
        options.slices = false;
        options.compressed = false;

        // Text remains SVG text where possible for artist editability. If downstream geometry requires
        // outlines, that should be a separate artist-approved step, not a destructive export default.
        try {
            options.fontType = SVGFontType.SVGFONT;
            options.fontSubsetting = SVGFontSubsetting.GLYPHSUSED;
        } catch (fontError) {
            $.writeln("SVG font options unavailable: " + fontError);
        }

        // Multi-artboard export options are version-dependent. CC builds support saveMultipleArtboards
        // and artboardRange; guarded assignments keep the script defensive on older installations.
        if (artboardNumber !== null) {
            try {
                options.saveMultipleArtboards = true;
                options.artboardRange = String(artboardNumber);
            } catch (artboardError) {
                $.writeln("Artboard range export option unavailable: " + artboardError);
            }
        }
        return options;
    }

    try {
        if (app.documents.length === 0) {
            showError("Chưa có tài liệu Illustrator nào đang mở.\nHãy mở file .ai rồi chạy lại script.");
            return;
        }

        var doc = app.activeDocument;
        var projectRoot = discoverProjectRoot();
        var outputFolder = new Folder(projectRoot.fsName + "/assets/2d/svg_raw");
        ensureFolder(outputFolder);

        var nameParts = parseDocumentName(doc.name);
        var artboardCount = doc.artboards.length;
        var exportedFiles = [];
        var originalArtboardIndex = doc.artboards.getActiveArtboardIndex();

        for (var index = 0; index < artboardCount; index += 1) {
            doc.artboards.setActiveArtboardIndex(index);
            var variant = artboardCount > 1 ? "ab" + pad2(index + 1) : nameParts.variant;
            var outputFile = versionedFile(
                outputFolder,
                nameParts.assetName,
                variant,
                nameParts.version
            );
            var options = buildExportOptions(artboardCount > 1 ? index + 1 : null);
            doc.exportFile(outputFile, ExportType.SVG, options);
            exportedFiles.push(outputFile.fsName);
        }

        doc.artboards.setActiveArtboardIndex(originalArtboardIndex);

        alert(
            "TuPhuongVoLo-ArtPipeline\n\n" +
            "Đã xuất SVG thành công.\n" +
            "File gốc .ai không bị lưu hoặc thay đổi.\n\n" +
            "Số file SVG: " + exportedFiles.length + "\n" +
            "Thư mục:\n" + outputFolder.fsName
        );
    } catch (error) {
        showError(String(error));
    }
})();
