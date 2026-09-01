1. Introduction

Air pollution is one of the major environmental challenges faced by rapidly developing cities. Air quality can vary significantly from one neighborhood to another because of factors such as traffic, industrial activities, construction, weather conditions, and local environmental conditions. A single AQI value for an entire city may therefore fail to represent the actual pollution conditions experienced by people in different areas.

The City-Scale Air Quality & Health Risk Intelligence System is a machine-learning-based system designed to provide more detailed air-quality intelligence at the neighborhood level. The system uses air pollutants such as PM2.5, PM10, NO₂, SO₂, CO and O₃ along with meteorological and contextual information such as temperature, humidity, wind speed, wind direction, traffic volume, weather conditions and historical AQI.

The proposed system aims to predict future air-quality conditions for different locations, identify possible pollution sources, and estimate an educational health-risk indicator based on pollution, exposure and person category. It can help users understand where pollution is high, why it may be high, what conditions may occur in the future, and which groups may require greater protection.


2. Problem Statement

Traditional air-quality monitoring systems generally provide pollution information for a city or a limited number of monitoring stations. Such information may not accurately represent pollution levels in individual neighborhoods because pollution varies according to traffic, industrial activity, construction, weather and other local factors.

For example, one neighborhood may experience high pollution because of heavy traffic, while another may be affected primarily by industrial activity or construction. The uploaded project concept specifically aims to move beyond simply stating that a city's air quality is poor and instead determine which neighborhoods are most polluted, why they are polluted, who may be at risk, what may happen in the future, and what actions could potentially reduce pollution.

Therefore, the solution is to develop a machine-learning-based system that can:

Predict air-quality conditions at the neighborhood level.
Use historical, environmental and contextual data to improve predictions.
Identify possible contributors to pollution using multiple data sources.
Estimate health-risk indicators for different categories of people.
Provide useful information for individuals and local authorities.


3. Objectives

The major objectives of the project are:

1. Neighborhood-level air-quality prediction

To develop a machine-learning model capable of predicting air-quality conditions for different neighborhoods rather than providing only a single city-wide prediction.

2. Use multiple environmental factors

To utilize pollutant, weather, traffic and historical air-quality data to improve the prediction process.

3. Future pollution prediction

To predict upcoming air-quality conditions so that people and authorities can take preventive measures.

4. Pollution-source identification

To analyze multiple data sources such as traffic, weather, industrial activity and pollution measurements to estimate possible contributors to pollution.

5. Health-risk estimation

To develop an educational risk indicator that combines air quality, exposure and person category to estimate relative health risk.

6. Support decision-making

To provide useful pollution-related information that can assist citizens and local authorities in understanding pollution patterns and considering protective or preventive actions.

7. Explore intervention impact

To explore the potential impact of pollution-control interventions using analytical/causal methods, as proposed in the project concept.


4. Existing System

Existing air-quality monitoring systems primarily depend on pollution-monitoring stations and provide information such as current AQI, pollutant concentrations and general air-quality categories.

A typical system may provide information such as:

Kolkata AQI = 90

However, this approach has several limitations.

Limitations of the Existing System

1. City-level information

The same AQI value may be presented for a large geographical area even though pollution levels can vary considerably between neighborhoods.

2. Limited prediction capability

Many basic systems focus primarily on current or historical air-quality information rather than predicting future conditions.

3. Limited pollution-source analysis

A basic AQI system may tell users how polluted an area is without explaining the possible contributors to that pollution.

4. No personalized risk indication

Different people may have different levels of exposure and vulnerability. Children, elderly people, outdoor workers and people who exercise outdoors may experience different levels of exposure.

5. Limited decision support

Traditional systems generally do not combine pollution, weather, traffic and exposure information into a unified intelligence system.

Therefore, there is a need for a more comprehensive ML-based approach.

5. Proposed System

The proposed City-Scale Air Quality & Health Risk Intelligence System uses machine learning and multiple data sources to create a more detailed air-quality prediction system.

The system will collect and preprocess data related to:

PM2.5
PM10
NO₂
SO₂
CO
O₃
Temperature
Humidity
Wind speed
Wind direction
Traffic volume
Weather conditions
Historical AQI

These variables will be processed and supplied to machine-learning models for predicting air-quality conditions at different locations.

Main components of the proposed system

1. Data Collection

Collect historical air-quality, weather, traffic and location-related data.

2. Data Preprocessing

Handle missing values, incorrect values, duplicates and outliers and prepare the dataset for machine learning.

3. Exploratory Data Analysis

Analyze relationships between pollutants, weather conditions, traffic and air quality.

4. Feature Engineering

Create useful features from the available environmental and historical data.

5. Machine Learning

Train and evaluate appropriate ML models to predict air-quality conditions.

6. Pollution Source Analysis

Analyze relationships between pollution and factors such as traffic, industrial activity, construction and weather. The project document notes that source percentages should be treated as model estimates rather than automatically proven facts.

7. Health Risk Indicator

Combine pollution level, exposure and person category to produce an educational risk score rather than a medical diagnosis.

8. Decision Support

Provide predictions and insights that can help users understand pollution conditions and take appropriate protective actions.