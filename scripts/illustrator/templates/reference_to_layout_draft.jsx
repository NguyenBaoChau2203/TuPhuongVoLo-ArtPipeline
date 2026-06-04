/*
  TuPhuongVoLo reference-to-layout draft template.

  Codex should copy this file and customize the scene-specific geometry from
  the artist's reference image and Vietnamese description.

  Run in Illustrator:
  File -> Scripts -> Other Script...

  Safety:
  - Creates editable vector groups/layers.
  - Does not overwrite any .ai source file.
  - Does not export SVG automatically; the artist reviews and exports manually.
*/

#target illustrator

(function () {
  if (app.documents.length === 0) {
    app.documents.add(DocumentColorSpace.RGB, 1200, 800);
  }

  var doc = app.activeDocument;

  function rgb(r, g, b) {
    var c = new RGBColor();
    c.red = r;
    c.green = g;
    c.blue = b;
    return c;
  }

  function layerNamed(name) {
    for (var i = 0; i < doc.layers.length; i++) {
      if (doc.layers[i].name === name) {
        return doc.layers[i];
      }
    }
    var layer = doc.layers.add();
    layer.name = name;
    return layer;
  }

  function makeGroup(parent, name) {
    var group = parent.groupItems.add();
    group.name = name;
    return group;
  }

  function rect(parent, name, left, top, width, height, fill, stroke, strokeWidth) {
    var item = parent.pathItems.rectangle(top, left, width, height);
    item.name = name;
    item.filled = true;
    item.fillColor = fill;
    item.stroked = true;
    item.strokeColor = stroke;
    item.strokeWidth = strokeWidth || 2;
    return item;
  }

  function line(parent, name, x1, y1, x2, y2, stroke, strokeWidth) {
    var item = parent.pathItems.add();
    item.name = name;
    item.setEntirePath([[x1, y1], [x2, y2]]);
    item.filled = false;
    item.stroked = true;
    item.strokeColor = stroke;
    item.strokeWidth = strokeWidth || 3;
    return item;
  }

  function label(parent, text, x, y) {
    var t = parent.textFrames.add();
    t.contents = text;
    t.left = x;
    t.top = y;
    t.textRange.size = 16;
    t.name = "note_artist_review";
    return t;
  }

  var layerGuide = layerNamed("00_artist_notes");
  var layerRoom = layerNamed("01_room_boundary");
  var layerOpenings = layerNamed("02_doors_windows");
  var layerProps = layerNamed("03_large_props");
  var layerFlow = layerNamed("04_flow_paths");

  var black = rgb(35, 31, 32);
  var floor = rgb(216, 232, 205);
  var doorColor = rgb(96, 159, 190);
  var windowColor = rgb(128, 178, 224);
  var propFill = rgb(185, 147, 98);
  var flowColor = rgb(216, 111, 71);

  // Replace these names per scene. Keep pipeline prefixes.
  var roomGroup = makeGroup(layerRoom, "room_phong_kho");
  rect(roomGroup, "room_boundary", 180, 620, 760, 420, floor, black, 5);

  var openingsGroup = makeGroup(layerOpenings, "openings_for_phong_kho");
  var doorGroup = makeGroup(openingsGroup, "door_main");
  rect(doorGroup, "door_main_marker", 160, 430, 45, 95, doorColor, black, 2);

  var windowGroup = makeGroup(openingsGroup, "window_back_01");
  rect(windowGroup, "window_back_01_marker", 560, 640, 160, 24, windowColor, black, 2);

  var propsGroup = makeGroup(layerProps, "props_for_phong_kho");
  var shelf1 = makeGroup(propsGroup, "prop_shelf_01");
  rect(shelf1, "prop_shelf_01_marker", 750, 570, 145, 42, propFill, black, 2);

  var shelf2 = makeGroup(propsGroup, "prop_shelf_02");
  rect(shelf2, "prop_shelf_02_marker", 750, 500, 145, 42, propFill, black, 2);

  var crate1 = makeGroup(propsGroup, "prop_wooden_crate_01");
  rect(crate1, "prop_wooden_crate_01_marker", 450, 430, 70, 62, propFill, black, 2);

  var crate2 = makeGroup(propsGroup, "prop_wooden_crate_02");
  rect(crate2, "prop_wooden_crate_02_marker", 540, 380, 64, 58, propFill, black, 2);

  var flowGroup = makeGroup(layerFlow, "flow_main_path");
  line(flowGroup, "flow_main_path_line", 225, 385, 840, 385, flowColor, 5);
  line(flowGroup, "flow_turn_to_shelves", 650, 385, 750, 515, flowColor, 4);

  label(
    layerGuide,
    "Draft generated for artist review. Edit layout by eye, keep room_/door_/window_/prop_/flow_ names, then export SVG manually.",
    160,
    720
  );

  app.redraw();
})();
