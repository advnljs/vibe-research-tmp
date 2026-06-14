const stage = document.querySelector("#stage");
const A = "../assets/generated/";
const TEXT_SCALE = 1.12;
let pageIndex = 0;
let isTurning = false;

function el(tag, className, styles = {}, parent = stage) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  Object.assign(node.style, styles);
  parent.appendChild(node);
  return node;
}

function box(className, x, y, w, h, parent = stage) {
  return el("div", className, {
    left: `${x}px`,
    top: `${y}px`,
    width: `${w}px`,
    height: `${h}px`,
  }, parent);
}

function txt(value, x, y, size, className = "", parent = stage, styles = {}) {
  const readableSize = Math.max(size + 1, Math.round(size * TEXT_SCALE));
  const node = el("div", `text ${className}`, {
    left: `${x}px`,
    top: `${y}px`,
    fontSize: `${readableSize}px`,
    ...styles,
  }, parent);
  node.textContent = value;
  return node;
}

function img(file, x, y, w, h, className = "", parent = stage, styles = {}) {
  const node = el("img", `asset ${className}`, {
    left: `${x}px`,
    top: `${y}px`,
    width: `${w}px`,
    height: `${h}px`,
    ...styles,
  }, parent);
  node.src = `${A}${file}`;
  return node;
}

function rule(x, y, w, parent = stage) {
  return box("rule", x, y, w, 1, parent);
}

function panel(x, y, w, h, parent = stage, className = "") {
  return box(`panel ${className}`, x, y, w, h, parent);
}

function showToast(message) {
  const toast = document.querySelector("#toast");
  toast.textContent = message;
  toast.classList.remove("show");
  void toast.offsetWidth;
  toast.classList.add("show");
}

function resize() {
  const scale = Math.min(window.innerWidth / 1672, window.innerHeight / 941);
  stage.style.transform = `translate(-50%, -50%) scale(${scale})`;
}

function createDesk() {
  img("medallion-compass.png", 20, -12, 90, 145, "decor", stage, {
    transform: "rotate(-18deg)",
    opacity: "0.88",
  });
  img("icon-key.png", 1537, 750, 55, 92, "decor ink-asset", stage, {
    transform: "rotate(50deg)",
    opacity: "0.78",
  });
  img("icon-quill.png", 1510, 100, 78, 122, "decor ink-asset", stage, {
    transform: "rotate(30deg)",
    opacity: "0.78",
  });
  img("icon-map.png", 8, 704, 124, 97, "decor ink-asset", stage, {
    transform: "rotate(-18deg)",
    opacity: "0.45",
  });
}

function createBook() {
  el("div", "book-shadow");
  el("div", "book-cover");
  el("div", "page-stack");
  el("div", "page page-left");
  el("div", "page page-right");
  el("div", "crease");
  img("corner-ornament.png", 278, 82, 57, 56, "ornament");
  img("corner-ornament.png", 1393, 82, 57, 56, "ornament", stage, { transform: "scaleX(-1)" });
  txt("12", 792, 845, 10, "muted");
  txt("13", 865, 845, 10, "muted");
}

function createNavigation() {
  const nav = el("nav", "nav");
  const items = [
    ["world", "WORLD"],
    ["characters", "CHARACTERS"],
    ["memories", "MEMORIES"],
    ["events", "EVENTS"],
    ["map", "MAP"],
    ["threads", "THREADS"],
  ];
  items.forEach(([name, label]) => {
    const button = el("button", `nav-button nav-${name}`, {}, nav);
    button.innerHTML = `<span>${label}</span>`;
    button.addEventListener("click", () => showToast(`${label} opened`));
  });
  const logs = el("button", "nav-button nav-logs", {}, nav);
  logs.innerHTML = `<img src="${A}icon-quill.png" alt=""><span>LOGS</span>`;
  logs.addEventListener("click", () => showToast("LOGS opened"));
}

