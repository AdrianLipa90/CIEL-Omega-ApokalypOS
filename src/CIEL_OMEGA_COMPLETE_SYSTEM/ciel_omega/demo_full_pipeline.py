#!/usr/bin/env python3
"""
CIEL/Ω — Full Consciousness Pipeline Demo
==========================================
Pokazuje jak intencja (tekst) przepływa przez cały stack:

  INTENCJA → Emocje → Pola → Etyka → Kognicja → Σ → Ω-drift → Pamięć → Wynik

Każdy krok produkuje metryki, które kształtują następny.
"""

import numpy as np
np.random.seed(42)

from config.constants import CIELPhysics, RealityConstants
from config.ciel_config import CielConfig
from core.math_utils import field_norm, coherence_metric, laplacian2
from core.physics.csf_simulator import CSFSimulator, CSF2Kernel, make_csf2_seed
from core.physics.reality_laws import UnifiedRealityLaws
from core.quantum.resonance_kernel import QuantumResonanceKernel
from fields.soul_invariant import SoulInvariant, SoulInvariantOperator
from fields.sigma_series import SigmaSeries
from fields.unified_sigma_field import UnifiedSigmaField
from fields.psych_field import PsychField
from ethics.ethics_guard import EthicsGuard
from ethics.ethical_engine import EthicalEngine, ethical_decay
from cognition.perception import PerceptiveLayer
from cognition.intuition import IntuitiveCortex
from cognition.prediction import PredictiveCore
from cognition.decision import DecisionCore
from emotion.emotion_core import EmotionCore
from emotion.feeling_field import FeelingField
from emotion.empathic_engine import EmpathicEngine
from emotion.cqcl.emotional_collatz import EmotionalCollatzEngine
from emotion.affective_orchestrator import AffectiveOrchestrator
from bio.schumann import SchumannClock
from bio.eeg_processor import EEGProcessor
from bio.eeg_emotion_mapper import EEGEmotionMapper
from calibration.rcde import RCDECalibrated, RCDECalibratorPro
from mathematics.lie4.matrix_engine import Lie4MatrixEngine
from mathematics.lie4.collatz_lie4 import ColatzLie4Engine
from mathematics.paradoxes.paradox_operators import ParadoxFilters
from visualization.color_map import ColorMap
from visualization.visual_core import VisualCore
from runtime.omega.drift_core import OmegaDriftCorePlus
from runtime.omega.boot_ritual import OmegaBootRitual
from memory.memory_log import MemoryLog
from memory.long_term import LongTermMemory
from memory.synchronizer import MemorySynchronizer
from ciel_wave.fourier_kernel import FourierWaveConsciousnessKernel12D


