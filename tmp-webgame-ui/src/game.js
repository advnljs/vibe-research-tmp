const DESIGN_WIDTH = 1672;
const DESIGN_HEIGHT = 941;
const PAPER = 0xeadcc1;
const INK = "#30271f";
const MUTED_INK = "#6d5c49";
const LINE = 0x8b7357;

const ASSETS = {
  paper: "paper-texture.png",
  leather: "leather-texture.png",
  wood: "wood-texture.png",
  navWorld: "nav-world.png",
  navCharacters: "nav-characters.png",
  navMemories: "nav-memories.png",
  navEvents: "nav-events.png",
  navMap: "nav-map.png",
  navThreads: "nav-threads.png",
  panelAged: "panel-aged.png",
  panelMap: "panel-map.png",
  panelNote: "panel-note.png",
  panelSealNote: "panel-seal-note.png",
  corner: "corner-ornament.png",
  iconWorld: "icon-world.png",
  iconCharacter: "icon-character.png",
  iconEvent: "icon-event.png",
  iconMap: "icon-map.png",
  iconNetwork: "icon-network.png",
  iconLocation: "icon-location.png",
  iconEye: "icon-eye.png",
  iconKey: "icon-key.png",
  iconMoon: "icon-moon.png",
  iconBook: "icon-book.png",
  iconQuill: "icon-quill.png",
  iconSeal: "icon-seal.png",
  medallionCompass: "medallion-compass.png",
};

const NAV_ITEMS = [
  ["navWorld", "WORLD", 103],
  ["navCharacters", "CHARACTERS", 181],
  ["navMemories", "MEMORIES", 259],
  ["navEvents", "EVENTS", 337],
  ["navMap", "MAP", 415],
  ["navThreads", "THREADS", 493],
];

class WhispersScene extends Phaser.Scene {
  constructor() {
    super("WhispersScene");
    this.pageIndex = 0;
    this.isTurning = false;
    this.selectedChoice = null;
  }

  preload() {
    for (const [key, file] of Object.entries(ASSETS)) {
      this.load.image(key, `./assets/generated/${file}`);
    }
  }

  create() {
    this.cameras.main.setBackgroundColor("#160f0a");
    this.createDesk();
    this.createBook();
    this.createNavigation();
    this.createLeftPage();
    this.rightPage = this.createRightPage();
    this.archivePage = this.createArchivePage().setVisible(false);
    this.createPageTurnInteraction();
    this.createTopControls();
  }

  createDesk() {
    this.add.tileSprite(0, 0, DESIGN_WIDTH, DESIGN_HEIGHT, "wood").setOrigin(0);
    this.add.rectangle(0, 0, DESIGN_WIDTH, DESIGN_HEIGHT, 0x0c0704, 0.18).setOrigin(0);

    this.add
      .image(65, 62, "medallionCompass")
      .setScale(0.95)
      .setAngle(-18)
      .setAlpha(0.88);
    this.add
      .image(1585, 825, "iconKey")
      .setScale(0.56)
      .setAngle(50)
      .setAlpha(0.78);
    this.add
      .image(1560, 170, "iconQuill")
      .setScale(0.65)
      .setAngle(30)
      .setAlpha(0.78);
    this.add
      .image(75, 775, "iconMap")
      .setScale(0.7)
      .setAngle(-18)
      .setAlpha(0.45);

    const vignette = this.add.graphics();
    vignette.fillStyle(0x050302, 0.25);
    vignette.fillRect(0, 0, DESIGN_WIDTH, 28);
    vignette.fillRect(0, DESIGN_HEIGHT - 28, DESIGN_WIDTH, 28);
    vignette.fillRect(0, 0, 28, DESIGN_HEIGHT);
    vignette.fillRect(DESIGN_WIDTH - 28, 0, 28, DESIGN_HEIGHT);
  }

