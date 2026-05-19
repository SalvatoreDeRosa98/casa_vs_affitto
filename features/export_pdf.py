# =============================================================================
# PDF EXPORT — Casa vs Affitto
# =============================================================================

from datetime import datetime
from io import BytesIO

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph,
    Spacer, Image, HRFlowable
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

# ── Brand palette ─────────────────────────────────────────────────────────────
GOLD       = colors.HexColor("#C8A96E")
GOLD_LIGHT = colors.HexColor("#FBF7EE")
GOLD_MID   = colors.HexColor("#E8D5A8")
DARK       = colors.HexColor("#1A1A1A")
GREY_TEXT  = colors.HexColor("#555555")
GREY_LIGHT = colors.HexColor("#F5F5F5")
WHITE      = colors.white
GREEN      = colors.HexColor("#2E7D32")
RED        = colors.HexColor("#C62828")

GOLD_HEX   = "#C8A96E"
DARK_HEX   = "#1A1A1A"
AFFITTO_HEX = "#8B7355"


def _make_chart(anni, patrimonio_acquisto, patrimonio_affitto) -> BytesIO:
    fig, ax = plt.subplots(figsize=(7, 3), dpi=150)
    fig.patch.set_facecolor("#FDFAF4")
    ax.set_facecolor("#FDFAF4")

    ax.plot(anni, [p / 1000 for p in patrimonio_acquisto],
            color=GOLD_HEX, linewidth=2.5, label="Acquisto")
    ax.plot(anni, [p / 1000 for p in patrimonio_affitto],
            color=AFFITTO_HEX, linewidth=2.0, linestyle="--", label="Affitto (ETF)")

    # Highlight crossover
    for i in range(len(anni) - 1):
        pa, pf = patrimonio_acquisto[i], patrimonio_affitto[i]
        pa2, pf2 = patrimonio_acquisto[i + 1], patrimonio_affitto[i + 1]
        if (pa - pf) * (pa2 - pf2) < 0:
            frac = (pf - pa) / ((pa2 - pa) - (pf2 - pf)) if ((pa2 - pa) - (pf2 - pf)) != 0 else 0
            cross_x = anni[i] + frac * (anni[i + 1] - anni[i])
            cross_y = (pa + frac * (pa2 - pa)) / 1000
            ax.axvline(x=cross_x, color=GOLD_HEX, linewidth=1, linestyle=":", alpha=0.7)
            ax.annotate(f"Break-even\nAnno {cross_x:.0f}",
                        xy=(cross_x, cross_y),
                        xytext=(cross_x + 1.5, cross_y * 1.08),
                        fontsize=6.5, color=DARK_HEX,
                        arrowprops=dict(arrowstyle="->", color=GOLD_HEX, lw=0.8))
            break

    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"€{v:.0f}k"))
    ax.set_xlabel("Anno", fontsize=8, color=DARK_HEX)
    ax.set_ylabel("Patrimonio netto", fontsize=8, color=DARK_HEX)
    ax.tick_params(labelsize=7, colors=DARK_HEX)
    for spine in ax.spines.values():
        spine.set_edgecolor("#DDDDDD")
    ax.grid(axis="y", color="#E8E8E8", linewidth=0.5)

    legend = ax.legend(fontsize=7, framealpha=0.9, facecolor="#FDFAF4",
                       edgecolor=GOLD_HEX, loc="upper left")

    plt.tight_layout(pad=0.5)
    buf = BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", facecolor="#FDFAF4")
    plt.close(fig)
    buf.seek(0)
    return buf


def _param_table(data, col_widths=None):
    if col_widths is None:
        col_widths = [60*mm, 60*mm]
    t = Table(data, colWidths=col_widths)
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (0, -1), GOLD_LIGHT),
        ("BACKGROUND",    (1, 0), (1, -1), WHITE),
        ("TEXTCOLOR",     (0, 0), (-1, -1), DARK),
        ("FONTNAME",      (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME",      (1, 0), (1, -1), "Helvetica"),
        ("FONTSIZE",      (0, 0), (-1, -1), 8.5),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LINEBELOW",     (0, 0), (-1, -2), 0.3, GOLD_MID),
        ("BOX",           (0, 0), (-1, -1), 0.8, GOLD),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [GOLD_LIGHT, WHITE]),
    ]))
    return t


