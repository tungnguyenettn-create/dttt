#!/usr/bin/env python3
"""Tinh tay (bang cong thuc) DC op + tin hieu nho cua amp_classAB_jfet_fb.cir,
sau do so voi ngspice (check.cir).  Khong dung ngspice de tinh, chi de DOI CHIEU.
Dung:  python3 hand_calc.py [nhiet_do_C]      (mac dinh 27 C)
"""
import re, subprocess, sys
from math import log, exp, sqrt, pi
import numpy as np

T_C = float(sys.argv[1]) if len(sys.argv) > 1 else 27.0
VT = 1.380649e-23*(T_C+273.15)/1.602176634e-19          # kT/q
VCC = 9.0

# ---------------- linh kien (lay tu netlist) ----------------
R = dict(Rsrc=100e3, Rg1=10e6, Rg2=10e6, Rs=2.2e3, Rin=1e3, Rb1a=11.5e3, Rb1b=11.5e3,
         Rb2=6e3, Rf=20e3, RE1=2.2, RE2=100., Rc1=330., Rc2=560., R1=3.1e3, R2=1e3,
         Rbl3=470., Rbl4=470., RE3=0.47, RE4=0.47, RL=4.)
C = dict(Cin=100e-9, C12=10e-6, Cf=100e-6, Cfb=470e-6, Ce=470e-6, Cc=470e-12,
         Cboot=470e-6, Cm=100e-6, Co=2200e-6)
BJT = {  # IS, BF, VAF, IKF, RB, RE
    'Q2':  (1.8e-14, 300, 100, .14, 10, 0),  'Qm':  (1.8e-14, 300, 100, .14, 10, 0),
    'Q3a': (1.8e-14, 300, 100, .14, 10, 0),  'Q4a': (2e-14, 300, 50, .1, 10, 0),
    'Q3':  (1.5e-13, 150, 100, 1.2, 1, .05), 'Q4':  (1.5e-13, 150, 60, 1.0, 1, .05)}
JF = dict(beta=1.125e-3, vto=-1.372, lam=2.3e-3, Rs_int=1., Rd_int=1.)

def vbe_of(ic, name, vce):
    """Vbe tu Ic (Gummel-Poon rut gon): Ic = IS e^{Vbe/Vt}(1+Vce/VAF)/qb, qb ~ 1+Ic/IKF."""
    IS, BF, VAF, IKF, RB, RE = BJT[name]
    qb = 1 + ic/IKF                                   # xap xi qb (Ic << IKF)
    return VT*log(ic*qb/(IS*(1+vce/VAF)))

