from __future__ import annotations

from typing import Any, Dict, List, Mapping, Optional
import math

try:
    from ...memory.coupling import COUPLING_MATRIX, CHANNEL_NAMES  # type: ignore
except Exception:
    try:
        from memory.coupling import COUPLING_MATRIX, CHANNEL_NAMES  # type: ignore
    except Exception:
        COUPLING_MATRIX = [
            [0.00, 0.45, 0.08, 0.05, 0.02, 0.25, 0.01, 0.00],
            [0.32, 0.00, 0.58, 0.35, 0.22, 0.62, 0.85, 0.12],
            [0.18, 0.52, 0.00, 0.72, 0.18, 0.38, 0.42, 0.15],
            [0.12, 0.28, 0.65, 0.00, 0.68, 0.45, 0.82, 0.35],
            [0.05, 0.20, 0.15, 0.62, 0.00, 0.32, 0.58, 0.28],
            [0.48, 0.55, 0.40, 0.48, 0.35, 0.00, 0.88, 0.45],
            [0.08, 0.78, 0.38, 0.75, 0.52, 0.82, 0.00, 0.92],
            [0.02, 0.15, 0.12, 0.32, 0.25, 0.42, 0.88, 0.00],
        ]
        CHANNEL_NAMES = [
            'M0_Perceptual', 'M1_Working', 'M2_Episodic', 'M3_Semantic',
            'M4_Procedural', 'M5_Affective_Ethical', 'M6_Identity', 'M7_Braid_Invariant',
        ]

BRAID_INDEX = 7
WORKING_INDEX = 1
EPISODIC_INDEX = 2
SEMANTIC_INDEX = 3
PROCEDURAL_INDEX = 4
AFFECTIVE_INDEX = 5
IDENTITY_INDEX = 6

_DOMAIN_PROFILES: Dict[str, Dict[str, Any]] = {
    'generic': {
        'bias': 0.85,
        'trace_channel_emphasis': {
            'M1_Working': 1.00,
            'M2_Episodic': 1.00,
            'M3_Semantic': 1.00,
            'M5_Affective_Ethical': 1.00,
            'M6_Identity': 1.00,
        },
        'summary_weight_emphasis': {
            'closure_weight': 1.00,
            'phase_lock_weight': 1.00,
            'berry_weight': 1.00,
            'ab_weight': 1.00,
            'defect_weight': 1.00,
            'regulation_weight': 1.00,
        },
        'priority_channels': ['M6_Identity', 'M3_Semantic', 'M5_Affective_Ethical'],
        'control_mode': 'balanced',
    },
    'orbital': {
        'bias': 1.00,
        'trace_channel_emphasis': {
            'M1_Working': 0.95,
            'M2_Episodic': 0.98,
            'M3_Semantic': 1.08,
            'M5_Affective_Ethical': 0.92,
            'M6_Identity': 1.16,
        },
        'summary_weight_emphasis': {
            'closure_weight': 1.18,
            'phase_lock_weight': 1.14,
            'berry_weight': 1.20,
            'ab_weight': 0.95,
            'defect_weight': 1.06,
            'regulation_weight': 1.15,
        },
        'priority_channels': ['M6_Identity', 'M3_Semantic', 'M4_Procedural'],
        'control_mode': 'orbital_lock',
    },
    'memory': {
        'bias': 0.95,
        'trace_channel_emphasis': {
            'M1_Working': 1.05,
            'M2_Episodic': 1.12,
            'M3_Semantic': 1.05,
            'M5_Affective_Ethical': 0.96,
            'M6_Identity': 1.02,
        },
        'summary_weight_emphasis': {
            'closure_weight': 1.02,
            'phase_lock_weight': 1.00,
            'berry_weight': 0.98,
            'ab_weight': 1.04,
            'defect_weight': 1.10,
            'regulation_weight': 1.04,
        },
        'priority_channels': ['M2_Episodic', 'M6_Identity', 'M3_Semantic'],
        'control_mode': 'memory_reconcile',
    },
    'ethics': {
        'bias': 0.90,
        'trace_channel_emphasis': {
            'M1_Working': 0.96,
            'M2_Episodic': 0.94,
            'M3_Semantic': 1.00,
            'M5_Affective_Ethical': 1.18,
            'M6_Identity': 1.10,
        },
        'summary_weight_emphasis': {
            'closure_weight': 1.08,
            'phase_lock_weight': 1.06,
            'berry_weight': 1.02,
            'ab_weight': 1.16,
            'defect_weight': 1.14,
            'regulation_weight': 1.10,
        },
        'priority_channels': ['M5_Affective_Ethical', 'M6_Identity', 'M3_Semantic'],
        'control_mode': 'ethical_guard',
    },
    'dialogue': {
        'bias': 0.88,
        'trace_channel_emphasis': {
            'M1_Working': 1.10,
            'M2_Episodic': 0.96,
            'M3_Semantic': 1.08,
            'M5_Affective_Ethical': 1.04,
            'M6_Identity': 1.00,
        },
        'summary_weight_emphasis': {
            'closure_weight': 0.98,
            'phase_lock_weight': 1.00,
            'berry_weight': 0.96,
            'ab_weight': 1.06,
            'defect_weight': 1.02,
            'regulation_weight': 1.00,
        },
        'priority_channels': ['M3_Semantic', 'M1_Working', 'M5_Affective_Ethical'],
        'control_mode': 'dialogue_balance',
    },
    'research': {
        'bias': 0.96,
        'trace_channel_emphasis': {
            'M1_Working': 1.08,
            'M2_Episodic': 1.02,
            'M3_Semantic': 1.14,
            'M5_Affective_Ethical': 0.92,
            'M6_Identity': 1.04,
        },
        'summary_weight_emphasis': {
            'closure_weight': 1.05,
            'phase_lock_weight': 1.02,
            'berry_weight': 1.10,
            'ab_weight': 0.94,
            'defect_weight': 1.08,
            'regulation_weight': 1.06,
        },
        'priority_channels': ['M3_Semantic', 'M6_Identity', 'M4_Procedural'],
        'control_mode': 'research_lock',
    },
}

