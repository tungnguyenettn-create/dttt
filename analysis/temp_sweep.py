#!/usr/bin/env python3
"""Quet nhiet do 20/25/30/40 C: DC, Av, THD, cong suat (ngspice)."""
import re, subprocess, os
src = open('core.inc').read()
CTL = """.control
set noaskquit
op
print v(out) @j1[id] @q2[ic] @qm[ic] @q3[ic] @q4[ic] i(vcc)
ac lin 1 1k 1k
print vm(outl)/vm(in)
tran 2u 20m
fourier 1k v(outl)
.endc
.end"""
def num(k, o): return float(re.search(re.escape(k)+r'\s*=\s*(\S+)', o).group(1))
print(f"{'T(C)':>5}{'Vout':>8}{'Id_J1(mA)':>10}{'Ic_Q2':>8}{'Ic_Q3':>8}{'Ic_Q4':>8}{'Icc(mA)':>9}{'Av':>7}{'THD%':>7}{'P_Q3(mW)':>9}")
for T in (20, 25, 27, 30, 40):
    open('_t.cir','w').write(src+f'\n.temp {T}\n'+CTL)
    o = subprocess.run(['ngspice','-b','_t.cir'],capture_output=True,text=True).stdout
    vo=num('v(out)',o); ic3=num('@q3[ic]',o)*1e3; ic4=-num('@q4[ic]',o)*1e3
    print(f"{T:5d}{vo:8.3f}{num('@j1[id]',o)*1e3:10.3f}{num('@q2[ic]',o)*1e3:8.3f}{ic3:8.2f}{ic4:8.2f}{-num('i(vcc)',o)*1e3:9.2f}"
          f"{num('vm(outl)/vm(in)',o):7.2f}{float(re.search(r'THD:\s*([\d.]+)',o).group(1)):7.3f}{(9-vo)*ic3:9.1f}")
import os; os.remove('_t.cir')

# ---- Tu nong cua BD139/BD140 (Qm, driver giu o nhiet do moi truong; khong ghep nhiet) ----
# Lap: Tj = Tamb + Rth*P ; P = (Vcc-Vout)*Ic3 (cong suat tinh/ transistor). Rth_JA = 100 C/W (datasheet BD139, khong tan nhiet)
print('\nTu nong BD139/BD140 (vong lap Tj = Tamb + RthJA*P), khong ghep nhiet voi Qm:')
print(f"{'Tamb':>5}{'RthJA':>7}{'Tj_out':>8}{'Ic_Q3(mA)':>10}{'P(mW)':>8}{'Icc(mA)':>9}")
src2 = src
for Tamb in (20, 30):
    for Rth in (100, 50, 25):
        Tj = Tamb
        for _ in range(25):
            s = re.sub(r'^(Q[34] .*)$', lambda m: m.group(1)+f' temp={Tj}', src2, flags=re.M)
            s = re.sub(r'^(Q[34]a .*)$', lambda m: m.group(1)+f' temp={Tamb}', s, flags=re.M)
            open('_t.cir','w').write(s+f'\n.temp {Tamb}\n.control\nset noaskquit\nop\nprint v(out) @q3[ic] i(vcc)\n.endc\n.end')
            o = subprocess.run(['ngspice','-b','_t.cir'],capture_output=True,text=True).stdout
            vo, i3, icc = num('v(out)',o), num('@q3[ic]',o), -num('i(vcc)',o)
            P = (9-vo)*i3; Tn = Tamb + Rth*P
            if abs(Tn-Tj) < 0.05: break
            Tj = 0.5*(Tj+Tn)
        print(f'{Tamb:5d}{Rth:7d}{Tj:8.1f}{i3*1e3:10.1f}{P*1e3:8.0f}{icc*1e3:9.1f}')
os.remove('_t.cir')