# ============================== 1) DC ==============================
def dc():
    r = {}
    # --- Tang 1: JFET (Vg = Vcc/2 vi Rg1 = Rg2, Ig ~ 0) ---
    Vg = VCC/2; b, vto, lam = JF['beta'], JF['vto'], JF['lam']
    Rs_t = R['Rs']+JF['Rs_int']                       # Rs ngoai + Rs noi
    # Id = b(1+lam*Vds)(Vg - Id*Rs_t - Vto)^2  -> phuong trinh bac 2 theo Id (lam*Vds ~ 1%, lap 1 lan)
    Id = 2e-3
    for _ in range(5):
        vds = VCC-Id*(R['Rs']+JF['Rs_int']+JF['Rd_int'])
        bb = b*(1+lam*vds); A = Vg-vto
        qa, qb_, qc = bb*Rs_t**2, -(2*bb*A*Rs_t+1), bb*A**2
        Id = (-qb_-sqrt(qb_**2-4*qa*qc))/(2*qa)
    r['Id'] = Id; r['Vs'] = Id*R['Rs']; r['Vgs'] = Vg-Id*Rs_t
    vds = VCC-Id*Rs_t
    r['gm1'] = 2*b*(1+lam*vds)*(r['Vgs']-vto); r['gds1'] = lam*b*(r['Vgs']-vto)**2
    # --- Tang 2 + 3: giai vong DC (bien Ic2) ---
    Rb1 = R['Rb1a']+R['Rb1b']
    def chain(Ic2, vcv_guess=3.6):
        vcv = vcv_guess
        for _ in range(30):
            Ib2 = Ic2/BJT['Q2'][1]
            vce2 = vcv-(Ic2+Ib2)*(R['RE1']+R['RE2'])
            Vbe2 = vbe_of(Ic2, 'Q2', vce2)
            Vb2 = Vbe2 + Ib2*BJT['Q2'][4] + (Ic2+Ib2)*(R['RE1']+R['RE2'])
            Vout = Vb2 + Rb1*(Vb2/R['Rb2'] + Ib2)             # chia ap hoi tiep DC
            # --- tang ra: Ic3 = Ic4 = I, tim tu Vab ---
            # dong Qm: Ic2 = Ic_qm + Ib_qm + Vbe_qm/R2 + Ib4a
            Ie = 0.05
            for _ in range(60):                               # Ie = dong emitter Q3 (=Q4)
                Ic3 = Ie*150/151
                Ib3, Ib4 = Ic3/150, Ic3/150
                Vbe3 = vbe_of(Ic3, 'Q3', 4.0)
                Veb4 = vbe_of(Ic3, 'Q4', 5.0)
                Ie3a = Ib3 + Vbe3/R['Rbl3']; Ic3a = Ie3a*300/301
                Ie4a = Ib4 + Veb4/R['Rbl4']; Ic4a = Ie4a*300/301
                Vbe3a = vbe_of(Ic3a, 'Q3a', 2.7); Veb4a = vbe_of(Ic4a, 'Q4a', 4.3)
                Vsum = (Vbe3a + Vbe3 + Veb4 + Veb4a + Ie*(R['RE3']+R['RE4']+2*BJT['Q3'][5]))
                # Vab phai bang Vsum -> hieu chinh Ie (nghiem Newton, d/dIe ~ 2*Vt/Ie)
                Vab_need = Vsum
                # tinh Vab tu Qm
                Ib4a = Ic4a/300
                Ic_qm = Ic2 - Ib4a - 0.0
                for _ in range(40):
                    Vbe_m = vbe_of(Ic_qm, 'Qm', 2.7)
                    Iq = Ic2 - Ib4a - Vbe_m/R['R2'] - Ic_qm/300
                    Ic_qm = 0.5*(Ic_qm+Iq)
                Vbe_m = vbe_of(Ic_qm, 'Qm', 2.7)
                Vab = Vbe_m + (Vbe_m/R['R2'] + Ic_qm/300)*R['R1']
                err = Vab - Vab_need
                Ie *= exp(err/(4*VT*1.0))                      # 4 moi noi ~ 4 Vt/Ie tren dl
                if abs(err) < 1e-7: break
            vcv_new = Vout - (Veb4a + Veb4 + Ie*(R['RE4']+BJT['Q4'][5]))
            if abs(vcv_new-vcv) < 1e-7: break
            vcv = vcv_new
        Ib3a = Ic3a/300
        Va_chain = vcv + Vab
        Va_rc = VCC - (R['Rc1']+R['Rc2'])*(Ic_qm + Ic_qm/300 + (Vab-Vbe_m)/R['R1']*0 + (Vab-Vbe_m)/R['R1'] + Ib3a)
        d = dict(Ic2=Ic2, Vb2=Vb2, Vbe2=Vbe2, Vout=Vout, Vcv=vcv, Va=Va_chain, Ie=Ie, Ic3=Ic3, Ic3a=Ic3a,
                 Ic4a=Ic4a, Icqm=Ic_qm, Vab=Vab, Vbe_m=Vbe_m, Vbe3a=Vbe3a, Vbe3=Vbe3, Veb4=Veb4, Veb4a=Veb4a,
                 Ve2=(Ic2+Ib2)*(R['RE1']+R['RE2']), Vmb=vcv+Vbe_m)
        return Va_rc - Va_chain, d
    # nghiem bang chia doi (dung 1 an Ic2)
    lo, hi = 1e-3, 6e-3
    for _ in range(80):
        mid = 0.5*(lo+hi)
        if chain(lo)[0]*chain(mid)[0] <= 0: hi = mid
        else: lo = mid
    f, d = chain(0.5*(lo+hi)); r.update(d)
    r['Vm'] = VCC - R['Rc1']*(d['Ic2'] - 0)  # dong qua Rc1 = dong qua Rc2 = (Vcc-Va)/890
    r['Vm'] = VCC - R['Rc1']*(VCC-d['Va'])/(R['Rc1']+R['Rc2'])
    r['Icc'] = Id + (VCC-d['Va'])/(R['Rc1']+R['Rc2']) + d['Ic3'] + d['Ic3a'] + 2*0   # Vcc: JFET + Rc1 + Q3 + Q3a (Ic) ; Q3a/Q3 collector o Vcc
    r['Icc'] = Id + (VCC-d['Va'])/(R['Rc1']+R['Rc2']) + d['Ic3'] + d['Ic3a'] + 2*VCC/10e6
    return r

