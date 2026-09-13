import os
from pathlib import Path
import pandas as pd
import matplotlib
# Use Agg backend for reliable server-side and script rendering without UI blocking
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

OUTPUT_DIR = Path("static/images")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def plot_aqi_distribution(df):
    """
    Plot distribution of AQI values and save image.
    """
    plt.figure(figsize=(9, 5))
    sns.histplot(
        df["AQI"],
        bins=30,
        kde=True,
        color="#3B82F6"
    )
    plt.title("Distribution of AQI", fontsize=14, pad=12)
    plt.xlabel("AQI", fontsize=11)
    plt.ylabel("Frequency", fontsize=11)
    plt.tight_layout()

    out_file = OUTPUT_DIR / "aqi_distribution.png"
    plt.savefig(out_file, dpi=150)
    plt.close()
    print(f"Saved distribution plot to {out_file}")


def plot_correlation_heatmap(df):
    """
    Plot correlation heatmap for numerical features and save image.
    """
    plt.figure(figsize=(14, 10))
    correlation = df.corr(numeric_only=True)
    sns.heatmap(
        correlation,
        annot=True,
        fmt=".2f",
        cmap="coolwarm",
        center=0,
        cbar_kws={'label': 'Pearson Correlation'}
    )
    plt.title("Feature Correlation Heatmap", fontsize=14, pad=12)
    plt.tight_layout()

    out_file = OUTPUT_DIR / "correlation_heatmap.png"
    plt.savefig(out_file, dpi=150)
    plt.close()
    print(f"Saved correlation heatmap to {out_file}")


def plot_feature_importance(model, feature_names):
    """
    Plot feature importance from a Random Forest model and save image.
    """
    importance_df = pd.DataFrame({
        "Feature": feature_names,
        "Importance": model.feature_importances_
    })

    # Sort descending
    importance_df = importance_df.sort_values(
        by="Importance",
        ascending=False
    )

    plt.figure(figsize=(9, 5.5))
    sns.barplot(
        data=importance_df,
        x="Importance",
        y="Feature",
        palette="viridis"
    )
    plt.title("Feature Importance for AQI Prediction", fontsize=14, pad=12)
    plt.xlabel("Importance Score", fontsize=11)
    plt.ylabel("Pollutant Feature", fontsize=11)
    plt.tight_layout()

    out_file = OUTPUT_DIR / "feature_importance.png"
    plt.savefig(out_file, dpi=150)
    plt.close()
    print(f"Saved feature importance plot to {out_file}")


def plot_actual_vs_predicted(y_test, y_pred):
    """
    Plot actual vs predicted AQI scatter plot and save image.
    """
    plt.figure(figsize=(7, 6))
    plt.scatter(
        y_test,
        y_pred,
        alpha=0.4,
        color="#2563EB",
        edgecolors="none",
        s=35
    )

    # Reference 45-degree identity line
    min_val = min(float(y_test.min()), float(y_pred.min()))
    max_val = max(float(y_test.max()), float(y_pred.max()))
    plt.plot(
        [min_val, max_val],
        [min_val, max_val],
        color="#EF4444",
        linestyle="--",
        linewidth=2,
        label="Perfect Fit (y = x)"
    )

    plt.title("Actual vs Predicted AQI", fontsize=14, pad=12)
    plt.xlabel("Actual AQI", fontsize=11)
    plt.ylabel("Predicted AQI", fontsize=11)
    plt.legend()
    plt.tight_layout()

    out_file = OUTPUT_DIR / "actual_vs_predicted.png"
    plt.savefig(out_file, dpi=150)
    plt.close()
    print(f"Saved actual vs predicted plot to {out_file}")


def visualize(df):
    plot_aqi_distribution(df)
    plot_correlation_heatmap(df)
