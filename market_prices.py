"""
Market prices utility - fetches mandi prices
Uses Agmarknet API or returns offline MSP data
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()


# MSP data 2024-25 as offline fallback
MSP_2024_25 = {
    "Wheat": 2275,
    "Rice": 2300,
    "Paddy": 2300,
    "Cotton": 7121,
    "Maize": 2225,
    "Soybean": 4892,
    "Mustard": 5950,
    "Groundnut": 6783,
    "Arhar (Toor)": 7550,
    "Moong": 8682,
    "Urad": 7400,
    "Sunflower": 7280,
    "Safflower": 5800,
    "Jowar (Hybrid)": 3371,
    "Bajra": 2625,
    "Sesame": 9267,
    "Sugarcane": 340,  # Per quintal FRP
}

# Simulated mandi data (in real app, fetch from agmarknet API)
SAMPLE_MANDI_DATA = {
    "Andhra Pradesh": {
        "Tomato": {
            "Kurnool Mandi": {"min_price": 800, "max_price": 1800, "modal_price": 1200},
            "Guntur Mandi": {"min_price": 700, "max_price": 1600, "modal_price": 1100},
            "Vijayawada Mandi": {"min_price": 900, "max_price": 2000, "modal_price": 1400},
        },
        "Rice": {
            "Nellore Mandi": {"min_price": 2100, "max_price": 2500, "modal_price": 2300},
            "Kakinada Mandi": {"min_price": 2200, "max_price": 2600, "modal_price": 2400},
        },
        "Cotton": {
            "Guntur Mandi": {"min_price": 6500, "max_price": 7500, "modal_price": 7000},
            "Adoni Mandi": {"min_price": 6800, "max_price": 7800, "modal_price": 7200},
        },
    },
    "Telangana": {
        "Tomato": {
            "Gaddiannaram Mandi": {"min_price": 1000, "max_price": 2200, "modal_price": 1600},
            "Hyderabad Mandi": {"min_price": 1200, "max_price": 2500, "modal_price": 1800},
        },
        "Cotton": {
            "Warangal Mandi": {"min_price": 6800, "max_price": 7600, "modal_price": 7100},
            "Nizamabad Mandi": {"min_price": 6600, "max_price": 7400, "modal_price": 6900},
        },
    },
    "Maharashtra": {
        "Onion": {
            "Lasalgaon Mandi": {"min_price": 800, "max_price": 2000, "modal_price": 1400},
            "Nashik Mandi": {"min_price": 900, "max_price": 2200, "modal_price": 1500},
        },
        "Wheat": {
            "Pune Mandi": {"min_price": 2100, "max_price": 2500, "modal_price": 2300},
        },
    },
    "Punjab": {
        "Wheat": {
            "Ludhiana Mandi": {"min_price": 2200, "max_price": 2600, "modal_price": 2400},
            "Amritsar Mandi": {"min_price": 2100, "max_price": 2500, "modal_price": 2300},
        },
        "Rice": {
            "Patiala Mandi": {"min_price": 2100, "max_price": 2500, "modal_price": 2300},
        },
    },
}


def get_market_prices(state: str, crop: str) -> dict:
    """
    Get market prices for a crop in a state.
    Returns mandi-wise prices.
    """
    if state in SAMPLE_MANDI_DATA and crop in SAMPLE_MANDI_DATA[state]:
        return SAMPLE_MANDI_DATA[state][crop]
    
    # Return MSP if no specific data
    if crop in MSP_2024_25:
        return {
            "MSP (Minimum Support Price)": {
                "min_price": MSP_2024_25[crop],
                "max_price": MSP_2024_25[crop],
                "modal_price": MSP_2024_25[crop]
            }
        }
    
    return {}


def get_msp_data() -> dict:
    """Return all MSP data."""
    return MSP_2024_25