# ====================== 2) Tin hieu nho (hybrid-pi) ======================
def small_signal(d, g):
    """Tham so gm, rpi, ro cua tung BJT tu dong DC."""
    p = {}
    for nm, ic, vce in (('Q2', d['Ic2'], d['Vcv']-d['Ve2']), ('Qm', d['Icqm'], 2.7), ('Q3a', d['Ic3a'], 2.7),
                         ('Q4a', d['Ic4a'], 4.3), ('Q3', d['Ic3'], 4.0), ('Q4', d['Ic3'], 5.0)):
        IS, BF, VAF, IKF, RB, RE = BJT[nm]
        gm = ic/VT*(1/(1+ic/IKF))                    # IKF sua nhe
        p[nm] = dict(gm=gm, gpi=gm/BF, go=ic/(VAF+vce), rb=RB, re=RE, ic=ic)
    return p

def mna(d, g, p, f, mode='av'):
    """Giai mang tin hieu nho phuc tai tan so f. mode: 'av' -> (Vout/Vin, Zin);  'zout' -> Zout."""
    w = 2*pi*f; s = 1j*w
    names = ['in', 'in1', 'g', 's', 'x2', 'b2', 'nfb', 'fbx', 'out', 'outl', 'cv', 'e2', 'e2b', 'm', 'a', 'mb',
             'e3a', 'e3', 'e4a', 'e4', 'b2i', 'qmi', 'q3ai', 'q4ai', 'q3i', 'q4i']
    # b2i: nut ben trong Q2 (sau rb); q3i... tuong tu
    idx = {n: i for i, n in enumerate(names)}; N = len(names)
    Y = np.zeros((N+1, N+1), complex); I = np.zeros(N+1, complex)   # hang cuoi: nguon ap Vin
    def y(a, b_, val):                                              # dan nap giua a,b
        for (i, j, sg) in ((a, a, 1), (b_, b_, 1), (a, b_, -1), (b_, a, -1)):
            if i != 'gnd' and j != 'gnd': Y[idx[i], idx[j]] += sg*val
    def gmv(c, e, bp, ep, gm):                                       # dong gm*(vbp-vep) tu c den e
        for node, sg in ((c, 1), (e, -1)):
            if node == 'gnd': continue
            if bp != 'gnd': Y[idx[node], idx[bp]] += sg*gm
            if ep != 'gnd': Y[idx[node], idx[ep]] -= sg*gm
    Rr = lambda a, b_, v: y(a, b_, 1/v)
    Cc_ = lambda a, b_, v: y(a, b_, s*v)
    Rr('in', 'in1', R['Rsrc']); Cc_('in1', 'g', C['Cin'])
    Rr('g', 'gnd', R['Rg1']); Rr('g', 'gnd', R['Rg2'])
    # JFET: drain = Vcc (AC dat), Cgs, Cgd, gm, gds
    Cc_('g', 's', 4.627e-12/(1+0)**0.3); Cc_('g', 'gnd', 2.0e-12)
    gmv('gnd', 's', 'g', 's', g['gm1']); y('gnd', 's', g['gds1'] + 1e-12)
    Rr('s', 'gnd', R['Rs']); Cc_('s', 'x2', C['C12']); Rr('x2', 'b2', R['Rin'])
    Rr('out', 'nfb', R['Rb1a']); Rr('nfb', 'b2', R['Rb1b']); Cc_('nfb', 'gnd', C['Cf']); Rr('b2', 'gnd', R['Rb2'])
    Rr('fbx', 'b2', R['Rf']); Cc_('fbx', 'out', C['Cfb'])
    def bjt(nm, c, b, e, bi):
        q = p[nm]
        Rr(b, bi, q['rb']) if q['rb'] > 0 else None
        y(bi, e, q['gpi']); gmv(c, e, bi, e, q['gm']); y(c, e, q['go'])
    bjt('Q2', 'cv', 'b2', 'e2', 'b2i')
    Rr('e2', 'e2b', R['RE1']); Rr('e2b', 'gnd', R['RE2']); Cc_('e2b', 'gnd', C['Ce']); Cc_('cv', 'b2', C['Cc'])
    Rr('gnd', 'm', R['Rc1']); Rr('m', 'a', R['Rc2']); Cc_('m', 'out', C['Cboot'])
    bjt('Qm', 'a', 'mb', 'cv', 'qmi'); Rr('a', 'mb', R['R1']); Rr('mb', 'cv', R['R2']); Cc_('a', 'cv', C['Cm'])
    # Q3a/Q3 (NPN, collector = Vcc = dat AC), emitter co dien tro RE noi
    bjt('Q3a', 'gnd', 'a', 'e3a', 'q3ai'); bjt('Q3', 'gnd', 'e3a', 'e3', 'q3i')
    Rr('e3a', 'e3', R['Rbl3']); Rr('e3', 'out', R['RE3']+BJT['Q3'][5])
    bjt('Q4a', 'gnd', 'cv', 'e4a', 'q4ai'); bjt('Q4', 'gnd', 'e4a', 'e4', 'q4i')
    Rr('e4a', 'e4', R['Rbl4']); Rr('e4', 'out', R['RE4']+BJT['Q4'][5])
    Cc_('out', 'outl', C['Co'])
    if mode == 'av':
        Rr('outl', 'gnd', R['RL'])
        Y[idx['in'], N] = 1; Y[N, idx['in']] = 1; I[N] = 1          # Vin = 1 V
        x = np.linalg.solve(Y, I)
        return x[idx['outl']], 1/(-x[N]) if abs(x[N]) > 0 else np.inf, x, idx
    # Zout: tat Vin (noi dat), bo RL, bom 1 A vao outl
    Rr('outl', 'gnd', 1e9)
    Rr('in', 'gnd', 1e-6)                                            # Vin = 0
    I[idx['outl']] = 1
    Y[N, N] = 1
    x = np.linalg.solve(Y, I)
    return x[idx['outl']], None, x, idx

