# Phân tích tay: DC, gm, Av, Zin, Zout – đối chiếu ngspice

Mạch: `amp_classAB_jfet_fb.cir` (Vcc = 9 V, RL = 4 Ω). T = 27 °C, Vt = kT/q = 25,87 mV (20 °C: 25,26 mV; 30 °C: 26,12 mV).
Các số dưới đây do `hand_calc.py` tính từ **công thức và tham số model** (không dùng ngspice), rồi so với `check.cir`/ngspice. Bảng tổng ở mục 5.

Công thức BJT: Ic = IS·e^{Vbe/Vt}·(1+Vce/VAF)/qb, qb ≈ 1+Ic/IKF; Ib = Ic/BF; gm = Ic/Vt; rπ = β/gm; ro = (VAF+Vce)/Ic.

## 1. DC – từng tầng

### Tầng 1 – JFET 2N5457 (source follower)
Ig ≈ 0, Rg1 = Rg2 ⇒ **Vg = Vcc/2 = 4,5 V**. Beta = 1,125 mA/V², Vto = −1,372 V, λ = 2,3 m/V.
Id = β(1+λVds)(Vgs − Vto)², Vgs = Vg − Id·Rs (Rs = 2,2 k + 1 Ω nội)
⇒ với A = Vg − Vto = 5,872 V: β'Rs²·Id² − (2β'A·Rs + 1)·Id + β'A² = 0 (β' = β(1+λVds), Vds ≈ 4,5 V ⇒ β' = 1,1366 m).
Nghiệm nhỏ: **Id = 2,057 mA**, Vs = Id·Rs = **4,525 V**, Vgs = −0,027 V.
**gm1 = 2β'(Vgs − Vto) = 3,058 mS**, gds = λβ(Vgs−Vto)² = 4,7 µS.

### Tầng 2 – VAS Q2 (BC547)
Tụ ngăn DC. Tại b2: dòng từ Vout qua Rb1a+Rb1b = 23 kΩ, xuống Rb2 = 6 kΩ và vào base:
(Vout − Vb2)/23k = Vb2/6k + Ib2 ⇒ **Vout = Vb2·(1 + 23/6) + 23k·Ib2**.
Vb2 = Vbe2 + Ib2·RB + Ie2·(RE1+RE2), RE1+RE2 = 102,2 Ω.
Với Ic2 ≈ 3,0 mA: Vbe2 = Vt·ln(Ic/(IS(1+Vce/VAF))) = 0,668 V; Ie2·102,2 = 0,308 V ⇒ **Vb2 = 0,976 V**, Ve2 = 0,308 V; Ib2 = 10 µA ⇒ Vout = 4,949 V.
(Ic2 được xác định bằng điều kiện đóng vòng, mục dưới.)

### Tầng 3 – bộ nhân Vbe + Darlington
- Qm (BC547): R2 song song BE ⇒ Vmb − Vcv = Vbe_m; dòng R1 = Vbe_m/R2 + Ib_m; **Vab = Va − Vcv = Vbe_m + R1·(Vbe_m/R2 + Ib_m)** ≈ Vbe_m(1 + R1/R2) = 2,74 V (Vbe_m = 0,662 V ở Icqm = 2,33 mA).
- Đường a→cv: Vab = Vbe3a + Vbe3 + Ie·(RE3+RE4+2·RE_nội) + Veb4 + Veb4a. Hai nhánh đối xứng, Ie ≈ Ic3 + Ib3 ⇒ giải lặp: mỗi lần Vab sai 1 mV, Ie đổi ~ 4% ⇒ Newton: Ie ← Ie·exp(ΔV/(4Vt)).
 Kết quả: Ic3 = Ic4 = **53,1 mA** (Ie = 53,4 mA); Vbe3 = 0,688 V; Vbe3a = 0,655 V (Ic3a = Ie3a ≈ Ib3 + Vbe3/Rbl3 = 1,81 mA); Veb4a = 0,651 V.
- Nút Vm, Va: dòng qua Rc1+Rc2 = 890 Ω là tổng dòng ra khỏi nút a: **Va = 9 − 890·(Ic_qm + Ib_qm + I_R1 + Ib3a) = 6,32 V**, Vm = 9 − 330·I = 8,01 V.

