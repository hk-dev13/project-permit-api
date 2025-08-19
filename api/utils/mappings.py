"""
Utility functions for data consistency and country name normalization.
This ensures reliable data joining across different data sources (EDGAR, EEA, ISO).
"""
from __future__ import annotations

from typing import Dict, Optional, Set
import logging

logger = logging.getLogger(__name__)

# Comprehensive country name mapping for consistent data joining
# Key: normalized name, Value: set of alternative names/spellings
COUNTRY_NAME_MAPPING: Dict[str, Set[str]] = {
    "austria": {"austria", "at", "aut"},
    "belgium": {"belgium", "be", "bel"},
    "bulgaria": {"bulgaria", "bg", "bgr"},
    "croatia": {"croatia", "hr", "hrv"},
    "cyprus": {"cyprus", "cy", "cyp"},
    "czech_republic": {"czech republic", "czechia", "cz", "cze", "czech rep.", "czech_republic"},
    "denmark": {"denmark", "dk", "dnk"},
    "estonia": {"estonia", "ee", "est"},
    "finland": {"finland", "fi", "fin"},
    "france": {"france", "fr", "fra"},
    "germany": {"germany", "de", "deu", "deutschland"},
    "greece": {"greece", "gr", "grc", "hellenic republic"},
    "hungary": {"hungary", "hu", "hun"},
    "ireland": {"ireland", "ie", "irl"},
    "italy": {"italy", "it", "ita"},
    "latvia": {"latvia", "lv", "lva"},
    "lithuania": {"lithuania", "lt", "ltu"},
    "luxembourg": {"luxembourg", "lu", "lux"},
    "malta": {"malta", "mt", "mlt"},
    "netherlands": {"netherlands", "nl", "nld", "holland"},
    "poland": {"poland", "pl", "pol"},
    "portugal": {"portugal", "pt", "prt"},
    "romania": {"romania", "ro", "rou"},
    "slovakia": {"slovakia", "sk", "svk", "slovak republic"},
    "slovenia": {"slovenia", "si", "svn"},
    "spain": {"spain", "es", "esp"},
    "sweden": {"sweden", "se", "swe"},
    "united_kingdom": {"united kingdom", "uk", "gbr", "great britain", "britain", "england", "scotland", "wales"},
    "united_states": {"united states", "usa", "us", "america", "united states of america"},
    "china": {"china", "cn", "chn", "people's republic of china", "prc"},
    "japan": {"japan", "jp", "jpn"},
    "south_korea": {"south korea", "korea", "kr", "kor", "republic of korea"},
    "brazil": {"brazil", "br", "bra"},
    "india": {"india", "in", "ind"},
    "russia": {"russia", "ru", "rus", "russian federation"},
    "canada": {"canada", "ca", "can"},
    "australia": {"australia", "au", "aus"},
    "norway": {"norway", "no", "nor"},
    "switzerland": {"switzerland", "ch", "che"},
    "iceland": {"iceland", "is", "isl"},
    "turkey": {"turkey", "tr", "tur", "türkiye"},
    "mexico": {"mexico", "mx", "mex"},
    "argentina": {"argentina", "ar", "arg"},
    "south_africa": {"south africa", "za", "zaf"},
    "egypt": {"egypt", "eg", "egy"},
    "saudi_arabia": {"saudi arabia", "sa", "sau"},
    "uae": {"united arab emirates", "uae", "ae", "are"},
    "israel": {"israel", "il", "isr"},
    "new_zealand": {"new zealand", "nz", "nzl"},
    "chile": {"chile", "cl", "chl"},
    "colombia": {"colombia", "co", "col"},
    "ukraine": {"ukraine", "ua", "ukr"},
}

# Reverse mapping for fast lookup
_REVERSE_MAPPING: Dict[str, str] = {}
for canonical, variants in COUNTRY_NAME_MAPPING.items():
    for variant in variants:
        _REVERSE_MAPPING[variant.lower().strip()] = canonical