function createMessage(x, y, h, icon, speaker, time, body, you = false, parent) {
  box(`message${you ? " you" : ""}`, x + 28, y, 410, h, parent);
  img(icon, x - 5, y + h / 2 - 20, 40, 40, "message-avatar", parent);
  txt(speaker, x + 52, y + 8, 9, "bold", parent);
  txt(time, x + 428, y + 8, 8, "muted", parent, { transform: "translateX(-100%)" });
  txt(body, x + 52, y + 25, 10, "", parent, { lineHeight: "1.3" });
}

function createChoice(x, y, icon, label, key, parent) {
  const button = box("choice", x, y, 438, 31, parent);
  button.innerHTML = `${icon}&nbsp;&nbsp;&nbsp; ${label}<span class="choice-key">${key}</span>`;
  button.addEventListener("click", () => {
    parent.querySelectorAll(".choice").forEach((item) => item.classList.remove("selected"));
    button.classList.add("selected");
    showToast(label);
  });
}

function createControl(x, y, w, label, parent) {
  const button = box("control", x, y, w, 34, parent);
  button.textContent = label;
  button.addEventListener("click", () => showToast(label));
}

function createLeftPage() {
  const page = el("section", "page-content left-content");
  txt("CURRENT SCENE", 338, 90, 10, "bold", page);
  txt("Whispers in the Fog", 338, 110, 18, "bold", page);
  txt("◆  Scene 12", 522, 116, 10, "muted", page);
  rule(338, 139, 420, page);

  txt(
    "A cold mist curls through the cobblestone alleys, swallowing the gaslight\n" +
      "in a pale hush. The tower clock tolls once in the distance. Somewhere\n" +
      "above, a shutter opens... then closes.",
    338, 154, 13, "", page, { lineHeight: "1.48" },
  );
  txt(
    "Ahead, the narrow lane forks—left toward the market square,\n" +
      "right toward the old watchhouse. A torn poster flutters against\n" +
      "the wall, half-burned, the name illegible.",
    338, 219, 13, "", page, { lineHeight: "1.48" },
  );

  createMessage(330, 290, 61, "icon-world.png", "NARRATOR", "10:21 AM",
    "The air smells of damp stone and smoke. Your boots splash lightly\nin a shallow puddle. A stray dog watches you from the shadows.", false, page);
  createMessage(330, 362, 48, "icon-character.png", "YOU", "10:21 AM",
    "I step closer to the poster and try to read what I can.", true, page);
  createMessage(330, 421, 61, "icon-world.png", "NARRATOR", "10:22 AM",
    "The paper is brittle. You catch fragments: “...reward... safe return...”\nand a faded crest—three intersecting rings.", false, page);

  txt("WHAT DO YOU DO?", 494, 497, 11, "bold", page);
  rule(330, 507, 165, page);
  rule(595, 507, 173, page);
  createChoice(330, 522, "✥", "Follow the lane left toward the market square.", "1", page);
  createChoice(330, 558, "♟", "Head right toward the old watchhouse.", "2", page);
  createChoice(330, 594, "♟", "Search the area for anything unusual.", "3", page);
  createChoice(330, 630, "⊕", "Or write your own action...", "✎", page);

  img("panel-note.png", 298, 677, 500, 112, "", page, { opacity: "0.58" });
  img("icon-book.png", 339, 711, 44, 34, "ink-asset", page);
  txt("SCENE SUMMARY", 407, 700, 10, "bold", page);
  txt(
    "You stand at a foggy crossroads in the old quarter. A torn poster hints\n" +
      "at a missing person and a mysterious order. The watchhouse may hold\n" +
      "answers, but the market could reveal other leads.",
    407, 721, 11, "", page, { lineHeight: "1.38" },
  );

  createControl(290, 807, 38, "✥", page);
  createControl(336, 807, 68, "●  Auto", page);
  createControl(413, 807, 164, "Narrative Style    Balanced", page);
  createControl(588, 807, 142, "Memory Use    Medium", page);
  createControl(739, 807, 38, "☷", page);
}