  createBook() {
    this.softShadow(190, 52, 1320, 830, 32, 14, 18, 0.34);

    this.add
      .image(850, 475, "leather")
      .setDisplaySize(1360, 865)
      .setTint(0x6e4428)
      .setAlpha(0.95);
    const coverBorder = this.add.graphics();
    coverBorder.lineStyle(4, 0x3a2417, 0.95);
    coverBorder.strokeRoundedRect(176, 38, 1350, 858, 35);
    coverBorder.lineStyle(2, 0xb27c3d, 0.45);
    coverBorder.strokeRoundedRect(187, 49, 1328, 836, 30);

    for (let i = 0; i < 7; i += 1) {
      const edge = this.add.graphics();
      edge.fillStyle(i % 2 ? 0xb9a783 : 0xd8c8a8, 0.98);
      edge.fillRoundedRect(218 + i, 61 + i * 2, 1239 - i * 2, 808, 25);
    }

    this.addPaperPage(230, 46, 602, 824, false);
    this.addPaperPage(831, 46, 610, 824, true);

    const crease = this.add.graphics();
    crease.fillStyle(0x4a3320, 0.08);
    crease.fillRect(817, 62, 8, 790);
    crease.fillStyle(0x2d1b10, 0.16);
    crease.fillRect(825, 62, 7, 790);
    crease.fillStyle(0xffffff, 0.1);
    crease.fillRect(832, 64, 5, 784);

    this.add
      .image(278, 82, "corner")
      .setOrigin(0)
      .setDisplaySize(57, 56)
      .setAlpha(0.5);
    this.add
      .image(1393, 82, "corner")
      .setOrigin(0)
      .setDisplaySize(57, 56)
      .setFlipX(true)
      .setAlpha(0.5);

    this.text(795, 845, "12", 10, MUTED_INK).setOrigin(0.5);
    this.text(868, 845, "13", 10, MUTED_INK).setOrigin(0.5);
  }

  addPaperPage(x, y, width, height, rightPage) {
    this.softShadow(x, y, width, height, 24, rightPage ? 9 : -5, 10, 0.24);
    const maskShape = this.make.graphics({ add: false });
    maskShape.fillStyle(0xffffff);
    maskShape.fillRoundedRect(x, y, width, height, 22);
    const mask = maskShape.createGeometryMask();

    this.add
      .tileSprite(x, y, width, height, "paper")
      .setOrigin(0)
      .setTint(rightPage ? 0xf3ead8 : 0xeee2ca)
      .setMask(mask);

    const pageShade = this.add.graphics();
    pageShade.fillStyle(rightPage ? 0x6f5136 : 0x7c5c3d, 0.055);
    pageShade.fillRoundedRect(x, y, width, height, 22);
    pageShade.lineStyle(1, 0x887256, 0.55);
    pageShade.strokeRoundedRect(x + 1, y + 1, width - 2, height - 2, 22);
    pageShade.lineStyle(1, 0xffffff, 0.24);
    pageShade.strokeRoundedRect(x + 8, y + 7, width - 16, height - 14, 18);
  }

  createNavigation() {
    for (const [texture, label, y] of NAV_ITEMS) {
      const button = this.add
        .image(182, y + 30, texture)
        .setDisplaySize(150, 60)
        .setInteractive({ useHandCursor: true });
      button.on("pointerover", () => button.setScale(button.scaleX * 1.035, button.scaleY * 1.035));
      button.on("pointerout", () => button.setDisplaySize(150, 60));
      button.on("pointerdown", () => this.showToast(`${label} opened`));
      this.text(182, y + 43, label, 10, "#f2dfb8", "bold").setOrigin(0.5);
    }

    const logs = this.add
      .image(182, 604, "navThreads")
      .setDisplaySize(150, 58)
      .setInteractive({ useHandCursor: true });
    logs.on("pointerdown", () => this.showToast("LOGS opened"));
    this.add.image(182, 594, "iconQuill").setDisplaySize(17, 26).setTint(0xf0dfbd);
    this.text(182, 614, "LOGS", 10, "#f2dfb8", "bold").setOrigin(0.5);
  }

