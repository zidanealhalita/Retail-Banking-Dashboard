# 🏦 Retail Banking Analytics Dashboard

An interactive, multi-page analytics dashboard built with **Streamlit** and **Plotly** for exploring retail banking transaction data — covering transaction behavior, customer segmentation (RFM), product adoption, and geographic insights.

**Author:** Muhammad Zidane Alhalita

---

## 📌 Overview

This dashboard analyzes 6,000 retail banking transactions from 500 unique customers across five major Indonesian cities, spanning January 2025 to June 2026. It was built to demonstrate an end-to-end data analytics workflow — from raw transactional data to actionable business insights — in a format suitable for a risk management / data analytics / consulting portfolio.

The dashboard is fully interactive: every chart responds to sidebar filters (date range, location, transaction type, gender, mobile banking status, age, and transaction amount), and every section includes **auto-generated, filter-aware narrative insights** rather than static commentary.

---

## ✨ Key Features

| Module | Description |
|---|---|
| 📈 **Overview** | KPI summary, transaction type distribution, volume breakdown, nominal distribution & brackets |
| 🗓️ **Time Trend Analysis** | Monthly transaction count & volume trend (dual-axis), day-of-week patterns, weekday × transaction-type heatmap |
| 👥 **Customer Segmentation** | Age & gender demographics, average ticket size by age group, and full **RFM (Recency, Frequency, Monetary)** scoring with customer segment classification (Champions, Loyal Customers, Potential Loyalist, At Risk, Need Attention) |
| 💳 **Product Adoption** | Credit card & mutual fund penetration, cross-tab with mobile banking engagement, product adoption curve by age group |
| 🗺️ **Geographic Analysis** | Transaction volume & count by city, treemap visualization, transaction-type composition per location |
| 🔬 **Deep Dive & Correlation** | Boxplots, scatter plots with trendlines, correlation heatmap, violin plots comparing product owners vs. non-owners |
| 🧾 **Data Explorer** | Searchable, filterable raw data table with CSV export and descriptive statistics |

All filters in the sidebar apply globally across every tab, and every KPI/chart recalculates live.

---

## 🗂️ Dataset

**File:** `data/retail_banking_dataset.csv`

| Column | Description |
|---|---|
| `Transaction_ID` | Unique transaction identifier |
| `Customer_ID` | Unique customer identifier |
| `Transaction_Date` | Date of transaction (2025-01-01 to 2026-06-30) |
| `Transaction_Type` | QRIS Payment, Transfer Out, Bill Payment, ATM Withdrawal |
| `Amount_IDR` | Transaction amount in Indonesian Rupiah |
| `Age` | Customer age |
| `Gender` | Male / Female |
| `Location` | Jabodetabek, Surabaya, Bandung, Medan, Makassar |
| `Mobile_Banking_Status` | Active / Inactive / Non-User |
| `Has_Credit_Card` | 1 = owns a credit card, 0 = does not |
| `Has_Mutual_Fund` | 1 = owns a mutual fund product, 0 = does not |

> Replace `data/retail_banking_dataset.csv` with your own dataset (same schema) to reuse this dashboard for other retail banking datasets.

---

## 🧮 Methodology Notes

- **RFM Segmentation**: Recency, Frequency, and Monetary values are computed per customer within the active filter window, scored into quartiles (1–4), summed into an RFM score, and mapped into five business-friendly segments.
- **Age Grouping**: Customers are bucketed into `18-25`, `26-35`, `36-45`, `46-55`, `56-64`.
- **Amount Bracketing**: Transactions are bucketed into `<100K`, `100K-500K`, `500K-1M`, `1M-2.5M`, `>2.5M` (IDR) for easier distribution reading.
- **Correlation Matrix**: Uses Pearson correlation across `Age`, `Amount_IDR`, `Has_Credit_Card`, `Has_Mutual_Fund`, and a binary-encoded `Mobile_Active` flag.

---

## 🛠️ Tech Stack

- [Streamlit](https://streamlit.io/) — dashboard framework
- [Plotly Express](https://plotly.com/python/plotly-express/) — interactive charting
- [Pandas](https://pandas.pydata.org/) / [NumPy](https://numpy.org/) — data processing
- [statsmodels](https://www.statsmodels.org/) — trendline regression (OLS) for scatter plots

---

## 🚀 Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/<your-username>/retail-banking-analytics-dashboard.git
cd retail-banking-analytics-dashboard
```

### 2. Create a virtual environment (recommended)
```bash
python -m venv venv
source venv/bin/activate      # on Windows: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the dashboard
```bash
streamlit run app.py
```

The app will open automatically at `http://localhost:8501`.

---

## 📁 Project Structure

```
retail-banking-analytics-dashboard/
│
├── app.py                          # Main Streamlit application
├── data/
│   └── retail_banking_dataset.csv  # Source dataset
├── requirements.txt                # Python dependencies
├── .gitignore
└── README.md
```

---

## 📊 Sample Business Insights Generated

- Identification of the dominant transaction type by volume **and** by frequency (which are often different — a key insight for fee/revenue strategy).
- Detection of monthly transaction growth/decline trends to flag re-engagement needs.
- RFM-based segmentation to prioritize retention (Champions) vs. reactivation (At Risk / Need Attention) campaigns.
- Correlation between mobile banking engagement and credit card / mutual fund ownership, supporting digital-first cross-sell strategy.
- Age-group-specific product adoption curves to guide targeted marketing for credit cards vs. investment products.
- City-level average ticket size vs. transaction volume, useful for branch prioritization and premium banking expansion.

---

## 📄 License

This project is released under the MIT License. Feel free to fork, adapt, and use it for your own portfolio or analysis.

---

## 👤 Author

**Muhammad Zidane Alhalita**
Mathematics Undergraduate — Universitas Negeri Jakarta | Bank Indonesia GenBI Scholar
Focus areas: Risk Management, Actuarial Science, Quantitative Finance

Feel free to connect or reach out for feedback and collaboration.
