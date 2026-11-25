#!/usr/bin/env python3
"""Nghien cuu do nhay khi dien tro lech +-10 %:
 (a) tung dien tro mot (OAT) -10 % / +10 %   (b) Monte-Carlo nhieu dien tro cung luc   (c) goc xau nhat + nhiet do 20/30 C
Dung:  python3 sens_resistors.py          (can ngspice, numpy, matplotlib; ~ vai phut)"""
import sys, csv, random
from pathlib import Path
from multiprocessing import Pool
import numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
sys.path.insert(0, str(Path(__file__).resolve().parent))
import sens_lib as L

OUT = L.HERE/'ket_qua_nhay'; OUT.mkdir(exist_ok=True)
RESL = L.RES + ['RL']
KEYS = ['Vout','Id','Ic2','Icqm','Ic3','Ic4','Icc','Av','Zin','Zout','THD','fL','fH','P3','Vclip_p','Vclip_n']
UNIT = dict(Vout=('V',1), Id=('mA',1e3), Ic2=('mA',1e3), Icqm=('mA',1e3), Ic3=('mA',1e3), Ic4=('mA',1e3), Icc=('mA',1e3),
            Av=('',1), Zin=('MΩ',1e-6), Zout=('Ω',1), THD=('%',1), fL=('Hz',1), fH=('kHz',1e-3), P3=('mW',1e3),
            Vclip_p=('V',1), Vclip_n=('V',1))
def work(job): return L.run(job[0], job[1])
def spec(r):
    """Dat yeu cau ky thuat? Av 10-20, THD<3 %, Ic3 20-100 mA, Vout 3.5-5.5 V, bien do cat >= 2 V moi phia."""
    return (10 < r['Av'] < 20 and r['THD'] < 3 and 0.020 < r['Ic3'] < 0.100 and 3.5 < r['Vout'] < 5.5
            and min(r['Vclip_p'], r['Vclip_n']) >= 2.0)

