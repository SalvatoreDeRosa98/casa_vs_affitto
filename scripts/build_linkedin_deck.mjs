import {
  Presentation,
  PresentationFile,
  column,
  row,
  grid,
  panel,
  text,
  rule,
  fill,
  hug,
  fixed,
  grow,
  fr,
  wrap,
} from "@oai/artifact-tool";
import { mkdir, writeFile } from "node:fs/promises";

const OUT = "output/linkedin_casa_vs_affitto.pptx";
const SCRATCH = "scratch/linkedin_deck";
const W = 1920;
const H = 1080;

const C = {
  ink: "#111827",
  muted: "#61758A",
  blue: "#0A66C2",
  paleBlue: "#EAF3FF",
  paper: "#FFFFFF",
  bg: "#F3F6F8",
  red: "#D93025",
  green: "#16803C",
  amber: "#F5A623",
  line: "#D9E2EC",
};

const title = {
  fontFace: "Aptos Display",
  fontSize: 70,
  bold: true,
  color: C.ink,
  lineSpacingMultiple: 0.92,
};

const giant = {
  fontFace: "Aptos Display",
  fontSize: 142,
  bold: true,
  color: C.ink,
  lineSpacingMultiple: 0.86,
};

const body = {
  fontFace: "Aptos",
  fontSize: 34,
  color: "#34495E",
  lineSpacingMultiple: 1.08,
};

const label = {
  fontFace: "Aptos",
  fontSize: 22,
  bold: true,
  color: C.blue,
  letterSpacing: 2,
};

const small = {
  fontFace: "Aptos",
  fontSize: 22,
  color: C.muted,
};

const whiteTitle = { ...title, color: C.paper };
const whiteBody = { ...body, color: "#DDEBFA" };

function footer(n) {
  return row(
    { name: `footer-${n}`, width: fill, height: hug, gap: 14 },
    [
      text("citta.", {
        name: `footer-brand-${n}`,
        width: fixed(120),
        height: hug,
        style: { ...small, bold: true, color: C.blue },
      }),
      rule({ name: `footer-rule-${n}`, width: grow(1), stroke: C.line, weight: 1 }),
      text(`${n}/7`, {
        name: `footer-page-${n}`,
        width: fixed(56),
        height: hug,
        style: { ...small, alignment: "right" },
      }),
    ],
  );
}

function chip(textValue, name, color = C.blue) {
  return panel(
    {
      name,
      width: hug,
      height: hug,
      padding: { x: 18, y: 8 },
      fill: color === C.blue ? C.paleBlue : "#FFF3D6",
      borderRadius: 999,
    },
    text(textValue, {
      name: `${name}-text`,
      width: hug,
      height: hug,
      style: { ...label, fontSize: 18, color },
    }),
  );
}

function statBlock(value, caption, name, color = C.blue) {
  return column(
    { name, width: fill, height: hug, gap: 8 },
    [
      text(value, {
        name: `${name}-value`,
        width: fill,
        height: hug,
        style: { ...giant, fontSize: 86, color },
      }),
      text(caption, {
        name: `${name}-caption`,
        width: fill,
        height: hug,
        style: { ...small, fontSize: 24 },
      }),
    ],
  );
}

function addCover(p) {
  const s = p.slides.add();
  s.compose(
    row(
      { name: "cover-root", width: fill, height: fill, padding: 76, gap: 48 },
      [
        column(
          { name: "cover-copy", width: grow(1.08), height: fill, gap: 24 },
          [
            row({ name: "cover-chips", width: fill, height: hug, gap: 12 }, [
              chip("CASA VS AFFITTO", "cover-chip"),
              chip("MODELLO PRUDENTE", "cover-chip-2", C.amber),
            ]),
            column({ name: "cover-title-stack", width: fill, height: hug, gap: 8 }, [
              text("Comprare casa", {
                name: "cover-title-1",
                width: fill,
                height: hug,
                style: { ...giant, fontSize: 96 },
              }),
              text("conviene davvero?", {
                name: "cover-title-2",
                width: fill,
                height: hug,
                style: { ...giant, fontSize: 96 },
              }),
            ]),
            text("Spoiler: la rata bassa non basta. Devi guardare anticipo, capitale investito e costi di uscita.", {
              name: "cover-subtitle",
              width: wrap(790),
              height: hug,
              style: body,
            }),
            rule({ name: "cover-left-rule", width: fixed(250), stroke: C.ink, weight: 8 }),
            footer(1),
          ],
        ),
        panel(
          {
            name: "cover-visual",
            width: grow(0.92),
            height: fill,
            padding: 0,
            fill: C.paleBlue,
            borderRadius: 8,
          },
          column(
            { name: "cover-visual-stack", width: fill, height: fill, padding: 40, gap: 26 },
            [
              text("BREAK-EVEN", {
                name: "cover-visual-label",
                width: fill,
                height: hug,
                style: { ...label, fontSize: 24 },
              }),
              text("non è una data magica", {
                name: "cover-visual-title",
                width: fill,
                height: hug,
                style: { ...title, fontSize: 62 },
              }),
              rule({ name: "cover-visual-rule", width: fill, stroke: C.blue, weight: 8 }),
              statBlock("X anni", "solo se il patrimonio batte affitto + investimento", "cover-stat", C.blue),
              statBlock("X anni", "solo se vendendo recuperi davvero i soldi", "cover-stat-2", C.red),
            ],
          ),
        ),
      ],
    ),
    { frame: { left: 0, top: 0, width: W, height: H }, baseUnit: 8 },
  );
}