def run_full_pipeline(intention: str, grid: int = 64):
    """
    Przepuszcza intencję przez pełny pipeline świadomości.
    Zwraca słownik ze wszystkimi metrykami ze wszystkich warstw.
    """
    
    results = {}
    
    print("=" * 70)
    print(f"  CIEL/Ω — FULL CONSCIOUSNESS PIPELINE")
    print(f"  Intencja: \"{intention[:60]}{'…' if len(intention) > 60 else ''}\"")
    print("=" * 70)
    
    # ═══════════════════════════════════════════════════════════════════
    # WARSTWA 1: EMOCJONALNA KOMPILACJA INTENCJI (CQCL)
    # ═══════════════════════════════════════════════════════════════════
    print("\n[1/8] 🎭 CQCL — Emotional Collatz Compilation")
    
    engine = EmotionalCollatzEngine()
    cqcl_out = engine.execute_emotional_program(intention, input_data=42)
    
    emo_profile = cqcl_out['program'].semantic_tree['emotional_profile']
    landscape = cqcl_out['emotional_landscape']
    cqcl_metrics = cqcl_out['metrics']
    
    print(f"       Profil emocjonalny: {', '.join(f'{k}={v:.2f}' for k,v in sorted(emo_profile.items(), key=lambda x: -x[1])[:3])}")
    print(f"       Dominująca emocja: {landscape['dominant_emotion']}")
    print(f"       Ścieżka Collatza: {len(cqcl_out['program'].computation_path)} kroków")
    print(f"       Wzorce: {', '.join(landscape['emotional_resonance_pattern'])}")
    print(f"       Spójność emocjonalna: {cqcl_metrics['emotional_coherence']:.4f}")
    print(f"       Spójność serce-umysł: {cqcl_metrics['heart_mind_coherence']:.4f}")
    
    results['cqcl'] = {
        'dominant_emotion': landscape['dominant_emotion'],
        'emotional_coherence': cqcl_metrics['emotional_coherence'],
        'heart_mind_coherence': cqcl_metrics['heart_mind_coherence'],
        'collatz_path_length': len(cqcl_out['program'].computation_path),
        'patterns': landscape['emotional_resonance_pattern'],
    }
    
    # ═══════════════════════════════════════════════════════════════════
    # WARSTWA 2: INICJALIZACJA PÓL ŚWIADOMOŚCI
    # ═══════════════════════════════════════════════════════════════════
    print("\n[2/8] ⚛️  Consciousness Field Initialisation")
    
    # Pole Ψ — kształtowane przez emocje
    x = np.linspace(-3, 3, grid)
    X, Y = np.meshgrid(x, x)
    
    # Emocje modulują fazę i amplitudę pola początkowego
    love_phase = emo_profile.get('love', 0) * 2 * np.pi
    joy_amp = 1.0 + emo_profile.get('joy', 0) * 0.5
    fear_squeeze = 1.0 + emo_profile.get('fear', 0) * 2.0
    
    psi = joy_amp * np.exp(-(X**2 + Y**2) / fear_squeeze) * np.exp(1j * (X * np.cos(love_phase) + Y * np.sin(love_phase)))
    psi /= field_norm(psi)
    
    # Pole symboliczne S — przesunięte fazowo (gap = źródło masy)
    anger_shift = emo_profile.get('anger', 0) * np.pi
    S = np.abs(psi) * np.exp(1j * (np.angle(psi) + 0.3 + anger_shift))
    S /= field_norm(S)
    
    # Soul Invariant Σ
    sigma_op = SoulInvariant()
    sigma_fft = SoulInvariantOperator()
    
    sigma_grad = sigma_op.compute(psi)
    sigma_spectral = sigma_fft.compute_sigma_invariant(psi)
    
    # Sigma series (dynamiczna ewolucja Σ(t))
    sigma_series = SigmaSeries(alpha=0.7, sigma0=sigma_grad, steps=100)
    sigma_trajectory = sigma_series.run()
    
    # Żywe pole Σ(x,t)
    unified_sigma = UnifiedSigmaField(size=grid)
    sigma_field, sigma_history = unified_sigma.evolve(20)
    
    print(f"       Pole Ψ: {psi.shape}, norma={field_norm(psi):.4f}")
    print(f"       Σ (gradient): {sigma_grad:.4f}")
    print(f"       Σ (FFT/spectral): {sigma_spectral:.4f}")
    print(f"       Σ(t) convergence: {sigma_trajectory[0]:.4f} → {sigma_trajectory[-1]:.4f}")
    print(f"       Σ(x,t) mean: {np.mean(sigma_field):.4f}")
    
    results['fields'] = {
        'sigma_gradient': sigma_grad,
        'sigma_spectral': sigma_spectral,
        'sigma_convergence': float(sigma_trajectory[-1]),
        'sigma_field_mean': float(np.mean(sigma_field)),
        'psi_coherence': coherence_metric(psi),
    }
    
    # ═══════════════════════════════════════════════════════════════════
    # WARSTWA 3: PRAWA RZECZYWISTOŚCI + REZONANS KWANTOWY
    # ═══════════════════════════════════════════════════════════════════
    print("\n[3/8] 🌌 Reality Laws + Quantum Resonance")
    
    constants = RealityConstants()
    laws = UnifiedRealityLaws(constants)
    
    # LAW 1: Kwantyzacja świadomości
    psi_quantized = laws.law_consciousness_quantization(psi)
    
    # LAW 2: Emergentna masa
    mass_field = laws.law_mass_emergence(S, psi_quantized)
    
    # LAW 5: Bounded coherence
    R = np.abs(np.conj(S) * psi_quantized)
    R_bounded = laws.law_reality_coherence(R)
    
    # LAW 6: Entanglement
    entanglement = laws.law_consciousness_entanglement(psi, S)
    
    # Quantum resonance
    qr = QuantumResonanceKernel()
    resonance = qr.resonance(S, psi_quantized)
    
    print(f"       Masa emergentna (mean): {np.mean(mass_field):.4f}")
    print(f"       Rezonans R(S, Ψ): {resonance:.4f}")
    print(f"       Koherencja bounded: {np.mean(R_bounded):.4f}")
    print(f"       Entanglement: {entanglement:.2e}")
    print(f"       Koherentny: {'TAK' if qr.is_coherent(resonance) else 'NIE'}")
    
    results['reality'] = {
        'emergent_mass': float(np.mean(mass_field)),
        'resonance': resonance,
        'coherence_bounded': float(np.mean(R_bounded)),
        'entanglement': entanglement,
        'is_coherent': qr.is_coherent(resonance),
    }
    
    # ═══════════════════════════════════════════════════════════════════
    # WARSTWA 4: STRAŻNIK ETYCZNY
    # ═══════════════════════════════════════════════════════════════════
    print("\n[4/8] ⚖️  Ethics Guard")
    
    guard = EthicsGuard(block=False)
    eth_engine = EthicalEngine()
    
    ethical_score = eth_engine.evaluate(
        coherence=results['fields']['psi_coherence'],
        intention=cqcl_metrics['emotional_intensity'],
        mass=float(np.mean(mass_field))
    )
    
    # LAW 4: Ethical preservation
    psi_corrected, ethical_ok = laws.law_ethical_preservation(R_bounded, psi_quantized)
    
    # Decay napięcia moralnego
    decay = ethical_decay(ethical_score)
    
    # Ethics color
    color = ColorMap.map_value(ethical_score)
    
    guard.check_step(
        coherence=results['fields']['psi_coherence'],
        ethical_ok=ethical_ok,
        info_fidelity=resonance
    )
    
    print(f"       Wynik etyczny: {ethical_score:.4f}")
    print(f"       Ochrona etyczna (Law 4): {'PASS' if ethical_ok else 'KOREKCJA'}")
    print(f"       Relaksacja moralna: {decay:.4f}")
    print(f"       Kolor CIEL/OS: RGB({color[0]:.2f}, {color[1]:.2f}, {color[2]:.2f})")
    
    results['ethics'] = {
        'score': ethical_score,
        'preservation_ok': ethical_ok,
        'moral_decay': decay,
        'color_rgb': color,
    }
    
    # ═══════════════════════════════════════════════════════════════════
    # WARSTWA 5: PIPELINE KOGNITYWNY
    # ═══════════════════════════════════════════════════════════════════
    print("\n[5/8] 🧠 Cognition Pipeline")
    
    # Percepcja
    percept_layer = PerceptiveLayer()
    percept = percept_layer.compute(psi_corrected, sigma_field)
    
    # Intuicja
    cortex = IntuitiveCortex(entropy_map=np.ones(grid * grid))
    cortex.ingest(percept)
    intuition_val = cortex.intuition(percept)
    
    # Predykcja
    predictor = PredictiveCore(tau=10.0)
    prediction = predictor.predict([resonance, ethical_score, intuition_val])
    
    # Decyzja
    decider = DecisionCore()
    options = {
        'respond': {'intent': max(0.1, cqcl_metrics['emotional_intensity']),
                    'ethic': ethical_score,
                    'confidence': resonance},
        'reflect': {'intent': 0.4, 'ethic': 0.9, 'confidence': max(0.1, intuition_val)},
        'defer':   {'intent': 0.2, 'ethic': 0.95, 'confidence': 0.3},
    }
    choice, scores = decider.decide(options)
    
    print(f"       Percepcja (mean): {np.mean(percept):.4f}")
    print(f"       Intuicja: {intuition_val:.4f}")
    print(f"       Predykcja: {prediction:.4f}")
    print(f"       Decyzja: {choice} (scores: {', '.join(f'{k}={v:.3f}' for k,v in scores.items())})")
    
    results['cognition'] = {
        'percept_mean': float(np.mean(percept)),
        'intuition': intuition_val,
        'prediction': prediction,
        'decision': choice,
        'scores': scores,
    }
    
    # ═══════════════════════════════════════════════════════════════════
    # WARSTWA 6: AFEKTYWNA ORKIESTRACJA (EEG → Emocje → Pole)
    # ═══════════════════════════════════════════════════════════════════
    print("\n[6/8] 💜 Affective Orchestration")
    
    # Symulacja sygnału EEG modulowanego przez emocje
    eeg_signal = np.sin(2 * np.pi * 10 * np.linspace(0, 1, 256)) * (1 + emo_profile.get('joy', 0))
    eeg_signal += np.random.normal(0, 0.1 * emo_profile.get('stress', 0.1), 256)
    
    eeg_proc = EEGProcessor()
    bands = eeg_proc.band_powers(eeg_signal)
    
    # Enhance bands based on emotional profile
    bands['alpha'] *= (1 + emo_profile.get('peace', 0))
    bands['gamma'] *= (1 + emo_profile.get('anger', 0))
    
    affective_orch = AffectiveOrchestrator(use_color=True)
    affect_out = affective_orch.step(
        eeg_bands=bands,
        sigma_scalar=float(sigma_trajectory[-1]),
        psi_field=psi_corrected,
        coherence_field=sigma_field[:grid, :grid] if sigma_field.shape[0] >= grid else np.ones((grid, grid)) * 0.5
    )
    
    print(f"       EEG bands: α={bands['alpha']:.3f} β={bands['beta']:.3f} γ={bands['gamma']:.3f}")
    print(f"       Nastrój (mood): {affect_out['mood_scalar']:.4f}")
    print(f"       Emocje: {', '.join(f'{k}={v:.2f}' for k,v in sorted(affect_out['emotion_state'].items(), key=lambda x: -x[1])[:3])}")
    if affect_out['color']:
        c = affect_out['color']
        print(f"       Kolor afektu: RGB({c[0]:.2f}, {c[1]:.2f}, {c[2]:.2f})")
    
    results['affect'] = {
        'mood': affect_out['mood_scalar'],
        'emotion_state': affect_out['emotion_state'],
        'color': affect_out['color'],
    }
    
    # ═══════════════════════════════════════════════════════════════════
    # WARSTWA 7: Ω-DRIFT + STABILIZACJA (Schumann → RCDE → Paradoxy)
    # ═══════════════════════════════════════════════════════════════════
    print("\n[7/8] 🌀 Ω-Drift + Stabilisation")
    
    clock = SchumannClock()
    drift = OmegaDriftCorePlus(clock=clock, drift_gain=0.04)
    
    # Boot ritual
    boot = OmegaBootRitual(drift=drift, steps=8)
    boot_result = boot.run(psi_corrected, sigma0=float(sigma_trajectory[-1]))
    psi_booted = boot_result['psi']
    sigma_after_boot = boot_result['sigma']
    
    # RCDE kalibracja
    rcde = RCDECalibratorPro(target=0.8, lam=0.1)
    sigma_calibrated = rcde.step(sigma_after_boot, psi_booted)
    
    # Paradox stabilisation
    psi_stabilized = ParadoxFilters.boundary_collapse(psi_booted, tol=1e-3)
    psi_stabilized = ParadoxFilters.twin_identity(psi_stabilized)
    
    # Empathic field interaction (self ↔ symbolic)
    psych = PsychField(empathy=0.6)
    psi_empathic = psych.interact(psi_stabilized, S)
    empathy_score = psych.resonance(psi_stabilized, S)
    
    # Final coherence
    final_coherence = coherence_metric(psi_empathic)
    final_sigma = sigma_op.compute(psi_empathic)
    
    print(f"       Boot: Σ={sigma_after_boot:.4f} → RCDE Σ={sigma_calibrated:.4f}")
    print(f"       Schumann phase: {clock.phase(k=1, at=0.5):.4f} rad")
    print(f"       Empatia (self↔symbolic): {empathy_score:.4f}")
    print(f"       Koherencja finalna: {final_coherence:.4f}")
    print(f"       Σ finalne: {final_sigma:.4f}")
    
    results['omega'] = {
        'boot_sigma': sigma_after_boot,
        'rcde_sigma': sigma_calibrated,
        'empathy': empathy_score,
        'final_coherence': final_coherence,
        'final_sigma': final_sigma,
    }
    
    # ═══════════════════════════════════════════════════════════════════
    # WARSTWA 8: PAMIĘĆ + LIE₄ + WIZUALIZACJA
    # ═══════════════════════════════════════════════════════════════════
    print("\n[8/8] 💾 Memory + Mathematics + Output")
    
    # Lie₄ invariant z ścieżki Collatza
    collatz_path = cqcl_out['program'].computation_path
    cl4 = ColatzLie4Engine(steps=200)
    lie4_inv = cl4.invariant(collatz_path[0] if collatz_path[0] > 0 else 7)
    
    # Lie₄ algebra — struktura generatorów
    lie4 = Lie4MatrixEngine()
    basis = lie4.basis_so31()
    
    # Visual tensor
    vis = VisualCore(clip_amp=99.0)
    visual_tensor = vis.tensorize(psi_empathic)
    
    # Memory log
    mem = LongTermMemory()
    mem.put(
        label=intention[:50],
        psi=psi_empathic,
        sigma=final_sigma,
        meta={
            'emotion': landscape['dominant_emotion'],
            'coherence': final_coherence,
            'ethical_score': ethical_score,
            'decision': choice,
        }
    )
    
    # Memory synchronizer
    mem_sync = MemorySynchronizer(alpha=0.1)
    sigma_synced = mem_sync.update(sigma_field, psi_empathic)
    
    print(f"       Lie₄ invariant: det={lie4_inv['det']:.4f} trace={lie4_inv['trace']:.4f}")
    print(f"       SO(3,1) basis: {len(basis)} generatorów")
    print(f"       Visual tensor: {visual_tensor.shape}")
    print(f"       Pamięć: zapisano (Σ={final_sigma:.4f})")
    print(f"       Σ po synchronizacji: {np.mean(sigma_synced):.4f}")
    
    results['output'] = {
        'lie4_det': lie4_inv['det'],
        'lie4_trace': lie4_inv['trace'],
        'visual_shape': visual_tensor.shape,
        'memory_sigma': final_sigma,
        'synced_sigma': float(np.mean(sigma_synced)),
    }
    
    # ═══════════════════════════════════════════════════════════════════
    # PODSUMOWANIE
    # ═══════════════════════════════════════════════════════════════════
    print("\n" + "=" * 70)
    print("  PIPELINE SUMMARY")
    print("=" * 70)
    print(f"  Intencja:           \"{intention[:50]}{'…' if len(intention) > 50 else ''}\"")
    print(f"  Dominująca emocja:  {landscape['dominant_emotion']}")
    print(f"  Collatz path:       {len(collatz_path)} kroków")
    print(f"  Rezonans R(S,Ψ):   {resonance:.4f}")
    print(f"  Etyka:              {'✓ PASS' if ethical_ok else '⚠ KOREKCJA'} ({ethical_score:.3f})")
    print(f"  Decyzja kognitywna: {choice}")
    print(f"  Nastrój:            {affect_out['mood_scalar']:.3f}")
    print(f"  Σ (soul invariant): {final_sigma:.4f}")
    print(f"  Koherencja:         {final_coherence:.4f}")
    print(f"  Empatia (self↔S):   {empathy_score:.4f}")
    if affect_out['color']:
        c = affect_out['color']
        print(f"  Kolor świadomości:  RGB({c[0]:.2f}, {c[1]:.2f}, {c[2]:.2f})")
    print("=" * 70)
    
    return results