_CARD_TEMPLATES: Dict[str, Dict[str, str]] = {
    'M1_Working': {
        'channel_code': 'M1',
        'title': 'Working braid gate',
        'purpose': 'Regulate transient salience and loop budget before nonlocal propagation.',
        'role': 'pre_gate',
        'observable': 'novelty_gate',
    },
    'M2_Episodic': {
        'channel_code': 'M2',
        'title': 'Episodic anchoring braid',
        'purpose': 'Bind recent memory traces to nonlocal recall without over-amplifying drift.',
        'role': 'memory_anchor',
        'observable': 'ab_weight',
    },
    'M3_Semantic': {
        'channel_code': 'M3',
        'title': 'Semantic closure braid',
        'purpose': 'Translate braid coherence into stable semantic closure and Berry transport.',
        'role': 'closure_bridge',
        'observable': 'berry_weight',
    },
    'M4_Procedural': {
        'channel_code': 'M4',
        'title': 'Procedural loop braid',
        'purpose': 'Carry loop discipline and repeatable orbital control into execution surfaces.',
        'role': 'loop_executor',
        'observable': 'regulation_weight',
    },
    'M5_Affective_Ethical': {
        'channel_code': 'M5',
        'title': 'Affective-ethical braid',
        'purpose': 'Modulate AB-style affective/ethical transport and soften unsafe overdrive.',
        'role': 'ethical_modulator',
        'observable': 'ab_weight',
    },
    'M6_Identity': {
        'channel_code': 'M6',
        'title': 'Identity phase braid',
        'purpose': 'Anchor phase lock against drift and preserve the canonical identity axis.',
        'role': 'phase_anchor',
        'observable': 'phase_lock_weight',
    },
}

