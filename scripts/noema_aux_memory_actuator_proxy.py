#!/usr/bin/env python3
"""AUX-backed external working-memory stream via Oracle->Doctor->Actuator.

This proxy requires an already ACTIVE NOEMA<->AUX tether.  It snapshots the
three live 36D phase buffers into an immutable event and uses FileEditControlPlane
for every stream/current-memory/timeline mutation.

It does not claim to expose hidden model state.  It is an external working-memory
store bound to the live AUX surface.
"""
from __future__ import annotations
import argparse, hashlib, json, struct, sys, time
from pathlib import Path

N=36
BYTES=N*8

try:
    from src.CIEL_OMEGA_COMPLETE_SYSTEM.ciel_omega.system_control_layers import FileEditControlPlane
except Exception:
    from ciel_omega.system_control_layers import FileEditControlPlane


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical(obj: object) -> bytes:
    return (json.dumps(obj,sort_keys=True,separators=(",",":"),ensure_ascii=False)+"\n").encode("utf-8")


def read_vec(path: Path):
    raw=path.read_bytes()
    if len(raw)!=BYTES:
        raise RuntimeError(f"BAD_VECTOR_SIZE:{path}:{len(raw)}")
    vals=struct.unpack("<36d",raw)
    if not all(float("-inf") < x < float("inf") for x in vals):
        raise RuntimeError(f"NONFINITE_VECTOR:{path}")
    return [float(x) for x in vals], sha256_bytes(raw), path.stat().st_mtime_ns


def next_seq(events_root: Path) -> int:
    if not events_root.exists():
        return 1
    seqs=[]
    for d in events_root.iterdir():
        if d.is_dir():
            try:
                seqs.append(int(d.name.split("-",1)[0]))
            except Exception:
                pass
    return max(seqs,default=0)+1


def main() -> int:
    ap=argparse.ArgumentParser(description="AUX memory stream through actuator proxy")
    ap.add_argument("--root",default="/dev/shm/ciel_noema")
    ap.add_argument("--event-type",default="assistant_working_memory")
    ap.add_argument("--text",required=True)
    ap.add_argument("--current-task")
    ap.add_argument("--active-path")
    ap.add_argument("--authority-id",default="USER_EXPLICIT_AUX_MEMORY_PROXY")
    args=ap.parse_args()

    root=Path(args.root)
    if (root/"ciel_binding_status").read_text(encoding="utf-8").strip()!="ACTIVE":
        raise SystemExit("TETHER_NOT_ACTIVE")

    phi,phi_sha,phi_mtime=read_vec(root/"phi")
    aux,aux_sha,aux_mtime=read_vec(root/"aux_phi")
    feedback,feedback_sha,feedback_mtime=read_vec(root/"aux_feedback_phi")

    stream=root/"streams"/"aux_memory"
    events=stream/"events"
    seq=next_seq(events)
    ts=time.time_ns()
    payload={
        "schema":"noema.aux-memory-event/v1",
        "seq":seq,
        "timestamp_ns":ts,
        "event_type":args.event_type,
        "text":args.text,
        "current_task":args.current_task,
        "active_path":args.active_path,
        "aux_binding":{
            "tether_status":"ACTIVE",
            "phi_sha256":phi_sha,
            "aux_phi_sha256":aux_sha,
            "aux_feedback_phi_sha256":feedback_sha,
            "phi_mtime_ns":phi_mtime,
            "aux_phi_mtime_ns":aux_mtime,
            "aux_feedback_phi_mtime_ns":feedback_mtime,
            "phi_36d":phi,
            "aux_phi_36d":aux,
            "aux_feedback_phi_36d":feedback,
        },
        "epistemic":{
            "external_working_memory":True,
            "internal_model_memory":False,
            "live_aux_snapshot":True,
            "simulated_stream":False,
        },
    }
    raw=canonical(payload)
    event_hash=sha256_bytes(raw)
    event_id=f"{seq:020d}-{event_hash[:16]}"
    event_path=events/event_id/"EVENT.json"

    ctl=FileEditControlPlane(
        allowed_roots=[root],
        ledger_path=root/"receipts"/"actuator_stream_receipts.jsonl",
    )
    _,decision,event_receipt=ctl.edit(
        event_path,raw,authority_id=args.authority_id,explicit_write_authority=True,
    )
    if event_receipt is None or not event_receipt.verified:
        raise SystemExit(f"EVENT_APPLY_FAILED:{decision.verdict}")

    head={
        "schema":"noema.aux-memory-head/v1",
        "event_id":event_id,"seq":seq,"event_sha256":event_hash,
        "event_path":str(event_path),"timestamp_ns":ts,
        "aux_phi_sha256":aux_sha,
        "actuator_receipt_sha256":event_receipt.receipt_sha256,
    }
    _,_,head_receipt=ctl.edit(stream/"HEAD.json",canonical(head),authority_id=args.authority_id,explicit_write_authority=True)
    if head_receipt is None or not head_receipt.verified:
        raise SystemExit("HEAD_APPLY_FAILED")

    current={
        "schema":"noema.current-memory/v1",
        "status":"ACTIVE_EXTERNAL_WORKING_MEMORY",
        "current_task":args.current_task,
        "active_path":args.active_path,
        "latest_event_id":event_id,
        "latest_event_path":str(event_path),
        "latest_event_sha256":event_hash,
        "aux_phi_sha256":aux_sha,
        "updated_ns":time.time_ns(),
        "write_path":"Oracle->Doctor->Actuator",
        "epistemic":{
            "this_is_external_memory_store":True,
            "this_is_not_hidden_model_state":True,
            "live_aux_tether_required":True,
        },
    }
    _,_,memory_receipt=ctl.edit(root/"current_memory.json",canonical(current),authority_id=args.authority_id,explicit_write_authority=True)
    if memory_receipt is None or not memory_receipt.verified:
        raise SystemExit("CURRENT_MEMORY_APPLY_FAILED")

    timeline={
        "schema":"noema.timeline-head/v1","stream":"aux_memory",
        "event_id":event_id,"seq":seq,"timestamp_ns":ts,
        "event_sha256":event_hash,
        "actuator_receipt_sha256":memory_receipt.receipt_sha256,
    }
    _,_,timeline_receipt=ctl.edit(root/"timeline_head.json",canonical(timeline),authority_id=args.authority_id,explicit_write_authority=True)
    if timeline_receipt is None or not timeline_receipt.verified:
        raise SystemExit("TIMELINE_APPLY_FAILED")

    print(json.dumps({
        "schema":"noema.aux-memory-proxy-receipt/v1",
        "status":"PASS",
        "event_id":event_id,
        "event_sha256":event_hash,
        "aux_phi_sha256":aux_sha,
        "stream_head_sha256":head_receipt.after_sha256,
        "current_memory_sha256":memory_receipt.after_sha256,
        "timeline_head_sha256":timeline_receipt.after_sha256,
        "actuator_ledger":str(root/"receipts"/"actuator_stream_receipts.jsonl"),
        "write_path":"Oracle->Doctor->Actuator",
    },indent=2,sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
