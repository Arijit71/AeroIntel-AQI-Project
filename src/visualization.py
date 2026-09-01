import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

df=pd.read_csv("data/processed/cleaned_city_day.csv")
def plot_aqi_distribution(df):
    """
    Plot distribution of AQI values.
    """

    plt.figure(figsize=(10, 6))

    sns.histplot(
        df["AQI"],
        bins=30,
        kde=True
    )

    plt.title("Distribution of AQI")
    plt.xlabel("AQI")
    plt.ylabel("Frequency")

    plt.show()

def plot_correlation_heatmap(df):
    """
    Plot correlation heatmap for numerical features.
    """

    plt.figure(figsize=(18, 12))

    correlation = df.corr(numeric_only=True)

    sns.heatmap(
        correlation,
        annot=False,
        cmap="coolwarm",
        center=0
    )

    plt.title("Feature Correlation Heatmap")

    plt.show()

def plot_feature_importance(model, feature_names):
    """
    Plot feature importance from a Random Forest model.
    """

    importance_df = pd.DataFrame({
        "Feature": feature_names,
        "Importance": model.feature_importances_
    })

    # Sort from most important to least important
    importance_df = importance_df.sort_values(
        by="Importance",
        ascending=False
    )

    plt.figure(figsize=(10, 6))

    sns.barplot(
        data=importance_df,
        x="Importance",
        y="Feature"
    )

    plt.title("Feature Importance for AQI Prediction")
    plt.tight_layout()
    plt.show()

def plot_actual_vs_predicted(y_test, y_pred):
        plt.figure(figsize=(8, 6))
            
        plt.scatter(
            y_test,
            y_pred,
            alpha=0.5
        )
            
        # Perfect prediction reference line
        min_value = min(y_test.min(), y_pred.min())
        max_value = max(y_test.max(), y_pred.max())            
        plt.plot(
            [min_value, max_value],
            [min_value, max_value]
        )
    
    
        plt.title("Actual vs Predicted AQI")
        plt.xlabel("Actual AQI")
        plt.ylabel("Predicted AQI")            
        plt.tight_layout()
        plt.show()


def visualize(df):
    plot_aqi_distribution(df)
    plot_correlation_heatmap(df)