function createRelationshipGraph(parent) {
  panel(1143, 112, 274, 181, parent);
  const connections = [
    [1277, 160, 1194, 210, "#476f5d"],
    [1277, 160, 1364, 210, "#a8752e"],
    [1194, 210, 1277, 257, "#625476"],
    [1364, 210, 1277, 257, "#625476"],
  ];
  connections.forEach(([x1, y1, x2, y2, color]) => {
    const length = Math.hypot(x2 - x1, y2 - y1);
    const angle = Math.atan2(y2 - y1, x2 - x1) * 180 / Math.PI;
    box("relationship-line", x1, y1, length, 2, parent).style.cssText +=
      `;transform:rotate(${angle}deg);background:${color};opacity:.8`;
  });
  const nodes = [
    [1277, 150, 62, "icon-character.png", "Evelyn", ""],
    [1194, 205, 51, "icon-character.png", "Silas", "Ally"],
    [1364, 205, 51, "icon-character.png", "Vera", "Contact"],
    [1277, 253, 46, "icon-event.png", "The Lantern Order", "Unknown"],
  ];
  nodes.forEach(([x, y, size, icon, name, role]) => {
    const node = box("relationship-node", x - size / 2, y - size / 2, size, size, parent);
    node.innerHTML = `<img src="${A}${icon}" alt="">`;
    txt(name, x, y + size / 2 + 6, 9, "bold", parent, { transform: "translateX(-50%)", textAlign: "center" });
    if (role) txt(role, x, y + size / 2 + 19, 8, "muted", parent, { transform: "translateX(-50%)", textAlign: "center" });
  });
}

function createInfoCard(parent, x, y, w, h, title, icon, body) {
  panel(x, y, w, h, parent);
  img(icon, x + 10, y + 11, 16, 16, "ink-asset", parent);
  txt(title, x + 31, y + 14, 10, "bold", parent);
  txt(body, x + 12, y + 48, 9, "", parent, { lineHeight: "1.48" });
  txt("3 LORES", x + 12, y + h - 22, 8, "bold", parent, { color: "#5e456d" });
  txt("→", x + w - 20, y + h - 25, 12, "bold", parent, { color: "#5e456d" });
}

