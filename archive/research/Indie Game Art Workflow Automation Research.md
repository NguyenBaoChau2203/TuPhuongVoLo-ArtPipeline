# **Art Production Workflow Optimization and Automation Report: Tứ Phương Vô Lộ**

## **1\. Tóm tắt dự án (Executive Summary)**

Báo cáo nghiên cứu này thiết lập một khung quy trình tự động hóa và tối ưu hóa hiệu suất mỹ thuật cho dự án game độc lập "Tứ Phương Vô Lộ", một tác phẩm sử dụng phong cách đồ họa vẽ tay và cách điệu (stylized/hand-drawn) đặc trưng. Mục tiêu cốt lõi của giải pháp không phải là thay thế vai trò sáng tạo của người họa sĩ, mà là giải phóng họ khỏi các tác vụ thủ công lặp đi lặp lại có giá trị gia tăng thấp. Các tác vụ này bao gồm: đồ nét vẽ nháp (tracing), dọn dẹp vector dư thừa (cleanup), tính toán phép chiếu trục đo (isometric projection), dựng hình khối bao cảnh thô (3D blockout) từ sơ đồ mặt bằng, và xuất bản tài nguyên thủ công sang các định dạng khác nhau.  
Thông qua việc khảo sát sâu các giải pháp kỹ thuật hiện hành, báo cáo đề xuất tích hợp một hệ thống kết hợp giữa trí tuệ nhân tạo tạo sinh vector trực tiếp (Direct Vector AI Generation), các bộ mã nguồn tự động hóa trên môi trường Adobe Illustrator (ExtendScript/UXP) 1, công cụ chuyển đổi sơ đồ mặt bằng 2D thành hình khối 3D 3, và đặc biệt là giao thức máy chủ tương cảnh Model Context Protocol (MCP).4 Hệ thống MCP này cho phép trợ lý AI điều khiển trực tiếp Illustrator trên hệ điều hành Windows thông qua cơ chế tự động hóa COM.4 Lộ trình triển khai được chia làm hai giai đoạn thực tế (7 ngày và 30 ngày) cùng ba cấp độ tiếp cận từ cơ bản đến nâng cao (Beginner, Semi-Automated, và Advanced Agentic), đảm bảo tính thích ứng cao với thói quen làm việc hiện tại của họa sĩ trên Adobe Illustrator và Autodesk Maya mà không gây gián đoạn tiến độ sản xuất của studio.

## **2\. Current Manual Workflow Analysis**

The aesthetic identity of the "Tứ Phương Vô Lộ" project relies heavily on stylized, hand-drawn 2D vector visual assets combined with structural 3D environmental blockouts. The current pipeline depends on manual execution across two primary workspaces: Adobe Illustrator for vector drafting and layout, and Autodesk Maya for 3D modeling and structural visualization. This traditional approach, while preserving artistic control, presents structural inefficiencies at every stage of the creative cycle.  
The process of developing the stylized game logo begins with a hand-drawn raster sketch. To vectorize this sketch, the artist manually plots anchor points and adjusts Bezier curves using the Pen Tool in Adobe Illustrator. This manual tracing requires significant time to maintain consistent line weights and curvature, often leading to physical fatigue.  
The creation of the 2D top-down island map involves similar manual overhead. The artist draws irregular coastlines, roads, and landmass boundaries stroke-by-stroke. Placing natural elements such as vegetation, rocks, and water ripples requires constant manual copying, rotating, and scaling of vector groups to avoid obvious repetition.  
For interior design and architectural room layouts, the artist manually drafts black-and-white top-down floor plans in Illustrator. Layer organization and path simplification are handled point-by-point. There is no automated system to ensure uniform wall thicknesses or clean path intersections.  
The transition to the isometric room illustration—such as the small island motel interior—requires manual projection calculations. To map flat 2D furniture assets and wall layouts onto an isometric plane, the artist manually calculates and applies Scale, Shear, and Rotate (SSR) transformations to every vector group. Because Illustrator lacks native isometric snapping tools, aligning elements along grid intersections is mathematically imprecise, leading to visible alignment seams at room corners.  
The connection between the 2D and 3D pipelines is also highly manual. To create a 3D blockout in Autodesk Maya, the artist imports flat 2D floor plans as reference image planes. She then manually places and extrudes primitive cubes to match the 2D lines. After completing the 3D model, she uses it as a visual reference to paint the final isometric scene back in Illustrator. This constant switching between applications and manually translating dimensions across different perspectives introduces significant friction and limits production speed.

## **3\. Bottlenecks and What Can Be Automated**

To improve production speed and reduce artist fatigue, the technical pipeline must target five high-overhead areas for systematic automation.  
The first bottleneck is manual path vectorization and cleanup. Converting hand-drawn concept sketches into clean vector art often produces messy vector structures with excessive anchor points and overlapping lines. Automating this phase requires high-fidelity raster-to-vector conversion engines that preserve hand-drawn line weights while outputting optimized, editable Bezier paths with minimal anchor points.6  
The second bottleneck is the conversion of 2D floor plans into 3D blockouts. Building 3D room geometries from 2D vector layouts can be automated. Rather than manually modeling walls and floors, the pipeline can procedurally parse 2D vector paths (SVG or DXF).8 These paths can then be translated into extruded 3D wall meshes and bounding volumes inside the 3D environment.8  
The third bottleneck is isometric projection calculations. The mathematical transformation required to project a flat 2D element onto an isometric plane can be automated using the standard SSR matrix:  
![][image1]  
For the left isometric wall, the transformation scales the vertical axis to ![][image2], shears the artwork by ![][image3], and rotates it by ![][image3].10 For the right isometric wall, the transformation scales vertical dimensions to ![][image2], shears by ![][image4], and rotates by ![][image4].10 Automating these calculations into hotkey-driven scripts removes the need for manual coordinate plotting.  
The fourth bottleneck is repeated asset placement and grid alignment. Distributing repeating environment assets, such as trees, paths, and docks on the top-down map, can be automated. Rather than copying and placing each asset manually, the pipeline can use procedural scattering scripts to distribute assets along selected paths or vector grids while automatically randomizing scale and rotation.2  
The fifth bottleneck is asset slicing and multi-format exports. Preparing assets for the game engine requires slicing artboards, isolating layers, naming assets according to design guidelines, and exporting them to SVG, PNG, and PSD formats. Automating this process via batch export scripts ensures file-name consistency and reduces export times from hours to seconds.1

## **4\. Comprehensive Tool Comparison Tables**

To select the most robust solutions for the "Tứ Phương Vô Lộ" pipeline, three comparative evaluations have been compiled, focusing on practical implementation, Windows compatibility, and exact file export formats.

### **AI Vector Generation & Vectorization Tools**