### Đóng vòng DC (ẩn số Ic2)
Một ẩn Ic2 cho hai biểu thức của Va:
(i) Va = Vcv + Vab, trong đó Vcv = Vout − (Veb4a + Veb4 + Ie·RE4') với Vout lấy từ chia áp hồi tiếp ở trên;
(ii) Va = 9 − 890·I(Rc).
Chia đôi trên Ic2 ∈ [1, 6] mA (`hand_calc.py: dc()`): **Ic2 = 3,004 mA**, Vcv = 3,583 V, Va = 6,319 V, Vout = **4,949 V**, Icc = Id + I(Rc) + Ic3 + Ic3a ≈ **59,9 mA**.
(Vout ≈ 4,95 V không phải 4,5 V: chia áp 11,5+11,5 k / 6 k và Vbe quyết định, không phải Vcc/2.)

## 2. Tham số tín hiệu nhỏ (1 kHz, tụ nối tắt)
| | Ic (mA) | gm (mS) | rπ (Ω) | ro |
|---|---|---|---|---|
| J1 | 2,057 | **3,058** | – | 1/gds = 213 k |
| Q2 | 3,004 | **113,7** | 2 638 | 34,4 k |
| Qm | 2,329 | 88,6 | 3 387 | 44,1 k |
| Q3a / Q4a | 1,81 | 69,1 / 68,7 | 4 339 / 4 366 | 56,7 k / 30 k |
| Q3 / Q4 | 53,1 | **1 964 / 1 948** | 76,4 / 77,0 | 2,0 k / 1,2 k |

Tại 1 kHz: Cin, C12, Cf, Cfb, Ce, Cboot, Cm, Co ≈ ngắn mạch; Cc (470 pF) hở. Đã cho: Cm nối a ≡ cv (AC); Cboot nối m ≡ out ⇒ Rc2 chỉ chịu (vx − vout), Rc1 = 330 Ω chuyển thành tải 330 Ω song song RL.

## 3. Hệ số khuếch đại Av (từng tầng)

**Tầng 1**: Av1 = gm1·Rs'/(1 + gm1·Rs'), Rs' = Rs ‖ Zin2. Zin2 = Rin + [Rsh ‖ Rf/(1−A)] (hồi tiếp song song làm nút b2 gần "đất ảo") = 1 066 Ω ⇒ Rs' = 718 Ω, gm1Rs' = 2,196 ⇒ **Av1 = 0,687**; chia áp nguồn: Zin1/(Zin1 + Rsrc) = 5 M/5,1 M = 0,980 ⇒ vs/vin = 0,673.

**Tầng 3 (đệm)**: Rout mỗi nhánh (nguồn lý tưởng):
R3 = (RE3+RE_nội) + (rb+rπ3)/(β3+1) + [(rb+rπ3a)/(β3a+1)]·(1+(rb+rπ3)/Rbl3)/(β3+1) = 0,52 + 0,513 + 0,111 = **1,144 Ω**; R4 = 1,149 Ω. Song song: 0,573 Ω; cộng trở nguồn phản xạ Zx/(2·β3β3a) ⇒ Rout3 = 0,614 Ω.
Tải AC RL' = RL ‖ Rc1 = 3,95 Ω ⇒ **G = RL'/(RL'+Rout3) = 0,865**.

**Tầng 2 (VAS, bootstrap)**: Rc2 hiệu dụng = Rc2/(1−G) = 4,2 kΩ ⇒ Zx = Rc2eff ‖ ro2 = 3,7 kΩ (lặp G, Zx).
gm hiệu dụng (RE1 = 2,2 Ω không bypass): gm2e = gm·rπ/(rb + rπ + (β+1)·RE1) = 113,7 m × 2638/3310 = **90,6 mS**.
Hệ số "mở vòng" tại b2: **A = vout/vb2 = −gm2e·Zx·G = −291** (ngspice: −306).

**Hồi tiếp song song**: KCL tại b2 (Rsh = Rb2 ‖ Rb1b ‖ Zb = 1,80 kΩ):
vb(1/Rin + 1/Rf + 1/Rsh) = vs/Rin + vout/Rf, vout = A·vb
⇒ **Av2 = vout/vs = (A/Rin)/(Gtot − A/Rf) = −18,0**, Gtot = 1/Rin+1/Rf+1/Rsh.
Tương đương: Av2 ≈ −(Rf/Rin)·T/(1+T), T = |A|·Zsh/(Rf+Zsh) = **10,5** ⇒ −20 · 0,913 = −18,3.

**Av toàn mạch**: Av = 0,980 × 0,687 × (−18,01) = **−12,13** (độ lớn 12,13 ≈ 21,7 dB; pha ≈ 180° do tầng 2 đảo, tầng 3 và 1 không đảo; ngspice báo 178° vì Co). Kiểm nhanh: Av ≈ (Rf/Rin2)·(vs/vin)·T/(1+T) = 20·0,673·0,913 ≈ 12,3.

## 4. Zin và Zout
**Zin** (tại `in`, Rsrc → 0, 1 kHz): Zin = 1/(jωCin) nối tiếp (Rg1 ‖ Rg2 ‖ Cgs…) ≈ **5,0 MΩ** (do không bootstrap cổng). Với Rsrc = 100 kΩ thực tế nguồn thấy 5,1 MΩ. f cắt dưới do Cin: 1/(2π·100n·5,1M) = 0,3 Hz.
(MNA: 5,07 MΩ; ngspice: 4,98 MΩ – chênh 1,8 % do rò gate/Cgd model.)

**Zout** (tắt Vin, bỏ RL, bơm 1 A tại tải): vì Cboot kéo cột x theo vout nên hệ số hồi tiếp cho Zout nhỏ hơn T của Av.
k = vb/vout = Zsh'/(Rf+Zsh') = 0,0361; Zq = Rc2 ‖ ro2 = 558 Ω; vx/vout (vb = 0) = Zq/Rc2 = 0,984;
a = (vout − vx)/vout = 1 − 0,984 + gm2e·Zq·k = 1,82.
**Zout = 1 / [a(1/Rout3 + 1/Rc2) + 1/Rc1 + (1−k)/Rf] = 0,337 Ω** (+ −j0,072 Ω của Co ở 1 kHz).
Mở vòng (không hồi tiếp): ≈ 4,6 Ω; hồi tiếp (+bootstrap) giảm còn ~0,34 Ω; bootstrap làm Zout mở vòng lớn hơn bình thường (≈ cỡ tải 4 Ω) nên mạch dựa vào hồi tiếp để có Zout thấp (damping factor ≈ 12).