  createLeftPage() {
    this.text(338, 90, "CURRENT SCENE", 10, INK, "bold");
    this.text(338, 110, "Whispers in the Fog", 18, INK, "bold");
    this.text(522, 116, "◆  Scene 12", 10, MUTED_INK);
    this.rule(338, 139, 420);

    this.text(
      338,
      154,
      "A cold mist curls through the cobblestone alleys, swallowing the gaslight\n" +
        "in a pale hush. The tower clock tolls once in the distance. Somewhere\n" +
        "above, a shutter opens... then closes.",
      13,
      INK,
      "normal",
      435,
      5,
    );
    this.text(
      338,
      219,
      "Ahead, the narrow lane forks—left toward the market square,\n" +
        "right toward the old watchhouse. A torn poster flutters against\n" +
        "the wall, half-burned, the name illegible.",
      13,
      INK,
      "normal",
      435,
      5,
    );

    this.messageBox(330, 290, 438, 61, "iconWorld", "NARRATOR", "10:21 AM", [
      "The air smells of damp stone and smoke. Your boots splash lightly",
      "in a shallow puddle. A stray dog watches you from the shadows.",
    ]);
    this.messageBox(330, 362, 438, 48, "iconCharacter", "YOU", "10:21 AM", [
      "I step closer to the poster and try to read what I can.",
    ], 0xd2ddd8);
    this.messageBox(330, 421, 438, 61, "iconWorld", "NARRATOR", "10:22 AM", [
      "The paper is brittle. You catch fragments: “...reward... safe return...”",
      "and a faded crest—three intersecting rings.",
    ]);

    this.text(545, 501, "WHAT DO YOU DO?", 11, INK, "bold").setOrigin(0.5);
    this.rule(330, 507, 165);
    this.rule(595, 507, 173);

    this.choice(330, 522, "✥", "Follow the lane left toward the market square.", "1");
    this.choice(330, 558, "♟", "Head right toward the old watchhouse.", "2");
    this.choice(330, 594, "♟", "Search the area for anything unusual.", "3");
    this.choice(330, 630, "⊕", "Or write your own action...", "✎");

    this.add.image(548, 733, "panelNote").setDisplaySize(500, 112).setAlpha(0.58);
    this.add.image(361, 728, "iconBook").setDisplaySize(44, 34).setTint(0x33291f);
    this.text(407, 700, "SCENE SUMMARY", 10, INK, "bold");
    this.text(
      407,
      721,
      "You stand at a foggy crossroads in the old quarter. A torn poster hints\n" +
        "at a missing person and a mysterious order. The watchhouse may hold\n" +
        "answers, but the market could reveal other leads.",
      11,
      INK,
      "normal",
      350,
      4,
    );

    this.smallControl(290, 807, 38, "✥");
    this.smallControl(336, 807, 68, "●  Auto");
    this.smallControl(413, 807, 164, "Narrative Style    Balanced");
    this.smallControl(588, 807, 142, "Memory Use    Medium");
    this.smallControl(739, 807, 38, "☷");
  }

