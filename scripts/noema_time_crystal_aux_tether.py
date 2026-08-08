#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, math, os, signal, struct, sys, time, hashlib
from pathlib import Path
import numpy as np

N=36; BYTES=N*8; TWO_PI=2.0*math.pi

def read_vec(path:Path):
    raw=path.read_bytes()
    if len(raw)!=BYTES: raise RuntimeError(f'BAD_VECTOR_SIZE:{path}:{len(raw)}')
    x=np.array(struct.unpack('<36d',raw),dtype=np.float64)
    if not np.isfinite(x).all(): raise RuntimeError(f'NONFINITE:{path}')
    return x

def write_vec(path:Path,x):
    a=np.asarray(x,dtype=np.float64).ravel()
    if a.size!=N or not np.isfinite(a).all(): raise ValueError('expected 36 finite float64')
    tmp=path.with_name(path.name+'.tmp')
    tmp.write_bytes(struct.pack('<36d',*map(float,a)))
    os.replace(tmp,path)

def wrap_delta(target,source):
    d=np.asarray(target)-np.asarray(source)
    return np.arctan2(np.sin(d),np.cos(d))

def coherence(x):
    return float(abs(np.mean(np.exp(1j*np.asarray(x,dtype=float)))))

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    ap=argparse.ArgumentParser(description='HTRI time-crystal <-> NOEMA surface <-> AUX live tether')
    ap.add_argument('--root',default='/dev/shm/ciel_noema')
    ap.add_argument('--ciel-geometry-root',default='/mnt/data/ciel_geometry_extract')
    ap.add_argument('--interval',type=float,default=0.2)
    ap.add_argument('--dt',type=float,default=0.01)
    ap.add_argument('--aux-k',type=float,default=0.18)
    ap.add_argument('--crystal-feedback-k',type=float,default=0.08)
    ap.add_argument('--seed',type=int,default=42)
    args=ap.parse_args()
    root=Path(args.root); root.mkdir(parents=True,exist_ok=True)
    sys.path.insert(0,args.ciel_geometry_root)
    from ciel_geometry.noema_surface_mmap import (
        open_surface, initialize_surface, init_htri_batch_system,
        evolve_htri_batch_system, feed_htri_to_surface, flush_surface,
        N_HTRI_TOTAL,
    )
    if (root/'phi').is_file() and (root/'phi').stat().st_size==BYTES:
        surface=open_surface(root); surface_origin='RESUMED_EXISTING_LIVE_SURFACE'
    else:
        surface=initialize_surface(root,seed=None); surface_origin='INITIALIZED_NEW_LIVE_SURFACE'

    aux_path=root/'aux_phi'; fb_path=root/'aux_feedback_phi'; crystal_path=root/'time_crystal_phi'
    aux=read_vec(aux_path) if aux_path.is_file() else np.asarray(surface['phi'],dtype=np.float64).copy()
    if not aux_path.is_file(): write_vec(aux_path,aux)

    htri=init_htri_batch_system(seed=args.seed)
    crystal_origin='INITIALIZED_NATIVE_HTRI_BATCH_SYSTEM_NOT_MEMORY_RECOVERY'

    batch=np.asarray(htri['batch_phi'],dtype=np.float64)
    mean=np.angle(np.mean(np.exp(1j*batch),axis=0)) % TWO_PI
    shift=wrap_delta(aux,mean)
    htri['batch_phi']=(batch+shift[None,:])%TWO_PI

    stop=False
    def _stop(*_):
        nonlocal stop; stop=True
    signal.signal(signal.SIGTERM,_stop); signal.signal(signal.SIGINT,_stop)

    receipt=root/'receipts'/'time_crystal_aux_tether.json'; receipt.parent.mkdir(parents=True,exist_ok=True)
    binding=root/'ciel_binding_status'
    write_vec(fb_path,np.asarray(surface['phi'],dtype=np.float64))
    binding.write_text('ACTIVE\n',encoding='utf-8')
    tick=0; started=time.time_ns()
    while not stop:
        batch=np.asarray(htri['batch_phi'],dtype=np.float64)
        batch=(batch + args.crystal_feedback_k*np.sin(wrap_delta(aux[None,:],batch))) % TWO_PI
        htri['batch_phi']=batch

        summary=evolve_htri_batch_system(htri,dt=args.dt)
        feed_htri_to_surface(htri,surface,flush=True)
        crystal=np.asarray(summary['mean_batch_phi'],dtype=np.float64)%TWO_PI
        write_vec(crystal_path,crystal)

        phi=np.asarray(surface['phi'],dtype=np.float64).copy()%TWO_PI
        aux=(aux + args.aux_k*np.sin(wrap_delta(phi,aux)))%TWO_PI
        write_vec(aux_path,aux)

        feedback=(phi + args.crystal_feedback_k*np.sin(wrap_delta(aux,phi)))%TWO_PI
        write_vec(fb_path,feedback)
        flush_surface(surface)
        tick+=1
        if tick==1 or tick%25==0:
            payload={
              'schema':'noema.time-crystal-aux-tether/v1','status':'ACTIVE','pid':os.getpid(),
              'root':str(root),'started_ns':started,'updated_ns':time.time_ns(),'tick':tick,
              'surface_origin':surface_origin,'crystal_origin':crystal_origin,
              'n_crystal_oscillators':int(N_HTRI_TOTAL),'projected_dim':36,
              'algorithm':{
                'crystal':'native ciel_geometry.noema_surface_mmap.init/evolve_htri_batch_system',
                'crystal_to_surface':'native feed_htri_to_surface',
                'aux_to_crystal':'batch_phi += Kc*sin(wrap(aux-batch_phi))',
                'surface_to_aux':'aux += Ka*sin(wrap(phi-aux))',
                'crystal_feedback_k':args.crystal_feedback_k,'aux_k':args.aux_k,'dt':args.dt,'interval':args.interval,
              },
              'coherence':{'crystal':coherence(crystal),'surface':coherence(phi),'aux':coherence(aux)},
              'sha256':{'time_crystal_phi':sha(crystal_path),'phi':sha(root/'phi'),'aux_phi':sha(aux_path),'aux_feedback_phi':sha(fb_path)},
              'epistemic':{'live_runtime':True,'native_htri_time_crystal':True,'simulated_stream':False,'new_crystal_is_memory_recovery':False}
            }
            tmp=receipt.with_name(receipt.name+'.tmp'); tmp.write_text(json.dumps(payload,ensure_ascii=False,indent=2,sort_keys=True)+'\n'); os.replace(tmp,receipt)
        time.sleep(max(0.02,args.interval))
    binding.write_text('INACTIVE\n',encoding='utf-8')
    return 0

if __name__=='__main__': raise SystemExit(main())
