from typing import Dict, Any, List, Optional

# CPCB / NAAQS 24-hour standard limits
NAAQS_STANDARDS = {
    "PM2.5": {"limit": 60.0, "unit": "µg/m³", "name": "Particulate Matter 2.5", "type": "Fine Inhalable Particles"},
    "PM10": {"limit": 100.0, "unit": "µg/m³", "name": "Particulate Matter 10", "type": "Coarse Inhalable Particles"},
    "NO2": {"limit": 80.0, "unit": "µg/m³", "name": "Nitrogen Dioxide", "type": "Combustion Gas"},
    "NO": {"limit": 50.0, "unit": "µg/m³", "name": "Nitric Oxide", "type": "Primary Combustion Byproduct"},
    "NOx": {"limit": 100.0, "unit": "µg/m³", "name": "Total Nitrogen Oxides", "type": "Oxides of Nitrogen"},
    "NH3": {"limit": 400.0, "unit": "µg/m³", "name": "Ammonia", "type": "Agricultural / Waste Byproduct"},
    "CO": {"limit": 2.0, "unit": "mg/m³", "name": "Carbon Monoxide", "type": "Incomplete Combustion Gas"},
    "SO2": {"limit": 80.0, "unit": "µg/m³", "name": "Sulfur Dioxide", "type": "Fossil Fuel & Industrial Gas"},
    "O3": {"limit": 100.0, "unit": "µg/m³", "name": "Ground-Level Ozone", "type": "Secondary Photochemical Oxidant"},
    "Benzene": {"limit": 5.0, "unit": "µg/m³", "name": "Benzene (VOC)", "type": "Carcinogenic Hydrocarbon"},
    "Toluene": {"limit": 50.0, "unit": "µg/m³", "name": "Toluene (VOC)", "type": "Industrial Solvent & Hydrocarbon"},
}

# Detailed Profiles for Pollutants
POLLUTANT_PROFILES = {
    "PM2.5": {
        "sources": ["Vehicular exhaust (especially diesel)", "Biomass & stubble burning", "Coal-fired power plants", "Secondary chemical aerosols"],
        "health_impact": "Deep alveolar lung penetration, enters bloodstream, aggravates cardiovascular and pulmonary disease.",
        "mitigation": "Enforce diesel particulate filters, curb crop residue burning, deploy localized air purification."
    },
    "PM10": {
        "sources": ["Road dust resuspension", "Construction & demolition activities", "Mechanical grinding/crushing", "Windblown barren soil"],
        "health_impact": "Deposits in upper airways, triggers severe asthma, bronchitis, and eye/throat irritation.",
        "mitigation": "Deploy mechanized road sweepers, anti-smog mist water cannons at construction sites, pave loose road shoulders."
    },
    "NO2": {
        "sources": ["High-temperature motor vehicle engines", "Thermal power stations", "Industrial boilers"],
        "health_impact": "Causes airway inflammation, exacerbates childhood asthma, and lowers immunity to lung infections.",
        "mitigation": "Promote EV adoption, impose strict vehicular emission testing (PUC), implement low-emission traffic zones."
    },
    "NO": {
        "sources": ["Immediate tailpipe exhaust", "Industrial thermal combustion", "Gas turbine engines"],
        "health_impact": "Rapidly oxidizes to NO2 in ambient air; contributes directly to tropospheric ozone and acid rain formation.",
        "mitigation": "Optimize engine combustion timing and install selective catalytic reduction (SCR) catalysts."
    },
    "NOx": {
        "sources": ["Heavy freight transport", "Diesel locomotives and machinery", "Cement and steel production facilities"],
        "health_impact": "Precursor to secondary fine nitrate particles and ground-level smog; severely damages lung tissue over time.",
        "mitigation": "Restrict heavy commercial vehicle entry during peak hours and mandate industrial flue gas denitrification."
    },
    "CO": {
        "sources": ["Incomplete fuel combustion in idling vehicles", "Open waste burning", "Residential biomass cookstoves"],
        "health_impact": "Binds with hemoglobin to form carboxyhemoglobin, impairing oxygen delivery to the heart and brain.",
        "mitigation": "Synchronize urban traffic signals to minimize stop-and-go congestion; ban open municipal solid waste burning."
    },
    "SO2": {
        "sources": ["Coal-fired thermal power plants", "Petroleum refining", "Smelters & metal processing", "High-sulfur fuel oils"],
        "health_impact": "Triggers immediate bronchoconstriction, chronic bronchitis, and forms corrosive secondary sulfate aerosols.",
        "mitigation": "Mandate Flue Gas Desulfurization (FGD) systems in thermal plants and transition industries to cleaner piped natural gas (PNG)."
    },
    "O3": {
        "sources": ["Photochemical reactions between sunlight, NOx, and Volatile Organic Compounds (VOCs)"],
        "health_impact": "Powerful oxidizing agent that inflames airways, reduces lung capacity, and damages vegetation and crops.",
        "mitigation": "Curtail midday precursor emissions (VOC vapor recovery at gas stations, NOx limits on manufacturing)."
    },
    "NH3": {
        "sources": ["Agricultural fertilizer volatilization", "Livestock manure management", "Decomposing urban sewage and landfills"],
        "health_impact": "Pungent respiratory irritant; reacts with nitric and sulfuric acids in air to form fine secondary ammonium salts.",
        "mitigation": "Improve fertilizer application practices, cover manure storage, and upgrade municipal wastewater treatment facilities."
    },
    "Benzene": {
        "sources": ["Evaporative losses from fuel pumps", "Gasoline exhaust", "Petrochemical manufacturing"],
        "health_impact": "Group 1 human carcinogen associated with leukemia and bone marrow dysfunction.",
        "mitigation": "Install Stage II vapor recovery nozzles at fueling stations and enforce solvent recovery in chemical plants."
    },
    "Toluene": {
        "sources": ["Industrial paints, thinners, and adhesives", "Printing operations", "Automotive refinishing"],
        "health_impact": "Affects the central nervous system, causing dizziness, headaches, and irritation of mucous membranes.",
        "mitigation": "Promote water-based coatings and enclosed solvent recovery ventilation systems."
    }
}


