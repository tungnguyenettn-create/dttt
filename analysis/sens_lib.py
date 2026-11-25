"""Thu vien chay ngspice cho nghien cuu do nhay (dung chung)."""
import re, subprocess, tempfile, os, shutil
import numpy as np
from pathlib import Path

HERE = Path(__file__).resolve().parent
CORE = (HERE/'core.inc').read_text()
RES = ['Rsrc','Rg1','Rg2','Rs','Rin2','Rb1a','Rb1b','Rb2','Rf','RE1','RE2','Rc1','Rc2','R1','R2','Rbl3','Rbl4','RE3','RE4']
NOMINAL = {}
for r in RES:
    m = re.search(rf'^{r}\s+\S+\s+\S+\s+(\{{?\w+\}}?|[\d.]+\w*)\s*$', CORE, flags=re.M|re.I)
    NOMINAL[r] = m.group(1)

PAR = {'rf':20e3,'rc2':560.,'rin':1e3}
def _val(tok):
    tok = tok.strip('{}')
    if tok in PAR: return PAR[tok]
    mult = {'meg':1e6,'k':1e3,'m':1e-3,'u':1e-6,'n':1e-9,'p':1e-12,'g':1e9}
    m = re.match(r'([\d.]+)(meg|k|m|u|n|p|g)?$', tok.lower())
    return float(m.group(1))*mult.get(m.group(2), 1)
NOM = {r: _val(NOMINAL[r]) for r in RES}
NOM['RL'] = 4.0

def build(scale=None, temp=27, extra_params=None):
    """Tra ve netlist (khong co .control) voi dien tro nhan he so scale[r] (dict) va nhiet do."""
    scale = scale or {}
    src = CORE
    for r in RES:
        if r in scale and scale[r] != 1.0:
            v = NOM[r]*scale[r]
            src = re.sub(rf'^({r}\s+\S+\s+\S+\s+)(\{{?\w+\}}?|[\d.]+\w*)\s*$', lambda m: f'{m.group(1)}{v:.6g}', src, count=1, flags=re.M|re.I)
    if 'RL' in scale:
        src = re.sub(r'rl=4', f'rl={4*scale["RL"]:.6g}', src, count=1)
    return src + f'\n.temp {temp}\n'

def num(key, o, default=float('nan')):
    m = re.search(re.escape(key)+r'\s*=\s*(\S+)', o)
    return float(m.group(1)) if m else default

CTL_MAIN = """.control
set noaskquit
op
print v(out) @j1[id] @q2[ic] @qm[ic] @q3[ic] @q4[ic] i(vcc)
ac lin 1 1k 1k
print vm(outl)/vm(in)
let zinx = mag(v(in1)/(v(in)-v(in1)))*RSRC
print zinx
ac dec 40 1 20Meg
let at=vm(outl)/vm(in)
wrdata AC at
tran 2u 20m
fourier 1k v(outl)
alter Vin = 0
.endc
.end"""
# clip: bien do lon, do dinh +/- cua v(outl)
CTL_CLIP = """.control
set noaskquit
tran 5u 12m
meas tran vmx max v(outl) from=6m to=12m
meas tran vmn min v(outl) from=6m to=12m
.endc
.end"""
CTL_ZOUT = """.control
set noaskquit
ac lin 1 1k 1k
print vm(outl)
.endc
.end"""

def run(scale=None, temp=27, tag='x'):
    d = Path(tempfile.mkdtemp(prefix='sens_'))
    try:
        base = build(scale, temp)
        rs = NOM['Rsrc']*(scale or {}).get('Rsrc', 1.0)
        (d/'a.cir').write_text(base + CTL_MAIN.replace('AC', str(d/'ac.txt')).replace('RSRC', f'{rs:.6g}'))
        o = subprocess.run(['ngspice','-b',str(d/'a.cir')], capture_output=True, text=True, timeout=300).stdout
        res = dict(Vout=num('v(out)',o), Id=num('@j1[id]',o), Ic2=num('@q2[ic]',o), Icqm=num('@qm[ic]',o),
                   Ic3=num('@q3[ic]',o), Ic4=-num('@q4[ic]',o), Icc=-num('i(vcc)',o),
                   Av=num('vm(outl)/vm(in)',o), Zin=num('zinx',o))
        m = re.search(r'THD:\s*([\d.]+)', o); res['THD'] = float(m.group(1)) if m else float('nan')
        try:
            ac = np.loadtxt(d/'ac.txt'); f, at = ac[:,0], ac[:,1]
            a1k = at[np.argmin(abs(f-1e3))]; ok = at >= a1k/np.sqrt(2)
            idx = np.where(ok & (f > 1))[0]
            res['fL'] = f[idx[0]] if len(idx) else np.nan; res['fH'] = f[idx[-1]] if len(idx) else np.nan
        except Exception: res['fL'] = res['fH'] = np.nan
        res['P3'] = (9-res['Vout'])*res['Ic3'] if res['Ic3'] == res['Ic3'] else np.nan
        # clip: amp lon
        src = re.sub(r'amp=\S+', 'amp=0.6', base, count=1)
        (d/'c.cir').write_text(src + CTL_CLIP)
        o = subprocess.run(['ngspice','-b',str(d/'c.cir')], capture_output=True, text=True, timeout=300).stdout
        res['Vclip_p'] = num('vmx', o); res['Vclip_n'] = -num('vmn', o)
        # Zout
        src = re.sub(r'iac=0', 'iac=1', base, count=1); src = re.sub(r'vac=1', 'vac=0', src, count=1); src = re.sub(r'rl=\S+', 'rl=1G', src, count=1)
        (d/'z.cir').write_text(src + CTL_ZOUT)
        o = subprocess.run(['ngspice','-b',str(d/'z.cir')], capture_output=True, text=True, timeout=300).stdout
        res['Zout'] = num('vm(outl)', o)
        return res
    finally:
        shutil.rmtree(d, ignore_errors=True)

if __name__ == '__main__':
    import time; t = time.time(); print(NOM); print(run()); print(f'{time.time()-t:.1f}s')
