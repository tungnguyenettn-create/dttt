#!/usr/bin/env python3
"""Chay ngspice cho amp_classAB_jfet_fb.cir, doc file ket qua, quet Rf/Vin va ve do thi.
Dung: python3 run_and_plot.py   (can ngspice va matplotlib)"""
import re, subprocess
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

NET = Path('amp_classAB_jfet_fb.cir')
OUT = Path('plots'); OUT.mkdir(exist_ok=True)
VPK_MAX = 2.6          # bien do dinh toi da tren tai 4 ohm khong bi cat (V)
RF_LIST = [16e3, 20e3, 22e3, 24e3, 26e3, 30e3, 36e3]

def spice(net):
    return subprocess.run(['ngspice', '-b', str(net)], capture_output=True, text=True).stdout

def num(pat, txt, default=float('nan')):
    m = re.search(pat, txt); return float(m.group(1)) if m else default

def sim(rf, amp):
    """Tra ve (Av, THD%) o 1kHz voi Rf va bien do vao amp."""
    src = NET.read_text().split('.control')[0]
    src = re.sub(r'\.param rf=\S+', f'.param rf={rf}', src, count=1)
    src = re.sub(r'amp=\S+', f'amp={amp}', src, count=1)
    src += ('.control\nac lin 1 1k 1k\nprint vm(outl)/vm(in)\ntran 2u 20m\nfourier 1k v(outl)\n.endc\n.end\n')
    Path('_tmp.cir').write_text(src)
    o = spice('_tmp.cir')
    return num(r'vm\(outl\)/vm\(in\)\s*=\s*(\S+)', o), num(r'THD:\s*([\d.]+)', o)

# 1) netlist chinh -> op.txt, ac.txt, tran.txt, thd.txt, zin.txt, zout.txt
spice(NET)
ac, tr = np.loadtxt('ac.txt'), np.loadtxt('tran.txt')
zin, zout = np.loadtxt('zin.txt'), np.loadtxt('zout.txt')
f, atdb = ac[:, 0], ac[:, 1]
t = tr[:, 0]*1e3; vin, vout = tr[:, 1], tr[:, 7]
m = (t >= 10) & (t <= 13)

# 2) quet Rf: Av va THD voi Vin = 0.2V va voi Vin = VPK_MAX/Av
rows = []
for rf in RF_LIST:
    av, th = sim(rf, 0.2)
    amp2 = min(0.2, VPK_MAX/av)
    av2, th2 = sim(rf, amp2)
    rows.append((rf, av, th, amp2, th2)); print(f'Rf={rf/1e3:4.0f}k Av={av:5.2f} THD(0.2V)={th:5.2f}%  Vin_max={amp2:.3f}V THD={th2:5.2f}%')
rows = np.array(rows); Path('_tmp.cir').unlink(missing_ok=True)

# 3) THD theo bien do vao cho vai muc gain
amps = np.array([0.02, 0.05, 0.08, 0.12, 0.16, 0.2])
thd_vs = {rf: [sim(rf, a)[1] for a in amps] for rf in (16e3, 22e3, 30e3)}

# 4) ve
fig, ax = plt.subplots(2, 3, figsize=(16, 8.5))
ax[0, 0].plot(t[m], vin[m], label='Vin'); ax[0, 0].plot(t[m], vout[m], label='V tải 4Ω')
ax[0, 0].set(title='Transient (Rf = 20k, Vin 0.2V)', xlabel='t (ms)', ylabel='V'); ax[0, 0].legend()
ax[0, 1].semilogx(f, atdb); ax[0, 1].set(title='Đáp ứng tần số toàn mạch', xlabel='f (Hz)', ylabel='dB')
ax[0, 2].loglog(zout[:, 0], zout[:, 1], label='Zout (Ω)'); ax[0, 2].axhline(4, color='r', ls='--', label='giới hạn 4Ω')
ax[0, 2].loglog(zin[:, 0], zin[:, 1]/1e6, label='Zin (MΩ)'); ax[0, 2].set(title='Zout và Zin', xlabel='f (Hz)'); ax[0, 2].legend()
ax[1, 0].plot(rows[:, 1], rows[:, 2], 'o-', label='Vin = 0.2V'); ax[1, 0].plot(rows[:, 1], rows[:, 4], 's--', label=f'Vin ≤ {VPK_MAX}V/Av')
ax[1, 0].axhline(3, color='r', ls=':', label='mục tiêu 3%'); ax[1, 0].axvspan(10, 20, color='g', alpha=.1)
ax[1, 0].set(title='THD theo Av', xlabel='Av', ylabel='THD (%)'); ax[1, 0].legend()
for rf, v in thd_vs.items(): ax[1, 1].plot(amps, v, 'o-', label=f'Rf={rf/1e3:.0f}k')
ax[1, 1].axhline(3, color='r', ls=':'); ax[1, 1].set(title='THD theo biên độ vào', xlabel='Vin đỉnh (V)', ylabel='THD (%)'); ax[1, 1].legend()
ax[1, 2].plot(rows[:, 0]/1e3, rows[:, 1], 'o-'); ax[1, 2].axhspan(10, 20, color='g', alpha=.15)
ax[1, 2].set(title='Chỉnh gain bằng Rf', xlabel='Rf (kΩ)', ylabel='Av')
for a in ax.ravel(): a.grid(True, which='both', alpha=.3)
plt.tight_layout(); plt.savefig(OUT/'ket_qua.png', dpi=130)

f1k = np.argmin(abs(f-1e3)); fz = np.argmin(abs(zout[:, 0]-1e3)); fi = np.argmin(abs(zin[:, 0]-1e3))
print(Path('op.txt').read_text())
print(f"Av(1k)={ac[f1k,3]:.2f}  Zin(1k)={zin[fi,1]/1e6:.2f} MΩ  Zout(1k)={zout[fz,1]:.2f} Ω  THD={num(r'THD:\s*([\d.]+)', Path('thd.txt').read_text()):.2f} %")