function addMyth(p) {
  const s = p.slides.add();
  s.compose(
    column(
      { name: "myth-root", width: fill, height: fill, padding: 76, gap: 30 },
      [
        text("Il calcolo che ci raccontiamo è troppo semplice.", {
          name: "myth-title",
          width: wrap(1260),
          height: hug,
          style: title,
        }),
        row(
          { name: "myth-row", width: fill, height: grow(1), gap: 34 },
          [
            panel(
              { name: "myth-wrong", width: grow(1), height: fill, fill: "#FFEDEC", padding: 38, borderRadius: 8 },
              column({ name: "myth-wrong-stack", width: fill, height: fill, gap: 20 }, [
                text("Versione pigra", { name: "myth-wrong-label", width: fill, height: hug, style: { ...label, color: C.red } }),
                text("Rata mutuo più bassa dell'affitto.", { name: "myth-wrong-main", width: fill, height: hug, style: { ...title, fontSize: 58, color: C.red } }),
                text("Quindi compro.", { name: "myth-wrong-end", width: fill, height: hug, style: { ...body, fontSize: 38 } }),
              ]),
            ),
            panel(
              { name: "myth-right", width: grow(1), height: fill, fill: C.ink, padding: 38, borderRadius: 8 },
              column({ name: "myth-right-stack", width: fill, height: fill, gap: 20 }, [
                text("Versione onesta", { name: "myth-right-label", width: fill, height: hug, style: { ...label, color: C.paper } }),
                text("Quanto resta se vendi?", { name: "myth-right-main", width: fill, height: hug, style: { ...title, fontSize: 58, color: C.paper } }),
                text("E cosa avrebbe fatto il capitale iniziale se fosse stato investito?", { name: "myth-right-end", width: fill, height: hug, style: whiteBody }),
              ]),
            ),
          ],
        ),
        footer(2),
      ],
    ),
    { frame: { left: 0, top: 0, width: W, height: H }, baseUnit: 8 },
  );
}