| Tool Name | Core Technology | Output Quality / Path Cleanliness | Pricing Structure | OS Compatibility | Production Readiness & Pipeline Risks |
| :---- | :---- | :---- | :---- | :---- | :---- |
| **Vectorizer.AI** 6 | Deep learning edge detection & Bezier curve optimization.12 | Excellent path cleanliness; minimal anchors; highly editable vectors.6 | Web App: $9.99/mo.6 API: usage-based.13 | Windows, macOS, Cloud.6 | **Production Ready.** Risk: Minor manual node adjustments needed for sharp non-orthogonal corners.7 |
| **Recraft v3** 6 | Text-to-Vector & Style-consistent vector generation.6 | Native clean SVG output; excellent stylized illustration details; matches reference styles.6 | Basic: $10/mo.15 Pro: $25/mo.14 | Windows, macOS, Cloud.6 | **Production Ready.** Excellent for style lock.6 Risk: Generation of overlapping shapes can complicate layer separation. |
| **Adobe Firefly / Illustrator Text to Vector** 6 | Licensed diffusion-based vector path engine.6 | Integrated directly into Illustrator; outputs layered graphics; pathing can sometimes be overly dense.6 | Included in Illustrator single-app ($22.99/mo) or CC ($59.99/mo).6 | Windows, macOS.6 | **Production Ready.** Risk: Artistic complexity lags behind Recraft.6 Lacks strict style-locking parameters.6 |
| **Illustrator Image Trace (Built-in)** | Traditional pixel-neighborhood cluster segmentation. | Decent for high-res B\&W line art; poor for complex gradients; generates excessive anchor points. | Included in Illustrator. | Windows, macOS. | **Legacy Production.** Risk: Messy vector topology; requires extensive manual cleanup. |
| **Kittl** 6 | Template-driven AI auto-tracing and text effects.16 | Good for text-based layouts and simple graphics; lacks precision for complex illustrations.16 | Free tier available; Pro plan is $10/mo.6 | Cloud-based.6 | **Concept Stage.** Risk: Optimized for merchandise and print, not game assets.6 |
| **VectorGurus** 7 | Hybrid AI vectorization \+ human hand-tracing.7 | Clean, production-ready vector assets; human-verified topology.7 | Free AI tool; paid hand-tracing starts at $25/image.7 | Cloud-based.7 | **Production Ready (for high-value assets).** Risk: 24-hour turnaround time for hand-tracing.7 |

### **2D Top-Down Map & Layout Generation Tools**

| Tool Name | Native SVG Vector Support | Integration with Adobe Illustrator | Pricing Structure | OS Compatibility | Production Readiness & Pipeline Risks |
| :---- | :---- | :---- | :---- | :---- | :---- |
| **Azgaar's Fantasy Map Generator** 17 | Yes, exports fully layered SVG files.17 | **High.** Layered SVGs map directly to Illustrator paths.17 | Free & Open Source.17 | Web-browser (All OS).17 | **Production Ready (as structural blockout).** Risk: Visual aesthetic is highly functional/technical 17; must be styled manually in Illustrator. |
| **Wonderdraft** 17 | No, exports raster PNG, JPEG, WebP only.18 | **Medium.** Raster map must be imported and auto-traced in Illustrator.18 | $29.99 one-time purchase.17 | Windows, macOS, Linux.18 | **Production Ready.** Excellent for generating natural geographic layouts and coastline guides.17 |
| **Watabou's Medieval Fantasy City & Village Generators** 20 | Yes, supports SVG export options. | **High.** Outlined village/city roads can be directly edited as vector lines.20 | Free.20 | Web-browser (All OS). | **Production Ready.** Best procedural baseline generator for city street layouts and house bounds.20 |
| **Inkarnate** 17 | No, exports high-res raster up to 8K only.18 | **Low.** Forces manual vector tracing or high-overhead Image Trace.18 | Free tier; Pro is $25/year.17 | Web-browser (All OS).17 | **Concept Stage Only.** Stunning hand-drawn brush assets 17 but completely unsuited for clean vector pipelines. |

### **2D-to-3D Floor Plan & Blockout Pipelines**

| Tool Name | Export Formats | Native Maya Compatibility | Pricing Structure | OS Compatibility | Production Readiness & Pipeline Risks |
| :---- | :---- | :---- | :---- | :---- | :---- |
| **FloorplanToBlender3d** 3 | .blender project files.3 | **Medium.** Transferred to Maya via FBX/OBJ exports.3 | Free & Open Source.3 | Linux natively; Windows via Docker.3 | **Semi-Ready.** Risk: Deep dependencies; requires Docker to avoid version conflicts on Windows.3 |
| **Sweet Home 3D** 21 | OBJ, PDF, SVG, Collada (DAE).21 | **High.** Native OBJ/DAE imports retain accurate dimensions.22 | Free & Open Source.22 | Windows, macOS, Linux.21 | **Production Ready.** Risk: Triangulated OBJ meshes require clean-up if modifying vertex structures in Maya.22 |
| **OpenSCAD Floor Plan** 25 | STL, OFF, DXF, SVG.25 | **Medium.** Requires STL-to-OBJ conversion for Maya editing. | Free & Open Source.25 | Windows, macOS, Linux.25 | **Semi-Ready.** Risk: Programmatic CAD focus; requires strict SVG input naming conventions.25 |
| **Maya SVG Import (Built-in)** 9 | Native Maya Polygonal Mesh.9 | **Direct.** Fully integrated into Maya's modeling workspace.9 | Included in Maya. | Windows, macOS, Linux. | **Production Ready.** Stable, fully integrated, maintains vector curve fidelity without third-party plugins. |

## **5\. Curated GitHub Repository Registry**

This curated registry identifies the most useful GitHub repositories for vector optimization, isometric transformation, and automatic room construction.