_SCAR_RESPONSE: Dict[str, Dict[str, float]] = {
    'rupture': {
        'closure_weight': 0.78,
        'phase_lock_weight': 0.82,
        'berry_weight': 0.86,
        'ab_weight': 0.92,
        'defect_weight': 1.28,
        'regulation_weight': 1.18,
    },
    'contradiction': {
        'closure_weight': 0.82,
        'phase_lock_weight': 0.84,
        'berry_weight': 0.88,
        'ab_weight': 0.94,
        'defect_weight': 1.22,
        'regulation_weight': 1.14,
    },
    'fray': {
        'closure_weight': 0.88,
        'phase_lock_weight': 0.90,
        'berry_weight': 0.92,
        'ab_weight': 0.96,
        'defect_weight': 1.12,
        'regulation_weight': 1.08,
    },
    'drift': {
        'closure_weight': 0.90,
        'phase_lock_weight': 0.86,
        'berry_weight': 0.90,
        'ab_weight': 0.96,
        'defect_weight': 1.16,
        'regulation_weight': 1.10,
    },
    'repair': {
        'closure_weight': 1.05,
        'phase_lock_weight': 1.04,
        'berry_weight': 1.04,
        'ab_weight': 1.02,
        'defect_weight': 0.92,
        'regulation_weight': 1.00,
    },
    'adaptive': {
        'closure_weight': 1.04,
        'phase_lock_weight': 1.02,
        'berry_weight': 1.03,
        'ab_weight': 1.01,
        'defect_weight': 0.95,
        'regulation_weight': 1.00,
    },
}

_DRIFT_RESPONSE: Dict[str, Dict[str, float]] = {
    'stable': {
        'closure_weight': 1.00,
        'phase_lock_weight': 1.00,
        'berry_weight': 1.00,
        'ab_weight': 1.00,
        'defect_weight': 1.00,
        'regulation_weight': 1.00,
    },
    'elevated': {
        'closure_weight': 0.94,
        'phase_lock_weight': 0.92,
        'berry_weight': 0.95,
        'ab_weight': 0.98,
        'defect_weight': 1.08,
        'regulation_weight': 1.04,
    },
    'critical': {
        'closure_weight': 0.82,
        'phase_lock_weight': 0.80,
        'berry_weight': 0.84,
        'ab_weight': 0.90,
        'defect_weight': 1.24,
        'regulation_weight': 1.16,
    },
}


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return float(default)
        return float(value)
    except Exception:
        return float(default)


def _clamp01(value: Any) -> float:
    return max(0.0, min(1.0, _safe_float(value, 0.0)))


def _clip(value: Any, lo: float, hi: float) -> float:
    val = _safe_float(value, lo)
    return max(lo, min(hi, val))


def _drift_scalar(drift: Any) -> float:
    if isinstance(drift, (int, float)):
        return abs(float(drift))
    if isinstance(drift, Mapping):
        preferred = (
            'norm', 'drift_norm', 'mean_abs_drift', 'magnitude', 'phase_span',
            'span', 'std', 'amplitude', 'drift',
        )
        for key in preferred:
            if key in drift:
                return abs(_safe_float(drift.get(key), 0.0))
        vals = [abs(_safe_float(v, 0.0)) for v in drift.values() if isinstance(v, (int, float))]
        if vals:
            return float(sum(vals) / len(vals))
    return 0.0


def _collect_loop_metric(eba_results: Any, field: str, *, absolute: bool = False) -> float:
    if not isinstance(eba_results, Mapping):
        return 0.0
    vals = []
    for item in eba_results.values():
        if isinstance(item, Mapping):
            value = item.get(field)
        else:
            value = getattr(item, field, None)
        if value is None:
            continue
        try:
            val = float(value)
        except Exception:
            continue
        vals.append(abs(val) if absolute else val)
    return float(sum(vals) / len(vals)) if vals else 0.0


def _collect_coherent_fraction(eba_results: Any) -> float:
    if not isinstance(eba_results, Mapping):
        return 0.0
    vals = []
    for item in eba_results.values():
        if isinstance(item, Mapping):
            value = item.get('is_coherent')
        else:
            value = getattr(item, 'is_coherent', None)
        if value is None:
            continue
        vals.append(1.0 if bool(value) else 0.0)
    return float(sum(vals) / len(vals)) if vals else 0.0