  createRightPage() {
    const container = this.add.container(0, 0);

    this.cText(container, 879, 91, "CHARACTER PROFILE", 10, INK, "bold");
    this.cText(container, 1155, 91, "RELATIONSHIPS", 10, INK, "bold");
    this.cRule(container, 877, 107, 245);
    this.cRule(container, 1153, 107, 255);

    this.cPanel(container, 871, 112, 262, 181);
    const portraitFrame = this.add
      .rectangle(919, 163, 76, 76, 0x31261d, 0.96)
      .setStrokeStyle(2, 0x9b7d50, 0.82);
    const portrait = this.add.image(919, 163, "iconCharacter").setDisplaySize(57, 57).setTint(0x2f251d);
    container.add([portraitFrame, portrait]);
    this.cText(container, 970, 120, "Evelyn Marlowe", 17, INK, "bold");
    this.cText(container, 970, 148, "Investigator", 11, MUTED_INK);
    this.cText(container, 970, 170, "Level 3", 12, INK);
    const xpBack = this.add.rectangle(970, 188, 143, 7, 0xb9aa90, 0.75).setOrigin(0);
    const xp = this.add.rectangle(970, 188, 50, 7, 0x9d6a28, 0.95).setOrigin(0);
    container.add([xpBack, xp]);
    this.cText(container, 1018, 202, "XP 1,240 / 2,000", 9, MUTED_INK);
    const stats = [
      ["♣", "3", "Mind"],
      ["♟", "2", "Body"],
      ["♥", "4", "Charm"],
      ["◉", "2", "Will"],
    ];
    stats.forEach(([icon, value, name], index) => {
      const x = 895 + index * 58;
      this.cText(container, x, 236, `${icon}  ${value}`, 13, INK, "bold");
      this.cText(container, x, 258, name, 10, MUTED_INK);
    });

    this.relationshipGraph(container);

    this.infoCard(container, 871, 309, 166, 168, "WORLD LORE", "iconBook", [
      "The city of Grayhaven was built",
      "on trade and shadow. Power",
      "shifts between old families, secret",
      "societies, and forgotten gods.",
    ]);

    this.cPanel(container, 1047, 309, 182, 223);
    this.cText(container, 1076, 325, "LOCATION", 10, INK, "bold");
    container.add(this.add.image(1065, 330, "iconLocation").setDisplaySize(13, 20).setTint(0x43372b));
    this.cText(container, 1062, 351, "Old Quarter", 13, INK, "bold");
    this.cText(container, 1062, 370, "District of Grayhaven", 9, MUTED_INK);
    container.add(this.add.image(1138, 425, "panelMap").setDisplaySize(150, 104).setAlpha(0.75));
    container.add(this.add.image(1138, 424, "iconLocation").setDisplaySize(24, 38).setTint(0x2b2118));
    this.cText(container, 1062, 485, "Atmosphere:  Gloomy", 9, INK);
    this.cText(container, 1062, 504, "Danger:  Moderate", 9, INK);

    this.memoryCard(container);
    this.threadCard(container);
    this.timelineCard(container);
    this.agendaCard(container);
    this.notes(container);
    return container;
  }

  createArchivePage() {
    const container = this.add.container(0, 0);
    this.cText(container, 884, 92, "CASE ARCHIVE", 12, INK, "bold");
    this.cText(container, 1328, 93, "PAGE 02", 9, MUTED_INK);
    this.cRule(container, 880, 113, 520);

    container.add(this.add.image(1000, 266, "panelSealNote").setDisplaySize(260, 255).setAlpha(0.78));
    container.add(this.add.image(1280, 266, "panelAged").setDisplaySize(260, 255).setAlpha(0.72));
    container.add(this.add.image(1000, 560, "panelMap").setDisplaySize(260, 255).setAlpha(0.7));
    container.add(this.add.image(1280, 560, "panelNote").setDisplaySize(260, 255).setAlpha(0.72));

    container.add(this.add.image(1000, 180, "iconSeal").setDisplaySize(42, 42).setTint(0x7a3827));
    this.cText(container, 925, 217, "THE LANTERN ORDER", 12, INK, "bold");
    this.cText(container, 911, 242, "Three intersecting rings recur across\nold notices and sealed records.", 11, INK, "normal", 180, 5);

    container.add(this.add.image(1280, 180, "iconNetwork").setDisplaySize(52, 44).setTint(0x3a3025));
    this.cText(container, 1211, 217, "KNOWN CONTACTS", 12, INK, "bold");
    this.cText(container, 1194, 242, "Silas knows the rooftops.\nVera watches the market.", 11, INK, "normal", 180, 5);

    container.add(this.add.image(1000, 485, "iconMap").setDisplaySize(56, 44).setTint(0x45382b));
    this.cText(container, 936, 519, "GRAYHAVEN ROUTES", 12, INK, "bold");
    this.cText(container, 905, 545, "Market square  •  Watchhouse\nOld quarter  •  River gate", 11, INK, "normal", 190, 5);

    container.add(this.add.image(1280, 485, "iconQuill").setDisplaySize(34, 52).setTint(0x45382b));
    this.cText(container, 1228, 519, "OPEN QUESTIONS", 12, INK, "bold");
    this.cText(container, 1194, 545, "Who tore down the poster?\nWhy was the crest burned?", 11, INK, "normal", 180, 5);

    this.cText(container, 1093, 745, "Turn the page to return to the live scene.", 10, MUTED_INK, "italic").setOrigin(0.5);
    return container;
  }