function addCalculator(p) {
  const s = p.slides.add();
  s.compose(
    row(
      { name: "calc-root", width: fill, height: fill, padding: 76, gap: 44 },
      [
        column(
          { name: "calc-copy", width: grow(0.85), height: fill, gap: 28 },
          [
            text("Abbiamo costruito un calcolatore più prudente.", {
              name: "calc-title",
              width: wrap(720),
              height: hug,
              style: title,
            }),
            text("Non premia automaticamente chi compra. Se la rata è più bassa dell'affitto, quel risparmio non viene reinvestito per magia.", {
              name: "calc-body",
              width: wrap(720),
              height: hug,
              style: body,
            }),
            column({ name: "calc-points", width: fill, height: hug, gap: 14 }, [
              chip("anticipo investito lato affitto", "calc-chip-1"),
              chip("costo vendita futuro", "calc-chip-2", C.amber),
              chip("manutenzione e costi proprietario", "calc-chip-3"),
            ]),
            footer(3),
          ],
        ),
        panel(
          { name: "app-shot-frame", width: grow(1.15), height: fill, padding: 18, fill: C.paper, borderRadius: 8 },
          column(
            { name: "app-mock", width: fill, height: fill, padding: 30, gap: 20 },
            [
              panel(
                { name: "mock-hero", width: fill, height: fixed(240), padding: 26, fill: C.paleBlue, borderRadius: 8 },
                column({ name: "mock-hero-stack", width: fill, height: fill, gap: 12 }, [
                  text("CASERTA · 2026", { name: "mock-kicker", width: fill, height: hug, style: { ...label, fontSize: 18 } }),
                  text("Compra solo se resti almeno X anni.", { name: "mock-title", width: fill, height: hug, style: { ...title, fontSize: 40 } }),
                  text("Verdetto prudente: include vendita futura e capitale investito.", { name: "mock-sub", width: fill, height: hug, style: { ...small, fontSize: 24 } }),
                ]),
              ),
              grid(
                { name: "mock-metrics", width: fill, height: fixed(180), columns: [fr(1), fr(1), fr(1)], rows: [fr(1)], columnGap: 14 },
                [
                  statBlock("175k", "valore casa", "mock-stat-1", C.blue),
                  statBlock("892", "affitto/mese", "mock-stat-2", C.green),
                  statBlock(">40", "break-even se vendi", "mock-stat-3", C.red),
                ],
              ),
              panel(
                { name: "mock-driver", width: fill, height: grow(1), padding: 28, fill: C.ink, borderRadius: 8 },
                column({ name: "mock-driver-stack", width: fill, height: fill, gap: 18 }, [
                  text("Cosa guida il risultato", { name: "mock-driver-title", width: fill, height: hug, style: { ...label, color: C.paper } }),
                  text("Anticipo alto", { name: "mock-driver-1", width: fill, height: hug, style: { ...whiteTitle, fontSize: 38 } }),
                  text("Rendimento alternativo alto", { name: "mock-driver-2", width: fill, height: hug, style: { ...whiteTitle, fontSize: 38 } }),
                  text("Costo vendita futuro", { name: "mock-driver-3", width: fill, height: hug, style: { ...whiteTitle, fontSize: 38 } }),
                ]),
              ),
            ],
          ),
        ),
      ],
    ),
    { frame: { left: 0, top: 0, width: W, height: H }, baseUnit: 8 },
  );
}

function addCaserta(p) {
  const s = p.slides.add();
  s.compose(
    column(
      { name: "caserta-root", width: fill, height: fill, padding: 76, gap: 30 },
      [
        text("Caso reale: Caserta, aprile 2026.", {
          name: "caserta-title",
          width: fill,
          height: hug,
          style: title,
        }),
        grid(
          { name: "caserta-grid", width: fill, height: grow(1), columns: [fr(1), fr(1), fr(1)], rows: [fr(1)], columnGap: 26 },
          [
            statBlock("1.751", "euro/mq vendita residenziale", "caserta-price", C.blue),
            statBlock("8,92", "euro/mq/mese affitto", "caserta-rent", C.green),
            statBlock("100 mq", "casa: 175.100 euro | affitto: 892 euro/mese", "caserta-size", C.ink),
          ],
        ),
        panel(
          { name: "caserta-note", width: fill, height: hug, padding: { x: 26, y: 18 }, fill: C.paleBlue, borderRadius: 8 },
          text("La domanda non è: pago meno di rata? La domanda è: tra X anni, se vendo, ho davvero battuto affitto + capitale investito?", {
            name: "caserta-note-text",
            width: fill,
            height: hug,
            style: { ...body, fontSize: 32, bold: true, color: C.ink },
          }),
        ),
        footer(4),
      ],
    ),
    { frame: { left: 0, top: 0, width: W, height: H }, baseUnit: 8 },
  );
}

function addDrivers(p) {
  const s = p.slides.add();
  const drivers = [
    ["Anticipo alto", "favorisce affitto + investimento", C.red],
    ["ETF alto", "sposta avanti il break-even", C.red],
    ["Affitto caro", "aiuta l'acquisto", C.green],
    ["Costo vendita", "morde se esci presto", C.red],
    ["Manutenzione", "non è opzionale", C.red],
    ["Rivalutazione", "puo' salvare o affondare", C.amber],
  ];
  s.compose(
    column(
      { name: "drivers-root", width: fill, height: fill, padding: 76, gap: 26 },
      [
        text("Il risultato cambia per motivi precisi.", {
          name: "drivers-title",
          width: fill,
          height: hug,
          style: title,
        }),
        grid(
          { name: "drivers-grid", width: fill, height: grow(1), columns: [fr(1), fr(1), fr(1)], rows: [fr(1), fr(1)], columnGap: 24, rowGap: 24 },
          drivers.map(([a, b, color], i) =>
            panel(
              { name: `driver-${i}`, width: fill, height: fill, padding: 28, fill: i % 2 === 0 ? C.paper : C.paleBlue, borderRadius: 8 },
              column({ name: `driver-stack-${i}`, width: fill, height: fill, gap: 12 }, [
                text(a, { name: `driver-title-${i}`, width: fill, height: hug, style: { ...title, fontSize: 40, color } }),
                text(b, { name: `driver-body-${i}`, width: fill, height: hug, style: { ...small, fontSize: 26, color: C.ink } }),
              ]),
            ),
          ),
        ),
        footer(5),
      ],
    ),
    { frame: { left: 0, top: 0, width: W, height: H }, baseUnit: 8 },
  );
}

