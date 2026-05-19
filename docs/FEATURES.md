# 🏠 città. — Funzionalità

**Casa o affitto? Il calcolatore della verità** — Una webapp Streamlit per analizzare la convenienza dell'acquisto di una casa rispetto all'affitto, con calcoli patrimoniali annuali su un orizzonte di 40 anni.

---

## ✨ Funzionalità Core

### 1. **Calcolo Break-Even Patrimoniale**
- Confronto annuale tra patrimonio in scenario acquisto vs affitto
- Break-even: primo anno in cui il patrimonio da acquisto supera l'affitto
- Logica patrimoniale completa:
  - **Acquisto:** equity della casa + investimenti da risparmi annuali
  - **Affitto:** capitale iniziale evitato + investimenti da risparmi annuali

### 2. **Parametri Mutuo Completi**
- **Durata:** 15, 20, 25, 30 anni
- **Tasso fisso:** range 1.0% — 7.0%
- **Anticipo:** 10% — 50% del valore casa
- **Regime fiscale:**
  - Prima casa ordinaria (registro 2%, no IMU)
  - Prima casa giovani (under 36)
  - Seconda casa / investimento (registro 9%, IMU 0.5%)

### 3. **Costi di Transazione Dettagliati**
- **Imposte iniziali:**
  - Imposta di registro: 2% (prima casa) o 9% (seconda casa)
  - Calcolate su base catastale stimata (parametro configurabile)
- **Agenzia:** ~3% del valore
- **Notaio e spese:** ~3.500 €
- **Costi IMU e manutenzione annui:** già modellati nel flusso

### 4. **Investimento Alternativo (Rendimento ETF)**
- Rendimento su capitale non investito in casa
- Include: anticipo, costi iniziali evitati, differenze annuali di cassa
- Range: 2.0% — 10.0% annuo

### 5. **Rivalutazione Immobiliare**
- Rivalutazione annua della casa
- Range: 0.0% — 4.0%
- Impatta equity e patrimonio

### 6. **Selezione Geografica — 107 Province Italiane**
- Database interno con prezzi al mq e affitti per città
- Fonte indicativa: OMI, Immobiliare.it, Idealista 2024
- Dato: non è una rilevazione ufficiale puntuale

---

## 📊 Visualizzazioni e Report

### 1. **Grafico Break-Even**
- **Tab 1:** Andamento patrimonio netto (acquisto vs affitto) su 40 anni
- Linea verde verticale marca il break-even
- Interattivo con Plotly

### 2. **Mappa Italia**
- **Tab 2:** 107 province con indicatore visuale del break-even
- Colore gradient: verde (break-even veloce) → rosso (affitto sempre conveniente)
- Hover per dettagli città-per-città

### 3. **Classifica Nazionale**
- **Tab 3:** Ranking completo delle province per break-even crescente
- Colonne: città, regione, prezzo €/mq, affitto €/mese, rata €/mese, break-even

### 4. **Metriche Sintetiche**
- Card principale: valore casa, anticipo, rata, affitto, break-even
- Codifica colore:
  - 🟢 Verde: break-even ≤ 15 anni (conveniente)
  - 🟡 Amber: break-even 15—25 anni (media)
  - 🔴 Rosso: break-even > 25 anni (affitto vince)

---

## 🎯 Funzionalità Avanzate (Track 4)

### 1. **📄 Esportazione PDF**
- **Descrizione:** Scarica un report PDF completo con i risultati dell'analisi
- **Contenuti:**
  - Titolo e data dell'analisi
  - Risultato break-even principale
  - Parametri immobile (città, mq, prezzo al mq, affitto)
  - Parametri finanziari (mutuo, regime fiscale, tasso, rendimento ETF)
  - Tabella anno-per-anno (ogni 5 anni) con evoluzione patrimoniale
  - Footer con disclaimer
- **Pulsante:** "📄 Scarica PDF" nella sezione metriche principale
- **Formato:** Documento A4 professionale con brand città.

**Demo scenario — Milano 80 mq:**
```
città. — Analisi Casa vs Affitto
Milano — 80 mq · 15/05/2026

Risultato Break-Even: 12 anni
Comprare conviene.

Parametri Immobile:
- Città: Milano
- Superficie: 80 mq
- Prezzo al mq: € 7.250
- Valore immobile: € 580.000
- Affitto mensile stimato: € 1.200

Parametri Finanziari:
- Regime fiscale: Prima casa ordinaria
- Anticipo: 20%
- Importo anticipo + costi: € 128.500
... [completa tabella patrimoniale]
```

### 2. **💾 Salvataggio e Confronto Scenari**
- **Descrizione:** Salva l'analisi attuale come "scenario" e confronta multiple configurazioni
- **Funzionalità:**
  - **Salva scenario:** Sidebar → "Salva Scenario Attuale" → digita nome → 💾 Salva
  - **Elimina scenario:** Dropdown "Elimina scenario" + pulsante 🗑️
  - **Visualizzazione:** Tabella comparativa tra scenari salvati (solo se salvati)
  - **Archiviazione:** In st.session_state (persiste durante la sessione)