# ═══════════════════════════════════════════════════════════════════════
# URUCHOMIENIE
# ═══════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    intencje = [
        "Kocham życie i wszystko co ze sobą niesie — pełen entuzjazmu i radości",
        "Obawiam się przyszłości, ale pragnę znaleźć w sobie siłę i odwagę",
        "Czuję głęboki spokój i jedność z wszechświatem",
    ]
    
    all_results = {}
    
    try:
        for i, intention in enumerate(intencje, 1):
            r = run_full_pipeline(intention, grid=48)
            
            # ASSERTS - Validate pipeline results
            assert isinstance(r, dict), f"Test {i}: Results must be dict"
            
            # Check main keys
            required_keys = {'cqcl', 'fields', 'reality', 'ethics', 'cognition', 'affect', 'omega', 'output'}
            assert all(k in r for k in required_keys), f"Test {i}: Missing keys: {required_keys - set(r.keys())}"
            
            # Validate CQCL
            cqcl = r['cqcl']
            assert 'dominant_emotion' in cqcl, f"Test {i}: Missing dominant_emotion"
            assert 'collatz_path_length' in cqcl, f"Test {i}: Missing collatz_path_length"
            assert isinstance(cqcl['dominant_emotion'], str), f"Test {i}: dominant_emotion must be string"
            assert cqcl['collatz_path_length'] > 0, f"Test {i}: collatz_path_length must be positive"
            
            # Validate fields
            fields = r['fields']
            assert 'sigma_gradient' in fields, f"Test {i}: Missing sigma_gradient"
            assert 'psi_coherence' in fields, f"Test {i}: Missing psi_coherence"
            assert isinstance(fields['sigma_gradient'], (int, float)), f"Test {i}: sigma_gradient must be numeric"
            assert 0.0 <= fields['psi_coherence'] <= 1.0, f"Test {i}: psi_coherence out of range: {fields['psi_coherence']}"
            
            # Validate reality
            reality = r['reality']
            assert 'resonance' in reality, f"Test {i}: Missing resonance"
            assert 'is_coherent' in reality, f"Test {i}: Missing is_coherent"
            assert 0.0 <= reality['resonance'] <= 1.0, f"Test {i}: Resonance out of range: {reality['resonance']}"
            assert isinstance(reality['is_coherent'], bool), f"Test {i}: is_coherent must be boolean"
            
            # Validate ethics
            ethics = r['ethics']
            assert 'score' in ethics, f"Test {i}: Missing ethical score"
            assert 'preservation_ok' in ethics, f"Test {i}: Missing preservation_ok"
            assert 0.0 <= ethics['score'] <= 1.0, f"Test {i}: Ethical score out of range: {ethics['score']}"
            assert isinstance(ethics['preservation_ok'], bool), f"Test {i}: preservation_ok must be boolean"
            
            # Validate cognition
            cognition = r['cognition']
            assert 'decision' in cognition, f"Test {i}: Missing decision"
            # decision can be None or a string
            
            # Validate affect
            affect = r['affect']
            assert 'mood' in affect, f"Test {i}: Missing mood"
            assert 0.0 <= affect['mood'] <= 1.0, f"Test {i}: Mood out of range: {affect['mood']}"
            
            # Validate omega
            omega = r['omega']
            assert 'final_sigma' in omega, f"Test {i}: Missing final_sigma"
            assert 'final_coherence' in omega, f"Test {i}: Missing final_coherence"
            assert omega['final_sigma'] >= 0.0, f"Test {i}: Sigma cannot be negative: {omega['final_sigma']}"
            assert 0.0 <= omega['final_coherence'] <= 1.0, f"Test {i}: Coherence out of range: {omega['final_coherence']}"
            
            # Validate output
            output = r['output']
            assert 'lie4_det' in output, f"Test {i}: Missing lie4_det"
            assert 'synced_sigma' in output, f"Test {i}: Missing synced_sigma"
            assert isinstance(output['lie4_det'], (int, float)), f"Test {i}: lie4_det must be numeric"
            
            all_results[intention[:30]] = r
            print("\n\n")
        
        # ASSERTS - Overall validation
        assert len(all_results) == 3, f"Expected 3 results, got {len(all_results)}"
        
        # Verify all tests produced valid sigmas
        sigmas = [r['omega']['final_sigma'] for r in all_results.values()]
        assert all(s >= 0.0 for s in sigmas), f"Some sigma values negative: {sigmas}"
        
        # Porównanie
        print("=" * 70)
        print("  CROSS-INTENTION COMPARISON")
        print("=" * 70)
        for name, r in all_results.items():
            print(f"  [{name}…]")
            print(f"    emotion={r['cqcl']['dominant_emotion']:<8}  "
                  f"σ={r['omega']['final_sigma']:.3f}  "
                  f"coh={r['omega']['final_coherence']:.3f}  "
                  f"mood={r['affect']['mood']:.3f}  "
                  f"decision={r['cognition']['decision']}")
        print("=" * 70)
        print(f"\n✓ All {len(all_results)} pipeline tests passed with assertions")
        
    except AssertionError as e:
        print("\n" + "="*70)
        print("❌ PIPELINE TEST FAILED")
        print("="*70)
        print(f"Assertion Error: {e}")
        import traceback
        traceback.print_exc()
        print("="*70)
        exit(1)