if __name__ == '__main__':
    N_MC = int(sys.argv[1]) if len(sys.argv) > 1 else 400
    pool = Pool(16)
    base = L.run()
    print('Co so:', {k: round(base[k]*UNIT[k][1], 4) for k in KEYS})
    # ---------------- (a) OAT ----------------
    jobs = [({r: f}, 27) for r in RESL for f in (0.9, 1.1)]
    res = pool.map(work, jobs)
    oat = {}
    for (sc, _), rr in zip(jobs, res): oat[(list(sc)[0], list(sc.values())[0])] = rr
    with open(OUT/'oat_pm10.csv', 'w', newline='') as fh:
        w = csv.writer(fh); w.writerow(['res', 'scale'] + KEYS + ['dat_yeu_cau'])
        w.writerow(['nominal', 1.0] + [base[k] for k in KEYS] + [spec(base)])
        for (r, f), rr in oat.items(): w.writerow([r, f] + [rr[k] for k in KEYS] + [spec(rr)])
    # bang % thay doi
    print('\n=== (a) Thay doi tuong doi (%) khi tung dien tro -10% / +10%  ===')
    hdr = ['Av', 'Vout', 'Ic3', 'Icc', 'THD', 'Zout', 'fL', 'fH', 'Vclip_p', 'Vclip_n']
    print(f"{'R':6s}{'±':>3s}" + ''.join(f'{h:>9s}' for h in hdr))
    for r in RESL:
        for f in (0.9, 1.1):
            rr = oat[(r, f)]
            print(f"{r:6s}{'-' if f < 1 else '+':>3s}" + ''.join(f'{(rr[h]/base[h]-1)*100:9.2f}' for h in hdr) + ('' if spec(rr) else '   <-- ngoai spec'))
    # tornado
    fig, axs = plt.subplots(2, 3, figsize=(17, 9))
    for ax, (k, ttl) in zip(axs.ravel(), [('Av', 'Hệ số khuếch đại Av'), ('Ic3', 'Dòng nghỉ Q3 (BD139)'), ('Vout', 'Điện áp ra DC'),
                                          ('THD', 'THD @ Vin=0.2 V'), ('Zout', 'Zout'), ('fH', 'Tần số cắt trên f-3dB')]):
        d = [(r, (oat[(r, 0.9)][k]/base[k]-1)*100, (oat[(r, 1.1)][k]/base[k]-1)*100) for r in RESL]
        d.sort(key=lambda t: max(abs(t[1]), abs(t[2])))
        d = d[-10:]; y = np.arange(len(d))
        ax.barh(y, [t[1] for t in d], color='tab:blue', label='R −10 %'); ax.barh(y, [t[2] for t in d], color='tab:red', alpha=.7, label='R +10 %')
        ax.set_yticks(y); ax.set_yticklabels([t[0] for t in d]); ax.set_title(ttl); ax.set_xlabel('thay đổi (%)'); ax.axvline(0, color='k', lw=.8); ax.grid(alpha=.3); ax.legend()
    plt.tight_layout(); plt.savefig(OUT/'tornado.png', dpi=120); plt.close()
    # ---------------- (b) Monte-Carlo ----------------
    random.seed(1)
    mc_all = {}
    for tol in (0.10, 0.05, 0.01):
        jobs = [({r: 1+random.uniform(-tol, tol) for r in L.RES}, 27) for _ in range(N_MC)]
        rr = pool.map(work, jobs); mc_all[tol] = rr
        with open(OUT/f'montecarlo_{int(tol*100)}pct.csv', 'w', newline='') as fh:
            w = csv.writer(fh); w.writerow(KEYS + ['dat_yeu_cau']); [w.writerow([x[k] for k in KEYS] + [spec(x)]) for x in rr]
    print(f'\n=== (b) Monte-Carlo ({N_MC} lan, phan bo deu, 27 C) ===')
    print(f"{'dai luong':10s}{'dung sai':>8s}{'min':>10s}{'TB':>10s}{'max':>10s}{'sigma':>10s}")
    for k in ['Av', 'Vout', 'Ic3', 'Icc', 'THD', 'Zout', 'fH', 'Vclip_p', 'Vclip_n']:
        for tol, rr in mc_all.items():
            a = np.array([x[k] for x in rr])*UNIT[k][1]
            print(f"{k:10s}{tol*100:7.0f}%{a.min():10.3f}{a.mean():10.3f}{a.max():10.3f}{a.std():10.3f}  {UNIT[k][0]}")
    for tol, rr in mc_all.items():
        ok = sum(spec(x) for x in rr); print(f'dat yeu cau voi dung sai {tol*100:.0f}%: {ok}/{N_MC}')
    fig, axs = plt.subplots(2, 3, figsize=(16, 8))
    for ax, k in zip(axs.ravel(), ['Av', 'Vout', 'Ic3', 'THD', 'Zout', 'fH']):
        for tol, c in ((0.10, 'tab:red'), (0.05, 'tab:orange'), (0.01, 'tab:green')):
            ax.hist(np.array([x[k] for x in mc_all[tol]])*UNIT[k][1], bins=30, alpha=.55, color=c, label=f'±{tol*100:.0f} %')
        ax.set_title(f'{k} ({UNIT[k][0]})'); ax.legend(); ax.grid(alpha=.3)
    plt.tight_layout(); plt.savefig(OUT/'montecarlo.png', dpi=120); plt.close()
    # ---------------- (c) goc xau nhat ----------------
    # dau cua dao ham OAT quyet dinh huong; moi chi tieu: chon dau tung dien tro de cuc tri hoa chi tieu
    print('\n=== (c) Goc xau nhat (moi dien tro ±10 % theo dau tu OAT) x nhiet do 20/30 C ===')
    corners = {}
    for k in ['Av', 'Ic3', 'Vout', 'THD', 'Vclip_p', 'Vclip_n', 'Zout', 'fH']:
        for sense, nm in ((+1, 'max'), (-1, 'min')):
            sc = {}
            for r in L.RES:
                dm, dp = oat[(r, 0.9)][k]-base[k], oat[(r, 1.1)][k]-base[k]
                sc[r] = 1.1 if sense*dp > sense*dm else 0.9
            corners[(k, nm)] = sc
    jobs = [(sc, T) for (k, nm), sc in corners.items() for T in (20, 30)]
    rr = pool.map(work, jobs)
    print(f"{'muc tieu':14s}{'T':>4s}{'Av':>7s}{'Vout':>7s}{'Ic3mA':>7s}{'Icc':>7s}{'THD%':>7s}{'Zout':>7s}{'fHkHz':>7s}{'Vclp+':>7s}{'Vclp-':>7s}  spec")
    for (sc, T), x in zip(jobs, rr):
        key = [kk for kk, v in corners.items() if v is sc][0]
        print(f"{key[1]+' '+key[0]:14s}{T:4d}{x['Av']:7.2f}{x['Vout']:7.2f}{x['Ic3']*1e3:7.1f}{x['Icc']*1e3:7.1f}{x['THD']:7.2f}{x['Zout']:7.2f}{x['fH']/1e3:7.1f}{x['Vclip_p']:7.2f}{x['Vclip_n']:7.2f}  {'OK' if spec(x) else 'XAU'}")
    with open(OUT/'corners.csv', 'w', newline='') as fh:
        w = csv.writer(fh); w.writerow(['corner', 'T'] + KEYS)
        for (sc, T), x in zip(jobs, rr): w.writerow([[kk for kk, v in corners.items() if v is sc][0], T] + [x[k] for k in KEYS])
