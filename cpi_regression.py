"""
Minimal example: compare CPI to division performance using linear regression.
Swap in your own division data in division_performance.csv (columns: date, value).
"""

from typing import Optional, Tuple

import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score


def get_cpi_data(api_key: Optional[str] = None) -> pd.DataFrame:
    """
    Load CPI (Consumer Price Index) data.
    - With BLS API key: fetches CPI-U from Bureau of Labor Statistics.
    - Without key: uses bundled sample data so the script runs out of the box.
    Get a free key at: https://www.bls.gov/developers/home.htm
    """
    if api_key:
        return _fetch_cpi_bls(api_key)
    return _sample_cpi()


def _sample_cpi() -> pd.DataFrame:
    """Sample CPI-U (1982-84=100) so the script runs without an API key."""
    # Monthly CPI-U from BLS, 2020-01 through 2024-12 (abbreviated)
    data = [
        ("2020-01", 257.971), ("2020-06", 257.797), ("2020-12", 260.474),
        ("2021-01", 261.582), ("2021-06", 271.696), ("2021-12", 278.802),
        ("2022-01", 281.148), ("2022-06", 296.311), ("2022-12", 296.797),
        ("2023-01", 299.170), ("2023-06", 305.109), ("2023-12", 306.746),
        ("2024-01", 308.417), ("2024-06", 314.069), ("2024-12", 314.069),
    ]
    df = pd.DataFrame(data, columns=["date", "cpi"])
    df["date"] = pd.to_datetime(df["date"])
    return df


def _fetch_cpi_bls(api_key: str) -> pd.DataFrame:
    """Fetch CPI-U from BLS API (series id CUUR0000SA0)."""
    import requests
    url = "https://api.bls.gov/publicAPI/v2/timeseries/data/"
    payload = {
        "seriesid": ["CUUR0000SA0"],
        "startyear": "2020",
        "endyear": "2024",
        "registrationkey": api_key,
    }
    resp = requests.post(url, json=payload)
    resp.raise_for_status()
    j = resp.json()

    # BLS returns status/message on error; success has Results.series
    if j.get("status") == "REQUEST_FAILED":
        msg = j.get("message", ["Unknown BLS error"])
        err = msg[0] if isinstance(msg, list) else msg
        raise ValueError(f"BLS API error: {err}")
    results = j.get("Results")
    if not results:
        raise ValueError("BLS returned no results. Check your API key at bls.gov/developers.")
    series_list = results.get("series") if isinstance(results, dict) else None
    if not series_list:
        raise ValueError("BLS returned no series. Check your API key and try again.")

    rows = []
    for item in series_list[0]["data"]:
        period = item["period"]
        year = item["year"]
        month = "01" if period == "M13" else period.replace("M", "")
        rows.append({"date": f"{year}-{month}", "cpi": float(item["value"])})
    df = pd.DataFrame(rows)
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").reset_index(drop=True)
    return df


def load_division_performance(path: str = "division_performance.csv") -> pd.DataFrame:
    """Load division metric from CSV: columns 'date' and 'value'."""
    df = pd.read_csv(path)
    df["date"] = pd.to_datetime(df["date"])
    return df[["date", "value"]].rename(columns={"value": "division"})


def run_regression(
    cpi: pd.DataFrame, division: pd.DataFrame
) -> Tuple[pd.DataFrame, LinearRegression, float, pd.Series]:
    """
    Merge CPI and division on date, fit linear regression, return merged df,
    fitted model, R², and predictions. Raises if fewer than 3 overlapping dates.
    """
    merged = pd.merge(cpi, division, on="date", how="inner")
    if len(merged) < 3:
        raise ValueError("Need at least 3 overlapping dates between CPI and division data.")
    X = merged[["cpi"]].values
    y = merged["division"].values
    model = LinearRegression().fit(X, y)
    y_pred = model.predict(X)
    r2 = r2_score(y, y_pred)
    return merged, model, r2, pd.Series(y_pred, index=merged.index)


def main():
    # 1) CPI
    cpi = get_cpi_data()  # pass api_key="YOUR_BLS_KEY" to use live data

    # 2) Division performance — use sample if CSV missing
    try:
        division = load_division_performance()
    except FileNotFoundError:
        # Synthetic example: division "revenue" that loosely tracks CPI with noise
        division = cpi[["date"]].copy()
        division["division"] = (cpi["cpi"].values * 1.2 + 50) + (
            pd.Series(range(len(cpi))).values * 0.5
        )

    # 3) Align and run regression
    merged, model, r2, y_pred = run_regression(cpi, division)

    # 5) Summary
    print("Linear regression: division performance vs CPI")
    print("-" * 40)
    print(f"  Slope (per 1 pt CPI): {model.coef_[0]:.4f}")
    print(f"  Intercept:            {model.intercept_:.4f}")
    print(f"  R² (fit):             {r2:.4f}")
    print()
    print("Equation: division ≈ {:.2f} + {:.2f} × CPI".format(model.intercept_, model.coef_[0]))

    # 6) Plot
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.scatter(merged["cpi"], merged["division"], alpha=0.7, label="Actual")
    ax.plot(merged["cpi"], y_pred, color="red", linewidth=2, label="Regression line")
    ax.set_xlabel("CPI (Consumer Price Index)")
    ax.set_ylabel("Division performance")
    ax.set_title("Division performance vs CPI")
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig("cpi_vs_division.png", dpi=150)
    print("\nPlot saved to cpi_vs_division.png")
    plt.close()


if __name__ == "__main__":
    main()
