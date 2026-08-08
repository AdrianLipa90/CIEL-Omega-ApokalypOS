"""
CIEL / TIR Information Dynamics v1.1

STATUS:
    PARTIAL_CANON / EXECUTABLE

Core continuity law:
    ∂_t rho_I + div J_I = sigma_I

Current split:
    J_I = J_phase + J_residual
    J_phase = I_phi D chi
    J_residual = J_background + J_source + J_holonomy + J_boundary

IMPORTANT NOTATION FIREWALL
---------------------------
`J_residual` is a spatial vector current. It is NOT the Hamiltonian scalar
`J0` appearing in

    J = I_phi D_t chi + J0.

The latter is a scalar phase-momentum offset and is represented in
`canonical_information_backreaction.CanonicalRelationalState.J0`.

No automatic semantic classification is performed from arbitrary thresholds.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Sequence, Tuple
import math
import numpy as np

FOUR_PI = 4.0 * math.pi


@dataclass(frozen=True)
class CurrentSectors:
    """Explicit components of the residual spatial information current."""
    background: np.ndarray
    source: np.ndarray
    holonomy: np.ndarray
    boundary: np.ndarray

    def __post_init__(self):
        arrays=[np.asarray(x,dtype=float) for x in (
            self.background,self.source,self.holonomy,self.boundary
        )]
        shape=arrays[0].shape
        if len(shape)<1 or shape[-1]!=3:
            raise ValueError("current sectors must have shape (...,3)")
        if any(a.shape!=shape for a in arrays):
            raise ValueError("all current sectors must have equal shape")
        object.__setattr__(self,"background",arrays[0])
        object.__setattr__(self,"source",arrays[1])
        object.__setattr__(self,"holonomy",arrays[2])
        object.__setattr__(self,"boundary",arrays[3])

    @property
    def total_residual_current(self) -> np.ndarray:
        return self.background+self.source+self.holonomy+self.boundary


@dataclass(frozen=True)
class InformationFieldState:
    rho: np.ndarray
    phase_current: np.ndarray
    sectors: CurrentSectors
    dx: float
    time: float=0.0

    def __post_init__(self):
        rho=np.asarray(self.rho,dtype=float)
        J=np.asarray(self.phase_current,dtype=float)
        if rho.ndim!=3:
            raise ValueError("rho must be 3D")
        if J.shape!=rho.shape+(3,):
            raise ValueError("phase_current shape must be rho.shape+(3,)")
        if self.sectors.total_residual_current.shape!=J.shape:
            raise ValueError("residual-current sector shape mismatch")
        if self.dx<=0:
            raise ValueError("dx must be positive")
        object.__setattr__(self,"rho",rho)
        object.__setattr__(self,"phase_current",J)

    @property
    def residual_current(self) -> np.ndarray:
        return self.sectors.total_residual_current

    @property
    def total_current(self) -> np.ndarray:
        return self.phase_current+self.residual_current

    @property
    def total_information(self) -> float:
        return float(np.sum(self.rho)*(self.dx**3))


def cell_to_face_flux(J: np.ndarray) -> Tuple[np.ndarray,np.ndarray,np.ndarray]:
    J=np.asarray(J,dtype=float)
    if J.ndim!=4 or J.shape[-1]!=3:
        raise ValueError("J must have shape (nx,ny,nz,3)")
    nx,ny,nz,_=J.shape
    Fx=np.zeros((nx+1,ny,nz),dtype=float)
    Fy=np.zeros((nx,ny+1,nz),dtype=float)
    Fz=np.zeros((nx,ny,nz+1),dtype=float)
    if nx>1: Fx[1:nx]=0.5*(J[:-1,:,:,0]+J[1:,:,:,0])
    if ny>1: Fy[:,1:ny]=0.5*(J[:,:-1,:,1]+J[:,1:,:,1])
    if nz>1: Fz[:,:,1:nz]=0.5*(J[:,:,:-1,2]+J[:,:,1:,2])
    return Fx,Fy,Fz


def set_boundary_flux(
    faces: Tuple[np.ndarray,np.ndarray,np.ndarray],*,
    x_min: Optional[np.ndarray]=None,x_max: Optional[np.ndarray]=None,
    y_min: Optional[np.ndarray]=None,y_max: Optional[np.ndarray]=None,
    z_min: Optional[np.ndarray]=None,z_max: Optional[np.ndarray]=None,
) -> Tuple[np.ndarray,np.ndarray,np.ndarray]:
    Fx,Fy,Fz=(np.array(x,dtype=float,copy=True) for x in faces)
    if x_min is not None: Fx[0]=np.asarray(x_min,dtype=float)
    if x_max is not None: Fx[-1]=np.asarray(x_max,dtype=float)
    if y_min is not None: Fy[:,0]=np.asarray(y_min,dtype=float)
    if y_max is not None: Fy[:,-1]=np.asarray(y_max,dtype=float)
    if z_min is not None: Fz[:,:,0]=np.asarray(z_min,dtype=float)
    if z_max is not None: Fz[:,:,-1]=np.asarray(z_max,dtype=float)
    return Fx,Fy,Fz


def divergence_from_faces(faces: Tuple[np.ndarray,np.ndarray,np.ndarray],dx: float) -> np.ndarray:
    Fx,Fy,Fz=(np.asarray(x,dtype=float) for x in faces)
    if dx<=0: raise ValueError("dx must be positive")
    divx=(Fx[1:]-Fx[:-1])/dx
    divy=(Fy[:,1:]-Fy[:,:-1])/dx
    divz=(Fz[:,:,1:]-Fz[:,:,:-1])/dx
    if divx.shape!=divy.shape or divx.shape!=divz.shape:
        raise ValueError("face shapes inconsistent")
    return divx+divy+divz


def boundary_outflow(faces: Tuple[np.ndarray,np.ndarray,np.ndarray],dx: float) -> float:
    Fx,Fy,Fz=(np.asarray(x,dtype=float) for x in faces)
    area=dx*dx
    return float(area*(
        np.sum(Fx[-1])-np.sum(Fx[0])+
        np.sum(Fy[:,-1])-np.sum(Fy[:,0])+
        np.sum(Fz[:,:,-1])-np.sum(Fz[:,:,0])
    ))


@dataclass(frozen=True)
class ContinuityReceipt:
    dt: float
    before_information: float
    after_information: float
    source_integral: float
    boundary_outflow: float
    balance_residual: float
    max_local_residual: float


def continuity_step_from_faces(
    state: InformationFieldState,
    faces: Tuple[np.ndarray,np.ndarray,np.ndarray],
    source_density: np.ndarray,
    dt: float,
) -> Tuple[InformationFieldState,ContinuityReceipt]:
    if dt<=0: raise ValueError("dt must be positive")
    sigma=np.asarray(source_density,dtype=float)
    if sigma.shape!=state.rho.shape:
        raise ValueError("source density shape mismatch")
    divJ=divergence_from_faces(faces,state.dx)
    rho_new=state.rho+dt*(sigma-divJ)
    before=state.total_information
    after=float(np.sum(rho_new)*state.dx**3)
    src=float(np.sum(sigma)*state.dx**3)
    bout=boundary_outflow(faces,state.dx)
    local=(rho_new-state.rho)/dt+divJ-sigma
    residual=(after-before)+dt*bout-dt*src
    new_state=InformationFieldState(rho_new,state.phase_current,state.sectors,state.dx,state.time+dt)
    return new_state,ContinuityReceipt(
        float(dt),before,after,src,bout,float(residual),float(np.max(np.abs(local)))
    )


def zero_sectors(shape3: Tuple[int,int,int]) -> CurrentSectors:
    z=np.zeros(tuple(shape3)+(3,),dtype=float)
    return CurrentSectors(z.copy(),z.copy(),z.copy(),z.copy())


def phase_rotor_current(D_chi: np.ndarray,I_phi: float) -> np.ndarray:
    """Spatial rotor current J_phase=I_phi D chi; not scalar canonical J."""
    d=np.asarray(D_chi,dtype=float)
    if d.ndim<1 or d.shape[-1]!=3:
        raise ValueError("D_chi must have shape (...,3)")
    I=float(I_phi)
    if I<=0: raise ValueError("I_phi must be positive")
    return I*d


def radial_green_current_cells(
    shape3: Tuple[int,int,int],dx: float,*,flux: float,
    center: Optional[Sequence[float]]=None,
) -> np.ndarray:
    nx,ny,nz=shape3
    if dx<=0: raise ValueError
    if center is None:
        center=((nx*dx)/2.0,(ny*dx)/2.0,(nz*dx)/2.0)
    c=np.asarray(center,dtype=float)
    if c.shape!=(3,): raise ValueError("center must be a 3-vector")
    xs=(np.arange(nx)+0.5)*dx; ys=(np.arange(ny)+0.5)*dx; zs=(np.arange(nz)+0.5)*dx
    X,Y,Z=np.meshgrid(xs,ys,zs,indexing="ij")
    R=np.stack([X-c[0],Y-c[1],Z-c[2]],axis=-1)
    rr=np.linalg.norm(R,axis=-1)
    J=np.zeros_like(R); mask=rr>0
    J[mask]=float(flux)/FOUR_PI*R[mask]/(rr[mask,None]**3)
    return J


def rotational_holonomy_cells(
    shape3: Tuple[int,int,int],dx: float,omega: Sequence[float],*,
    center: Optional[Sequence[float]]=None,
) -> np.ndarray:
    nx,ny,nz=shape3
    if center is None:
        center=((nx*dx)/2.0,(ny*dx)/2.0,(nz*dx)/2.0)
    c=np.asarray(center,dtype=float); w=np.asarray(omega,dtype=float)
    if c.shape!=(3,) or w.shape!=(3,): raise ValueError
    xs=(np.arange(nx)+0.5)*dx; ys=(np.arange(ny)+0.5)*dx; zs=(np.arange(nz)+0.5)*dx
    X,Y,Z=np.meshgrid(xs,ys,zs,indexing="ij")
    R=np.stack([X-c[0],Y-c[1],Z-c[2]],axis=-1)
    return np.cross(np.broadcast_to(w,R.shape),R)


@dataclass(frozen=True)
class ResidualCurrentClassification:
    background_declared: bool
    source_declared: bool
    holonomy_declared: bool
    boundary_declared: bool
    status: str


def classify_declared_residual_current(sectors: CurrentSectors) -> ResidualCurrentClassification:
    return ResidualCurrentClassification(True,True,True,True,"EXPLICIT_SECTOR_DECLARATION")


@dataclass(frozen=True)
class InformationDynamicsSnapshot:
    time: float
    total_information: float
    phase_current_norm: float
    residual_current_norm: float
    total_current_norm: float


def snapshot(state: InformationFieldState) -> InformationDynamicsSnapshot:
    return InformationDynamicsSnapshot(
        float(state.time),state.total_information,
        float(np.linalg.norm(state.phase_current)),
        float(np.linalg.norm(state.residual_current)),
        float(np.linalg.norm(state.total_current)),
    )


__all__=[
    "CurrentSectors","InformationFieldState","cell_to_face_flux","set_boundary_flux",
    "divergence_from_faces","boundary_outflow","ContinuityReceipt","continuity_step_from_faces",
    "zero_sectors","phase_rotor_current","radial_green_current_cells","rotational_holonomy_cells",
    "ResidualCurrentClassification","classify_declared_residual_current",
    "InformationDynamicsSnapshot","snapshot",
]