def genera_report_pdf(
    citta: str,
    mq: int,
    prezzo_mq: float,
    affitto_mens: float,
    tasso_mutuo: float,
    anticipo_perc: float,
    anni_mutuo: int,
    rendimento_etf: float,
    rivalutazione: float,
    regime_label: str,
    result: dict,
) -> BytesIO:
    buffer = BytesIO()
    page_w, page_h = A4
    margin = 15 * mm

    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        topMargin=margin, bottomMargin=margin,
        leftMargin=margin, rightMargin=margin,
    )

    styles = getSampleStyleSheet()

    def style(name, **kw):
        return ParagraphStyle(name, parent=styles["Normal"], **kw)

    s_body  = style("body",  fontSize=9,  textColor=GREY_TEXT, spaceAfter=4)
    s_small = style("small", fontSize=7.5, textColor=GREY_TEXT, alignment=TA_CENTER)
    s_section = style("section", fontSize=10, textColor=DARK,
                      fontName="Helvetica-Bold", spaceBefore=10, spaceAfter=4)

    story = []

    # ── HEADER BAND ───────────────────────────────────────────────────────────
    header_data = [[
        Paragraph("<font color='#1A1A1A'><b>città.</b></font>",
                  style("h_title", fontSize=18, fontName="Helvetica-Bold",
                        textColor=DARK, alignment=TA_LEFT)),
        Paragraph(
            f"<font color='#3A3A3A'>Analisi Casa vs Affitto</font><br/>"
            f"<font color='#666666' size='8'>{citta} · {mq} mq · "
            f"{datetime.now().strftime('%d/%m/%Y')}</font>",
            style("h_sub", fontSize=9, alignment=TA_RIGHT, textColor=DARK)
        ),
    ]]
    header_table = Table(header_data, colWidths=[(page_w - 2*margin) * 0.4,
                                                  (page_w - 2*margin) * 0.6])
    header_table.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), GOLD),
        ("TOPPADDING",    (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("LEFTPADDING",   (0, 0), (0, -1),  12),
        ("RIGHTPADDING",  (-1, 0), (-1, -1), 12),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 5*mm))

    # ── HERO: BREAK-EVEN ──────────────────────────────────────────────────────
    be = result.get("breakeven_anno")
    be_label = f"{be} anni" if be else "> 40 anni"
    be_desc = (
        f"Acquistare diventa conveniente dopo <b>{be} anni</b>."
        if be else
        "Con questi parametri, affittare è sempre più conveniente."
    )

    hero_data = [[
        Paragraph(
            f"<font size='9' color='#8B7355'>Break-even</font><br/>"
            f"<font size='28' color='#1A1A1A'><b>{be_label}</b></font>",
            style("hero_num", alignment=TA_CENTER, leading=32)
        ),
        Paragraph(
            f"{be_desc}<br/><br/>"
            f"<font size='8' color='#888888'>Patrimonio acquisto supera affitto "
            f"{'nell\'anno ' + str((datetime.now().year + be)) if be else 'mai nei 40 anni simulati'}."
            f"</font>",
            style("hero_txt", fontSize=9, textColor=GREY_TEXT, leading=14)
        ),
    ]]
    hero_table = Table(hero_data,
                       colWidths=[(page_w - 2*margin) * 0.28,
                                  (page_w - 2*margin) * 0.72])
    hero_table.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), GOLD_LIGHT),
        ("BOX",           (0, 0), (-1, -1), 1.5, GOLD),
        ("LINEBEFORE",    (1, 0), (1, -1),  1.5, GOLD),
        ("TOPPADDING",    (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
        ("LEFTPADDING",   (0, 0), (-1, -1), 12),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 12),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(hero_table)
    story.append(Spacer(1, 5*mm))

    # ── DUE COLONNE PARAMETRI ─────────────────────────────────────────────────
    story.append(HRFlowable(width="100%", thickness=0.5, color=GOLD_MID, spaceAfter=3))
    story.append(Paragraph("Parametri", s_section))

    col_w = (page_w - 2*margin - 6*mm) / 2

    imm_data = [
        ["Città", citta],
        ["Superficie", f"{mq} mq"],
        ["Prezzo al mq", f"€ {prezzo_mq:,.0f}"],
        ["Valore immobile", f"€ {result['valore_casa']:,.0f}"],
        ["Affitto mensile", f"€ {affitto_mens:,.0f}"],
    ]
    fin_data = [
        ["Regime fiscale", regime_label],
        ["Anticipo", f"{anticipo_perc:.0f}%  (€ {result['anticipo']:,.0f})"],
        ["Mutuo", f"€ {result['capitale_mutuo']:,.0f} · {anni_mutuo}a · {tasso_mutuo}%"],
        ["Rata mensile", f"€ {result['rata_mensile']:,.0f}"],
        ["Interessi totali", f"€ {result['interessi_mutuo']:,.0f}"],
        ["Rendimento ETF", f"{rendimento_etf}%"],
        ["Rivalutazione annua", f"{rivalutazione}%"],
    ]

    two_col = Table(
        [[_param_table(imm_data, [col_w * 0.45, col_w * 0.55]),
          _param_table(fin_data, [col_w * 0.48, col_w * 0.52])]],
        colWidths=[col_w, col_w],
        hAlign="LEFT",
    )
    two_col.setStyle(TableStyle([
        ("LEFTPADDING",  (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING",   (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 0),
        ("ALIGN",        (0, 0), (-1, -1), "LEFT"),
        ("VALIGN",       (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING",  (1, 0), (1, -1),  6),
    ]))
    story.append(two_col)
    story.append(Spacer(1, 5*mm))

    # ── GRAFICO ───────────────────────────────────────────────────────────────
    anni = result.get("anni", [])
    patrimonio_acquisto = result.get("patrimonio_acquisto", [])
    patrimonio_affitto  = result.get("patrimonio_affitto", [])

    if anni and patrimonio_acquisto and patrimonio_affitto:
        story.append(HRFlowable(width="100%", thickness=0.5, color=GOLD_MID, spaceAfter=3))
        story.append(Paragraph("Evoluzione Patrimoniale", s_section))
        chart_buf = _make_chart(anni, patrimonio_acquisto, patrimonio_affitto)
        chart_img = Image(chart_buf, width=page_w - 2*margin - 4*mm, height=55*mm)
        story.append(chart_img)
        story.append(Spacer(1, 4*mm))

    # ── TABELLA ANNO PER ANNO ─────────────────────────────────────────────────
    story.append(HRFlowable(width="100%", thickness=0.5, color=GOLD_MID, spaceAfter=3))
    story.append(Paragraph("Dettaglio ogni 5 anni", s_section))

    usable_w = page_w - 2*margin
    hdr_style = style("th", fontSize=8, fontName="Helvetica-Bold",
                      textColor=WHITE, alignment=TA_CENTER)
    cell_style_r = style("td_r", fontSize=8, textColor=DARK, alignment=TA_RIGHT)
    cell_style_c = style("td_c", fontSize=8, textColor=DARK, alignment=TA_CENTER)

    table_data = [[
        Paragraph("Anno",                        hdr_style),
        Paragraph("Patrimonio<br/>Acquisto",     hdr_style),
        Paragraph("Patrimonio<br/>Affitto",      hdr_style),
        Paragraph("Differenza",                  hdr_style),
    ]]

    for i, anno in enumerate(anni):
        if anno % 5 == 0 or i == 0:
            pa   = patrimonio_acquisto[i] if i < len(patrimonio_acquisto) else 0
            pf   = patrimonio_affitto[i]  if i < len(patrimonio_affitto)  else 0
            diff = pa - pf
            diff_color = "#2E7D32" if diff >= 0 else "#C62828"
            table_data.append([
                Paragraph(str(anno),              cell_style_c),
                Paragraph(f"€ {pa:,.0f}",         cell_style_r),
                Paragraph(f"€ {pf:,.0f}",         cell_style_r),
                Paragraph(
                    f"<font color='{diff_color}'><b>€ {diff:,.0f}</b></font>",
                    cell_style_r
                ),
            ])

    col_ws = [usable_w * f for f in [0.12, 0.27, 0.27, 0.34]]
    yearly = Table(table_data, colWidths=col_ws, repeatRows=1)

    row_count = len(table_data)
    ts = [
        ("BACKGROUND",    (0, 0),  (-1, 0),  GOLD),
        ("TEXTCOLOR",     (0, 0),  (-1, 0),  WHITE),
        ("TOPPADDING",    (0, 0),  (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0),  (-1, -1), 4),
        ("LEFTPADDING",   (0, 0),  (-1, -1), 6),
        ("RIGHTPADDING",  (0, 0),  (-1, -1), 6),
        ("LINEBELOW",     (0, 0),  (-1, -1), 0.3, GOLD_MID),
        ("BOX",           (0, 0),  (-1, -1), 0.8, GOLD),
        ("VALIGN",        (0, 0),  (-1, -1), "MIDDLE"),
    ]
    for r in range(1, row_count):
        bg = GOLD_LIGHT if r % 2 == 1 else WHITE
        ts.append(("BACKGROUND", (0, r), (-1, r), bg))
    yearly.setStyle(TableStyle(ts))
    story.append(yearly)
    story.append(Spacer(1, 6*mm))

    # ── FOOTER ────────────────────────────────────────────────────────────────
    story.append(HRFlowable(width="100%", thickness=0.8, color=GOLD, spaceAfter=4))
    story.append(Paragraph(
        "<i>Report generato da <b>città.</b> — Il calcolatore della verità (2026). "
        "Dati indicativi basati su stime. Non costituisce consulenza finanziaria.</i>",
        s_small,
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer
