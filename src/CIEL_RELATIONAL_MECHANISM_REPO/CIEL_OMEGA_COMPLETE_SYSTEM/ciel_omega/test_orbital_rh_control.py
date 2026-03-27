from orbital.rh_control import RHController, ThresholdProfile


def test_rh_controller_modes():
    ctl = RHController(ThresholdProfile(r1=0.3, r2=0.7))
    assert ctl.classify(0.1) == "normal_operation"
    assert ctl.classify(0.4) == "slow_execution_local_correction"
    assert ctl.classify(0.9) == "freeze_and_rebuild_closure"


def test_rh_controller_sector_override():
    ctl = RHController()
    dec = ctl.evaluate(0.5, sector="memory")
    assert dec.severity == "medium"
    assert "memory" in dec.sector_overrides
    assert dec.mode == "slow_execution_local_correction"