def normalize_domain(domain: Any) -> str:
    key = str(domain or 'generic').strip().lower()
    if key in _DOMAIN_PROFILES:
        return key
    if 'orbit' in key or 'phase' in key or 'euler' in key:
        return 'orbital'
    if 'ethic' in key or 'safety' in key:
        return 'ethics'
    if 'memory' in key or 'recall' in key:
        return 'memory'
    if 'research' in key or 'analysis' in key or 'theory' in key:
        return 'research'
    if 'dialog' in key or 'chat' in key:
        return 'dialogue'
    return 'generic'


def domain_profile_for(domain: Any) -> Dict[str, Any]:
    profile_key = normalize_domain(domain)
    profile = dict(_DOMAIN_PROFILES[profile_key])
    profile['key'] = profile_key
    return profile


def classify_drift(drift: Any) -> str:
    magnitude = _drift_scalar(drift)
    if magnitude >= 1.2:
        return 'critical'
    if magnitude >= 0.45:
        return 'elevated'
    return 'stable'


def _normalize_scar_taxonomy(scar_taxonomy: Any) -> Dict[str, int]:
    if not isinstance(scar_taxonomy, Mapping):
        return {}
    out: Dict[str, int] = {}
    for key, value in scar_taxonomy.items():
        try:
            count = int(value)
        except Exception:
            continue
        if count <= 0:
            continue
        out[str(key).strip().lower()] = count
    return out


def _dominant_scar_class(scar_taxonomy: Mapping[str, int], dominant: Any = None) -> Optional[str]:
    if dominant is not None:
        val = str(dominant).strip().lower()
        if val:
            return val
    if not scar_taxonomy:
        return None
    return max(scar_taxonomy.items(), key=lambda item: (int(item[1]), item[0]))[0]


def _merge_multipliers(*maps: Mapping[str, float]) -> Dict[str, float]:
    base = {
        'closure_weight': 1.0,
        'phase_lock_weight': 1.0,
        'berry_weight': 1.0,
        'ab_weight': 1.0,
        'defect_weight': 1.0,
        'regulation_weight': 1.0,
    }
    for mapping in maps:
        for key, value in mapping.items():
            if key in base:
                base[key] *= _safe_float(value, 1.0)
    return base


def _card_signal_value(card_observable: str, weights: Mapping[str, Any], signals: Mapping[str, Any]) -> float:
    if card_observable in weights:
        return _clamp01(weights.get(card_observable))
    fallback_map = {
        'novelty_gate': 'coherence_gate',
        'ab_weight': 'scar_pressure',
        'berry_weight': 'mean_phasor_abs',
        'phase_lock_weight': 'coherence',
        'regulation_weight': 'loop_density',
    }
    return _clamp01(signals.get(fallback_map.get(card_observable, 'coherence'), 0.0))


def braid_channel_couplings() -> Dict[str, Dict[str, float]]:
    couplings: Dict[str, Dict[str, float]] = {}
    for idx, name in enumerate(CHANNEL_NAMES):
        if idx == BRAID_INDEX:
            continue
        braid_to_channel = _safe_float(COUPLING_MATRIX[idx][BRAID_INDEX], 0.0)
        channel_to_braid = _safe_float(COUPLING_MATRIX[BRAID_INDEX][idx], 0.0)
        couplings[str(name)] = {
            'braid_to_channel': braid_to_channel,
            'channel_to_braid': channel_to_braid,
            'reciprocity': 0.5 * (braid_to_channel + channel_to_braid),
        }
    return couplings


