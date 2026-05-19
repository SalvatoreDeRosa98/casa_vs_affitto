# Casa o Affitto? — Il Calcolatore della Verità 🏠

A comprehensive financial calculator to help Italian homebuyers and renters make data-driven decisions about the biggest financial choice of their lives.

**Live Demo:** [casa-vs-affitto.streamlit.app](https://casa-vs-affitto.streamlit.app)

---

## Overview

Whether buying or renting? This interactive web application cuts through the noise and answers the fundamental question: **Is it financially better to buy a house or rent in Italy?**

Using real provincial Italian property data, mortgage market rates, and comprehensive cost modeling, Casa o Affitto provides personalized breakeven analysis, scenario comparison, and sensitivity testing to help you understand the true financial implications of buying vs. renting.

### Key Features

- **Interactive Property Search** — Browse 100+ Italian provinces with real pricing data
- **Multi-Scenario Analysis** — Compare first home, second home, and investor scenarios with tax implications
- **Breakeven Calculation** — See exactly when buying becomes financially advantageous
- **Sensitivity Analysis** — Test how property appreciation, interest rates, and rental growth affect your decision
- **Scenario Comparison** — Compare up to 3 different scenarios side-by-side
- **PDF Export** — Download comprehensive reports with all calculations and charts
- **Mobile Responsive** — Works perfectly on desktop, tablet, and mobile devices
- **Dark/Light Themes** — Modern UI with comfortable viewing in any lighting condition

---

## How It Works

### Input → Calculation → Output

The app follows a clear workflow:

1. **Location & Property Setup**
   - Select an Italian province
   - Choose a city within that province
   - Enter property price and optional down payment

2. **Financial Parameters**
   - Loan duration (mortgage term)
   - Interest rate (pre-filled with market rates)
   - Annual rent value
   - Property appreciation and rental growth rates

3. **Tax & Scenario Selection**
   - Choose fiscal regime (prima casa ordinaria, affitto non commerciale, etc.)
   - Select property ownership scenario
   - Input annual expenses (maintenance, utilities, insurance)

4. **Calculations**
   - Monthly mortgage, rent, and expense comparisons
   - Net worth projections (10, 20, 30 years)
   - Breakeven year (when cumulative buying advantage exceeds costs)
   - Total lifetime cost comparison

5. **Results Visualization**
   - Breakeven timeline chart
   - Cumulative cost analysis
   - Monthly payment breakdown
   - Net worth comparison
   - Detailed financial summary

---

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/casa-vs-affitto.git
   cd casa-vs-affitto
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the app**
   ```bash
   streamlit run app.py
   ```

   The app will open at `http://localhost:8501`

### Docker Setup (Optional)

```bash
docker build -t casa-vs-affitto .
docker run -p 8501:8501 casa-vs-affitto
```

---

## Project Structure

```
casa-vs-affitto/
├── app.py                    # Main Streamlit application
├── calcoli.py               # Financial calculation engine
├── dati.py                  # Property data and province/city database
├── requirements.txt         # Python dependencies
├── .streamlit/
│   ├── config.toml         # Streamlit production configuration
│   └── secrets.toml        # Secrets management (gitignored)
├── .gitignore              # Git ignore rules
├── README.md               # This file
├── docs/
│   └── DEPLOY.md          # Deployment guide
└── assets/
    ├── screenshot.png     # App screenshot for social media
    └── linkedin-post.md   # LinkedIn post copy
```

### Module Overview

- **app.py** — Streamlit UI with interactive forms, visualizations, and user experience logic
- **calcoli.py** — Core financial calculation engine using `ParamsCalcolo` dataclass
- **dati.py** — Italian property data, provincial breakdowns, city information, and market rates

---

## Development

### Updating Real Market Data

The app can use a local cache generated from Immobiliare.it market pages:

```bash
python scripts/update_market_data.py
```

This creates `data/market_data_immobiliare.json` with residential asking prices:

- `prezzo_mq`: sale asking price in EUR/m2
- `affitto_mq_mese`: rent asking price in EUR/m2/month
- `affitto_80mq`: rent estimate for 80 m2

If the cache is missing or incomplete, the app falls back to the internal indicative dataset in `dati.py`.

### Running Tests

```bash
python -m pytest tests/ -v
```

### Type Checking

```bash
mypy app.py calcoli.py dati.py --ignore-missing-imports
```

### Code Style

This project uses black for code formatting:

```bash
black app.py calcoli.py dati.py
```

Check code style:
```bash
black --check app.py calcoli.py dati.py
```

### Linting

```bash
pylint app.py calcoli.py dati.py
```

---

## Methodology

### Data Sources

- **Property Prices**: Italian real estate market data (provincial averages)
- **Mortgage Rates**: Current market rates from Italian banking sector
- **Tax Regimes**: Official Italian tax law for:
  - Prima casa ordinaria (first home)
  - Affitto non commerciale (non-commercial rental)
  - Investimento immobiliare (real estate investment)
- **Living Costs**: Regional average utility, maintenance, and insurance costs

### Key Assumptions

1. **Constant appreciation** — Property and rental values grow at user-specified annual rates
2. **Fixed-rate mortgage** — Interest rate doesn't change over loan term
3. **No early repayment** — Mortgage is held to maturity
4. **Stable rental market** — Rental prices grow at specified rate
5. **No capital gains tax** — Italian law exempts principal residence from capital gains tax
6. **Linear expense growth** — Annual expenses grow at specified rate

### Limitations

- **Point-in-time snapshot** — Property prices are historical averages, not real-time data
- **Market volatility** — Actual returns may differ significantly from historical trends
- **Regional variations** — Costs vary within provinces; this uses averages
- **Personal circumstances** — Results don't account for personal credit worthiness, family status, relocation plans
- **Tax law changes** — Assumes current Italian tax law remains stable
- **Interest rate risk** — Assumes fixed-rate mortgages; variable rates add complexity
- **Liquidity** — Doesn't account for the cost/time to buy or sell property

### Breakeven Calculation

The app calculates when cumulative buying advantage exceeds total buying costs:

```
Breakeven Year = Year where:
  Cumulative (Rent Payments) - Cumulative (Mortgage + Expenses) > Total Buying Costs
```

Where:
- **Total Buying Costs** = Down payment + closing costs + any initial renovations
- **Annual Rent** = Market value of renting equivalent property
- **Annual Expenses** = Maintenance, insurance, utilities, property tax

---

## FAQ

### Q: Why does buying not always win?
**A:** In low-appreciation markets with high down payments, or when interest rates are high relative to rental yields, renting can be more financially advantageous. The calculator shows the true economic picture, not the emotional desire to "own."

### Q: Can I change the interest rate?
**A:** Yes! The calculator pre-fills with current market rates, but you can adjust based on your personal credit rating and lender offers.

### Q: How does tax regime affect the calculation?
**A:** Different regimes (first home, rental, investment) have different tax treatments on rent income and capital gains. The app models each scenario's tax implications.

### Q: What if I want to live in multiple properties?
**A:** Try the scenario comparison feature to model different ownership patterns (e.g., principal + vacation home).

### Q: Is the data for my specific address?
**A:** No—the app uses provincial averages. For precision analysis on a specific property, use the property-specific parameters to override defaults.

### Q: Can I export results?
**A:** Yes! Click the "Download PDF Report" button to export comprehensive analysis including all charts and calculations.

### Q: How often is property data updated?
**A:** Data is refreshed quarterly based on market surveys. Check the app footer for the latest data date.

### Q: Does this account for rental price controls?
**A:** The Italian "canone concordato" (agreed rent) regime isn't explicitly modeled—the app uses market rates. Adjust the "Annual Rent" parameter to reflect agreed pricing.

### Q: What about renovation costs?
**A:** Include initial renovation in the "down payment" field, or add ongoing renovation costs to annual expenses.

### Q: Can I compare properties in different regions?
**A:** Yes! Use the scenario comparison feature to compare same property in different provinces, or different scenarios for same property.

---

## Technology Stack

- **Streamlit** — Web app framework for data applications
- **Plotly** — Interactive financial charts and visualizations
- **Pandas** — Data manipulation and analysis
- **Python 3.8+** — Programming language

---

## Deployment

### Streamlit Cloud (Recommended)

See [docs/DEPLOY.md](docs/DEPLOY.md) for detailed deployment instructions.

**Quick Start:**
1. Push code to GitHub (public repository)
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect GitHub account
4. Select this repository
5. Deploy

### Alternative: Self-Hosted

For Docker, Heroku, or other hosting options, see [docs/DEPLOY.md](docs/DEPLOY.md).

---

## Contributing

Contributions are welcome! Areas for improvement:

- [ ] International property market comparison
- [ ] Mortgage comparison across Italian banks
- [ ] Historical data visualization
- [ ] Additional tax regime modeling
- [ ] Inflation adjustment tools
- [ ] Integration with real estate APIs for live data

To contribute:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

## Author

**Salvatore De Rosa**
- Email: salvatore98derosa@gmail.com
- LinkedIn: [linkedin.com/in/salvatorederosa](https://linkedin.com/in/salvatorederosa)
- GitHub: [github.com/salvatorederosa](https://github.com/salvatorederosa)

---

## Support

Found a bug? Have a feature request? Questions about the calculations?

- **Issues**: Open an issue on [GitHub Issues](https://github.com/salvatorederosa/casa-vs-affitto/issues)
- **Email**: salvatore98derosa@gmail.com
- **LinkedIn**: Message me on LinkedIn

---

## Acknowledgments

- Italian property market data sources
- Streamlit community for excellent documentation
- Plotly for financial visualization tools
- All users providing feedback and suggestions

---

## Last Updated

May 2026

**Version:** 1.0.0
