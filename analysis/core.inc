* AMPLI AM TAN - JFET 2N5457 -> VAS CE (hoi tiep song song) -> Darlington class AB
* Nguon don 9V, tai 4 ohm. Chinh gain bang Rf (hoi tiep AC tu ngo ra ve de Q2):
*   Rf = 16k -> Av ~ 10 | 20k -> ~12 | 24k -> ~14.3 (xem run_and_plot.py)
.param rf=20k rc2=560 rin=1k cc=470p amp=0.2 vac=1 iac=0 rl=4

.model BC547 NPN(IS=1.8e-14 BF=300 NF=1 VAF=100 IKF=0.14 RB=10 RC=1 CJE=11p CJC=4p TF=0.4n)
.model BC557 PNP(IS=2e-14 BF=300 NF=1 VAF=50 IKF=0.1 RB=10 RC=1 CJE=12p CJC=6p TF=0.5n)
.model BD139 NPN(IS=1.5e-13 BF=150 NF=1 VAF=100 IKF=1.2 RB=1 RC=0.1 RE=0.05 CJE=60p CJC=20p TF=1n)
.model BD140 PNP(IS=1.5e-13 BF=150 NF=1 VAF=60 IKF=1.0 RB=1 RC=0.1 RE=0.05 CJE=60p CJC=25p TF=1n)
.MODEL 2N5457 NJF(Beta=1.125m Betatce=-.5 Rd=1 Rs=1 Lambda=2.3m Vto=-1.372
+ Vtotc=-2.5m Is=181.3f Isr=1.747p N=1 Nr=2 Xti=3 Alpha=2.543u
+ Vk=152.2 Cgd=4p M=.3114 Pb=.5 Fc=.5 Cgs=4.627p Kf=10.45E-18 Af=1)

Vcc vcc 0 9
Vin in 0 DC 0 AC {vac} SIN(0 {amp} 1k)

* ---- Tang 1: JFET source follower ----
Rsrc in in1 100k
Cin  in1 g 100n
Rg1  vcc g 10Meg
Rg2  g 0 10Meg
J1   vcc g s 2N5457
Rs   s 0 2.2k
C12  s x2 10u
Rin2 x2 b2 {rin}

* ---- Tang 2: VAS (CE) ----
* Hoi tiep DC giu diem giua ngo ra (Cf chan AC)
Rb1a out nfb 11.5k
Rb1b nfb b2 11.5k
Cf   nfb 0 100u
Rb2  b2 0 6.0k
* Hoi tiep AC song song (ngo ra -> de Q2), quyet dinh gain va giam THD
Rf   fbx b2 {rf}
Cfb  fbx out 470u
Q2   cv b2 e2 BC547
RE1  e2 e2b 2.2
RE2  e2b 0 100
Ce   e2b 0 470u
Cc   cv b2 {cc}
* Tai bootstrap cho VAS (tang tro khang tai AC, mo rong bien do dinh duong)
Rc1  vcc m 330
Rc2  m a {rc2}
Cboot m out 470u

* ---- Tang 3: Class AB Darlington + Vbe multiplier (4 Vbe) ----
Qm   a mb cv BC547
R1   a mb 3.1k
R2   mb cv 1k
Cm   a cv 100u
Q3a  vcc a e3a BC547
Q3   vcc e3a e3 BD139
Rbl3 e3a e3 470
RE3  e3 out 0.47
Q4a  0 cv e4a BC557
Q4   0 e4a e4 BD140
Rbl4 e4a e4 470
RE4  e4 out 0.47
Co   out outl 2200u
RL   outl 0 {rl}
Itest 0 outl DC 0 AC {iac}

