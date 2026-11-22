# System & Project Requirements

## 1. Hardware Requirements
| Component | Requirement |
| :--- | :--- |
| **Processor** | Intel Core i5 or equivalent |
| **RAM** | Minimum 8 GB, 16 GB recommended |
| **Storage** | At least 10 GB free space |
| **GPU** | Not required for basic ML models |
| **Internet** | Required for downloading datasets/libraries |

Primary architecture is a Python-based ML intelligence pipeline; dedicated GPU hardware is not required.

## 2. Software Requirements
| Software / Technology | Purpose |
| :--- | :--- |
| **Python** | Main programming language |
| **NumPy** | Numerical computation |
| **Pandas** | Data manipulation and preprocessing |
| **Matplotlib** | Data visualization |
| **Seaborn** | Exploratory data analysis |
| **Scikit-learn** | Machine learning regression |
| **SciPy** | Statistical analysis |
| **Flask** | Web server and REST API |
| **Streamlit** | Interactive companion dashboard |
| **Joblib/Pickle** | Serializing and loading trained models |

## 3. Functional Requirements
The system provides capabilities to:
1. Load and process air-quality datasets.
2. Clean and preprocess collected sensor data.
3. Analyze pollutant and environmental variables.
4. Perform exploratory data analysis and correlation mapping.
5. Engineer relevant features.
6. Train machine-learning models.
7. Evaluate model performance metrics (MAE, MSE, RMSE, R²).
8. Predict air-quality conditions from chemical pollutant inputs.
9. Identify threat driver pollutants against standard NAAQS thresholds.
10. Estimate pollution source contributions and atmospheric diagnostics.
11. Generate educational health-risk indicators and advisories.
12. Export executive reports in PDF, JSON, and summary clipboard formats.
