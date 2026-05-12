"""Language-family grammar routing for CIELingo v2.3."""
from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, List
import json

def load_language_families(path: str | Path) -> Dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))
def load_language_profiles(path: str | Path) -> Dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))
def find_family_for_language(language_code: str, families: Dict[str, Any]) -> Dict[str, Any]:
    for family in families.get("families", []):
        for language in family.get("languages", []):
            if language.get("code") == language_code: return family
    return {"id": "UNRESOLVED_LANGUAGE_FAMILY", "algorithm_modules": [], "core_axes": []}
def get_language_profile(language_code: str, profiles: Dict[str, Any], variant: str = "standard") -> Dict[str, Any]:
    profile = profiles.get("profiles", {}).get(f"language:{language_code}:{variant}")
    if profile is None and variant != "standard": profile = profiles.get("profiles", {}).get(f"language:{language_code}:standard")
    return profile or {"id": "UNRESOLVED_LANGUAGE_PROFILE", "language": language_code, "variant": variant, "required_modules": []}
def grammar_algorithm_stack(language_code: str, families: Dict[str, Any], profiles: Dict[str, Any], variant: str = "standard") -> Dict[str, Any]:
    family = find_family_for_language(language_code, families); profile = get_language_profile(language_code, profiles, variant)
    modules: List[str] = []
    for item in family.get("algorithm_modules", []) + profile.get("required_modules", []):
        if item not in modules: modules.append(item)
    unresolved = []
    if family.get("id") == "UNRESOLVED_LANGUAGE_FAMILY": unresolved.append("UNRESOLVED_LANGUAGE_FAMILY")
    if profile.get("id") == "UNRESOLVED_LANGUAGE_PROFILE": unresolved.append("UNRESOLVED_LANGUAGE_PROFILE")
    return {"language": language_code, "variant": variant, "family": family.get("id"), "grammar_strategy": profile.get("grammar_strategy", "UNRESOLVED_GRAMMAR_STRATEGY"), "modules": modules, "unresolved": unresolved}
