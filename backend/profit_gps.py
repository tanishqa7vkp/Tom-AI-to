
from pydantic import BaseModel, Field
from typing import Literal


class FarmConditions(BaseModel):
    crop: str
    temperature_c: float
    humidity_percent: float = Field(ge=0, le=100)
    rainfall_mm: float = Field(ge=0)
    area_acres: float = Field(gt=0)


def calculate_profit_gps(data: FarmConditions):
    recommendations = []

    if data.humidity_percent >= 80 and data.rainfall_mm >= 10:
        recommendations.append({
      "action": get_crop_specific_action(data.crop, "high_humidity") or "Inspect your crop for signs of fungal disease today.",
            "reason": "High humidity and rainfall can increase fungal disease risk.",
            "priority": "HIGH",
            "score": 90
        })

    if data.temperature_c >= 35:
        recommendations.append({
            "action": get_crop_specific_action(data.crop, "high_temperature") or "Check soil moisture and consider irrigation if needed.",
            "reason": "High temperatures can increase crop water stress.",
            "priority": "HIGH",
            "score": 85
        })

    if data.rainfall_mm >= 40:
        recommendations.append({
            "action": get_crop_specific_action(data.crop, "heavy_rain") or "Inspect drainage and check for standing water.",
            "reason": "Heavy rainfall can cause waterlogging.",
            "priority": "HIGH",
            "score": 88
        })

    if not recommendations:
        recommendations.append({
            "action": "Inspect your crop and monitor soil moisture today.",
            "reason": "No major weather-based warning was triggered.",
            "priority": "LOW",
            "score": 30
        })

    # Connect each weather warning to its financial impact.
    risk_types = {
        "high_humidity": (
            data.humidity_percent >= 80 and data.rainfall_mm >= 10
        ),
        "high_temperature": data.temperature_c >= 35,
        "heavy_rain": data.rainfall_mm >= 40
    }

    active_risks = [
        risk_type
        for risk_type, triggered in risk_types.items()
        if triggered
    ]

    # Recommendations were added in the same order as these risks.
    for recommendation, risk_type in zip(recommendations, active_risks):
        impact = estimate_profit_impact(
            data.crop,
            data.area_acres,
            risk_type
        )

        recommendation["financial_impact"] = impact
        recommendation["risk_type"] = risk_type

    
    recommendations.sort(
        key=lambda item: (
            (item.get("financial_impact") or {}).get(
                "potential_loss_avoided_inr", 0
            ),
            item["score"]
        ),
        reverse=True
    )

    )

    return {
        "crop": data.crop,
        "top_action": recommendations[0],
        "other_actions": recommendations[1:],
        "note": "Initial weather-rule recommendations; not a validated financial forecast."
    }

import json
from urllib.request import urlopen
from urllib.parse import urlencode


def get_live_weather(latitude: float, longitude: float):
    params = urlencode({
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m,relative_humidity_2m,precipitation",
        "timezone": "auto"
    })

    url = f"https://api.open-meteo.com/v1/forecast?{params}"

    with urlopen(url, timeout=10) as response:
        data = json.load(response)

    current = data["current"]

    return {
        "temperature_c": current["temperature_2m"],
        "humidity_percent": current["relative_humidity_2m"],
        "rainfall_mm": current["precipitation"]
    }



CROP_ADVICE = {
    "tomato": {
        "high_humidity": "Inspect tomato leaves for spots, lesions, or signs of fungal disease.",
        "high_temperature": "Check tomato soil moisture and look for wilting or heat stress.",
        "heavy_rain": "Check tomato beds for waterlogging and ensure drainage is clear."
    },
    "rice": {
        "high_humidity": "Inspect rice plants for unusual leaf spots or disease symptoms.",
        "high_temperature": "Check field water levels and watch for heat stress.",
        "heavy_rain": "Inspect paddy bunds and drainage channels for overflow."
    },
    "wheat": {
        "high_humidity": "Inspect wheat leaves for rust-like symptoms or unusual discoloration.",
        "high_temperature": "Check wheat soil moisture and assess heat stress.",
        "heavy_rain": "Inspect wheat fields for standing water and drainage problems."
    }
}


def get_crop_specific_action(crop: str, risk_type: str):
    crop_key = crop.strip().lower()

    advice = CROP_ADVICE.get(crop_key)

    if advice is None:
        return None

    return advice.get(risk_type)

    
# Demo-only assumptions, NOT verified market prices.
# Expected yield: kilograms per acre.
DEMO_CROP_ECONOMICS = {
    "tomato": {"yield_kg_per_acre": 8000, "price_per_kg": 15},
    "rice": {"yield_kg_per_acre": 2000, "price_per_kg": 25},
    "wheat": {"yield_kg_per_acre": 1800, "price_per_kg": 25}
}

# Illustrative potential loss and preventable fraction.
DEMO_RISK_FACTORS = {
    "high_humidity": {"loss_fraction": 0.08, "preventable_fraction": 0.30},
    "high_temperature": {"loss_fraction": 0.06, "preventable_fraction": 0.25},
    "heavy_rain": {"loss_fraction": 0.10, "preventable_fraction": 0.35}
}


def estimate_profit_impact(crop: str, area_acres: float, risk_type: str):
    economics = DEMO_CROP_ECONOMICS.get(crop.strip().lower())
    risk = DEMO_RISK_FACTORS.get(risk_type)

    if economics is None or risk is None:
        return None

    estimated_crop_value = (
        area_acres
        * economics["yield_kg_per_acre"]
        * economics["price_per_kg"]
    )

    potential_loss = estimated_crop_value * risk["loss_fraction"]

    avoidable_loss = potential_loss * risk["preventable_fraction"]

    return {
        "estimated_crop_value_inr": round(estimated_crop_value),
        "potential_loss_inr": round(potential_loss),
        "potential_loss_avoided_inr": round(avoidable_loss),
        "currency": "INR",
        "estimate_type": "illustrative_demo_only",
        "assumptions": {
            **economics,
            **risk
        }
    }