def build_braid_nonlocal_cards(
    *,
    domain: Any,
    channels: Mapping[str, Mapping[str, Any]],
    weights: Mapping[str, Any],
    signals: Mapping[str, Any],
    scar_taxonomy: Optional[Mapping[str, int]] = None,
    dominant_scar_class: Any = None,
    drift_class: Optional[str] = None,
) -> List[Dict[str, Any]]:
    profile = domain_profile_for(domain)
    scar_taxonomy = _normalize_scar_taxonomy(scar_taxonomy)
    dominant_scar = _dominant_scar_class(scar_taxonomy, dominant_scar_class)
    drift_class = drift_class or classify_drift(signals.get('drift_scalar'))

    cards: List[Dict[str, Any]] = []
    for channel_name, reciprocity_payload in channels.items():
        if channel_name not in _CARD_TEMPLATES:
            continue
        template = _CARD_TEMPLATES[channel_name]
        reciprocity = _clamp01(reciprocity_payload.get('reciprocity', 0.0))
        emphasis = _safe_float(profile.get('trace_channel_emphasis', {}).get(channel_name, 1.0), 1.0)
        observable = template['observable']
        observable_value = _card_signal_value(observable, weights, signals)
        priority_boost = 1.12 if channel_name in profile.get('priority_channels', []) else 1.0
        activation = _clip(reciprocity * emphasis * observable_value * priority_boost, 0.0, 1.0)
        if activation <= 0.0:
            continue
        card_id = f"BNC-{profile['key'].upper()}-{template['channel_code']}-{observable.replace('_weight', '').replace('_gate', '').upper()}"
        cards.append({
            'card_id': card_id,
            'domain': profile['key'],
            'channel': channel_name,
            'title': template['title'],
            'purpose': template['purpose'],
            'operational_role': template['role'],
            'observable': observable,
            'activation_weight': activation,
            'reciprocity': reciprocity,
            'channel_emphasis': emphasis,
            'recommended_mode': profile.get('control_mode', 'balanced'),
            'dominant_scar_class': dominant_scar,
            'drift_class': drift_class,
            'scar_taxonomy': dict(scar_taxonomy),
        })
    cards.sort(key=lambda rec: (-float(rec['activation_weight']), rec['card_id']))
    return cards


def build_orbital_braid_diagnostics(
    coupling: Optional[Mapping[str, Any]],
    *,
    closure_score: float = 0.0,
) -> Dict[str, Any]:
    if not isinstance(coupling, Mapping):
        return {
            'active': False,
            'status': 'inactive',
            'recommended_mode': 'noop',
            'alerts': [],
            'top_card_ids': [],
        }

    weights = coupling.get('weights', {}) if isinstance(coupling.get('weights'), Mapping) else {}
    signals = coupling.get('signals', {}) if isinstance(coupling.get('signals'), Mapping) else {}
    cards = coupling.get('cards', []) if isinstance(coupling.get('cards'), list) else []
    profile = coupling.get('domain_profile', {}) if isinstance(coupling.get('domain_profile'), Mapping) else {}

    closure_weight = _clamp01(weights.get('closure_weight', signals.get('coherence_gate', 0.0)))
    phase_lock_weight = _clamp01(weights.get('phase_lock_weight', 0.0))
    regulation_weight = _clamp01(weights.get('regulation_weight', 0.0))
    defect_weight = _clamp01(weights.get('defect_weight', signals.get('defect_sensitivity', 0.0)))
    drift_class = str(coupling.get('drift_class') or classify_drift(signals.get('drift_scalar')))
    dominant_scar = coupling.get('dominant_scar_class')

    effective_closure = _clamp01(_safe_float(closure_score, 0.0) * max(closure_weight, 0.05))
    stability_index = _clamp01(0.45 * effective_closure + 0.35 * phase_lock_weight + 0.20 * (1.0 - defect_weight))

    alerts: List[str] = []
    if defect_weight >= 0.70:
        alerts.append('defect_pressure')
    if drift_class != 'stable':
        alerts.append(f'drift_{drift_class}')
    if dominant_scar:
        alerts.append(f'scar_{dominant_scar}')
    if effective_closure < 0.35:
        alerts.append('weak_closure')

    if stability_index >= 0.70 and not alerts:
        status = 'stable'
    elif stability_index >= 0.42:
        status = 'watch'
    else:
        status = 'intervene'

    recommended_mode = str(profile.get('control_mode', 'balanced'))
    if status == 'intervene':
        recommended_mode = 'braid_repair'
    elif 'defect_pressure' in alerts:
        recommended_mode = 'defect_regulation'

    return {
        'active': True,
        'status': status,
        'recommended_mode': recommended_mode,
        'stability_index': stability_index,
        'effective_closure': effective_closure,
        'alerts': alerts,
        'top_card_ids': [card.get('card_id') for card in cards[:3]],
        'consumed_weights': {
            'closure_weight': closure_weight,
            'phase_lock_weight': phase_lock_weight,
            'regulation_weight': regulation_weight,
            'defect_weight': defect_weight,
        },
        'domain': profile.get('key', normalize_domain(coupling.get('domain'))),
        'drift_class': drift_class,
        'dominant_scar_class': dominant_scar,
    }