function createLiveRightPage() {
  const page = el("section", "page-content right-content", {}, stage);
  txt("CHARACTER PROFILE", 879, 91, 10, "bold", page);
  txt("RELATIONSHIPS", 1155, 91, 10, "bold", page);
  rule(877, 107, 245, page);
  rule(1153, 107, 255, page);

  panel(871, 112, 262, 181, page);
  box("portrait-frame", 881, 125, 76, 76, page);
  img("icon-character.png", 890, 134, 57, 57, "ink-asset", page);
  txt("Evelyn Marlowe", 970, 120, 17, "bold", page);
  txt("Investigator", 970, 148, 11, "muted", page);
  txt("Level 3", 970, 170, 12, "", page);
  box("xp-back", 970, 188, 143, 7, page);
  box("xp-value", 970, 188, 50, 7, page);
  txt("XP 1,240 / 2,000", 1018, 202, 9, "muted", page);
  [["♣  3", "Mind"], ["♟  2", "Body"], ["♥  4", "Charm"], ["◉  2", "Will"]].forEach(([value, label], i) => {
    txt(value, 895 + i * 58, 236, 13, "bold", page);
    txt(label, 895 + i * 58, 258, 10, "muted", page);
  });
  createRelationshipGraph(page);

  createInfoCard(page, 871, 309, 166, 168, "WORLD LORE", "icon-book.png",
    "The city of Grayhaven was built\non trade and shadow. Power\nshifts between old families, secret\nsocieties, and forgotten gods.");

  panel(1047, 309, 182, 223, page);
  img("icon-location.png", 1058, 320, 13, 20, "ink-asset", page);
  txt("LOCATION", 1076, 325, 10, "bold", page);
  txt("Old Quarter", 1062, 351, 13, "bold", page);
  txt("District of Grayhaven", 1062, 370, 9, "muted", page);
  img("panel-map.png", 1063, 373, 150, 104, "", page, { opacity: "0.75" });
  img("icon-location.png", 1126, 405, 24, 38, "ink-asset", page);
  txt("Atmosphere:  Gloomy", 1062, 485, 9, "", page);
  txt("Danger:  Moderate", 1062, 504, 9, "", page);

  panel(1240, 309, 187, 223, page);
  img("icon-key.png", 1252, 320, 10, 17, "ink-asset", page);
  txt("MEMORIES", 1272, 325, 10, "bold", page);
  txt("Torn Poster", 1272, 355, 11, "bold", page);
  txt("Fragments of a reward\nnotice with a strange crest.", 1272, 374, 9, "", page);
  rule(1256, 416, 154, page);
  img("icon-eye.png", 1251, 434, 15, 15, "ink-asset", page);
  txt("Watcher in the Dark", 1272, 430, 11, "bold", page);
  txt("A figure observed on\nthe rooftops.", 1272, 449, 9, "", page);
  rule(1256, 488, 154, page);
  txt("VIEW ALL (8)", 1257, 504, 9, "bold", page, { color: "#4d315f" });
  txt("→", 1398, 504, 13, "", page, { color: "#4d315f" });

  panel(872, 515, 166, 239, page);
  txt("ACTIVE THREADS", 903, 531, 10, "bold", page);
  [
    ["#2775b7", "Find the Missing", "Learn who is behind\nthe abductions."],
    ["#68477d", "The Lantern Order", "Uncover the purpose\nof the secret society."],
    ["#b57c1c", "Debt to Be Paid", "Someone wants\nwhat you owe."],
  ].forEach(([color, title, body], i) => {
    box("thread-dot", 883, 563 + i * 62, 10, 10, page).style.background = color;
    txt(title, 898, 560 + i * 62, 9, "bold", page);
    txt(body, 898, 578 + i * 62, 8, "", page);
  });
  rule(884, 720, 140, page);
  txt("+  NEW THREAD", 884, 732, 8, "bold", page, { color: "#52714c" });

  panel(1049, 547, 195, 207, page);
  txt("TIMELINE", 1080, 563, 10, "bold", page);
  rule(1076, 607, 140, page);
  [1076, 1146, 1216].forEach((x, i) => box(`timeline-dot${i === 2 ? " active" : ""}`, x - 8, 599, 16, 16, page));
  ["Scene 10", "Scene 11", "Scene 12"].forEach((value, i) => txt(value, 1062 + i * 68, 625, 8, "bold", page, i === 2 ? { color: "#334d76" } : {}));
  txt("You noticed a\nwatcher.", 1062, 642, 7, "", page);
  txt("Met Vera at\nthe ink-stained\ntavern.", 1129, 642, 7, "", page);
  txt("Found the\ntorn poster.", 1199, 642, 7, "", page);
  rule(1062, 704, 168, page);
  txt("VIEW FULL TIMELINE", 1062, 718, 8, "bold", page, { color: "#4d315f" });

  panel(1256, 547, 171, 207, page);
  txt("AGENDA & TRIGGERS", 1286, 563, 10, "bold", page);
  img("icon-eye.png", 1264, 593, 14, 14, "ink-asset", page);
  txt("If you visit the watchhouse,\nSilas may have information.", 1290, 587, 8, "", page);
  txt("High Priority", 1290, 624, 7, "bold", page, { color: "#a46a2e" });
  rule(1270, 648, 142, page);
  img("icon-moon.png", 1266, 665, 14, 15, "ink-asset", page);
  txt("The Lantern Order monitors\nstrangers after curfew.", 1290, 660, 8, "", page);
  txt("Night Trigger", 1290, 697, 7, "bold", page, { color: "#69517a" });
  rule(1270, 716, 142, page);
  txt("VIEW ALL (5)", 1270, 729, 8, "bold", page, { color: "#4d315f" });

  txt("NOTES", 883, 775, 9, "bold", page);
  [
    [871, 774, -3, "#eee5d3", "The crest—three\nintersecting rings.\nSeen before..."],
    [1013, 774, 2, "#f4e5a7", "Ask around about the\nreward. Check with\nthe printing house?"],
    [1155, 774, -1, "#d7d2c8", "Watch the rooftops.\nSomeone doesn't want\nto be seen."],
  ].forEach(([x, y, angle, color, body]) => {
    const note = box("note", x, y, 118, 75, page);
    note.style.background = color;
    note.style.transform = `rotate(${angle}deg)`;
    note.textContent = body;
  });
  panel(1336, 774, 74, 75, page, "note-add");
  txt("+", 1364, 797, 20, "muted", page);
  return page;
}