  relationshipGraph(container) {
    this.cPanel(container, 1143, 112, 274, 181);
    const lines = this.add.graphics();
    lines.lineStyle(1.5, 0x476f5d, 0.8);
    lines.lineBetween(1277, 160, 1194, 210);
    lines.lineStyle(1.5, 0xa8752e, 0.8);
    lines.lineBetween(1277, 160, 1364, 210);
    lines.lineStyle(1.2, 0x625476, 0.75);
    lines.lineBetween(1194, 210, 1277, 257);
    lines.lineBetween(1364, 210, 1277, 257);
    container.add(lines);

    const nodes = [
      [1277, 150, "iconCharacter", 54, "Evelyn", ""],
      [1194, 205, "iconCharacter", 43, "Silas", "Ally"],
      [1364, 205, "iconCharacter", 43, "Vera", "Contact"],
      [1277, 253, "iconEvent", 38, "The Lantern Order", "Unknown"],
    ];
    nodes.forEach(([x, y, key, size, name, role]) => {
      container.add(this.add.circle(x, y, size / 2 + 4, 0xd9c7a5, 1).setStrokeStyle(2, 0x3b3024, 0.9));
      container.add(this.add.image(x, y, key).setDisplaySize(size, size).setTint(0x30271f));
      this.cText(container, x, y + size / 2 + 8, name, 9, INK, "bold").setOrigin(0.5, 0);
      if (role) this.cText(container, x, y + size / 2 + 21, role, 8, MUTED_INK).setOrigin(0.5, 0);
    });
  }

  memoryCard(container) {
    this.cPanel(container, 1240, 309, 187, 223);
    this.cText(container, 1272, 325, "MEMORIES", 10, INK, "bold");
    container.add(this.add.image(1257, 329, "iconKey").setDisplaySize(10, 17).setTint(0x42362a));
    this.cText(container, 1272, 355, "Torn Poster", 11, INK, "bold");
    this.cText(container, 1272, 374, "Fragments of a reward\nnotice with a strange crest.", 9, INK, "normal", 130, 3);
    this.cRule(container, 1256, 416, 154);
    container.add(this.add.image(1258, 441, "iconEye").setDisplaySize(15, 15).setTint(0x42362a));
    this.cText(container, 1272, 430, "Watcher in the Dark", 11, INK, "bold");
    this.cText(container, 1272, 449, "A figure observed on\nthe rooftops.", 9, INK, "normal", 130, 3);
    this.cRule(container, 1256, 488, 154);
    this.cText(container, 1257, 504, "VIEW ALL (8)", 9, "#4d315f", "bold");
    this.cText(container, 1407, 504, "→", 13, "#4d315f").setOrigin(1, 0);
  }

  threadCard(container) {
    this.cPanel(container, 872, 515, 166, 239);
    this.cText(container, 903, 531, "ACTIVE THREADS", 10, INK, "bold");
    const threads = [
      [0x2775b7, "Find the Missing", "Learn who is behind\nthe abductions."],
      [0x68477d, "The Lantern Order", "Uncover the purpose\nof the secret society."],
      [0xb57c1c, "Debt to Be Paid", "Someone wants\nwhat you owe."],
    ];
    threads.forEach(([color, title, body], index) => {
      const y = 560 + index * 62;
      container.add(this.add.circle(888, y + 8, 5, color));
      this.cText(container, 898, y, title, 9, INK, "bold");
      this.cText(container, 898, y + 18, body, 8, INK, "normal", 125, 2);
    });
    this.cRule(container, 884, 720, 140);
    this.cText(container, 884, 732, "+  NEW THREAD", 8, "#52714c", "bold");
  }

