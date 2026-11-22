import os
from src.data_loader import load_data, inspect_data
from src.preprocessing import preprocess_data
from src.analysis import analyze
from src.visualization import visualize, plot_feature_importance, plot_actual_vs_predicted
from src.feature_engineering import prepare_features, prepare_full_dataset
from src.model_training import train_random_forest
from src.evaluation import evaluate_model
from src.model_saving import save_model
from src.predict import predict_aqi_full_report, FEATURE_COLUMNS


def main():
    file_path = "data/raw/city_day.csv"

    df = load_data(file_path)
    inspect_data(df)

    df = preprocess_data(df)
    os.makedirs("data/processed", exist_ok=True)
    df.to_csv("data/processed/cleaned_city_day.csv", index=False)
    print("✓ Saved cleaned dataset -> data/processed/cleaned_city_day.csv")

    analyze(df)
    visualize(df)

    print("\n--- Evaluating Model on 80/20 Train/Test Split ---")
    X_train, X_test, y_train, y_test, eval_imputer, eval_scaler = prepare_features(df)
    eval_model = train_random_forest(X_train, y_train)
    y_pred = evaluate_model(eval_model, X_test, y_test)
    plot_feature_importance(eval_model, FEATURE_COLUMNS)
    plot_actual_vs_predicted(y_test, y_pred)

    print("\n--- Fitting Final Production Model on 100% of Dataset (All Records) ---")
    X_full, y_full, full_imputer, full_scaler = prepare_full_dataset(df)
    final_model = train_random_forest(X_full, y_full)
    print(f"✓ Final Production Model trained on all {len(X_full)} records across all cities.")

    save_model(final_model, full_imputer, full_scaler)

    # Sample evaluation inference
    sample_telemetry = {
        "PM2.5": 85, "PM10": 120, "NO": 15, "NO2": 30, "NOx": 40,
        "NH3": 20, "CO": 1.2, "SO2": 10, "O3": 35, "Benzene": 2.5, "Toluene": 5
    }

    report = predict_aqi_full_report(sample_telemetry)

    print("\n" + "=" * 55)
    print("AIR QUALITY & POLLUTANT IDENTIFICATION REPORT")
    print("=" * 55)
    print(f"Predicted AQI: {report['aqi']:.1f} ({report['category']})")
    print(f"Summary: {report['summary']}")

    pol_id = report.get("pollutant_identification", {})
    primary = pol_id.get("primary_driver")
    if primary:
        print("\n[POLLUTANT IDENTIFICATION]")
        print(f"  * Primary Threat: {primary['name']} ({primary['key']})")
        print(f"  * Status: {primary['status']}")
        print(f"  * Concentration: {primary['concentration']} {primary['unit']} (Standard: {primary['standard_limit']} {primary['unit']} - {primary['exceedance_ratio']}x)")
        print(f"  * Key Health Hazard: {primary['health_impact']}")

    secondaries = pol_id.get("secondary_drivers", [])
    if secondaries:
        print(f"  * Secondary Elevated: {', '.join([f'{s['key']} ({s['exceedance_ratio']}x)' for s in secondaries])}")

    src_data = report.get("source_attribution", {})
    if src_data:
        dominant_src = src_data.get("dominant_source", {})
        print("\n[ESTIMATED SOURCE ATTRIBUTION]")
        print(f"  * Top Emission Contributor: {dominant_src.get('name')} ({dominant_src.get('percentage')}%)")
        for s in src_data.get("sources_breakdown", []):
            print(f"    - {s['name']}: {s['percentage']}%")
        print(f"\n  * Atmospheric Diagnostic:\n    {src_data.get('diagnostic_summary')}")
        print("\n  * Targeted Interventions:")
        for action in src_data.get("interventions", []):
            print(f"    - {action}")
    print("=" * 55)


if __name__ == "__main__":
    main()
