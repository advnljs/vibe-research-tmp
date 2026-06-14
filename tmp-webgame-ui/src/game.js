const DESIGN_WIDTH = 1672;
const DESIGN_HEIGHT = 941;

const NAVIGATION_HOTSPOTS = [
  ["world", 98, 96, 146, 72, "World"],
  ["characters", 96, 177, 146, 72, "Characters"],
  ["memories", 91, 258, 151, 73, "Memories"],
  ["events", 87, 338, 153, 74, "Events"],
  ["map", 83, 419, 156, 74, "Map"],
  ["threads", 78, 501, 159, 73, "Threads"],
  ["logs", 75, 582, 161, 74, "Logs"],
];

const CHOICE_HOTSPOTS = [
  ["choice-1", 318, 523, 442, 32, "Follow the lane left toward the market square."],
  ["choice-2", 318, 558, 442, 32, "Head right toward the old watchhouse."],
  ["choice-3", 318, 593, 442, 32, "Search the area for anything unusual."],
  ["choice-custom", 318, 628, 442, 32, "Write your own action..."],
];

const CARD_HOTSPOTS = [
  ["world-lore", 871, 309, 166, 168, "World lore"],
  ["location", 1047, 309, 182, 223, "Old Quarter"],
  ["memories-card", 1240, 309, 187, 223, "Memories"],
  ["active-threads", 872, 515, 166, 240, "Active threads"],
  ["timeline", 1049, 547, 195, 207, "Timeline"],
  ["agenda", 1256, 547, 171, 207, "Agenda and triggers"],
  ["relationship-silas", 1157, 171, 55, 55, "Silas"],
  ["relationship-evelyn", 1245, 108, 61, 61, "Evelyn"],
  ["relationship-vera", 1344, 171, 55, 55, "Vera"],
  ["relationship-order", 1249, 226, 50, 50, "The Lantern Order"],
];

const CONTROL_HOTSPOTS = [
  ["settings", 278, 807, 38, 36, "Settings"],
  ["auto", 325, 807, 68, 36, "Auto mode"],
  ["narrative-style", 403, 807, 162, 36, "Narrative style: Balanced"],
  ["memory-use", 577, 807, 146, 36, "Memory use: Medium"],
  ["tuning", 731, 807, 39, 36, "Advanced controls"],
  ["theme", 698, 84, 55, 25, "Theme controls"],
  ["more", 759, 84, 25, 25, "More options"],
];

class WhispersScene extends Phaser.Scene {
  constructor() {
    super("WhispersScene");
    this.selectedChoice = null;
  }

  create() {
    const stage = this.game.canvas.parentElement;
    stage.style.backgroundImage = 'url("./ui-proto.png")';
    stage.style.backgroundPosition = "center";
    stage.style.backgroundRepeat = "no-repeat";
    stage.style.backgroundSize = "contain";

    for (const hotspot of NAVIGATION_HOTSPOTS) this.createHotspot(hotspot);
    for (const hotspot of CARD_HOTSPOTS) this.createHotspot(hotspot);
    for (const hotspot of CONTROL_HOTSPOTS) this.createHotspot(hotspot);
    for (const hotspot of CHOICE_HOTSPOTS) {
      this.createHotspot(hotspot, () => this.selectChoice(hotspot[0]));
    }
  }

  createHotspot([id, x, y, width, height, label], onActivate) {
    const zone = this.add
      .zone(x, y, width, height)
      .setOrigin(0)
      .setName(id)
      .setInteractive({ useHandCursor: true });
    const highlight = this.add
      .rectangle(x, y, width, height, 0xf4d898, 0)
      .setOrigin(0)
      .setStrokeStyle(1, 0xffebb8, 0)
      .setName(`${id}-highlight`);

    zone.on("pointerover", () => {
      highlight.setFillStyle(0xf4d898, 0.13);
      highlight.setStrokeStyle(1, 0xffebb8, 0.48);
    });
    zone.on("pointerout", () => {
      if (this.selectedChoice !== id) {
        highlight.setFillStyle(0xf4d898, 0);
        highlight.setStrokeStyle(1, 0xffebb8, 0);
      }
    });
    zone.on("pointerdown", () => {
      onActivate?.();
      this.showToast(label);
    });
  }

  selectChoice(id) {
    if (this.selectedChoice) {
      const previous = this.children.getByName(`${this.selectedChoice}-highlight`);
      previous?.setFillStyle(0xf4d898, 0).setStrokeStyle(1, 0xffebb8, 0);
    }
    this.selectedChoice = id;
    this.children
      .getByName(`${id}-highlight`)
      ?.setFillStyle(0xa17434, 0.18)
      .setStrokeStyle(1, 0xffebb8, 0.48);
  }

  showToast(message) {
    this.toastContainer?.destroy();

    const toastText = this.add
      .text(0, 0, message, {
        fontFamily: "Georgia, serif",
        fontSize: "14px",
        color: "#f1dfbd",
      })
      .setOrigin(0.5);
    const width = Phaser.Math.Clamp(toastText.width + 40, 120, 360);
    const toastBackground = this.add
      .rectangle(0, 0, width, 34, 0x18110c, 0.88)
      .setStrokeStyle(1, 0xcca360, 0.72);

    this.toastContainer = this.add.container(DESIGN_WIDTH / 2, DESIGN_HEIGHT - 37, [
      toastBackground,
      toastText,
    ]);
    this.tweens.add({
      targets: this.toastContainer,
      alpha: 0,
      delay: 1200,
      duration: 600,
      onComplete: () => {
        this.toastContainer?.destroy();
        this.toastContainer = null;
      },
    });
  }
}

new Phaser.Game({
  type: Phaser.CANVAS,
  parent: "game",
  width: DESIGN_WIDTH,
  height: DESIGN_HEIGHT,
  transparent: true,
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