def identify_pollutants(input_data: Dict[str, float], sub_indices: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
    """
    Identifies and classifies all input pollutants against national ambient benchmarks,
    highlighting the primary driver, secondary contributors, and standard exceedances.
    """
    if sub_indices is None:
        sub_indices = {}

    pollutant_evaluations = []
    exceeded_pollutants = []

    for key, meta in NAAQS_STANDARDS.items():
        val = input_data.get(key)
        if val is None:
            continue
        
        try:
            val_float = float(val)
        except (ValueError, TypeError):
            continue

        limit = meta["limit"]
        ratio = round(val_float / limit, 2)
        sub_idx = sub_indices.get(key)

        # Status categorization based on exceedance ratio and sub-index
        if ratio > 2.0 or (sub_idx and sub_idx > 300):
            status = "Critical Exceedance"
            status_level = "critical"
            badge_color = "#EF4444"
            badge_bg = "rgba(239, 68, 68, 0.15)"
        elif ratio > 1.0 or (sub_idx and sub_idx > 200):
            status = "Moderate Exceedance"
            status_level = "elevated"
            badge_color = "#F97316"
            badge_bg = "rgba(249, 115, 22, 0.15)"
        elif ratio > 0.75 or (sub_idx and sub_idx > 100):
            status = "Watch / Elevated"
            status_level = "watch"
            badge_color = "#F59E0B"
            badge_bg = "rgba(245, 158, 11, 0.15)"
        else:
            status = "Within Permissible Limit"
            status_level = "safe"
            badge_color = "#10B981"
            badge_bg = "rgba(16, 185, 129, 0.15)"

        profile = POLLUTANT_PROFILES.get(key, {})

        eval_item = {
            "key": key,
            "name": meta["name"],
            "type": meta["type"],
            "concentration": round(val_float, 2),
            "unit": meta["unit"],
            "standard_limit": limit,
            "exceedance_ratio": ratio,
            "sub_index": sub_idx,
            "status": status,
            "status_level": status_level,
            "badge_color": badge_color,
            "badge_bg": badge_bg,
            "health_impact": profile.get("health_impact", "Ambient respiratory exposure."),
            "sources": profile.get("sources", ["General combustion"]),
            "mitigation": profile.get("mitigation", "Source reduction measures.")
        }

        pollutant_evaluations.append(eval_item)

        if ratio > 1.0:
            exceeded_pollutants.append(eval_item)

    # Sort evaluations by severity (exceedance ratio descending, then sub-index)
    pollutant_evaluations.sort(
        key=lambda x: (x["sub_index"] if x["sub_index"] is not None else 0, x["exceedance_ratio"]),
        reverse=True
    )

    primary_driver = pollutant_evaluations[0] if pollutant_evaluations else None
    secondary_drivers = [p for p in pollutant_evaluations[1:] if p["status_level"] in ["critical", "elevated", "watch"]]

    return {
        "primary_driver": primary_driver,
        "secondary_drivers": secondary_drivers[:3],
        "exceeded_pollutants": exceeded_pollutants,
        "all_evaluations": pollutant_evaluations,
        "total_exceeded": len(exceeded_pollutants)
    }


def analyze_pollution_sources(input_data: Dict[str, float]) -> Dict[str, Any]:
    """
    Performs atmospheric ratio analysis and estimates percentage contributions from:
    1. Vehicular Traffic
    2. Construction & Resuspended Road Dust
    3. Industrial & Power Generation Combustion
    4. Biomass Burning & Agricultural Waste
    5. Photochemical Secondary Smog
    """
    pm25 = max(0.0, float(input_data.get("PM2.5", 0.0) or 0.0))
    pm10 = max(0.0, float(input_data.get("PM10", 0.0) or 0.0))
    no2 = max(0.0, float(input_data.get("NO2", 0.0) or 0.0))
    no = max(0.0, float(input_data.get("NO", 0.0) or 0.0))
    nox = max(0.0, float(input_data.get("NOx", 0.0) or 0.0))
    co = max(0.0, float(input_data.get("CO", 0.0) or 0.0))
    so2 = max(0.0, float(input_data.get("SO2", 0.0) or 0.0))
    o3 = max(0.0, float(input_data.get("O3", 0.0) or 0.0))
    nh3 = max(0.0, float(input_data.get("NH3", 0.0) or 0.0))
    benzene = max(0.0, float(input_data.get("Benzene", 0.0) or 0.0))
    toluene = max(0.0, float(input_data.get("Toluene", 0.0) or 0.0))

    # Calculate atmospheric diagnostic indicators
    pm_coarse = max(0.0, pm10 - pm25)
    pm_fine_ratio = (pm25 / pm10) if pm10 > 0 else 0.5
    combustion_nox = max(no2, nox * 0.7, no * 1.2)

    # 1. Vehicular Emissions Score
    # Characterized by high NOx, CO, Benzene, Toluene and combustion fine PM
    vehicular_score = (
        (combustion_nox / 40.0) * 35.0 +
        (co / 1.5) * 25.0 +
        (pm25 / 50.0) * 20.0 +
        ((benzene + toluene) / 5.0) * 20.0
    )

    # 2. Construction & Resuspended Road Dust Score
    # Characterized by high coarse particulate fraction (PM10 - PM2.5) relative to combustion gases
    dust_score = (
        (pm_coarse / 60.0) * 70.0 +
        (max(0.0, 1.0 - pm_fine_ratio)) * 30.0
    )

    # 3. Industrial Combustion & Thermal Power Score
    # Characterized by high SO2, NOx, and moderate particulate loading
    industrial_score = (
        (so2 / 25.0) * 55.0 +
        (combustion_nox / 60.0) * 25.0 +
        (pm25 / 75.0) * 20.0
    )

    # 4. Biomass Burning & Agricultural Waste Score
    # Characterized by high PM2.5 with very high CO, elevated NH3, but moderate SO2
    biomass_score = (
        (pm25 / 70.0) * 40.0 +
        (co / 2.0) * 35.0 +
        (nh3 / 30.0) * 25.0
    )

    # 5. Photochemical Secondary Smog Score
    # Characterized by elevated Ground-level Ozone and secondary reactions
    photochemical_score = (
        (o3 / 50.0) * 60.0 +
        (combustion_nox / 50.0) * 20.0 +
        (pm25 / 60.0) * 20.0
    )

    # Prevent negative or zero sum
    raw_scores = {
        "vehicular": max(5.0, vehicular_score),
        "dust": max(5.0, dust_score),
        "industrial": max(5.0, industrial_score),
        "biomass": max(5.0, biomass_score),
        "photochemical": max(5.0, photochemical_score)
    }

    total_score = sum(raw_scores.values())
    pcts = {k: round((v / total_score) * 100, 1) for k, v in raw_scores.items()}

    # Adjust rounding discrepancy so sum is exactly 100%
    diff = round(100.0 - sum(pcts.values()), 1)
    if diff != 0:
        max_k = max(pcts, key=pcts.get)
        pcts[max_k] = round(pcts[max_k] + diff, 1)

    sources_breakdown = [
        {
            "id": "vehicular",
            "name": "Vehicular Traffic",
            "percentage": pcts["vehicular"],
            "color": "#3B82F6",
            "icon": "ph-car",
            "description": "Tailpipe combustion emissions (diesel/petrol NOx, CO, and VOCs)."
        },
        {
            "id": "dust",
            "name": "Road Dust & Construction",
            "percentage": pcts["dust"],
            "color": "#F59E0B",
            "icon": "ph-hard-hat",
            "description": "Mechanical resuspension, construction debris, and barren road dust (coarse PM10)."
        },
        {
            "id": "industrial",
            "name": "Industrial & Power Combustion",
            "percentage": pcts["industrial"],
            "color": "#EF4444",
            "icon": "ph-factory",
            "description": "Coal, heavy fuel oil, smelter and refinery emissions characterized by SO2 and NOx."
        },
        {
            "id": "biomass",
            "name": "Biomass & Waste Burning",
            "percentage": pcts["biomass"],
            "color": "#8B5CF6",
            "icon": "ph-fire",
            "description": "Open crop stubble, domestic biomass cooking, and municipal solid waste combustion."
        },
        {
            "id": "photochemical",
            "name": "Photochemical Secondary Smog",
            "percentage": pcts["photochemical"],
            "color": "#EC4899",
            "icon": "ph-sun-dim",
            "description": "Atmospheric solar reactions synthesizing ground-level ozone and secondary aerosol."
        }
    ]

    # Sort by percentage descending
    sources_breakdown.sort(key=lambda x: x["percentage"], reverse=True)
    dominant_source = sources_breakdown[0]
    secondary_source = sources_breakdown[1]

    # Generate diagnostic reasoning narrative
    narrative_parts = []
    narrative_parts.append(
        f"**{dominant_source['name']}** is identified as the foremost pollution driver, accounting for an estimated **{dominant_source['percentage']}%** of ambient impact."
    )

    if dominant_source["id"] == "vehicular":
        narrative_parts.append(
            f"The chemical profile exhibits elevated combustion markers (NO2: {no2:.1f} µg/m³, CO: {co:.2f} mg/m³), pointing strongly toward dense motor traffic, stop-and-go congestion, and diesel freight operations."
        )
    elif dominant_source["id"] == "dust":
        narrative_parts.append(
            f"A high coarse-to-fine particulate spread (PM10: {pm10:.1f} vs PM2.5: {pm25:.1f} µg/m³) indicates that unpaved roads, construction sites, and mechanical ground agitation are the dominant contributors."
        )
    elif dominant_source["id"] == "industrial":
        narrative_parts.append(
            f"Significant SO2 concentrations ({so2:.1f} µg/m³) accompanied by heavy NOx point to industrial furnace activity, thermal power generation, or high-sulfur combustion."
        )
    elif dominant_source["id"] == "biomass":
        narrative_parts.append(
            f"Elevated fine particulate PM2.5 coupled with high CO ({co:.2f} mg/m³) indicates intense biomass burning, seasonal crop residue clearance, or open waste burning."
        )
    elif dominant_source["id"] == "photochemical":
        narrative_parts.append(
            f"Pronounced ground-level ozone ({o3:.1f} µg/m³) indicates active photochemical oxidation between atmospheric sunlight and volatile precursor gases."
        )

    if secondary_source["percentage"] >= 20.0:
        narrative_parts.append(
            f"**{secondary_source['name']}** provides a strong secondary compounding effect at **{secondary_source['percentage']}%**."
        )

    diagnostic_summary = " ".join(narrative_parts)

    # Actionable interventions based on the identified profile
    interventions = []
    if dominant_source["id"] == "vehicular" or secondary_source["id"] == "vehicular":
        interventions.append("Enforce commercial vehicle entry restrictions during peak morning and evening corridors.")
        interventions.append("Intensify synchronized traffic signal corridors to curb stop-and-go idling emissions.")
    if dominant_source["id"] == "dust" or secondary_source["id"] == "dust":
        interventions.append("Deploy high-pressure water mist cannons at major civil construction projects.")
        interventions.append("Mandate covering of freight trucks transporting earth and construction aggregates.")
    if dominant_source["id"] == "industrial" or secondary_source["id"] == "industrial":
        interventions.append("Audit industrial flue gas desulfurization (FGD) and SCR emission control systems.")
        interventions.append("Encourage temporary transition of manufacturing boilers to piped natural gas (PNG).")
    if dominant_source["id"] == "biomass" or secondary_source["id"] == "biomass":
        interventions.append("Mobilize localized patrol teams to detect and extinguish open municipal waste fires.")
        interventions.append("Promote mechanized crop residue management alternatives to open stubble burning.")
    if dominant_source["id"] == "photochemical":
        interventions.append("Limit vapor-releasing chemical transfers and solvent handling to early morning or night.")

    return {
        "sources_breakdown": sources_breakdown,
        "dominant_source": dominant_source,
        "secondary_source": secondary_source,
        "diagnostic_summary": diagnostic_summary,
        "interventions": interventions[:4]
    }
