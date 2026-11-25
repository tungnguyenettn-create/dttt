#!/usr/bin/env python3
"""Tao hinh minh hoa cho README (matplotlib). Chay trong thu muc analysis/. Mach goc: ../amp_classAB_jfet_fb.cir"""
import re, subprocess, tempfile, shutil, sys
from pathlib import Path
import numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
HERE = Path(__file__).resolve().parent; FIG = HERE/'figures'; FIG.mkdir(exist_ok=True)
NET = HERE.parent/'amp_classAB_jfet_fb.cir'
sys.path.insert(0, str(HERE)); import hand_calc as H
num = lambda k, o: float(re.search(re.escape(k)+r'\s*=\s*(\S+)', o).group(1))

# 1) so do khoi
fig, ax = plt.subplots(figsize=(14, 4.6)); ax.axis('off'); ax.set_xlim(0, 14); ax.set_ylim(0, 4.6)
def box(x, w, t, c, y=1.2, h=2.2):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.05', fc=c, ec='k')); ax.text(x+w/2, y+h/2, t, ha='center', va='center', fontsize=9)
def arr(x0, x1, y=2.3): ax.add_patch(FancyArrowPatch((x0, y), (x1, y), arrowstyle='->', mutation_scale=15))
box(0.1, 1.1, 'Vin\n0,2 V\n1 kHz', '#eee'); box(1.6, 1.1, 'Rsrc\n100 kΩ', '#eee')
box(3.1, 2.6, 'Tầng 1\nJFET 2N5457\nsource follower\nRg1‖Rg2 = 5 MΩ\nId≈2,06 mA\nAv1≈0,69', '#cfe8ff')
box(6.1, 3.2, 'Tầng 2: VAS\nBC547 CE\nIc≈3 mA, bootstrap Rc1/Rc2\nhồi tiếp AC Rf (shunt)\nAv2≈−18', '#ffe0b3')
box(9.7, 2.6, 'Tầng 3: class-AB\nVbe-multiplier Qm\nBD139/BD140 Darlington\nIq≈52 mA, Zout≈0,33 Ω', '#d5f0d0')
box(12.6, 1.2, 'RL = 4 Ω\n(Co 2200 µF)\nVpk≈2,9 V\n(kỳ vọng Av≈12)', '#eee')
for a, b in ((1.2, 1.6), (2.7, 3.1), (5.7, 6.1), (9.3, 9.7), (12.3, 12.6)): arr(a, b)
ax.annotate('', xy=(7.7, 1.15), xytext=(13.0, 1.15), arrowprops=dict(arrowstyle='->', ls='--', color='r', connectionstyle='arc3,rad=0'))
ax.text(10.3, 0.65, 'hồi tiếp: Rf+Cfb (AC) và Rb1a/Rb1b (DC) từ ngõ ra về đế Q2', color='r', ha='center', fontsize=9)
ax.text(7, 4.2, 'Cấu trúc tổng thể amp_classAB_jfet_fb.cir  (Vcc = 9 V)', ha='center', fontsize=12, weight='bold')
plt.savefig(FIG/'so_do_khoi.png', dpi=130, bbox_inches='tight'); plt.close()

# 2) tay vs ngspice
d = H.dc(); g = dict(gm1=d['gm1'], gds1=d['gds1']); p = H.small_signal(d, g); a = H.analytic(d, g, p); ref = H.ngspice_ref()
vo, zin, _, _ = H.mna(d, g, p, 1e3, 'av'); zo, *_ = H.mna(d, g, p, 1e3, 'zout')
rows = [('Id J1', d['Id']*1e3, ref['@j1[id]']*1e3), ('gm J1', g['gm1']*1e3, ref['@j1[gm]']*1e3), ('Vb2', d['Vb2'], ref['v(b2)']),
        ('Ic Q2', d['Ic2']*1e3, ref['@q2[ic]']*1e3), ('Vcv', d['Vcv'], ref['v(cv)']), ('Va', d['Va'], ref['v(a)']),
        ('Ic Q3', d['Ic3']*1e3, ref['@q3[ic]']*1e3), ('Vout DC', d['Vout'], ref['v(out)']), ('Icc', d['Icc']*1e3, -ref['i(vcc)']*1e3),
        ('Av', abs(a['Av']), ref['vm(outl)/vm(in)']), ('Zin', a['Zin1']/1e6, ref['zin']/1e6), ('Zout', a['Zout'], ref['zout'])]
err = [(h/s-1)*100 for _, h, s in rows]
fig, ax = plt.subplots(1, 2, figsize=(14, 4.8))
ax[0].bar([r[0] for r in rows], err, color=['tab:red' if abs(e) > 1 else 'tab:blue' for e in err]); ax[0].axhline(0, color='k')
ax[0].set(title='Sai lệch tính tay so với ngspice (%)', ylabel='%'); ax[0].tick_params(axis='x', rotation=60); ax[0].grid(alpha=.3)
ac_names = ['Av1 (vs/vin)', 'Av2', 'Av tổng']; sp = [0.6718, None, ref['vm(outl)/vm(in)']]
ax[1].bar(['Av tay', 'Av ngspice'], [abs(a['Av']), ref['vm(outl)/vm(in)']], color=['tab:blue', 'tab:orange'])
ax[1].set(title=f"Av 1 kHz: tay {abs(a['Av']):.2f} / ngspice {ref['vm(outl)/vm(in)']:.2f}", ylim=(0, 14)); ax[1].grid(alpha=.3)
plt.tight_layout(); plt.savefig(FIG/'tay_vs_spice.png', dpi=130); plt.close()
for f_ in ('_t.cir',): (HERE/f_).unlink(missing_ok=True)

