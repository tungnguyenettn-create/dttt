#!/usr/bin/env python3
"""Do cac thong so cua .model trong ngspice o 20/25/30 C va so voi bang du lieu (datasheet) trong thu muc."""
import re, subprocess, os
M = open('core.inc').read()
models = '\n'.join(l for l in M.splitlines() if l.lower().startswith('.model'))
def sp(body, T):
    open('_d.cir', 'w').write(f'* dc\n{models}\n{body}\n.temp {T}\n.end\n')
    return subprocess.run(['ngspice', '-b', '_d.cir'], capture_output=True, text=True).stdout
def g(o, k):
    m = re.search(re.escape(k)+r'\s*=\s*(\S+)', o); return float(m.group(1)) if m else float('nan')

def bjt_pt(model, pol, ic, vce, T):
    """Dat dong Ic bang nguon dong vao base lap -> dung 'Ic' lam bien: dung nguon ap Vbe quet roi noi suy; don gian: dung nguon dong Ib vao va doc Ic."""
    s = 1 if pol == 'n' else -1
    # tim Vbe bang quet (bang .dc roi noi suy) -> dung nguon ap Vbe va ve Ic, Ib
    body = f"Vce c 0 {s*vce}\nVbe b 0 0\nQ1 c b 0 {model}\n.control\nset noaskquit\ndc Vbe {s*0.45} {s*0.95} {s*0.0005}\nlet icc=-i(Vce)\nlet ibb=-i(Vbe)\nwrdata _o.txt icc ibb\n.endc"
    open('_d.cir', 'w').write(f'* t\n{models}\n{body}\n.temp {T}\n.end\n')
    subprocess.run(['ngspice', '-b', '_d.cir'], capture_output=True, text=True)
    import numpy as np
    a = np.loadtxt('_o.txt'); vb = a[:, 0]; icv = a[:, 1]*(-1 if False else 1); ibv = a[:, 3]
    ic_a = abs(a[:, 1]); ib_a = abs(a[:, 3])
    i = np.argmin(abs(np.log(ic_a+1e-30)-np.log(ic)))
    return abs(vb[i]), ic_a[i]/max(ib_a[i], 1e-30)

print('=== BJT: Vbe(on) va hFE (Vce theo bang du lieu) ===')
print(f"{'linh kien':10s}{'dieu kien':24s}{'T':>4s}{'Vbe(V)':>8s}{'hFE':>8s}   datasheet")
for T in (20, 25, 30):
    for mdl, pol, ic, vce, ds in (('BC547','n',2e-3,5,'Vbe 0.58-0.70 (typ 0.66), hFE 110-800'),
                                  ('BC557','p',2e-3,5,'Vbe 0.55-0.70 (typ 0.62), hFE 180-460 (B), typ 290'),
                                  ('BD139','n',150e-3,2,'hFE 40-250 (BD139-10: 63-160; -16: 100-250)'),
                                  ('BD140','p',150e-3,2,'hFE 40-250'),
                                  ('BD139','n',500e-3,2,'Vbe(on) <= 1 V, hFE >= 25'),
                                  ('BD140','p',500e-3,2,'Vbe(on) <= 1 V, hFE >= 25'),
                                  ('BD139','n',5e-3,2,'hFE >= 25')):
        vb, hfe = bjt_pt(mdl, pol, ic, vce, T)
        print(f'{mdl:10s}{f"Ic={ic*1e3:g}mA Vce={vce}V":24s}{T:4d}{vb:8.3f}{hfe:8.0f}   {ds}')