**Băng thông (xấp xỉ)**: fL(Cin) = 0,3 Hz; fL(Cfb) = 0,02 Hz; fL(C12) ≈ 12 Hz; fL(Co) = 1/(2π·Co·(RL+Zout)) = **16 Hz** (ngspice tổng −3 dB ở 25 Hz). fH ≈ 12–15 kHz (nút Cc/Cπ, từ ngspice).

## 5. Đối chiếu tay – ngspice (T = 27 °C)
(`hand_calc.py` ⇒ `hand_calc_out.txt`)

| Đại lượng | Tay | ngspice | Sai lệch |
|---|---|---|---|
| Id J1 | 2,0567 mA | 2,0567 | 0,00 % |
| Vs | 4,5247 V | 4,5248 | 0,00 % |
| gm J1 | 3,058 mS | 3,058 | 0,00 % |
| Vb2 | 0,9762 V | 0,9769 | −0,07 % |
| Ve2 | 0,3081 V | 0,3085 | −0,14 % |
| Ic Q2 | 3,004 mA | 3,009 | −0,15 % |
| gm Q2 | 113,7 mS | 113,95 | −0,21 % |
| Vcv | 3,583 V | 3,585 | −0,05 % |
| Va | 6,319 V | 6,322 | −0,04 % |
| Vm | 8,006 V | 8,007 | −0,01 % |
| Vmb | 4,245 V | 4,247 | −0,05 % |
| Ic Qm | 2,329 mA | 2,333 | −0,19 % |
| Ic Q3 | 53,06 mA | 52,30 | +1,4 % |
| gm Q3 | 1 964 mS | 1 943 | +1,1 % |
| Ic Q3a | 1,811 mA | 1,815 | −0,22 % |
| Vout DC | 4,949 V | 4,951 | −0,05 % |
| Icc | 59,9 mA | 59,2 | +1,3 % |
| **Av 1 kHz** (MNA) | 12,15 | 12,13 | +0,2 % |
| **Av** (công thức tay) | 12,13 | 12,13 | 0,0 % |
| **Zin** (công thức / MNA) | 5,00 / 5,07 MΩ | 4,98 MΩ | +0,3 / +1,8 % |
| **Zout** (công thức / MNA) | 0,337 / 0,328 Ω | 0,332 Ω | +1,5 / −1,1 % |

Nguyên nhân sai lệch lớn nhất (Ic Q3 +1,4 %): xấp xỉ hiệu ứng IKF/Early của Gummel-Poon và RB/RE nội; ở dòng 52 mA, 1 % dòng ↔ 0,6 mV Vbe. Mọi đại lượng DC/AC trong ≤ 2 % ⇒ **phân tích tay được xác nhận**.

Kiểm tra bằng ngspice nằm trong `check.cir` (op, `@dev[gm]`, tỷ số điện áp từng tầng: vs/vin = 0,672; vb2/vs = 0,059; vout/vb2 = 306; Av = 12,13).
