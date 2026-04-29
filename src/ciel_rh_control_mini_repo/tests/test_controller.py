from ciel_rh_control import RHController, ThresholdProfile

def test_low_rh():
    assert RHController(ThresholdProfile(0.3, 0.7)).evaluate(0.1, "runtime").mode == "normal_operation"

def test_mid_rh():
    assert RHController(ThresholdProfile(0.3, 0.7)).evaluate(0.5, "bridge").mode == "slow_execution_local_correction"

def test_high_rh():
    assert RHController(ThresholdProfile(0.3, 0.7)).evaluate(0.9, "constraints").mode == "freeze_and_rebuild_closure"