- **Colonne comparativa:**
  - Scenario (nome), Città, mq, Prezzo €/mq, Affitto €/mese
  - Rata €/mese, Tasso mutuo, Anticipo, Durata mutuo
  - Rendimento ETF, Rivalutazione, Break-even

**Demo scenari:**
```
1. "Milano base" — Break-even 12 anni
2. "Milano aggresivo" (tasso basso, rendimento alto) — Break-even 9 anni
3. "Roma conservativo" (tasso alto, rendimento basso) — Break-even 18 anni

→ Tabella comparativa mostra le differenze a colpo d'occhio
```

### 3. **🔬 Analisi di Sensibilità**
- **Descrizione:** Esplora come il break-even cambia al variare di un parametro
- **Parametri analizzabili:**
  - **Tasso Mutuo (%):** 1.0% — 6.0%
  - **Rendimento ETF (%):** 1.0% — 10.0%
  - **Rivalutazione Immobile (%):** 0.0% — 4.0%
- **Funzionalità:**
  - Dropdown per selezionare il parametro
  - Grafico interattivo Plotly con:
    - Curva break-even vs parametro
    - Linea verde tratteggiata = valore attuale (per contesto)
    - Gradiente giallo sotto la curva per visualizzazione
  - Metriche di riepilogo:
    - Break-even minimo (a quale valore del parametro?)
    - Break-even massimo
    - Break-even attuale (con il valore selezionato)
- **Posizionamento:** Sezione collapsibile "🔬 Analisi Sensibilità" sotto le mappe/classifiche

**Demo sensibilità — Milano, tasso mutuo:**
```
Tasso Mutuo | Break-even
1.0%        | 8 anni
2.0%        | 10 anni
3.0%        | 11 anni
3.5% (valore attuale) → 12 anni
4.0%        | 13 anni
5.0%        | 15 anni
6.0%        | 18 anni

→ Grafico mostra relazione lineare: tasso più alto = break-even più tardi
```

---

## 🌍 Demo Città — Callout Scenario

### Milano (80 mq, prima casa, 20% anticipo)
- **Prezzo:** € 7.250/mq (€ 580.000 totale)
- **Affitto:** € 1.200/mese
- **Rata:** € 2.150/mese
- **Break-even:** ~12 anni → ✅ Comprare conviene (pazienza sotto i 20 anni)
- **Insight:** Città con valori alti ma affitti relativamente moderati; l'acquisto supera l'affitto in tempi ragionevoli.

### Roma (80 mq, prima casa, 20% anticipo)
- **Prezzo:** € 4.500/mq (€ 360.000 totale)
- **Affitto:** € 850/mese
- **Rata:** € 1.650/mese
- **Break-even:** ~14 anni → ✅ Comprare conviene
- **Insight:** Città con prezzi più moderati; il break-even arriva più tardi rispetto a Milano ma è comunque ragionevole.

### Palermo (80 mq, prima casa, 20% anticipo)
- **Prezzo:** € 2.800/mq (€ 224.000 totale)
- **Affitto:** € 500/mese
- **Rata:** € 950/mese
- **Break-even:** ~18 anni → ⚠️ Affitto conviene per lungo tempo
- **Insight:** Città con prezzi bassissimi ma anche affitti bassi; il break-even arriva tardi, affittare è conveniente per chi non è sicuro di restarvi 20+ anni.

---

## 🔧 Stack Tecnico

- **Framework:** Streamlit (1.45.0)
- **Data:** pandas (≥2.0.0)
- **Visualizzazione:** Plotly (≥5.18.0)
- **Export PDF:** Reportlab (≥4.0.0)
- **Logica:** Python puro (dataclasses, numpy per sensibilità)

---

## 📝 Note Importanti

1. **Non è consulenza finanziaria** — I dati sono indicativi e basati su stime pubbliche.
2. **Base catastale:** È un proxy del valore catastale; per precisione reale serve la rendita catastale dell'immobile specifico.
3. **Inflazione:** Assunta al 2% annuo per gli affitti; non modellata per altri costi.
4. **Scenario 40 anni:** Orizzonte massimo; se il break-even non arriva, viene segnalato come ">40 anni".
5. **Garanzia mutuo under 36:** Non è modellata; l'effetto principale sarebbe sulla riduzione del tasso, già parametrizzabile manualmente.

---

## 🚀 Roadmap Futura

- [ ] Persistenza scenari (database / salvataggio JSON)
- [ ] Export dati (CSV, Excel)
- [ ] Analisi "What-if" avanzate (multi-parametro)
- [ ] Integrazione OMI ufficiale (API)
- [ ] Simulatore mutuo passo-passo (rata per rata)
- [ ] Confronto città in real-time (selettore multiplo)

---

**città. — Fatto con ❤️ per chi pensa al futuro. 2026**
