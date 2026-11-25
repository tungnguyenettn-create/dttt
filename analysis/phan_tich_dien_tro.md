# Ảnh hưởng khi điện trở lệch ±10 %

Script: `sens_resistors.py` (+ `sens_lib.py`). Dữ liệu: `ket_qua_nhay/*.csv`, log `ket_qua_nhay.log`, hình `ket_qua_nhay/tornado.png`, `montecarlo.png`. Điều kiện 27 °C, Vin = 0,2 V/1 kHz.
"Đạt yêu cầu" (tự đặt): Av 10–20, THD < 3 %, Ic nghỉ Q3 20–100 mA, Vout 3,5–5,5 V, biên độ cắt ≥ 2 V mỗi phía.

Cơ sở: Av = 12,13; Vout = 4,95 V; Ic3 = 52 mA; THD = 0,63 %; Zout = 0,33 Ω; Zin = 4,98 MΩ; f−3dB = 25 Hz … 15 kHz; cắt ±2,8 V (≈1 W/4 Ω).

## (a) Từng điện trở ±10 % (thay đổi tương đối)
| R | Av | Vout | Ic nghỉ Q3 | THD | Zout |
|---|---|---|---|---|---|
| **R1** (−/+) | **−28,5 / +2,3 %** | ∓0,8 % | **−92 / +212 %** | +96 / +5 % | **+509 / −28 %** |
| **R2** (−/+) | +2,4 / **−20,7 %** | ∓0,9 % | **+230 / −89 %** | +2,5 / +77 % | −29 / +332 % |
| **Rb2** | −1,0 / +0,7 | **+4,9 / −4,2** | **−12 / +10** | +12 / −13 | +13 / −9 |
| **Rf** | **−9,2 / +9,1** | 0 | 0 | −6,7 / +1,2 | −9,2 / +9,3 |
| **Rin2** | **+8,0 / −6,9** | 0 | 0 | +8,6 / −9,3 | +4,6 / −3,9 |
| Rb1a, Rb1b | ±0,4 | ∓2,4 | ±5,9 | ∓4–5 | ∓4–5 |
| RE2 | ±0,3 | ∓1,8 | ±4,4 | ∓3,4 | ∓3,6 |
| Rc1 / Rc2 | ±0,2–0,5 | ∓0,8–1,4 | ∓3–5 | ±2–6 | ±2,5–5,7 |
| **RE3 / RE4** | ±0,2 | 0 | ∓2 | **∓23 / ∓17** | ∓2,8 |
| Rbl3/4, Rs, Rg1/2, Rsrc, RE1 | < 1 | 0 | < 2 | ≤ 2,7 | < 1,6 |
| RL (tải) | −0,8 / +0,7 | 0 | 0 | +9 / −7 | 0 |

Kết luận (a):
1. **R1, R2 (bộ nhân Vbe) quyết định dòng nghỉ**: Ic ∝ exp(ΔVab/(4·Vt)), mà Vab = Vbe·(1+R1/R2) ⇒ ±10 % R1 làm ΔVab ≈ ±0,27 V ⇒ dòng đổi gấp 3 hay giảm ~12×. R1 −10 % → class-AB gần thành class-B (Ic 4 mA, Av −28 %, Zout +509 %); R2 −10 % → Ic 173 mA (Icc ~180 mA, BD139 ~0,7 W). Cả hai vượt spec.
2. **Gain**: Av ≈ (Rf/Rin2)·T/(1+T) ⇒ gần như tỉ lệ Rf/Rin2 (±9 %/∓7 %); các điện trở khác ảnh hưởng < 1 %.
3. **Điểm giữa Vout**: do Rb2 và Rb1a/b (chia áp hồi tiếp DC) – ±5 % nhưng vẫn trong 4,25–5,7 V. Mặc định đã lệch +0,45 V so với 4,5 V (cắt +2,88 V / −2,81 V, không đối xứng nhẹ).
4. **THD** nhạy nhất ở RE3/RE4 (cân bằng 2 nhánh push-pull) và R1/R2 (chế độ class-AB).
5. Tần số cắt dưới (25 Hz) chỉ do Co·RL; hầu như không đổi với điện trở (chỉ RL).

## (b) Monte-Carlo (400 lần, tất cả điện trở ngẫu nhiên đều)
| Dung sai | Av (min–max) | Ic nghỉ Q3 | THD max | Zout max | Đạt yêu cầu |
|---|---|---|---|---|---|
| ±1 % | 11,9–12,4 | 38–70 mA | 0,67 % | 0,39 Ω | **400/400** |
| ±5 % | 9,5–13,3 | 6–160 mA | 1,2 % | 1,4 Ω | 291/400 (73 %) |
| ±10 % | 1,9–14,4 | 0,3–276 mA | 5,6 % | 19,7 Ω | **177/400 (44 %)** |

Với ±10 %: 106 mẫu Ic > 100 mA, 115 mẫu Ic < 20 mA (méo xuyên tâm), 63 mẫu Av < 10. Vout chỉ lệch 4,56–5,38 V; Av chỉ ổn khi Ic ổn (do R1/R2).
Khuyến nghị: R1/R2 dùng 1 % (hoặc thay R1 bằng trimmer 5 kΩ để chỉnh Ic nghỉ ≈ 50 mA); Rf, Rin2 1 %; còn lại 5–10 % chấp nhận được.

## (c) Góc xấu nhất (tất cả điện trở ±10 % theo dấu từ (a)), 20 và 30 °C
Mọi góc cực trị đều **ngoài spec**: Av 0,9–15,3; Ic nghỉ 0,1–397 mA; THD 0,44–11,6 %; Zout 0,15–50 Ω; nhiệt độ 20↔30 °C chỉ đổi ≈ 3 % so với ảnh hưởng của điện trở (xem `ket_qua_nhay.log`, `corners.csv`). Nghĩa là thiết kế không chịu được toàn bộ điện trở ±10 % cùng lúc; dung sai nhiệt (20–30 °C) không phải yếu tố chính.