def _domain_bias(domain: Any) -> float:
    return _safe_float(domain_profile_for(domain).get('bias', 0.85), 0.85)


def compute_trace_to_nonlocal_coupling(
    braid_trace: Optional[Mapping[str, Any]],
    base_metadata: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    base = dict(base_metadata or {})
    channels = braid_channel_couplings()
    if not isinstance(braid_trace, Mapping):
        return {
            'source': 'braid_trace',
            'active': False,
            'channels': channels,
            'signals': {},
            'weights': {},
            'adjusted_metadata': base,
            'cards': [],
        }

    domain = normalize_domain(braid_trace.get('domain') or base.get('domain') or 'generic')
    profile = domain_profile_for(domain)
    emphasis = profile.get('trace_channel_emphasis', {})

    coherence = _clamp01(braid_trace.get('coherence', 0.0))
    contradiction = _clamp01(_safe_float(braid_trace.get('avg_contradiction', 0.0), 0.0) / 1.5)
    scar_count = max(0, int(_safe_float(braid_trace.get('scar_count', 0), 0.0)))
    scar_pressure = _clamp01(scar_count / max(1.0, scar_count + 3.0))
    available_budget = max(0.0, _safe_float(braid_trace.get('available_budget', 0.0), 0.0))
    budget_norm = _clamp01(available_budget)

    identity_recip = channels['M6_Identity']['reciprocity'] * _safe_float(emphasis.get('M6_Identity', 1.0), 1.0)
    semantic_recip = channels['M3_Semantic']['reciprocity'] * _safe_float(emphasis.get('M3_Semantic', 1.0), 1.0)
    episodic_recip = channels['M2_Episodic']['reciprocity'] * _safe_float(emphasis.get('M2_Episodic', 1.0), 1.0)
    affective_recip = channels['M5_Affective_Ethical']['reciprocity'] * _safe_float(emphasis.get('M5_Affective_Ethical', 1.0), 1.0)
    working_recip = channels['M1_Working']['reciprocity'] * _safe_float(emphasis.get('M1_Working', 1.0), 1.0)

    coherence_gate = _clamp01(
        (0.45 * identity_recip + 0.35 * semantic_recip + 0.20 * episodic_recip)
        * (0.40 + 0.60 * coherence)
    )
    phase_lock_weight = _clamp01(identity_recip * (0.35 + 0.65 * coherence) * (0.50 + 0.50 * budget_norm))
    affective_weight = _clamp01(affective_recip * (0.45 + 0.55 * coherence) * (1.0 - 0.35 * scar_pressure))
    novelty_gate = _clamp01((0.35 + 0.65 * working_recip) * (0.60 + 0.40 * budget_norm))
    defect_sensitivity = _clamp01((0.20 + 0.80 * scar_pressure) * (0.40 + 0.60 * max(contradiction, 1.0 - coherence)))

    salience_scale = _clip(
        _domain_bias(domain) * (0.82 + 0.28 * coherence_gate + 0.12 * affective_weight - 0.18 * defect_sensitivity),
        0.55,
        1.35,
    )
    confidence_scale = _clip(0.80 + 0.40 * phase_lock_weight - 0.25 * defect_sensitivity, 0.50, 1.40)
    novelty_scale = _clip(0.82 + 0.25 * novelty_gate - 0.12 * scar_pressure, 0.55, 1.25)

    adjusted = dict(base)
    adjusted['domain'] = domain
    adjusted['salience'] = _clip(_safe_float(base.get('salience', 0.7), 0.7) * salience_scale, 0.0, 1.0)
    adjusted['confidence'] = _clip(_safe_float(base.get('confidence', 0.7), 0.7) * confidence_scale, 0.0, 1.0)
    adjusted['novelty'] = _clip(_safe_float(base.get('novelty', 0.7), 0.7) * novelty_scale, 0.0, 1.0)
    if 'loop_budget' in base or available_budget > 0.0:
        adjusted['loop_budget'] = min(_safe_float(base.get('loop_budget', available_budget), available_budget), available_budget)
    adjusted['braid_coupling'] = {
        'phase_lock_weight': phase_lock_weight,
        'coherence_gate': coherence_gate,
        'affective_weight': affective_weight,
        'novelty_gate': novelty_gate,
        'defect_sensitivity': defect_sensitivity,
        'available_budget': available_budget,
        'scar_pressure': scar_pressure,
        'source_domain': domain,
        'domain_profile_key': profile['key'],
    }

    signals = {
        'coherence': coherence,
        'contradiction': contradiction,
        'available_budget': available_budget,
        'scar_count': scar_count,
        'scar_pressure': scar_pressure,
    }
    weights = {
        'phase_lock_weight': phase_lock_weight,
        'coherence_gate': coherence_gate,
        'affective_weight': affective_weight,
        'novelty_gate': novelty_gate,
        'defect_sensitivity': defect_sensitivity,
        'salience_scale': salience_scale,
        'confidence_scale': confidence_scale,
        'novelty_scale': novelty_scale,
    }
    cards = build_braid_nonlocal_cards(
        domain=domain,
        channels=channels,
        weights=weights,
        signals=signals,
        scar_taxonomy={},
        drift_class='stable',
    )

    return {
        'source': 'braid_trace',
        'active': True,
        'domain': domain,
        'domain_profile': profile,
        'channels': channels,
        'signals': signals,
        'weights': weights,
        'adjusted_metadata': adjusted,
        'cards': cards,
        'drift_class': 'stable',
        'scar_taxonomy': {},
        'dominant_scar_class': None,
    }


def compute_summary_to_nonlocal_coupling(
    braid_summary: Optional[Mapping[str, Any]],
    eba_results: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    channels = braid_channel_couplings()
    if not isinstance(braid_summary, Mapping):
        return {
            'source': 'braid_summary',
            'active': False,
            'channels': channels,
            'signals': {},
            'weights': {},
            'weighted_observables': {},
            'cards': [],
        }

    domain = normalize_domain(braid_summary.get('domain') or 'generic')
    profile = domain_profile_for(domain)
    scar_taxonomy = _normalize_scar_taxonomy(braid_summary.get('scar_taxonomy'))
    dominant_scar = _dominant_scar_class(scar_taxonomy, braid_summary.get('dominant_scar_class'))

    coherence = _clamp01(braid_summary.get('coherence', 0.0))
    loop_count = max(0, int(_safe_float(braid_summary.get('loop_count', 0), 0.0)))
    scar_count = max(0, int(_safe_float(braid_summary.get('scar_count', 0), 0.0)))
    mean_phasor_abs = _clamp01(braid_summary.get('mean_phasor_abs', 0.0))
    scar_pressure = _clamp01(scar_count / max(1.0, loop_count + scar_count + 1.0))
    loop_density = math.tanh(loop_count / 3.0)
    drift_scalar = _drift_scalar(braid_summary.get('drift'))
    drift_pressure = _clamp01(drift_scalar / math.pi)
    drift_class = classify_drift(braid_summary.get('drift'))

    coherent_fraction = _clamp01(_collect_coherent_fraction(eba_results))
    defect_mean = _clamp01(_collect_loop_metric(eba_results, 'defect_magnitude') / math.pi)
    phi_ab_mean_abs = _collect_loop_metric(eba_results, 'phi_ab', absolute=True)
    phi_berry_mean_abs = _collect_loop_metric(eba_results, 'phi_berry', absolute=True)

    identity_recip = channels['M6_Identity']['reciprocity']
    semantic_recip = channels['M3_Semantic']['reciprocity']
    episodic_recip = channels['M2_Episodic']['reciprocity']
    affective_recip = channels['M5_Affective_Ethical']['reciprocity']
    procedural_recip = channels['M4_Procedural']['reciprocity']

    closure_weight = _clamp01(identity_recip * (0.40 + 0.60 * coherence) * (0.50 + 0.50 * coherent_fraction) * (1.0 - 0.40 * scar_pressure))
    phase_lock_weight = _clamp01(identity_recip * (0.35 + 0.65 * coherence) * (0.35 + 0.65 * mean_phasor_abs) * (1.0 - 0.30 * drift_pressure))
    berry_weight = _clamp01(((identity_recip + semantic_recip + procedural_recip) / 3.0) * (0.35 + 0.65 * coherence) * (0.35 + 0.65 * mean_phasor_abs) * (1.0 - 0.30 * drift_pressure))
    ab_weight = _clamp01(((affective_recip + episodic_recip) / 2.0) * (0.35 + 0.65 * mean_phasor_abs) * (0.50 + 0.50 * coherent_fraction) * (1.0 - 0.25 * scar_pressure))
    defect_weight = _clamp01((0.20 + 0.80 * scar_pressure) * (0.35 + 0.65 * max(defect_mean, drift_pressure)))
    regulation_weight = _clamp01(0.45 * closure_weight + 0.35 * berry_weight + 0.20 * (1.0 - defect_weight))

    profile_mult = profile.get('summary_weight_emphasis', {})
    scar_mult = _SCAR_RESPONSE.get(dominant_scar or '', {})
    drift_mult = _DRIFT_RESPONSE.get(drift_class, _DRIFT_RESPONSE['stable'])
    combined_mult = _merge_multipliers(profile_mult, scar_mult, drift_mult)

    weights = {
        'closure_weight': _clamp01(closure_weight * combined_mult['closure_weight']),
        'phase_lock_weight': _clamp01(phase_lock_weight * combined_mult['phase_lock_weight']),
        'berry_weight': _clamp01(berry_weight * combined_mult['berry_weight']),
        'ab_weight': _clamp01(ab_weight * combined_mult['ab_weight']),
        'defect_weight': _clamp01(defect_weight * combined_mult['defect_weight']),
        'regulation_weight': _clamp01(regulation_weight * combined_mult['regulation_weight']),
    }

    signals = {
        'coherence': coherence,
        'loop_count': loop_count,
        'loop_density': loop_density,
        'scar_count': scar_count,
        'scar_pressure': scar_pressure,
        'mean_phasor_abs': mean_phasor_abs,
        'drift_scalar': drift_scalar,
        'drift_pressure': drift_pressure,
        'coherent_fraction': coherent_fraction,
        'defect_mean': defect_mean,
        'phi_ab_mean_abs': phi_ab_mean_abs,
        'phi_berry_mean_abs': phi_berry_mean_abs,
    }
    weighted_observables = {
        'weighted_coherent_fraction': coherent_fraction * weights['closure_weight'],
        'weighted_phi_ab_mean_abs': phi_ab_mean_abs * weights['ab_weight'],
        'weighted_phi_berry_mean_abs': phi_berry_mean_abs * weights['berry_weight'],
        'weighted_defect_mean': defect_mean * weights['defect_weight'],
        'weighted_loop_density': loop_density * weights['regulation_weight'],
        'weighted_closure_index': coherence * weights['closure_weight'] * (0.50 + 0.50 * coherent_fraction),
        'weighted_phase_lock_index': mean_phasor_abs * weights['phase_lock_weight'],
    }
    cards = build_braid_nonlocal_cards(
        domain=domain,
        channels=channels,
        weights=weights,
        signals=signals,
        scar_taxonomy=scar_taxonomy,
        dominant_scar_class=dominant_scar,
        drift_class=drift_class,
    )

    return {
        'source': 'braid_summary',
        'active': True,
        'domain': domain,
        'domain_profile': profile,
        'channels': channels,
        'signals': signals,
        'weights': weights,
        'weighted_observables': weighted_observables,
        'cards': cards,
        'scar_taxonomy': dict(scar_taxonomy),
        'dominant_scar_class': dominant_scar,
        'drift_class': drift_class,
        'adaptation_multipliers': combined_mult,
    }


__all__ = [
    'braid_channel_couplings',
    'build_braid_nonlocal_cards',
    'build_orbital_braid_diagnostics',
    'classify_drift',
    'compute_trace_to_nonlocal_coupling',
    'compute_summary_to_nonlocal_coupling',
    'domain_profile_for',
    'normalize_domain',
]