  timelineCard(container) {
    this.cPanel(container, 1049, 547, 195, 207);
    this.cText(container, 1080, 563, "TIMELINE", 10, INK, "bold");
    const line = this.add.graphics();
    line.lineStyle(1.3, 0x655647, 0.75);
    line.lineBetween(1076, 607, 1216, 607);
    container.add(line);
    [1076, 1146, 1216].forEach((x, index) => {
      container.add(this.add.circle(x, 607, 8, 0xe7dcc6).setStrokeStyle(2, index === 2 ? 0x334d76 : 0x625448));
      container.add(this.add.circle(x, 607, 2.5, index === 2 ? 0x334d76 : 0x625448));
    });
    this.cText(container, 1062, 625, "Scene 10", 8, INK, "bold");
    this.cText(container, 1129, 625, "Scene 11", 8, INK, "bold");
    this.cText(container, 1199, 625, "Scene 12", 8, "#334d76", "bold");
    this.cText(container, 1062, 642, "You noticed a\nwatcher.", 7, INK, "normal", 50, 2);
    this.cText(container, 1129, 642, "Met Vera at\nthe ink-stained\ntavern.", 7, INK, "normal", 55, 2);
    this.cText(container, 1199, 642, "Found the\ntorn poster.", 7, INK, "normal", 50, 2);
    this.cRule(container, 1062, 704, 168);
    this.cText(container, 1062, 718, "VIEW FULL TIMELINE", 8, "#4d315f", "bold");
  }

  agendaCard(container) {
    this.cPanel(container, 1256, 547, 171, 207);
    this.cText(container, 1286, 563, "AGENDA & TRIGGERS", 10, INK, "bold");
    container.add(this.add.image(1271, 600, "iconEye").setDisplaySize(14, 14).setTint(0x42362a));
    this.cText(container, 1290, 587, "If you visit the watchhouse,\nSilas may have information.", 8, INK, "normal", 120, 3);
    this.cText(container, 1290, 624, "High Priority", 7, "#a46a2e", "bold");
    this.cRule(container, 1270, 648, 142);
    container.add(this.add.image(1273, 673, "iconMoon").setDisplaySize(14, 15).setTint(0x43305a));
    this.cText(container, 1290, 660, "The Lantern Order monitors\nstrangers after curfew.", 8, INK, "normal", 120, 3);
    this.cText(container, 1290, 697, "Night Trigger", 7, "#69517a", "bold");
    this.cRule(container, 1270, 716, 142);
    this.cText(container, 1270, 729, "VIEW ALL (5)", 8, "#4d315f", "bold");
  }

  notes(container) {
    this.cText(container, 883, 775, "NOTES", 9, INK, "bold");
    const noteData = [
      [930, 811, -3, 0xeee5d3, "The crest—three\nintersecting rings.\nSeen before..."],
      [1072, 811, 2, 0xf4e5a7, "Ask around about the\nreward. Check with\nthe printing house?"],
      [1214, 811, -1, 0xd7d2c8, "Watch the rooftops.\nSomeone doesn't want\nto be seen."],
    ];
    noteData.forEach(([x, y, angle, color, body]) => {
      const note = this.add.rectangle(x, y, 118, 75, color, 0.9).setStrokeStyle(1, 0x8d806c, 0.5).setAngle(angle);
      const pin = this.add.circle(x, y - 31, 4, 0x756b59).setAngle(angle);
      const text = this.text(x - 48, y - 24, body, 8, INK, "normal", 98, 3).setAngle(angle);
      container.add([note, pin, text]);
    });
    const add = this.add.rectangle(1373, 811, 74, 75, 0xd7c8a9, 0.16).setStrokeStyle(1, 0x8d806c, 0.5);
    container.add(add);
    this.cText(container, 1373, 804, "+", 20, MUTED_INK).setOrigin(0.5);
  }

  createPageTurnInteraction() {
    this.turnPage = this.add
      .image(831, 458, "paper")
      .setOrigin(0, 0.5)
      .setDisplaySize(610, 812)
      .setTint(0xf0e4cf)
      .setDepth(80)
      .setVisible(false);
    this.turnShadow = this.add
      .rectangle(831, 458, 30, 790, 0x1b1008, 0)
      .setDepth(79);

    const corner = this.add.graphics().setDepth(40);
    corner.fillStyle(0x8c6f4c, 0.14);
    corner.fillTriangle(1392, 821, 1430, 821, 1430, 783);
    corner.lineStyle(1, 0x7a6044, 0.5);
    corner.lineBetween(1392, 821, 1430, 783);

    const zone = this.add
      .zone(1375, 770, 70, 95)
      .setOrigin(0)
      .setName("page-turn-zone")
      .setInteractive({ useHandCursor: true, draggable: true })
      .setDepth(100);
    zone.on("pointerover", () => corner.setAlpha(1));
    zone.on("pointerout", () => corner.setAlpha(0.7));
    zone.on("pointerdown", () => this.turnPageAnimation());
  }