def run_spice(extra_ctl, mods=()):
    """Chay ngspice (batch) tren ban sao core.inc co the doi gia tri; tra ve stdout."""
    src = open('core.inc').read()
    for pat, rep in mods: src = re.sub(pat, rep, src, count=1, flags=re.M)
    open('_t.cir', 'w').write(src + '\n.control\n' + extra_ctl + '\n.endc\n.end\n')
    return subprocess.run(['ngspice', '-b', '_t.cir'], capture_output=True, text=True).stdout

def getv(out, key):
    return float(re.search(re.escape(key)+r'\s*=\s*(\S+)', out).group(1))

def ngspice_ref():
    out = subprocess.run(['ngspice', '-b', 'check.cir'], capture_output=True, text=True).stdout
    keys = ['v(g)', 'v(s)', 'v(b2)', 'v(e2)', 'v(cv)', 'v(a)', 'v(m)', 'v(mb)', 'v(out)', '@j1[id]', '@j1[gm]',
            '@q2[ic]', '@q2[gm]', '@qm[ic]', '@q3[ic]', '@q3[gm]', '@q3a[ic]', '@q3a[gm]', '@q4[ic]', '@q4a[ic]',
            'i(vcc)', 'vm(outl)/vm(in)']
    ref = {k: getv(out, k) for k in keys}
    # Zin: Rsrc ~ 0, do vm(in)/|i(vin)|
    o = run_spice('ac lin 1 1k 1k\nprint vm(in)/mag(i(vin))', [(r'^Rsrc in in1 100k', 'Rsrc in in1 1m')])
    ref['zin'] = getv(o, 'vm(in)/mag(i(vin))')
    # Zout: tat nguon vao (vac=0), bo RL, bom dong 1 A
    o = run_spice('ac lin 1 1k 1k\nprint vm(outl)', [(r'iac=0', 'iac=1'), (r'vac=1', 'vac=0'), (r'rl=4', 'rl=1G')])
    ref['zout'] = getv(o, 'vm(outl)')
    return ref