| Repository Name & Link | Core Capabilities & Features | Last Update & Maintenance | License | Difficulty Level | Practical Utility & Workflow Fit |
| :---- | :---- | :---- | :---- | :---- | :---- |
| **[jinkeda/Illustrator\_MCP](https://github.com/jinkeda/Illustrator_MCP)** 5 | Python MCP server with a CEP WebSocket panel inside Illustrator.5 Executes ExtendScript, supports path booleans, and provides annotated previews and checkpoints.5 | Highly active; supports Illustrator CC 2021 to CC 2026+.5 | MIT | Advanced | **Essential.** Enables an offline AI agent (e.g., Claude) to execute ExtendScript commands to automate layout, styling, and path operations in real time.5 |
| [**krVatsal/illustrator-mcp**](https://github.com/krVatsal/illustrator-mcp) 4 | Cross-platform MCP server utilizing COM automation on Windows and AppleScript on macOS.4 Connects AI clients to Illustrator via stdio transport.4 | Active; supports Python 3.12+ and modern Illustrator versions.4 | MIT | Medium | **High Utility.** Lightweight Windows-compatible alternative for letting local LLMs run basic ExtendScript tasks, take screenshots, and auto-generate vector primitives.4 |
| [**creold/illustrator-scripts**](https://github.com/creold/illustrator-scripts) 1 | Sergey Osokin's script library.1 Automates batch artboard creation, layer sorting, ungrouping, mask trimming, and path optimizations.1 | Highly active; verified on Windows/macOS Illustrator CS6 to CC 2026\.1 | MIT | Easy | **Essential.** Instant speed gains for standard daily tasks. Features ExportSequence (export layers to PNG), SortLayerItems, and TrimMasks.1 No programming required. |
| [**sky-chaser-high/adobe-illustrator-scripts**](https://github.com/sky-chaser-high/adobe-illustrator-scripts) 2 | Utility script collection solving alignment, step-and-repeat grids, layer cleanup, and folder relinking.2 | Highly active; compatible with Illustrator CS6 to CC 2026+.2 | MIT | Easy | **High Utility.** Useful for top-down map generation. Features stepAndRepeat.js 11 and alignInCenterOfSpace.js 2 for automated asset scattering. |
| [**mpbrucker/illustrator-isometric-transforms**](https://github.com/mpbrucker/illustrator-isometric-transforms) 10 | Automates Scale, Shear, and Rotate (SSR) transformations on Illustrator selections via a pop-up GUI, allowing rapid mapping of 2D art to isometric planes.10 | Unmaintained but stable and fully operational on modern Illustrator CC versions.10 | MIT | Easy | **High Utility.** Solves the core math of isometric room creation. Eliminates manual input of shear/rotation values.10 |
| **([https://github.com/grebtsew/FloorplanToBlender3d](https://github.com/grebtsew/FloorplanToBlender3d))** 3 | Automatically detects wall lines from flat floor plan images (PNG/PDF) using OpenCV and constructs extruded 3D room geometries inside Blender.3 | Maintained; supports Python \>= 3.8 and Blender \> 2.93.3 | GPL-3.0 | Advanced | **Medium Utility.** Best for generating rapid low-poly blockouts of indoor scenes. Output can be exported to Maya via FBX/OBJ.3 |

## **6\. Recommended Workflow Diagrams & Step-by-Step Pipelines**

These three pipelines illustrate how the selected tools connect to automate design tasks without disrupting the artist's creative control.

### **Pipeline A: Automated Sketch-to-Vector & Logo Workflow**

Designed to convert hand-drawn sketch assets, such as the game logo or custom UI icons, into clean, production-ready vector files.

\+------------------------------------------------------------+  
|                  1\. Raster Sketch Capture                  |  
|  Artist scans hand-drawn stylized logo / asset sketch to   |  
|  high-contrast black-and-white PNG / JPEG.                 |  
\+------------------------------------+-----------------------+  
                                     |  
                                     v  
\+------------------------------------------------------------+  
|             2\. High-Fidelity Vector Conversion             |  
|  Pass raster image to Vectorizer.AI (via Web UI or API)    |  
|  to generate clean, math-optimized SVG vector curves.      |  
\+------------------------------------+-----------------------+  
                                     |  
                                     v  
\+------------------------------------------------------------+  
|                3\. Gated Path Simplification                |  
|  Import SVG into Adobe Illustrator. Run Sergey Osokin's    |  
|  'TrimMasks' / 'SplitPath' scripts to delete redundant    |  
|  points and overlapping vector anchors.                    |  
\+------------------------------------+-----------------------+  
                                     |  
                                     v  
\+------------------------------------------------------------+  
|                 4\. Automated Layer Styling                 |  
|  Use Illustrator\_MCP with Claude to apply custom swatches  |  
|  or run 'ColorToner' to auto-assign game-palette tints.     |  
\+------------------------------------+-----------------------+  
                                     |  
                                     v  
\+------------------------------------------------------------+  
|                    5\. Export Automation                    |  
|  Run 'ExportSequence.jsx' to automatically generate nested |  
|  layered assets and slice them into game-ready PNG/SVG files. |  
\+------------------------------------------------------------+

### **Pipeline B: Procedural Map & Architectural Layout Workflow**

Designed to automate the creation of top-down island layouts, roads, and structural motel floor plans.

\+--------------------------------------------------------------------------+  
|                  1\. Geographic / Structural Generation                   |  
|  Use Azgaar's (for island shapes) or Watabou (for village street networks|  
|  & house footprints) to generate procedural layout templates.            |  
\+------------------------------------+-------------------------------------+  
                                     |  
                                     v  
\+--------------------------------------------------------------------------+  
|                  2\. Vector Clean & Grid Alignment                        |  
|  Import SVG vectors into Illustrator. Align paths to grid using          |  
|  'alignInCenterOfSpace.js' and clean isolated anchor points.             |  
\+------------------------------------+-------------------------------------+  
                                     |  
                                     v  
\+--------------------------------------------------------------------------+  
|                  3\. Split Paths & Layer Separation                        |  
|  Segregate paths: Layer\_Walls (pure lines), Layer\_Doors (openings),       |  
|  Layer\_Ground (polygons). Export clean SVGs separately.                  |  
\+--------------------+-------------------------------------+---------------+  
                     |                                     |  
                     v                                     v  
\+------------------------------------+     \+-------------------------------+  
|      4a. 3D Wall Extrusion         |     |     4b. Asset Scattering      |  
|  Import Layer\_Walls into Maya via  |     |  Use 'stepAndRepeat.js' to    |  
|  the native 'Create \> SVG' tool.   |     |  scatter stylized environmental|  
|  Extrude SVG curve height to 2.8m  |     |  stamps (trees, grass, rocks)  |  
|  procedurally to form 3D walls.    |     |  along island map paths.      |  
\+--------------------+---------------+     \+---------------+---------------+  
                     |                                     |  
                     \+-----------------+-------------------+  
                                       |  
                                       v  
\+--------------------------------------------------------------------------+  
|                   5\. Unified Scene Staging (Maya)                        |  
|  Combine extruded walls with procedural furniture meshes. Export the     |  
|  completed room blockout as a reference FBX file.                        |  
\+--------------------------------------------------------------------------+

### **Pipeline C: Isometric Interior Illustration Workflow**

Designed to construct motel room scenes in isometric projection, linking Maya 3D reference blocks with Illustrator vector art.

\+--------------------------------------------------------------------------+  
|                  1\. 3D Isometric View Staging (Maya)                     |  
|  Import the 2D floor plan layout as a floor plane. Arrange 3D blockout   |  
|  meshes (beds, tables, doors) along the walls.                           |  
\+------------------------------------+-------------------------------------+  
                                     |  
                                     v  
\+--------------------------------------------------------------------------+  
|                     2\. Orthographic Camera Lock                          |  
|  Configure a custom camera rotated exactly 45.0 degrees on the Y-axis    |  
|  and 35.264 degrees on the X-axis. Set projection to 'Orthographic'.     |  
\+------------------------------------+-------------------------------------+  
                                     |  
                                     v  
\+--------------------------------------------------------------------------+  
|                  3\. AI-Driven Visual Drafting (Recraft)                  |  
|  Export 3D viewport flat-renders. Feed renders to Recraft v3 with        |  
|  Style Lock activated (using a hand-drawn motel reference). Generate     |  
|  highly textured isometric style drafts.                                 |  
\+------------------------------------+-------------------------------------+  
                                     |  
                                     v  
\+--------------------------------------------------------------------------+  
|               4\. Vector Transformation & Line-Art Ink                    |  
|  Import the AI draft into Illustrator as a tracing layer. Draw clean vector|  
|  art. Transform flat assets using 'IsometricTransform.jsx' to snap flat   |  
|  shapes instantly onto Left, Right, or Top isometric walls.               |  
\+------------------------------------+-------------------------------------+  
|                                                                          |  
|                      SSR Geometric Projection Math                       |  
|  \- Left Face: Scale Vertical 86.602%, Shear \-30 deg, Rotate \-30 deg      |  
|  \- Right Face: Scale Vertical 86.602%, Shear 30 deg, Rotate 30 deg       |  
|  \- Top Face (Option A): Scale Vertical 86.602%, Shear 30 deg, Rotate \-30 deg|  
|                                                                          |  
\+------------------------------------+-------------------------------------+  
                                     |  
                                     v  
\+--------------------------------------------------------------------------+  
|                       5\. Layered Slicing & Engine Push                   |  
|  Organize elements into grouped layers. Batch export clean SVGs/PNGs     |  
|  with transparent backgrounds, optimized for Unity/Unreal Engine sprites.  |  
\+--------------------------------------------------------------------------+

## **7\. Concrete Setup Plan for the Next 7 Days**

This step-by-step onboarding plan is designed for a Windows workstation environment, focusing on installing and configuring the local toolsets.

### **Day 1: Local System Environment & Python Setup**

To establish a stable environment on Windows, Python and Node.js must be configured.

1. Download and install Python 3.12. Ensure the "Add Python to PATH" checkbox is ticked during installation.4  
2. Download and install Node.js 20 LTS to enable package management.27  
3. Verify the installations in a PowerShell terminal:  
   PowerShell  
   python \-\-version  
   node \-\-version

4. In Adobe Illustrator, navigate to *Preferences \> General* and ensure "Enable Scripting" is active to allow external scripting access.

### **Day 2: Install and Build the Gated Illustrator MCP Server**

This step configures the Python server and the Common Extensibility Platform (CEP) panel inside Illustrator.

1. Clone the primary automation repository:  
   PowerShell  
   git clone https://github.com/jinkeda/Illustrator\_MCP.git  
   cd Illustrator\_MCP  
   \`\`\` \[5\]

2. Create a virtual environment and install the required Python dependencies:  
   PowerShell  
   python \-m venv.venv

..venv\\Scripts\\activate  
pip install \-e ".\[geometry\]"

Đoạn mã  
3\. Build the CEP extension panel:  
\`\`\`powershell  
cd cep-extension  
npm install  
npm run build  
cd..  
\`\`\`   
4\. Run the installer script as an Administrator to link the extension folder to Adobe's directory:  
\`\`\`powershell  
.\\install-cep.bat  
\`\`\`   
5\. Start Illustrator. Go to \*Window \> Extensions\* and open \*MCP Control\*. Verify that the panel status displays "Connected".

\#\#\# Day 3: Setup AI Assistant Bridge & Claude Desktop Configuration  
This step connects Claude Desktop to the local Illustrator environment.  
1\. Install Claude Desktop on Windows.  
2\. Locate the global configuration file: \`%APPDATA%\\Claude\\claude\_desktop\_config.json\`.  
3\. Edit the file to register the local Illustrator MCP server, using absolute file paths:  
\`\`\`json  
{  
  "mcpServers": {  
    "illustrator": {  
      "command": "C:\\\\Users\\\\\<YourUser\>\\\\Illustrator\_MCP\\\\.venv\\\\Scripts\\\\python.exe",  
      "args": \["-m", "illustrator\_mcp.server"\]  
    }  
  }  
}  
\`\`\`   
4\. Restart Claude Desktop. Verify that the tool icon appears in the UI, indicating that Claude can send ExtendScript commands directly to Illustrator.

\#\#\# Day 4: Deploy Osokin's & Isometric Transform Script Toolsets  
This step installs the automated script utilities for vector cleaning and projections.  
1\. Download the script archive from the Sergey Osokin repository (\`creold/illustrator-scripts\`).  
2\. Extract the JSX files and copy \`ExportSequence.jsx\`, \`SortLayerItems.jsx\`, \`TrimMasks.jsx\`, and \`SplitPath.jsx\` into Illustrator's script folder :  
\`C:\\Program Files\\Adobe\\Adobe Illustrator \[Version\]\\Presets\\en\_US\\Scripts\\\`   
3\. Download the \`IsometricTransform.jsx\` script.  
4\. Copy the JSX file and its accompanying \`/assets\` folder into the same Illustrator script directory.  
5\. Restart Illustrator and verify that the scripts are visible under \*File \> Scripts\*.

\#\#\# Day 5: Establish Hotkeys and Custom Actions inside Illustrator  
This step maps the installed scripts to hotkeys for faster access.  
1\. Open the Actions Panel (\*Window \> Actions\*). Create a new Action Set named "Pipeline\_Automation".  
2\. Record a new action named "Run\_Isometric\_Transforms".  
3\. While recording, click the panel's menu button, select "Insert Menu Item", type \`IsometricTransform.jsx\`, click OK, and stop recording.\[28\]  
4\. Assign the Function Key \`F2\` to this action. Repeat the process to map \`ExportSequence.jsx\` to \`F3\` and \`TrimMasks.jsx\` to \`F4\`.\[28\]

\#\#\# Day 6: Setup 3D Floor Plan-to-Blender Docker Container  
This step configures the container environment for automated 2D-to-3D conversions.  
1\. Install Docker Desktop for Windows. Verify that Linux containers are active.  
2\. Pull the prebuilt container image:  
\`\`\`powershell  
docker pull grebtsew/floorplan-to-blender  
\`\`\`   
3\. Create a local folder \`C:\\Tuvu\_Pipeline\\floorplan\_input\\\` to store reference floor plan images.  
4\. Run a test container to confirm the environment is configured correctly:  
\`\`\`powershell  
docker run \-v C:\\Tuvu\_Pipeline\\floorplan\_input\\:/workspace/target grebtsew/floorplan-to-blender  
\`\`\` 

\#\#\# Day 7: Pilot Testing & Integration Validation  
This step verifies that the integration works correctly from start to finish.  
1\. Take a hand-drawn line sketch, convert it via Vectorizer.AI, and import the resulting SVG into Illustrator.  
2\. Select the vector art and press \`F4\` to clean up redundant points and overlapping paths.  
3\. Select an isolated element, press \`F2\`, and choose the left wall transformation.  
4\. Press \`F3\` to run \`ExportSequence.jsx\` and confirm that all sliced assets export cleanly.

\#\# 8\. Concrete Setup Plan for the Next 30 Days

This phase shifts the studio from localized script usage to an automated, scale-ready production pipeline.

\#\#\# Week 2: High-Volume Art Asset Template Optimization  
This week standardizes the canvas templates and asset library.  
1\. \*\*Artboard Template Rigging:\*\* Build a master Illustrator template (.ait) containing standardized artboards for top-down island maps, building footprints, and isolated sprite layouts.  
2\. \*\*Procedural Color Mapping:\*\* Write an ExtendScript script that parses the document, identifies specific path name prefixes (e.g., \`\#base\`, \`\#shadow\`), and applies matching global color swatches from the "Tứ Phương Vô Lộ" palette.  
3\. \*\*Foliage Scattering Automation:\*\* Set up sky-chaser-high's \`stepAndRepeat.js\` script to automate the placement of repeating natural elements like bushes, grass, and rocks along vector paths for top-down maps.

\#\#\# Week 3: Maya Procedural Layout & Camera Locking  
This week implements the 3D-to-2D asset bridge inside Maya.  
1\. \*\*SVG Wall Extrusion:\*\* Write a python utility script for Autodesk Maya's shelf that automates the import of clean floor plan SVGs and extrudes the vector lines to a standard wall height of 2.8 meters.  
2\. \*\*Isometric Camera Locking:\*\* Script a camera setup utility in Maya that locks an orthographic camera at a pitch of $35.264^\\circ$ and yaw of $45^\\circ$, preventing accidental movement during asset blockout reviews.  
3\. \*\*MASH Procedural Grid:\*\* Configure MASH nodes in Maya to automatically distribute interior furniture assets along the floor plan grid lines using empty locator nodes as placement coordinates.\[29, 30\]

\#\#\# Week 4: Multi-Model Agentic Workflow Deployment  
This week deploys the AI-driven asset validation and file management systems.  
1\. \*\*Visual Feedback Loop:\*\* Configure Claude via the \`Illustrator\_MCP\` VLM grounding framework. This allows the AI to automatically capture screenshots, detect vector overlapping, and flag out-of-bounds elements using coordinate rulers.  
2\. \*\*Asset Organization Automation:\*\* Set up a local Filesystem MCP server.\[31\] Use it to monitor newly exported FBX files from Maya, match them with corresponding vector sheets in Illustrator, and automatically update the studio's asset registry markdown files.\[32, 33\]

\#\# 9\. Contextual Prompt Engineering Suite

To leverage AI models effectively within this pipeline, the following copy-pasteable templates provide clear guidelines for asset generation and cleanup.

\#\#\# Prompt 1: Stylized Isometric Room Draft Generation (Recraft v3 / Firefly)  
This prompt should be used in Recraft v3 with \*Style Lock\* activated, using a hand-drawn motel room illustration as a visual style reference.

A highly stylized, isometric interior illustration of an old island motel room, in the style of hand-drawn vector game art.  
The scene includes an old wooden bed with messy green sheets, a rustic side table with a glowing desk lamp, a dynamic light source casting soft shadows, and worn wooden floorboards.  
The perspective must be a perfect 30-degree orthographic isometric projection with no vanishing points.  
Lines are clean, slightly irregular, hand-drawn ink line art with a warm, limited color palette containing teal, pale yellow, and deep mahogany brown.  
Clean, isolated composition on a solid, pure magenta background (\#FF00FF) for easy background extraction.  
Absolutely no text, no signatures, and no human characters in the room.

\#\#\# Prompt 2: 2D Stylized Top-Down Island Map Generation (Recraft v3)  
This prompt generates top-down layout concepts for regional landmasses.

A stylized, top-down regional game map of a rustic fantasy island.  
Hand-drawn vector game asset aesthetic.  
Includes winding dirt roads, dense groupings of stylized pine trees, small rocky cliffs, sandy coastlines with gentle blue water ripples, and a small wooden dock protruding from the southern coast.  
The style must feature clean black outer outlines on all geographic landmasses, with simplified solid color fills of sage green, sand tan, and ocean blue.  
Minimalistic detail density, optimized for clear game level navigation.  
Flat 2D view, perpendicular perspective, orthogonal projection.  
Vector SVG style, no realistic textures, no gradients, clean color segments.

\#\#\# Prompt 3: Agentic Vector Path Cleanup & Layer Organization (Illustrator\_MCP)  
This prompt instructs Claude to analyze and clean up active documents in Illustrator.

Using the active document in Adobe Illustrator, perform a systematic preflight and structural path cleanup on the active selection:  
1\. Run a preflight scan to identify any off-artboard items, empty text frames, or locked vector elements.  
2\. Group all paths that share the exact stroke width of 3pt or higher, and move them to a new main layer named "Layer\_Outlines".  
3\. Group all closed filled paths with no stroke, and move them to a layer named "Layer\_Fills".  
4\. For all selected overlapping path intersections, execute a path simplification operation to reduce redundant vector anchor points by 20% while preserving original path shapes.  
5\. Create an annotated canvas preview with bounding boxes and output the final JSON map linking visual coordinates to the updated path IDs.  
Apply the 'validate' and 'geometry' libraries for precise bounding box evaluations.

\#\# 10\. Final Recommendation: The Most Realistic Workflow for Tứ Phương Vô Lộ

To maximize production efficiency while preserving the hand-drawn visual style of "Tứ Phương Vô Lộ", a hybrid integration strategy is recommended. This setup blends traditional drawing workflows with targeted automation tools.

\#\#\# Production Pipeline Tiers

   \+-------------------------------------------------------+  
   | TIER A: Beginner / Low-Risk                           |  
   | \- Manual Illustrator \+ Sergey's Scripts               |  
   | \- Wonderdraft raster references                       |  
   | \- Manual Maya Isometric Camera setup                  |  
   \+---------------------------+---------------------------+  
                               |  
                               v  
   \+-------------------------------------------------------+  
   | TIER B: Semi-Automated (RECOMMENDED BASELINE)         |  
   | \- Vectorizer.AI for high-fidelity tracing             |  
   | \- mpBrucker script for instant SSR transforms         |  
   | \- Sweet Home 3D \+ Maya OBJ Import (Wall extrusion)    |  
   \+---------------------------+---------------------------+  
                               |  
                               v  
   \+-------------------------------------------------------+  
   | TIER C: Advanced Agentic                              |  
   | \- Illustrator\_MCP / krVatsal stdio servers            |  
   | \- Claude Desktop natural language vector automation  |  
   | \- Procedural asset scattering on grids                |  
   \+-------------------------------------------------------+

The studio should adopt \*\*Tier B\*\* as the primary production pipeline immediately, while parallel-testing \*\*Tier C\*\* operations on a separate workstation.

This approach minimizes disruption to the artist's existing workflow by introducing improvements incrementally:  
1\.  \*\*Vectorizer.AI Integration:\*\* The artist can continue to hand-sketch logos and map elements. Instead of manually tracing them in Illustrator, she routes them through Vectorizer.AI. This produces clean, production-ready vector curves in seconds, preserving the stylized organic linework with minimal anchor points.  
2\.  \*\*Isometric Grid Automation:\*\* By using Sergey Osokin's script library  and the \`IsometricTransform.jsx\` panel , the artist avoids manually shearing and rotating shapes. She simply designs assets flat on the orthographic grid and projects them onto left, right, or top isometric planes with a single keystroke.  
3\.  \*\*The Maya-to-Illustrator Blockout Bridge:\*\* For architectural interiors, the artist should layout rooms in Sweet Home 3D  or import the clean 2D floor plan layout directly into Maya using the native SVG import tool. Walls are extruded procedurally in Maya with a single command, and basic cubes are placed as furniture guides. The locked isometric orthographic camera then outputs perfect blockout templates. This reference geometry is placed back into Illustrator as a tracing layer, eliminating the perspective alignment errors common to purely manual drawing.

\#\#\# Pipeline Risks & Practical Mitigations

Implementing new automation scripts and AI tools introduces specific production risks that must be addressed:

\*   \*\*Messy Vectors and Anchor Point Bloat:\*\* Pure AI vector generators often create overlapping shapes and redundant anchor points.  
    \*   \*Mitigation:\* Force all imported AI vectors through Sergey Osokin's path simplification and path splitting scripts before manual polishing.  
\*   \*\*Poor 3D Mesh Topology:\*\* Auto-generated 3D blockouts from 2D floor plans can produce messy, triangulated meshes that are difficult to edit.  
    \*   \*Mitigation:\* Keep the automated 3D blockout strictly as a non-rendering reference guide. Only use it to establish correct perspective angles and bounding box coordinates. The final game-ready assets should be built on top of these blocks using clean, manual quad-topology inside Maya.  
\*   \*\*Style Inconsistency in AI Drafts:\*\* AI-generated room layouts can drift from the hand-drawn, cozy visual identity of "Tứ Phương Vô Lộ".  
    \*   \*Mitigation:\* Never use raw AI renders as final game sprites. Treat them as high-speed concept drafts to block in composition and lighting. The artist must perform the final vector inking and line-art polish manually to ensure cohesive art direction.  
\*   \*\*Platform and Version Instability:\*\* Third-party Illustrator and Maya scripts can break when Adobe or Autodesk releases software updates.  
    \*   \*Mitigation:\* Rely on actively maintained repositories with permissive licenses (such as MIT). Standardize the studio's workstations on specific long-term support software builds (e.g., Illustrator CC 2026 and Maya 2024+), and disable automatic updates during active production phases. Ensure all custom script files are safely committed and version-controlled inside the studio's Git repository.

#### **Nguồn trích dẫn**

1. creold/illustrator-scripts: Some powerfull JSX scripts for extending Adobe Illustrator · GitHub, truy cập vào tháng 5 28, 2026, [https://github.com/creold/illustrator-scripts](https://github.com/creold/illustrator-scripts)  
2. sky-chaser-high/adobe-illustrator-scripts \- GitHub, truy cập vào tháng 5 28, 2026, [https://github.com/sky-chaser-high/adobe-illustrator-scripts](https://github.com/sky-chaser-high/adobe-illustrator-scripts)  
3. grebtsew/FloorplanToBlender3d: Create 3d rooms in ... \- GitHub, truy cập vào tháng 5 28, 2026, [https://github.com/grebtsew/FloorplanToBlender3d](https://github.com/grebtsew/FloorplanToBlender3d)  
4. krVatsal/illustrator-mcp · GitHub \- GitHub, truy cập vào tháng 5 28, 2026, [https://github.com/krVatsal/illustrator-mcp](https://github.com/krVatsal/illustrator-mcp)  
5. jinkeda/Illustrator\_MCP · GitHub \- GitHub, truy cập vào tháng 5 28, 2026, [https://github.com/jinkeda/Illustrator\_MCP](https://github.com/jinkeda/Illustrator_MCP)  
6. 10 Best Recraft Alternatives for AI Vector and Brand Asset Generation in 2026 \- Flowith Blog, truy cập vào tháng 5 28, 2026, [https://flowith.io/blog/10-best-recraft-alternatives-ai-vector-brand-asset-generation-2026/](https://flowith.io/blog/10-best-recraft-alternatives-ai-vector-brand-asset-generation-2026/)  
7. Best Vector Conversion Services in 2026: Complete Comparison Guide \- VectorGurus, truy cập vào tháng 5 28, 2026, [https://vectorgurus.com/blog/best-vector-conversion-services-2026](https://vectorgurus.com/blog/best-vector-conversion-services-2026)  
8. GitHub \- akramguediri/FloorPlan3DConverter: convert a floor plan to an actual 3d rendering, truy cập vào tháng 5 28, 2026, [https://github.com/akramguediri/FloorPlan3DConverter](https://github.com/akramguediri/FloorPlan3DConverter)  
9. Maya Help | Create polygon meshes from SVG objects | Autodesk, truy cập vào tháng 5 28, 2026, [https://help.autodesk.com/view/MAYAUL/2024/ENU/?guid=GUID-F28EA595-1FA8-496A-A620-A32D1BE2F0E7](https://help.autodesk.com/view/MAYAUL/2024/ENU/?guid=GUID-F28EA595-1FA8-496A-A620-A32D1BE2F0E7)  
10. mpbrucker/illustrator-isometric-transforms: A neat little script ... \- GitHub, truy cập vào tháng 5 28, 2026, [https://github.com/mpbrucker/illustrator-isometric-transforms](https://github.com/mpbrucker/illustrator-isometric-transforms)  
11. Step and Repeat in Illustrator \- Adobe Community, truy cập vào tháng 5 28, 2026, [https://community.adobe.com/questions-652/step-and-repeat-in-illustrator-790974](https://community.adobe.com/questions-652/step-and-repeat-in-illustrator-790974)  
12. Recraft vs. Vectorizer Comparison \- SourceForge, truy cập vào tháng 5 28, 2026, [https://sourceforge.net/software/compare/Recraft-vs-Vectorizer/](https://sourceforge.net/software/compare/Recraft-vs-Vectorizer/)  
13. Vectorizer.AI Pricing | Web App Plans & Image Vectorization API Credits, truy cập vào tháng 5 28, 2026, [https://vectorizer.ai/pricing](https://vectorizer.ai/pricing)  
14. Recraft v3 Vector Pro vs. Adobe Illustrator AI: Which Is Better for Generating Scalable Brand Assets? \- Flowith Blog, truy cập vào tháng 5 28, 2026, [https://flowith.io/blog/recraft-v3-vs-adobe-illustrator-ai-scalable-brand-assets-icon-sets/](https://flowith.io/blog/recraft-v3-vs-adobe-illustrator-ai-scalable-brand-assets-icon-sets/)  
15. Pricing and plans \- Recraft.ai, truy cập vào tháng 5 28, 2026, [https://www.recraft.ai/pricing](https://www.recraft.ai/pricing)  
16. Best AI Vector Generators of 2024: Top Tools Compared \- Recraft AI, truy cập vào tháng 5 28, 2026, [https://www.recraft.ai/blog/best-ai-vector-generators](https://www.recraft.ai/blog/best-ai-vector-generators)  
17. 10 Best Tools to Create Fantasy, D\&D, and World Maps (2026) \- AI Photo Generator, truy cập vào tháng 5 28, 2026, [https://www.aiphotogenerator.net/blog/2026/03/ai-map-generator-fantasy-dnd-guide](https://www.aiphotogenerator.net/blog/2026/03/ai-map-generator-fantasy-dnd-guide)  
18. Best Fantasy Map Generators 2026 \- Robb Wallace Author, truy cập vào tháng 5 28, 2026, [https://www.robbwallace.co.uk/news/best-fantasy-map-generators/](https://www.robbwallace.co.uk/news/best-fantasy-map-generators/)  
19. How to make a map for a fictional city (fairly sized), similar to the style of the GTA ones, truy cập vào tháng 5 28, 2026, [https://www.quora.com/How-do-I-make-a-map-for-a-fictional-city-fairly-sized-similar-to-the-style-of-the-GTA-ones-Im-not-looking-for-any-fictional-fantasy-stuff-either-just-simple-blocks-and-stuff](https://www.quora.com/How-do-I-make-a-map-for-a-fictional-city-fairly-sized-similar-to-the-style-of-the-GTA-ones-Im-not-looking-for-any-fictional-fantasy-stuff-either-just-simple-blocks-and-stuff)  
20. Free Fantasy Map Generators / Assorted Links \- Feed the Multiverse, truy cập vào tháng 5 28, 2026, [https://feedthemultiverse.com/free-fantasy-map-generators-assorted-links/](https://feedthemultiverse.com/free-fantasy-map-generators-assorted-links/)  
21. Can't Export Floor Plan in Sweet Home 3D? Save as Image or PDF \- Coohom, truy cập vào tháng 5 28, 2026, [https://www.coohom.com/article/sweet-home-3d-export-floor-plan](https://www.coohom.com/article/sweet-home-3d-export-floor-plan)  
22. Exporting Models or simple Kitchen furniture sample \- Sweet Home 3D Forum \- View Thread, truy cập vào tháng 5 28, 2026, [https://www.sweethome3d.com/support/forum/viewthread\_thread,10780](https://www.sweethome3d.com/support/forum/viewthread_thread,10780)  
23. Exporting a 3D Model – Live Home 3D for Windows, truy cập vào tháng 5 28, 2026, [https://www.livehome3d.com/support/help/win/en/working-with-projects-exporting-a-3d-model](https://www.livehome3d.com/support/help/win/en/working-with-projects-exporting-a-3d-model)  
24. Exporting FloorPlan with Dimensions \- Sweet Home 3D Forum \- View Thread, truy cập vào tháng 5 28, 2026, [https://www.sweethome3d.com/support/forum/viewthread\_thread,12365](https://www.sweethome3d.com/support/forum/viewthread_thread,12365)  
25. doratracyer/floor\_plan: 3D-printable floor plan generator: Convert SVG layouts into 3D models. \- GitHub, truy cập vào tháng 5 28, 2026, [https://github.com/doratracyer/floor\_plan](https://github.com/doratracyer/floor_plan)  
26. ADD "Relink to Folder..." to the Links panel as in InDesign \- Adobe Illustrator \- Uservoice, truy cập vào tháng 5 28, 2026, [https://illustrator.uservoice.com/forums/333657-illustrator-desktop-feature-requests/suggestions/39739852-add-relink-to-folder-to-the-links-panel-as-in](https://illustrator.uservoice.com/forums/333657-illustrator-desktop-feature-requests/suggestions/39739852-add-relink-to-folder-to-the-links-panel-as-in)  
27. MCP server for reading, manipulating, and exporting Adobe Illustrator design data \- GitHub, truy cập vào tháng 5 28, 2026, [https://github.com/ie3jp/illustrator-mcp-server](https://github.com/ie3jp/illustrator-mcp-server)

[image1]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAmwAAAAxCAYAAABnGvUlAAADu0lEQVR4Xu3cTahtYxgH8EcoQhT5ioEi+crAVwbKREhmBhSSCQMGFEZud2Jm4rN8TCSEEikxcpiYKAZCSl1iQjJBUT7ef+9a56697jmnfU6X27F/v3rae73r2WutvUf/3netXQUAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAsML+ntSVs31xdy32nLa4e9dbq8XvN9a+Vieudy3nxjrwOPm91mZj6VvWMdU/88vw+lqr9xc6AICV8G2rx1r93OrC2b6XW73S6pv6/4W10QvVw9Alk7HLhrHjJ2PLyDF+rR7Sjp2Mj+fYTlg7r9VPrY6bjCVErk22AYAVsa/VtdUDxd7J+NGtrqseNlYtsOV9xi6ejC3jYAa266t/5orZ+NpsGwBYAZ9WD2PfVQ8IoyeG11ULbKe3eqnVj+sdyxsD25etbm1101Af1vYDWwLz27W4nPpDq8OnTQDAahgD25O1uAw43iu1WwLb2dWXdzerW/a3LhgD27xOmDYtaQxsf1YPwOO5/6jtB7Y4ow68rgcXOgCAlTAGtszovFv9nrUEhfF+tnlgyzJh7q86WKb3aE3d2+rF+eC/YD7Ddkqrr6svFW/k/ur9R8131M6WRHO+BLyrZ+Mntbpqsn1kq/uqHwcAWDFjYIuTqweC3/fvXghsCSkPtLqo1Z2tHmn18NB3V6vnWp0/9LxR/WGG96oHlUerz97lyce9rR5vdWqrz1o9W/2erVdbPT/0ZsbvmepyzCxTjsu0G8lxxyXIjWqzkDkPbAlaa8NYbBTMNrOTwLaZ9P41G8sxc3wAYIUkhH1efdYsMziRYJGZtsOG/a+3+n7oyf1TmRFLMHl66MmM0xHV79nKU4zvDD0fDPsTxC6tHrgS6p4aelMJYNMQc0erL6r/fUWe1Mw9XBe0+rjVua2+Wu88OHK9+X75znnwIrNd+S6ZZcxYrv+eWi60pSfH+K3VR9WXaPN7Tc9x+9C3jPwu+cye6teVY2VZN+EWAGBLmeVJYDuzegB7q9Xlw1hkNmmcpYqMZzvjD1Vfahx7I8EkIemc4X36Ij1vVv9Mwt5/LQF2nFU8FHL+zBqO7w/ltQAAu8wY2G4bthOmMpuUvwAZn2zcKrBlBu7m6rNXN1QPadmfP+ndKLBd0+qTYeys4RUAgCUkcE3v04pxWXUZ095xJmkr2/0TWwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAB24h/aasST2jvdngAAAABJRU5ErkJggg==>

[image2]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEoAAAAZCAYAAACWyrgoAAAEmElEQVR4Xu2XW+hmUxjGHxlFM0jGDCFjGuRQM5NTChkhLkioMWiaSKY5hSmHadRfkkhCOSZG0riQQ2PK6eIfpRzKISSHRMqdC0Ukh+c3737ttfe39zffdz37qafv23uvvdb7Pus9rC0NGDBgcswzF5h7tx8U4Nn+7Zt7Ei4z3zW3mC+ZhzYf7wIi3Wbe3H4wDvuZV5lPmveZJ5h7NUbUOE4xhrGXa/yOlWC+082HzUfNs6t7Jcq5sQe72jjMvEMx5k5zSfOxjjQ/Mc+srq8xfzFnzGMU719ovmm+oYi8iXCgQvXVikmWmu+Ym9V0ZB9zq/mhebK52Nxhri3G9GGu+Yz5snm8eaL5kXl+MQbRvzSXKYy/y3xLYV/itOreWQo7d5r/qmnrReYP5hHVNXY+YB5tXmFebV6q8Hl5NWYibFCEaImTzI8VkycQ5BtzUXWNQRj5bA7oAQ48qBA/nSbceffW6pooYG6cSByk2BTsA0TXK+a1qqP4YPMD8zfF5gHmRCg2HfCLjWXk3KApUw4wyb1qRg+TIxS7BtIR0iaB00QY6TQOOIAjGJdgt+9W7DZAoNJZgD3Pm7MKJ7EJAX5VbRdgkxE9Hac+lUKx1uPmvtU10fycpki5BAazECKQImClIqxzsiurMTjEghgx6UIz5l+KmpEOp9EJ1m4LBdjEnxWCkvoPKepKigCIoDI6qXNfmadW19Sjm6r/ROU2TZlyiaPMrxWLfasQjo7B/QSO8Jy6wW6sVxRMIhEH+oAgCI4I95hPKHae6FynOooRpE+orvuJOeaL5t/mOdU95qRmkeqk6Wuq6xVrT51yJSiwPyrEyLpzQPGca+7Pqo4kOgi7jVF9YOys4t2nFI6BFYoUuqQY0yXI7oQi7XlOB2xvGN3wYtV+EEUvqLY/O+wqjb7bCdQmgqghdD4WxrH3FMUSpFBlnUkHvzDnF/dL5Jh/zPOK+1lviDbWeFvdgowTihrJe0R4low+YAciZcrRPd+vrq83b9ToUaUBcnaH6vwGCPeqQpjsOEQD1+xQYlwkJHCgS4QUKotunyB994kACjRtv+us1UaZckT1dkWJAbzPXIdX152ge1CfSL0SvPy66taf7XxaoQAit8e0hcLo9hjA+j+prjEgRbpd9TEB+y/4f0QT7ZRbaH6nZnBs1OjaDfCQQ1626RK03TwOnGH+qeY5pyv1MHyRml2Njsm7dL1EmXqMpVZRkMv0zEaQYwDpsVnRxcpUoSRwLGijnXIg1y6FInPwsRdMxFGe3SkXPkQhQr6cKVoW5K5ifp0i8gjtHMeH6edqGrZCdTEH1CkOjjM5QFGMiSaEBti3xvy9uk/zSfKJUm5Egkwo6yrgI5ianPYw7/0azaoRYNCnCsGIGCKJKKGwl+IxEdH3tEKQz8zH1OwYpOYf5i1qvnuuwjmOCJuq/whcjjnF/F7xLp8anMrL40dGQnbmknnWKkEUbVN3DUMkPqeYG/9J5a5xIyBlSEMMJNf7uggT8zHLuGO1m07RAnMyN99ZnPS7MMmYSUCqPqLRD+YEorAJRBbfjnxfDhgwYMCAAQMGTIr/AIIo/ZnEYuhDAAAAAElFTkSuQmCC>

[image3]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAC0AAAAZCAYAAACl8achAAAB70lEQVR4Xu2VSyjEURTGj1AUSV4pCrGQBbKQIlKkZIMFUXbIViilFDZ2LCykJFlRVqw9looVNiQlorCTjcf3zbm3uTNjPDLzX/2/+tXc1/y/e+4594r48uXrK+WDKbAMRkFh6HBACaAWLIIl0A4SQ2aIVIN1sAkaRNfERR1gF1SCHDADXkGnM4cfHwf7oBhkgQ3RTSabORVgWHQjnN8FmsxYTJUCdsCzaJSoEnAHTkG26asB96DetCnOuwZtpt0rOs+KpzfmtGMmmt4GbxKMSgG4AZcgz/TNiRqkEat0cAhWRSPbChqd8TLQ77RjKhrncdv8Y+TewQpIMuM8jXDTaWAPHIFMkCq6OaYV83keZNjJ8RSjfCBqhL8pay6aabefG2cAciWySGMufoRHzbQ4Fi1KG3kaorHfmP6TWMHMPy7+iZ+i0AxewLQE/5f5HW7u36arRK+f37AAigKrvpYtMBZni0Q3F60/7mKhTIM+CX0I1sAHmBAtxi2JNGdNc4PcqGfiw0JzriFrhv1Dpo/mH0G5aVO8w3mX84X0VHwMnsCsBF+2UnALziV4g7CPRdpj2hSvtQdQ5/R5IqbEiGjEJkXT5ARciNaJK96/V2AQDIAz0bVuWnkq5jZftG7R6Ee7XXgHM6UIf/vy5cuXr+/1CR9TXozQIgfQAAAAAElFTkSuQmCC>

[image4]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAB0AAAAZCAYAAADNAiUZAAABvUlEQVR4Xu2UvyuGURTHj1Dkd8RCJPlRCjEZ9A7yY5FiEKOBQSGFTPRmQBZlMZGUP4CJ4S0buwUpiUmiLEp8v859PD889yWx6PnUZ7jn3vece89z7ysS8Z/JheNwAy7AapjiW6HUwGXRdYMw0z8tFXAd7sE+mOqb9dAAEzAGC+AIfIZT4i/MJKewEWbDODyAeWa+GM6Ku5FW0Y2FsgZfYI8Zs/AJvIN1JlYGz+CQGRNn3ZgZt8Mud/p9Y3MwwxP7YBW+wmEzzoFH8FG0C4TFnmCzGRN2YUe0SyzAOXbDoVD0k4WSDovE7X89vBc3GWE3gkXJFryFlTANTohunutWYLm71A4vFHd/JfrtHJjcVjQYz4cloodJShbcFS12ATvFPTlPm5DPyUlY0R9RC2/gtuhm6KGEJ/+1os4F4eUaNTFbcls8Kez7pNH7DWZEizIpWZTw5Jy/hqWBeFKYhMmCCZmMRXlrCd8w3zLfogPf374x9C3acB79prj/LHxfx6LPpikQmzdjUiV6ygFP7Nt0w3O4JJqAO38wcS8t8BJOw37RfyP+5sunYYPtiYkmaxN7It7kDtgr2qWIiIi/5Q0xeVavRWGBQgAAAABJRU5ErkJggg==>