def normalize_country_name(country: Optional[str]) -> Optional[str]:
    """
    Normalize country name to a canonical form for consistent data joining.
    
    Args:
        country: Raw country name from any data source
        
    Returns:
        Canonical country name or None if input is empty/invalid
        
    Examples:
        >>> normalize_country_name("USA")
        "united_states"
        >>> normalize_country_name("Czech Republic")
        "czech_republic"
        >>> normalize_country_name("Deutschland")
        "germany"
    """
    if not country:
        return None
    
    # Clean and normalize input
    cleaned = country.strip().lower()
    cleaned = cleaned.replace("-", " ").replace("_", " ")
    
    # Direct lookup
    canonical = _REVERSE_MAPPING.get(cleaned)
    if canonical:
        return canonical
    
    # Partial matching for common patterns
    for variant, canonical in _REVERSE_MAPPING.items():
        if cleaned in variant or variant in cleaned:
            return canonical
    
    # Log unmapped countries for future improvement
    logger.debug(f"Unmapped country name: '{country}' -> '{cleaned}'")
    
    # Return cleaned version if no mapping found
    return cleaned.replace(" ", "_")


def get_country_variants(canonical_name: str) -> Set[str]:
    """
    Get all known variants for a canonical country name.
    
    Args:
        canonical_name: Canonical country name
        
    Returns:
        Set of all known variants/spellings
    """
    return COUNTRY_NAME_MAPPING.get(canonical_name, {canonical_name})


# Pollutant mapping for EDGAR client consistency
POLLUTANT_MAPPING: Dict[str, Dict[str, str]] = {
    "PM2.5": {
        "unit": "tonnes/year",
        "description": "Particulate matter < 2.5 micrometers",
        "edgar_key": "PM2_5"
    },
    "NOx": {
        "unit": "tonnes/year", 
        "description": "Nitrogen oxides",
        "edgar_key": "NOX"
    },
    "CO2": {
        "unit": "tonnes/year",
        "description": "Carbon dioxide",
        "edgar_key": "CO2"
    },
    "GWP_100_AR5_GHG": {
        "unit": "tonnes CO2 equivalent/year",
        "description": "Greenhouse gas emissions (AR5 GWP-100)",
        "edgar_key": "GWP_100_AR5_GHG"
    }
}


def normalize_pollutant_name(pollutant: Optional[str]) -> Optional[str]:
    """
    Normalize pollutant name for consistency across data sources.
    
    Args:
        pollutant: Raw pollutant name
        
    Returns:
        Canonical pollutant name or None
    """
    if not pollutant:
        return None
    
    cleaned = pollutant.strip()
    
    # Direct mapping
    for canonical, info in POLLUTANT_MAPPING.items():
        if cleaned.upper() == canonical.upper():
            return canonical
        if cleaned.upper() == info["edgar_key"].upper():
            return canonical
    
    # Common alternative names
    alternatives = {
        "particulate matter": "PM2.5",
        "pm25": "PM2.5",
        "pm_2.5": "PM2.5",
        "nitrogen oxide": "NOx",
        "nox": "NOx",
        "carbon dioxide": "CO2",
        "co2": "CO2",
        "greenhouse gas": "GWP_100_AR5_GHG",
        "ghg": "GWP_100_AR5_GHG"
    }
    
    for alt, canonical in alternatives.items():
        if alt.lower() in cleaned.lower():
            return canonical
    
    return cleaned


def validate_data_consistency(data_sources: Dict[str, any]) -> Dict[str, str]:
    """
    Validate consistency across multiple data sources and return warnings.
    
    Args:
        data_sources: Dict containing data from multiple sources
        
    Returns:
        Dict of validation warnings/issues found
    """
    warnings = {}
    
    # Check for country name consistency
    countries = []
    for source, data in data_sources.items():
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict) and "country" in item:
                    countries.append((source, item["country"]))
        elif isinstance(data, dict) and "country" in data:
            countries.append((source, data["country"]))
    
    # Group by normalized country names
    country_groups = {}
    for source, country in countries:
        normalized = normalize_country_name(country)
        if normalized not in country_groups:
            country_groups[normalized] = []
        country_groups[normalized].append((source, country))
    
    # Warn about inconsistent spellings
    for normalized, sources in country_groups.items():
        if len(set(country for _, country in sources)) > 1:
            variants = [f"{source}: '{country}'" for source, country in sources]
            warnings[f"country_spelling_{normalized}"] = f"Inconsistent spellings: {', '.join(variants)}"
    
    return warnings


__all__ = [
    "normalize_country_name",
    "get_country_variants", 
    "normalize_pollutant_name",
    "validate_data_consistency",
    "COUNTRY_NAME_MAPPING",
    "POLLUTANT_MAPPING"
]