print('\n=== JFET 2N5457 (Vds = 15 V) ===')
for T in (20, 25, 30):
    o = sp(f"Vd d 0 15\nVg g 0 0\nJ1 d g 0 2N5457\n.control\nset noaskquit\nop\nlet idd=-i(Vd)\nprint idd @j1[gm] @j1[gds]\n.endc", T)
    # VGS(off): Id=10 nA -> dc sweep
    open('_d.cir','w').write(f'* t\n{models}\nVd d 0 15\nVg g 0 -1\nJ1 d g 0 2N5457\n.control\nset noaskquit\ndc Vg -3 0 0.001\nlet idd=-i(Vd)\nwrdata _o.txt idd\n.endc\n.temp {T}\n.end\n')
    subprocess.run(['ngspice','-b','_d.cir'],capture_output=True,text=True)
    import numpy as np; a=np.loadtxt('_o.txt'); vg=a[:,0]; idv=a[:,1]
    voff = vg[np.argmin(abs(np.log(np.abs(idv)+1e-30)-np.log(10e-9)))]
    v100 = vg[np.argmin(abs(idv-100e-6))]
    print(f"T={T}: IDSS={g(o,'idd')*1e3:.3f} mA (1-5, typ 3)  gm0={g(o,'@j1[gm]')*1e3:.3f} mS (1-5, typ 3)  yos={g(o,'@j1[gds]')*1e6:.1f} uS (typ 10, max 50)  VGS(off)@10nA={voff:.2f} V (-0.5..-6)  VGS@100uA={v100:.2f} V (typ -2.5 ? ghi chu: sheet in 'iD=100 mAdc' = 100 uA)")
print('\n=== Dien dung (tinh tu tham so .model, VT=0) ===')
print('  BC547: Cob(Vcb=10V) = CJC/(1+10/VJC)^MJC =', round(4/(1+10/0.75)**0.33,2), 'pF   (datasheet typ 3.5, max 6)')
print('  BC557: Cob(Vcb=10V) =', round(6/(1+10/0.75)**0.33,2), 'pF   (datasheet typ 3.0, max 6)')
print('  fT BC547 @10mA,5V ~ 1/(2pi(TF+(CJE+CJC)/gm)) =', round(1/(6.2832*(0.4e-9+15e-12/0.386))/1e6), 'MHz (datasheet typ 300)')
print('  fT BC557 @10mA,5V =', round(1/(6.2832*(0.5e-9+18e-12/0.386))/1e6), 'MHz (datasheet typ 320)')
print('\n=== Anh huong do phan tan JFET 2N5457 (trong khoang bang du lieu) len mach (27 C) ===')
print('  Bang du lieu: IDSS 1-5 mA, gm0 1-5 mS, VGS(off) -0.5..-6 V. Chon 5 "con" hop le (Beta = IDSS/Vto^2):')
print(f"  {'IDSS':>6s}{'Vto':>6s}{'gm0':>7s} | {'Id(mA)':>7s}{'Vs(V)':>7s}{'Vgs(V)':>8s}{'Vout':>7s}{'Av':>7s}{'THD%':>7s}")
def run_core(beta, vto):
    src = re.sub(r'Beta=\S+', f'Beta={beta:.6g}', M.split('.control')[0] if False else M, count=1)
    src = re.sub(r'Vto=\S+', f'Vto={vto}', src, count=1)
    open('_d.cir','w').write(src+'\n.control\nset noaskquit\nop\nprint v(out) v(s) @j1[id]\nac lin 1 1k 1k\nprint vm(outl)/vm(in)\ntran 2u 20m\nfourier 1k v(outl)\n.endc\n.end')
    return subprocess.run(['ngspice','-b','_d.cir'],capture_output=True,text=True).stdout
for idss, vto in ((1.0e-3,-1.0),(2.12e-3,-1.372),(3.0e-3,-2.0),(5.0e-3,-2.0),(3.0e-3,-3.0)):
    beta = idss/vto**2; o = run_core(beta, vto)
    thd = float(re.search(r'THD:\s*([\d.]+)', o).group(1))
    vs = g(o,'v(s)'); print(f"  {idss*1e3:6.2f}{vto:6.2f}{2*idss/abs(vto)*1e3:7.2f} | {g(o,'@j1[id]')*1e3:7.3f}{vs:7.3f}{4.5-vs:8.3f}{g(o,'v(out)'):7.3f}{g(o,'vm(outl)/vm(in)'):7.2f}{thd:7.2f}")
for f in ('_d.cir','_o.txt'):
    try: os.remove(f)
    except OSError: pass