def analytic(d, g, p):
    """Cong thuc gan dung tung tang (khop voi hand_analysis.md)."""
    a = {}
    Rsh = 1/(1/R['Rb2'] + 1/R['Rb1b'] + 1/(p['Q2']['rb'] + 1/p['Q2']['gpi'] + (1+BJT['Q2'][1])*R['RE1']))
    gm2e = p['Q2']['gm']*(1/p['Q2']['gpi'])/(p['Q2']['rb'] + 1/p['Q2']['gpi'] + (1+BJT['Q2'][1])*R['RE1'])
    # tang 3: Rout cua moi nhanh Darlington (nguon ap ly tuong)
    def rpath(n, na, RE, Rbl, b3, b3a):
        r_pi3 = 1/p[n]['gpi']; r_pi3a = 1/p[na]['gpi']
        return (RE + BJT[n][5] + (BJT[n][4]+r_pi3)/(b3+1) +
                (BJT[na][4]+r_pi3a)/(b3a+1)*(1+(BJT[n][4]+r_pi3)/Rbl)/(b3+1))
    R3 = rpath('Q3', 'Q3a', R['RE3'], R['Rbl3'], 150, 300); R4 = rpath('Q4', 'Q4a', R['RE4'], R['Rbl4'], 150, 300)
    Rp = R3*R4/(R3+R4); RLp = 1/(1/R['RL'] + 1/R['Rc1'])
    Zx = 5e3
    for _ in range(30):                                  # dong thoi G va Zx (bootstrap)
        Rout3 = Rp + Zx/(150*300*2)
        G = RLp/(RLp+Rout3)
        Zx = 1/(1/(R['Rc2']/(1-G)) + p['Q2']['go'] + p['Qm']['go']*0)
    Zb2 = Rsh*(R['Rf']/(1+0))                            # chi dung de in
    A = -gm2e*Zx*G
    Zs1 = 1/(g['gm1'] + 1/R['Rs'])                      # tro ra tang 1 (= 1/gm || Rs)
    Zsh_in = 1/(1/Rsh + 1/(R['Rin'] + Zs1))               # tro khang tai nut b2 (nguon ve 0)
    T = -A*Zsh_in/(R['Rf'] + Zsh_in)
    # Av
    Zin2_pre = R['Rin'] + 1/(1/Rsh + 1/R['Rf']*(1-A))    # 1/Rsh + (1-A)/Rf
    Zin2 = R['Rin'] + 1/(1/Rsh + (1-A)/R['Rf'])
    Rsp = 1/(1/R['Rs'] + 1/Zin2)
    Av1 = g['gm1']*Rsp/(1+g['gm1']*Rsp)
    Zin1 = R['Rg1']*R['Rg2']/(R['Rg1']+R['Rg2'])
    div = Zin1/(Zin1+R['Rsrc'])
    Av2 = -R['Rf']/R['Rin']*T/(1+T)*(R['Rin']/ (R['Rin']+0))   # xap xi: vo/vs = -(Rf/Rin) T/(1+T)
    # chinh xac hon: vo/vs = (A/Rin) / (Gtot - A/Rf)
    Gtot = 1/R['Rin'] + 1/R['Rf'] + 1/Rsh
    Av2 = (A/R['Rin'])/(Gtot - A/R['Rf'])
    # Zout: ep vo bang dong thu 1 A. Cot x bi 'bootstrap' keo theo vo => he so hoi tiep cho Zout nho hon T cho Av
    k = Zsh_in/(R['Rf']+Zsh_in)                              # vb/vo
    Zq = 1/(1/R['Rc2'] + p['Q2']['go'])
    Gb = Zq/R['Rc2']                                         # vx/vo (khi vb = 0)
    a_ = 1 - Gb + p['Q2']['gm']*0 + a['gm2e'] if False else 1 - Gb + gm2e*Zq*k   # (vo-vx)/vo
    Zout_r = 1/(a_*(1/Rout3 + 1/R['Rc2']) + 1/R['Rc1'] + (1-k)/R['Rf'])
    Zo_ol = 1/(1/(Rout3/(1-Zx/(Zx+R['Rc2']))) + 1/R['Rc1'])
    a.update(Rsh=Rsh, gm2e=gm2e, R3=R3, R4=R4, Rout3=Rout3, G=G, Zx=Zx, A=A, T=T, Zin2=Zin2, Rsp=Rsp,
             Av1=Av1, Av2=Av2, div=div, Av=div*Av1*Av2, Zin1=Zin1, Zo_ol=Zo_ol,
             Zout=Zout_r, Zs1=Zs1, k=k, Gb=Gb, a_=a_)
    # goc BW (xap xi)
    a['fL_Cin'] = 1/(2*pi*C['Cin']*(R['Rsrc']+Zin1)); a['fL_C12'] = 1/(2*pi*C['C12']*(Rsp*0+R['Rs'] + Zin2)) \
        if False else 1/(2*pi*C['C12']*(Zs1 + R['Rin'] + 1/(1/Rsh+(1-A)/R['Rf'])))
    a['fL_Co'] = 1/(2*pi*C['Co']*(R['RL'] + Zo_ol/(1+T)))
    a['fL_Cfb'] = 1/(2*pi*C['Cfb']*(R['Rf'] + Zsh_in))
    return a