# 3) tan so: chay mach goc trong thu muc tam
tmp = Path(tempfile.mkdtemp()); shutil.copy(NET, tmp/'amp.cir')
subprocess.run(['ngspice', '-b', 'amp.cir'], cwd=tmp, capture_output=True, text=True)
ac = np.loadtxt(tmp/'ac.txt'); zi = np.loadtxt(tmp/'zin.txt'); zout = np.loadtxt(tmp/'zout.txt'); tr = np.loadtxt(tmp/'tran.txt')
t = tr[:, 0]*1e3; m = (t >= 10) & (t <= 13)
fig, ax = plt.subplots(2, 2, figsize=(14, 9))
ax[0, 0].plot(t[m], tr[m, 1], label='Vin'); ax[0, 0].plot(t[m], tr[m, 7], label='V tải 4Ω'); ax[0, 0].set(title='Transient 1 kHz, Vin = 0,2 V (THD 0,63 %)', xlabel='ms', ylabel='V'); ax[0, 0].legend()
ax[0, 1].semilogx(ac[:, 0], ac[:, 1]); ax[0, 1].set(title='Đáp ứng tần số toàn mạch (f−3dB ≈ 25 Hz … 15 kHz)', xlabel='Hz', ylabel='dB')
ax[1, 0].loglog(zout[:, 0], zout[:, 1]); ax[1, 0].set(title='Zout (Ω) – bỏ RL, hồi tiếp đóng', xlabel='Hz', ylabel='Ω')
ax[1, 1].loglog(zi[:, 0], zi[:, 1]/1e6); ax[1, 1].set(title='Zin (MΩ) tại ngõ vào (Rsrc→0)', xlabel='Hz', ylabel='MΩ')
for x in ax.ravel(): x.grid(True, which='both', alpha=.3)
plt.tight_layout(); plt.savefig(FIG/'tan_so_zin_zout.png', dpi=130); plt.close()
shutil.rmtree(tmp, ignore_errors=True)

# 4) nhiet do
core = (HERE/'core.inc').read_text()
CTL = '\n.control\nset noaskquit\nop\nprint v(out) @q3[ic] i(vcc)\nac lin 1 1k 1k\nprint vm(outl)/vm(in)\n.endc\n.end'
def sim(src):
    (HERE/'_t.cir').write_text(src+CTL); o = subprocess.run(['ngspice', '-b', str(HERE/'_t.cir')], capture_output=True, text=True).stdout
    return num('v(out)', o), num('@q3[ic]', o)*1e3, -num('i(vcc)', o)*1e3, num('vm(outl)/vm(in)', o)
Ts = np.arange(10, 61, 5); allT = np.array([sim(core+f'\n.temp {T}\n') for T in Ts])
bd = []
for T in Ts:
    s = re.sub(r'^(Q[34] .*)$', lambda m_: m_.group(1)+f' temp={T}', core, flags=re.M); bd.append(sim(s))
bd = np.array(bd)
heat = {}
for Rth in (100, 50, 25):
    xs = []
    for Tamb in (20, 25, 30):
        Tj = Tamb
        for _ in range(30):
            s = re.sub(r'^(Q[34] .*)$', lambda m_: m_.group(1)+f' temp={Tj}', core, flags=re.M)
            vo, i3, icc, av = sim(s+f'\n.temp {Tamb}\n'); Tn = Tamb+Rth*(9-vo)*i3*1e-3
            if abs(Tn-Tj) < .05: break
            Tj = .5*(Tj+Tn)
        xs.append((Tamb, Tj, i3))
    heat[Rth] = xs
(HERE/'_t.cir').unlink(missing_ok=True)
fig, ax = plt.subplots(1, 3, figsize=(17, 4.8))
ax[0].plot(Ts, allT[:, 1], 'o-', label='mọi linh kiện cùng T'); ax[0].plot(Ts, bd[:, 1], 's--', label='chỉ BD139/BD140 nóng (Qm, driver ở 27 °C)')
ax[0].axvspan(20, 30, color='g', alpha=.12); ax[0].set(title='Dòng nghỉ Ic(Q3) theo nhiệt độ', xlabel='T (°C)', ylabel='mA'); ax[0].legend(); ax[0].grid(alpha=.3)
ax[1].plot(Ts, allT[:, 3], 'o-'); ax[1].axvspan(20, 30, color='g', alpha=.12); ax[1].set(title='Av 1 kHz theo nhiệt độ (mọi linh kiện cùng T)', xlabel='T (°C)'); ax[1].grid(alpha=.3)
for Rth, c in ((100, 'r'), (50, 'orange'), (25, 'g')): ax[2].plot([x[0] for x in heat[Rth]], [x[2] for x in heat[Rth]], 'o-', color=c, label=f'RθJA = {Rth} °C/W')
ax[2].set(title='Tự nóng BD139/140: Ic nghỉ vs Tamb', xlabel='Tamb (°C)', ylabel='mA'); ax[2].legend(); ax[2].grid(alpha=.3)
plt.tight_layout(); plt.savefig(FIG/'nhiet_do.png', dpi=130); plt.close()
print('xong:', sorted(p.name for p in FIG.iterdir()))
