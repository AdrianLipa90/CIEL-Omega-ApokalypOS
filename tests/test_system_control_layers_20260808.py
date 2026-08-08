from pathlib import Path
import json

from src.CIEL_OMEGA_COMPLETE_SYSTEM.ciel_omega.system_control_layers import (
    FileEditControlPlane, FileOracle, Doctor, Verdict,
)


def test_create_update_and_receipt_chain(tmp_path: Path):
    ledger=tmp_path/'receipts'/'actuator.jsonl'
    ctl=FileEditControlPlane(allowed_roots=[tmp_path],ledger_path=ledger)
    target=tmp_path/'a.txt'
    _,d1,r1=ctl.edit(target,'one',authority_id='USER_EXPLICIT_TEST',explicit_write_authority=True)
    assert d1.verdict==Verdict.CONTINUE and r1 and r1.verified
    before=r1.after_sha256
    _,d2,r2=ctl.edit(target,'two',authority_id='USER_EXPLICIT_TEST',explicit_write_authority=True,expected_sha256=before)
    assert d2.verdict==Verdict.CONTINUE and r2 and r2.before_sha256==before
    assert target.read_text()=='two'
    rows=[json.loads(x) for x in ledger.read_text().splitlines()]
    assert rows[1]['predecessor_receipt_sha256']==rows[0]['receipt_sha256']


def test_missing_authority_is_stage_only(tmp_path: Path):
    plan=FileOracle([tmp_path]).inspect(tmp_path/'x.txt',b'x')
    dec=Doctor().evaluate(plan,authority_id=None,explicit_write_authority=False)
    assert dec.verdict==Verdict.STAGE_ONLY and not dec.allow_apply


def test_scope_violation_is_denied(tmp_path: Path):
    allowed=tmp_path/'allowed'; allowed.mkdir()
    other=tmp_path/'other'; other.mkdir()
    plan=FileOracle([allowed]).inspect(other/'x.txt',b'x')
    dec=Doctor().evaluate(plan,authority_id='AUTH',explicit_write_authority=True)
    assert dec.verdict==Verdict.DENY_DESTRUCTIVE_APPLY and not dec.allow_apply


def test_expected_sha_prevents_lost_update(tmp_path: Path):
    target=tmp_path/'x.txt'; target.write_text('old')
    plan=FileOracle([tmp_path]).inspect(target,b'new',expected_sha256='0'*64)
    dec=Doctor().evaluate(plan,authority_id='AUTH',explicit_write_authority=True)
    assert dec.verdict==Verdict.DENY_DESTRUCTIVE_APPLY
    assert target.read_text()=='old'


def test_symlink_is_denied(tmp_path: Path):
    real=tmp_path/'real.txt'; real.write_text('real')
    link=tmp_path/'link.txt'; link.symlink_to(real)
    plan=FileOracle([tmp_path]).inspect(link,b'mutated')
    dec=Doctor().evaluate(plan,authority_id='AUTH',explicit_write_authority=True)
    assert 'TARGET_IS_SYMLINK' in dec.findings and not dec.allow_apply
    assert real.read_text()=='real'


def test_noop_is_verified_and_receipted(tmp_path: Path):
    target=tmp_path/'x.txt'; target.write_text('same')
    ctl=FileEditControlPlane(allowed_roots=[tmp_path],ledger_path=tmp_path/'ledger.jsonl')
    plan,dec,rec=ctl.edit(target,'same',authority_id='AUTH',explicit_write_authority=True)
    assert plan.operation=='NOOP' and dec.verdict==Verdict.CONTINUE
    assert rec and rec.operation=='NOOP' and rec.verified