if __name__ == '__main__':
    d = dc()
    g = dict(gm1=d['gm1'], gds1=d['gds1'])
    p = small_signal(d, g)
    print(f'T = {T_C} C   Vt = {VT*1e3:.3f} mV\n')
    print('===== DC (tinh tay) =====')
    for k in ['Id', 'Vgs', 'Vs', 'Ic2', 'Vbe2', 'Ve2', 'Vb2', 'Vout', 'Vcv', 'Va', 'Vab', 'Vbe_m', 'Icqm', 'Ie', 'Ic3a', 'Vbe3a', 'Vbe3', 'Veb4', 'Veb4a', 'Icc']:
        print(f'  {k:6s} = {d[k]:.5g}')
    print('\n===== gm, rpi (tinh tay) =====')
    print(f"  gm J1 = {g['gm1']*1e3:.3f} mS")
    for k, q in p.items():
        print(f"  {k:3s}: Ic={q['ic']*1e3:8.4f} mA  gm={q['gm']*1e3:9.3f} mS  rpi={1/q['gpi']:9.2f} ohm  ro={1/q['go']/1e3:7.2f} k")
    # --- cong thuc gan dung tung tang (de dua vao bao cao) ---
    Rin2_load = None
    print('\n===== Tin hieu nho 1 kHz: nut-giai MNA tu tham so tinh tay =====')
    vo, zin, x, idx = mna(d, g, p, 1e3, 'av'); print(f'  Av = {abs(vo):.3f}  (pha {np.degrees(np.angle(vo)):.1f} do)   Zin = {abs(zin)/1e6:.3f} Mohm')
    zo, _, x2, _ = mna(d, g, p, 1e3, 'zout'); print(f'  Zout = {abs(zo):.4f} ohm')
    nm = lambda n: abs(x[idx[n]])
    print(f"  |vs/vin|={nm('s')/1:.3f}  |vb2/vs|={nm('b2')/nm('s'):.4f}  |vout/vb2|={nm('out')/nm('b2'):.1f}")
    a = analytic(d, g, p)
    print('\n===== Cong thuc gan dung tung tang (tinh tay) =====')
    for k, u in (('Rsh', 'ohm'), ('gm2e', 'S'), ('R3', 'ohm'), ('R4', 'ohm'), ('Rout3', 'ohm'), ('G', ''), ('Zx', 'ohm'),
                 ('A', ''), ('T', ''), ('Zin2', 'ohm'), ('Rsp', 'ohm'), ('Av1', ''), ('div', ''), ('Av2', ''), ('Av', ''),
                 ('Zin1', 'ohm'), ('Zo_ol', 'ohm'), ('k', ''), ('Gb', ''), ('a_', ''), ('Zout', 'ohm'), ('fL_Cin', 'Hz'), ('fL_C12', 'Hz'), ('fL_Cfb', 'Hz'), ('fL_Co', 'Hz')):
        print(f'  {k:7s} = {a[k]:.5g} {u}')
    ref = ngspice_ref()
    print('\n===== SO SANH: tinh tay vs ngspice =====')
    rows = [('Id J1 (mA)', d['Id']*1e3, ref['@j1[id]']*1e3), ('Vs (V)', d['Vs'], ref['v(s)']),
            ('gm J1 (mS)', g['gm1']*1e3, ref['@j1[gm]']*1e3), ('Vb2 (V)', d['Vb2'], ref['v(b2)']),
            ('Ve2 (V)', d['Ve2'], ref['v(e2)']), ('Ic Q2 (mA)', d['Ic2']*1e3, ref['@q2[ic]']*1e3),
            ('gm Q2 (mS)', p['Q2']['gm']*1e3, ref['@q2[gm]']*1e3), ('Vcv (V)', d['Vcv'], ref['v(cv)']),
            ('Va (V)', d['Va'], ref['v(a)']), ('Vm (V)', d['Vm'], ref['v(m)']), ('Vmb (V)', d['Vmb'], ref['v(mb)']),
            ('Ic Qm (mA)', d['Icqm']*1e3, ref['@qm[ic]']*1e3), ('Ic Q3 (mA)', d['Ic3']*1e3, ref['@q3[ic]']*1e3),
            ('gm Q3 (mS)', p['Q3']['gm']*1e3, ref['@q3[gm]']*1e3), ('Ic Q3a (mA)', d['Ic3a']*1e3, ref['@q3a[ic]']*1e3),
            ('Vout DC (V)', d['Vout'], ref['v(out)']), ('Icc (mA)', d['Icc']*1e3, -ref['i(vcc)']*1e3),
            ('Av 1kHz (MNA)', abs(vo), ref['vm(outl)/vm(in)']), ('Av 1kHz (cong thuc)', abs(a['Av']), ref['vm(outl)/vm(in)']),
            ('Zin (Mohm) (MNA)', abs(zin)/1e6, ref['zin']/1e6), ('Zin (Mohm) (cong thuc)', a['Zin1']/1e6, ref['zin']/1e6),
            ('Zout (ohm) (MNA)', abs(zo), ref['zout']), ('Zout (ohm) (cong thuc)', a['Zout'], ref['zout'])]
    print(f"  {'dai luong':26s}{'tay':>12s}{'ngspice':>12s}{'sai lech':>10s}")
    for n, h, sp in rows: print(f'  {n:26s}{h:12.5g}{sp:12.5g}{(h/sp-1)*100:9.2f}%')