  turnPageAnimation() {
    if (this.isTurning) return;
    this.isTurning = true;
    this.turnPage
      .setVisible(true)
      .setAlpha(1)
      .setPosition(831, 458)
      .setOrigin(0, 0.5)
      .setDisplaySize(610, 812);
    this.turnShadow.setAlpha(0.05);

    const baseScale = this.turnPage.scaleX;
    this.tweens.add({
      targets: this.turnPage,
      scaleX: baseScale * 0.025,
      duration: 360,
      ease: "Sine.easeIn",
      onUpdate: () => {
        const edge = 831 + this.turnPage.width * this.turnPage.scaleX;
        this.turnShadow.setX(edge).setAlpha(0.26);
      },
      onComplete: () => {
        this.pageIndex = this.pageIndex === 0 ? 1 : 0;
        this.rightPage.setVisible(this.pageIndex === 0);
        this.archivePage.setVisible(this.pageIndex === 1);
        this.tweens.add({
          targets: this.turnPage,
          scaleX: -baseScale,
          alpha: 0.2,
          duration: 430,
          ease: "Sine.easeOut",
          onUpdate: () => {
            const edge = 831 + this.turnPage.width * this.turnPage.scaleX;
            this.turnShadow.setX(edge).setAlpha(Math.max(0.04, this.turnPage.alpha * 0.2));
          },
          onComplete: () => {
            this.turnPage.setVisible(false);
            this.turnShadow.setAlpha(0);
            this.isTurning = false;
          },
        });
      },
    });
  }

  createTopControls() {
    this.smallControl(705, 84, 28, "☼");
    this.smallControl(738, 84, 28, "◐");
    this.smallControl(771, 84, 28, "⋯");
  }

  messageBox(x, y, width, height, icon, speaker, time, lines, fill = 0xe6dbc6) {
    const box = this.add.graphics();
    box.fillStyle(fill, 0.68);
    box.fillRoundedRect(x + 28, y, width - 28, height, 12);
    box.lineStyle(1, LINE, 0.38);
    box.strokeRoundedRect(x + 28, y, width - 28, height, 12);
    this.add.circle(x + 15, y + height / 2, 20, 0xe7dcc8, 0.95).setStrokeStyle(1, 0x6c5841, 0.6);
    this.add.image(x + 15, y + height / 2, icon).setDisplaySize(31, 31).setTint(0x30271f);
    this.text(x + 52, y + 8, speaker, 9, INK, "bold");
    this.text(x + width - 10, y + 8, time, 8, MUTED_INK).setOrigin(1, 0);
    this.text(x + 52, y + 25, lines.join("\n"), 10, INK, "normal", width - 78, 3);
  }

  choice(x, y, icon, label, key) {
    const fill = this.add.graphics();
    fill.fillStyle(0xe8deca, 0.56);
    fill.fillRoundedRect(x, y, 438, 31, 6);
    fill.lineStyle(1, 0x685746, 0.72);
    fill.strokeRoundedRect(x, y, 438, 31, 6);
    this.text(x + 15, y + 7, icon, 12, INK, "bold");
    this.text(x + 39, y + 8, label, 10, INK);
    this.text(x + 423, y + 7, key, 10, INK, "bold").setOrigin(1, 0);
    const zone = this.add.zone(x, y, 438, 31).setOrigin(0).setInteractive({ useHandCursor: true });
    zone.on("pointerover", () => fill.setAlpha(1.25));
    zone.on("pointerout", () => fill.setAlpha(this.selectedChoice === label ? 1.35 : 1));
    zone.on("pointerdown", () => {
      this.selectedChoice = label;
      fill.setAlpha(1.35);
      this.showToast(label);
    });
  }