function createArchivePage() {
  const page = el("section", "page-content archive-content hidden");
  txt("CASE ARCHIVE", 884, 92, 12, "bold", page);
  txt("PAGE 02", 1328, 93, 9, "muted", page);
  rule(880, 113, 520, page);
  [
    [870, 138, "panel-seal-note.png", "icon-seal.png", "THE LANTERN ORDER", "Three intersecting rings recur across\nold notices and sealed records."],
    [1150, 138, "panel-aged.png", "icon-network.png", "KNOWN CONTACTS", "Silas knows the rooftops.\nVera watches the market."],
    [870, 432, "panel-map.png", "icon-map.png", "GRAYHAVEN ROUTES", "Market square  •  Watchhouse\nOld quarter  •  River gate"],
    [1150, 432, "panel-note.png", "icon-quill.png", "OPEN QUESTIONS", "Who tore down the poster?\nWhy was the crest burned?"],
  ].forEach(([x, y, bg, icon, title, body]) => {
    img(bg, x, y, 260, 255, "", page, { opacity: "0.76" });
    img(icon, x + 109, y + 20, 42, 42, "ink-asset", page);
    txt(title, x + 130, y + 80, 12, "bold", page, { transform: "translateX(-50%)", textAlign: "center" });
    txt(body, x + 40, y + 110, 11, "", page, { lineHeight: "1.6" });
  });
  txt("Turn the page to return to the live scene.", 1093, 745, 10, "italic muted", page, { transform: "translateX(-50%)" });
  return page;
}

function createPageTurn(livePage, archivePage) {
  const shadow = box("turn-shadow", 831, 63, 30, 790);
  const turnPage = box("turn-page", 831, 52, 610, 812);
  const corner = el("button", "page-corner");
  corner.setAttribute("aria-label", "Turn page");

  corner.addEventListener("click", () => {
    if (isTurning) return;
    isTurning = true;
    turnPage.className = "turn-page turning-in";
    shadow.className = "turn-shadow turning-in";
    setTimeout(() => {
      pageIndex = pageIndex === 0 ? 1 : 0;
      livePage.classList.toggle("hidden", pageIndex !== 0);
      archivePage.classList.toggle("hidden", pageIndex !== 1);
      turnPage.className = "turn-page turning-out";
      shadow.className = "turn-shadow turning-out";
      setTimeout(() => {
        turnPage.className = "turn-page";
        shadow.className = "turn-shadow";
        isTurning = false;
      }, 440);
    }, 360);
  });
}

function createTopControls() {
  createControl(705, 84, 28, "☼", stage);
  createControl(738, 84, 28, "◐", stage);
  createControl(771, 84, 28, "⋯", stage);
}

function init() {
  createDesk();
  createBook();
  createNavigation();
  createLeftPage();
  const live = createLiveRightPage();
  const archive = createArchivePage();
  createPageTurn(live, archive);
  createTopControls();
  const toast = el("div", "toast");
  toast.id = "toast";
  resize();
}

window.addEventListener("resize", resize);
init();