function addVerdict(p) {
  const s = p.slides.add();
  s.compose(
    row(
      { name: "verdict-root", width: fill, height: fill, padding: 76, gap: 52 },
      [
        panel(
          { name: "verdict-dark", width: grow(1), height: fill, padding: 46, fill: C.ink, borderRadius: 8 },
          column({ name: "verdict-dark-stack", width: fill, height: fill, gap: 26 }, [
            text("Verdetto onesto", { name: "verdict-label", width: fill, height: hug, style: { ...label, color: C.paper } }),
            text("Conviene comprare solo se resti almeno X anni.", {
              name: "verdict-main",
              width: fill,
              height: hug,
              style: { ...whiteTitle, fontSize: 78 },
            }),
            text("Dove X non è il desiderio di comprare. È il punto in cui il patrimonio netto batte l'alternativa.", {
              name: "verdict-copy",
              width: fill,
              height: hug,
              style: whiteBody,
            }),
          ]),
        ),
        column(
          { name: "verdict-light", width: grow(1), height: fill, gap: 26 },
          [
            text("Le frasi giuste non sono assolute.", {
              name: "verdict-side-title",
              width: fill,
              height: hug,
              style: { ...title, fontSize: 58 },
            }),
            text("Affittare resta competitivo se investi il capitale.", { name: "verdict-line-1", width: fill, height: hug, style: body }),
            text("La rata è più bassa, ma l'anticipo pesa.", { name: "verdict-line-2", width: fill, height: hug, style: body }),
            text("Il risultato è sensibile al rendimento alternativo.", { name: "verdict-line-3", width: fill, height: hug, style: body }),
            footer(6),
          ],
        ),
      ],
    ),
    { frame: { left: 0, top: 0, width: W, height: H }, baseUnit: 8 },
  );
}

function addCta(p) {
  const s = p.slides.add();
  s.compose(
    column(
      { name: "cta-root", width: fill, height: fill, padding: 76, gap: 34 },
      [
        column({ name: "cta-title-stack", width: fill, height: hug, gap: 8 }, [
          text("La casa non è solo un sogno.", {
            name: "cta-title-1",
            width: fill,
            height: hug,
            style: { ...giant, fontSize: 82 },
          }),
          text("È anche un modello finanziario.", {
            name: "cta-title-2",
            width: fill,
            height: hug,
            style: { ...giant, fontSize: 82 },
          }),
        ]),
        text("Prima di decidere, prova 3 scenari: resti 5 anni, resti 10 anni, resti 20 anni. Poi cambia anticipo, ETF e costo vendita. Il verdetto serio nasce lì.", {
          name: "cta-body",
          width: wrap(1180),
          height: hug,
          style: body,
        }),
        panel(
          { name: "cta-strip", width: fill, height: hug, padding: { x: 34, y: 24 }, fill: C.blue, borderRadius: 8 },
          text("Vuoi comprare casa? Prima fai litigare i numeri.", {
            name: "cta-strip-text",
            width: fill,
            height: hug,
            style: { ...whiteTitle, fontSize: 50 },
          }),
        ),
        footer(7),
      ],
    ),
    { frame: { left: 0, top: 0, width: W, height: H }, baseUnit: 8 },
  );
}

await mkdir("output", { recursive: true });
await mkdir(SCRATCH, { recursive: true });

const presentation = Presentation.create({ slideSize: { width: W, height: H } });
addCover(presentation);
addMyth(presentation);
addCalculator(presentation);
addCaserta(presentation);
addDrivers(presentation);
addVerdict(presentation);
addCta(presentation);

const pptxBlob = await PresentationFile.exportPptx(presentation);
await pptxBlob.save(OUT);

for (const [idx, slide] of presentation.slides.items.entries()) {
  const pngBlob = await slide.export({ format: "png" });
  await writeFile(`${SCRATCH}/slide_${String(idx + 1).padStart(2, "0")}.png`, Buffer.from(await pngBlob.arrayBuffer()));
  const layoutBlob = await slide.export({ format: "layout" });
  await writeFile(`${SCRATCH}/slide_${String(idx + 1).padStart(2, "0")}.layout.json`, await layoutBlob.text());
}

console.log(JSON.stringify({ deck: OUT, slides: presentation.slides.items.length, previews: SCRATCH }));