  infoCard(container, x, y, width, height, title, icon, lines) {
    this.cPanel(container, x, y, width, height);
    container.add(this.add.image(x + 18, y + 19, icon).setDisplaySize(16, 16).setTint(0x42362a));
    this.cText(container, x + 31, y + 14, title, 10, INK, "bold");
    this.cText(container, x + 12, y + 48, lines.join("\n"), 9, INK, "normal", width - 24, 4);
    this.cText(container, x + 12, y + height - 22, "3 LORES", 8, "#5e456d", "bold");
    this.cText(container, x + width - 12, y + height - 24, "→", 12, "#5e456d").setOrigin(1, 0);
  }

  cPanel(container, x, y, width, height) {
    const panel = this.add.graphics();
    panel.fillStyle(PAPER, 0.37);
    panel.fillRoundedRect(x, y, width, height, 7);
    panel.lineStyle(1, LINE, 0.45);
    panel.strokeRoundedRect(x, y, width, height, 7);
    container.add(panel);
    return panel;
  }

  smallControl(x, y, width, label) {
    const panel = this.add.graphics();
    panel.fillStyle(0xe9ddc7, 0.56);
    panel.fillRoundedRect(x, y, width, 34, 5);
    panel.lineStyle(1, 0x826b51, 0.48);
    panel.strokeRoundedRect(x, y, width, 34, 5);
    this.text(x + width / 2, y + 10, label, 9, INK).setOrigin(0.5, 0);
    const zone = this.add.zone(x, y, width, 34).setOrigin(0).setInteractive({ useHandCursor: true });
    zone.on("pointerover", () => panel.setAlpha(1.25));
    zone.on("pointerout", () => panel.setAlpha(1));
    zone.on("pointerdown", () => this.showToast(label));
  }

  showToast(message) {
    this.toastContainer?.destroy();
    const text = this.text(0, 0, message, 13, "#f0dfbd", "normal").setOrigin(0.5);
    const width = Phaser.Math.Clamp(text.width + 40, 150, 380);
    const back = this.add.rectangle(0, 0, width, 36, 0x1b120b, 0.93).setStrokeStyle(1, 0xc0914d, 0.8);
    this.toastContainer = this.add.container(DESIGN_WIDTH / 2, DESIGN_HEIGHT - 42, [back, text]).setDepth(120);
    this.tweens.add({
      targets: this.toastContainer,
      alpha: 0,
      delay: 1100,
      duration: 500,
      onComplete: () => {
        this.toastContainer?.destroy();
        this.toastContainer = null;
      },
    });
  }

  softShadow(x, y, width, height, radius, dx, dy, alpha) {
    const shadow = this.add.graphics();
    for (let i = 6; i >= 1; i -= 1) {
      shadow.fillStyle(0x080503, (alpha / 6) * (7 - i));
      shadow.fillRoundedRect(x + dx - i * 2, y + dy - i, width + i * 4, height + i * 2, radius + i);
    }
    return shadow;
  }

  text(x, y, value, size, color = INK, style = "normal", width, lineSpacing = 2) {
    return this.add.text(x, y, value, {
      fontFamily: "Georgia, 'Times New Roman', serif",
      fontSize: `${size}px`,
      fontStyle: style === "bold" || style === "italic" ? style : "normal",
      color,
      wordWrap: width ? { width, useAdvancedWrap: true } : undefined,
      lineSpacing,
    });
  }

  rule(x, y, width) {
    const line = this.add.graphics();
    line.lineStyle(1, LINE, 0.4);
    line.lineBetween(x, y, x + width, y);
    return line;
  }

  cText(container, ...args) {
    const object = this.text(...args);
    container.add(object);
    return object;
  }

  cRule(container, ...args) {
    const object = this.rule(...args);
    container.add(object);
    return object;
  }
}

window.whispersGame = new Phaser.Game({
  type: Phaser.CANVAS,
  parent: "game",
  width: DESIGN_WIDTH,
  height: DESIGN_HEIGHT,
  backgroundColor: "#160f0a",
  render: {
    antialias: true,
    pixelArt: false,
    roundPixels: true,
  },
  scale: {
    mode: Phaser.Scale.FIT,
    autoCenter: Phaser.Scale.CENTER_BOTH,
    width: DESIGN_WIDTH,
    height: DESIGN_HEIGHT,
  },
  scene: WhispersScene,
});
