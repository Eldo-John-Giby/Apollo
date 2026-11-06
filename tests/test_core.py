import math, numpy as np
from gazeforge_core.core import *
C=Config()
def test_sweep():
    s=sweep_inputs()
    assert len(s)==10 and s[0][2]==0 and abs(s[0][3]-1)<1e-15
    assert abs(s[3][2]-0.9510565162951536)<1e-15 and abs(s[3][3]+0.30901699437494734)<1e-15
    assert abs(s[3][1]-1.8849555921538759)<1e-15
def test_rest():
    q=shortest_arc(FWD,FWD); assert np.allclose(q,[1,0,0,0])
def test_gaze_hits_target():
    for h,v in [(0,0),(1,0),(-1,1),(0.3,-0.7)]:
        st,P=eye_state(h,v,C)
        for n,Ce in eye_centers(C).items():
            g=st[n]["R"]@FWD; assert np.allclose(g,st[n]["gaze"],atol=1e-12)
            t=np.dot(P-Ce,g); assert np.linalg.norm(Ce+t*g-P)<1e-12
def test_no_torsion_listing():
    # rotation axis perpendicular to primary direction
    for h,v in [(1,1),(-1,0.5),(0,-1)]:
        st,_=eye_state(h,v,C)
        for n in 'LR':
            q=st[n]["quat"]; assert abs(q[1:]@FWD)<1e-12
def test_center_px():
    st,_=eye_state(0,0,C)
    assert abs(st["L"]["pupil2d"][0]-735.1828745)<1e-5 and abs(st["L"]["pupil2d"][1]-512)<1e-9
    assert abs(st["R"]["pupil2d"][0]-288.8171255)<1e-5
def test_directions():
    c0,_=eye_state(0,0,C)
    for (h,v,sx,sy) in [(1,0,+1,0),(-1,0,-1,0),(0,1,0,-1),(0,-1,0,+1)]:  # image y is down
        s,_=eye_state(h,v,C)
        for n in 'LR':
            dx=s[n]["pupil2d"][0]-c0[n]["pupil2d"][0]; dy=s[n]["pupil2d"][1]-c0[n]["pupil2d"][1]
            if sx: assert dx*sx>9 and abs(dy)<0.2
            if sy: assert dy*sy>9 and abs(dx)<0.2
def test_euler_roundtrip():
    for h,v in [(1,1),(-1,0.2)]:
        st,_=eye_state(h,v,C)
        for n in 'LR':
            x,y,z=st[n]["euler"]
            Rx=np.array([[1,0,0],[0,math.cos(x),-math.sin(x)],[0,math.sin(x),math.cos(x)]])
            Ry=np.array([[math.cos(y),0,math.sin(y)],[0,1,0],[-math.sin(y),0,math.cos(y)]])
            Rz=np.array([[math.cos(z),-math.sin(z),0],[math.sin(z),math.cos(z),0],[0,0,1]])
            assert np.allclose(Rz@Ry@Rx, st[n]["R"], atol=1e-12)
def test_clockwise():
    c0,_=eye_state(0,0,C); pts=[]
    for k,th,h,v in sweep_inputs():
        s,_=eye_state(h,v,C); pts.append((s["L"]["pupil2d"][0]-c0["L"]["pupil2d"][0], -(s["L"]["pupil2d"][1]-c0["L"]["pupil2d"][1])))
    ang=[math.atan2(y,x) for x,y in pts]
    d=[(ang[(i+1)%10]-ang[i]+math.pi)%(2*math.pi)-math.pi for i in range(10)]
    assert all(x<0 for x in d)   # decreasing math-angle (y up) == clockwise on screen
def test_record_keys():
    r=make_record(3,*sweep_inputs()[3][1:],C,"frame_03.png")
    assert list(r)[:8]==["frame","theta","input","eye_rotation_L","eye_rotation_R","pupil_center_2D_L","pupil_center_2D_R","camera_matrix"]

def test_gaze_angles_and_ellipse():
    st,_=eye_state(0,0,C)
    p,y=gaze_pitch_yaw(st["L"]["gaze"]); assert abs(p)<1e-12
    assert y>0 and abs(y-math.radians(5.1427645))<1e-6     # converged eye: nasal yaw, small
    up,_=eye_state(0,1,C); assert gaze_pitch_yaw(up["L"]["gaze"])[0]>0.13   # looking up => positive pitch
    e=pupil_ellipse_2d(st["L"]["pupil3d"],st["L"]["gaze"],PUPIL_RADIUS,C)
    assert abs(e["center"][0]-st["L"]["pupil2d"][0])<0.01 and abs(e["center"][1]-st["L"]["pupil2d"][1])<0.01
    assert 12<e["semi_axes"][0]<16 and e["semi_axes"][1]<=e["semi_axes"][0]   # ~ 2mm radius = ~14 px
def test_eccentricity_bound():
    for h,v in [(1,1),(-1,-1),(1,-1)]:
        st,_=eye_state(h,v,C)
        for n in 'LR': assert angle_from_primary(st[n]["quat"])<MAX_ECCENTRICITY

