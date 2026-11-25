# Kiểm tra model SPICE so với datasheet (20–30 °C)

Nguồn: 2N5457-D, BC550-D (họ BC546–550), BC556B-D (họ BC556–558), BD139-D, BD140-D (họ BD136/138/140).
Số liệu đo bằng ngspice-42: `datasheet_check.py` → `datasheet_check_out.txt`; nhiệt độ: `temp_sweep.py` → `temp_sweep_out.txt`.
Ngspice mặc định TEMP = TNOM = 27 °C, nằm trong dải 20–30 °C; đã chạy lại với `.temp 20/25/30` (và 40 °C làm biên).

## 1. Kết luận ngắn
- **Model khớp datasheet ở mức DC/gm/hFE/Vbe** cho BC547, BC557, BD139, BD140 → dùng được.
- **2N5457**: IDSS, gm nằm trong dải, nhưng model là một con **pinch-off thấp (Vto = −1,37 V)**; datasheet điển hình VGS ≈ −2,5 V ở ID = 100 µA, model cho −1,08 V. Mạch phụ thuộc nhiều vào con JFET thực (xem mục 4).
- **Nhiệt độ 20–30 °C**: nếu mọi linh kiện cùng nhiệt độ thì mạch gần như không đổi (Av 12,20→12,09; dòng nghỉ 51→52,8 mA). **Vấn đề thật là tự nóng của BD139/BD140 khi không có tản nhiệt** (mục 5).
- Datasheet trong thư mục là họ linh kiện (BC550-D cho BC547, BC556B-D cho BC557); netlist dùng tên BC547/BC557 – khớp họ nhưng không chỉ rõ nhóm hFE (A/B/C).

## 2. Bảng so sánh model – datasheet
| Linh kiện | Thông số | Datasheet | Model (25 °C) | KQ |
|---|---|---|---|---|
| BC547 | VBE(on) @2 mA, 5 V | 0,58–0,70 (typ 0,66) V | 0,660 V | ✓ |
| BC547 | hFE @2 mA | 110–800 (nhóm B 200–450) | 309 | ✓ |
| BC547 | fT @10 mA | 300 MHz typ | ≈363 MHz | ✓ (cao ~20 %) |
| BC547 | Cob @10 V | 3,5 typ / 6 max pF | 1,66 pF | ⚠ thấp ~2× (chỉ ảnh hưởng HF) |
| BC557 | VBE(on) @2 mA | 0,55–0,70 (typ 0,62) V | 0,657 V | ✓ (cao 35 mV so với typ) |
| BC557 | hFE @2 mA | nhóm B 180–460 (typ 290) | 320 | ✓ |
| BC557 | fT / Cob | 320 MHz / 3,0 pF | ≈291 MHz / 2,5 pF | ✓ |
| BD139 | hFE @150 mA, 2 V | 40–250 (−10: 63–160, −16: 100–250) | 135 | ✓ |
| BD139 | hFE @0,5 A / @5 mA | ≥25 / ≥25 | 108 / 151 | ✓ |
| BD139 | VBE(on) @0,5 A | ≤1 V | 0,79 V | ✓ |
| BD140 | hFE @150 mA, VBE @0,5 A | 40–250, ≤1 V | 134, 0,79 V | ✓ |
| 2N5457 | IDSS (VDS=15 V) | 1–5 (typ 3) mA | 2,21 mA | ✓ (thấp hơn typ) |
| 2N5457 | gm0 (|Yfs|) | 1–5 (typ 3) mS | 3,22 mS | ✓ |
| 2N5457 | VGS(off) | −0,5…−6 V | −1,37 V | ✓ (đầu thấp) |
| 2N5457 | VGS @ID=100 µA | typ −2,5 V | −1,08 V | ⚠ khác nhiều |
| 2N5457 | yos | typ 10 / max 50 µS | 4,9 µS | ✓ |
| 2N5457 | Cgs / Cgd | Ciss 4,5, Crss 1,5 pF (typ, VDS=15 V) | 4,6 / 4 pF (zero-bias → ≈2 pF ở VDG 4,5 V) | ≈ ✓ |

Ghi chú: ngspice bỏ qua các tham số `Isr, N, Nr, Alpha, Vk` của dòng `.model 2N5457` (kiểu LTspice) – không ảnh hưởng DC/AC tín hiệu nhỏ, chỉ mất dòng rò cổng/ion hóa va chạm.

## 3. Giới hạn tuyệt đối trong mạch (27 °C, tĩnh)
| Linh kiện | Giá trị trong mạch | Giới hạn | KQ |
|---|---|---|---|
| BD139/BD140 | Ic nghỉ 52 mA, đỉnh ≈ 2,9 V/4 Ω ≈ 0,72 A, Vce ≤ 9 V | Ic 1,5 A, VCEO 80 V | ✓ |
| BD139 | P nghỉ 0,21 W; PD không tản nhiệt chỉ 1,25 W (RθJA 100 °C/W) | PD 12,5 W chỉ khi Tc = 25 °C | ⚠ xem mục 5 |
| BC547 Q2 | Ic 3 mA, P ≈ 10 mW | 100 mA, 500 mW | ✓ |
| 2N5457 | Id 2,06 mA, Vds 4,5 V, P ≈ 9 mW | VDS 25 V, 310 mW | ✓ |
| Điện áp | 9 V | thấp hơn mọi VCEO/VDS | ✓ |

## 4. Phân tán của 2N5457 (trong dải datasheet) → mạch
Cổng JFET đặt cố định 4,5 V, nguồn ra qua Rs = 2,2 kΩ nên Id ≈ IDSS-ish; Vgs thay đổi theo con JFET.

| IDSS | Vto | gm0 | Id (mA) | Vgs (V) | Av | THD % |
|---|---|---|---|---|---|---|
| 1,0 mA | −1,0 | 2,0 mS | 1,78 | **+0,59** | 10,9 | **3,7** |
| 2,12 (model) | −1,37 | 3,1 | 2,06 | −0,03 | 12,1 | 0,63 |
| 3,0 | −2,0 | 3,0 | 2,18 | −0,30 | 11,4 | 0,61 |
| 5,0 | −2,0 | 5,0 | 2,34 | −0,64 | 12,6 | 0,59 |
| 3,0 | −3,0 | 2,0 | 2,24 | −0,42 | 9,8 | 0,59 |

→ Con IDSS thấp (~1 mA, vẫn hợp lệ datasheet) làm Vgs > 0 (mối nối cổng gần dẫn ~0,6 V), THD tăng ~6×. Av chỉ lệch 10–12,6 nhờ hồi tiếp. Đã thử tự bias cổng 0 V (Rg1 bỏ, Rs = 1k/1,5k/2,2k): Vgs luôn âm nhưng **kém hơn** – Av chỉ 7,0–9,9 (<10), THD 1,1–3,7 %, Id trải 0,24–1,15 mA. Bias gốc (Vg = 4,5 V, Vgs≈0) giữ Id ≈ Vg/Rs ≈ 2 mA khá ổn định giữa các con (1,78–2,34 mA), chỉ hỏng với con IDSS ≈ 1 mA. Hướng chưa thử: hạ Vg còn ≈ 2–3 V (Rg1 lớn hơn Rg2).

## 5. Nhiệt độ 20–30 °C
a) Mọi linh kiện cùng nhiệt độ (ngspice `.temp`):

| T (°C) | Vout | Ic Q3 (mA) | Icc (mA) | Av | THD % |
|---|---|---|---|---|---|
| 20 | 4,976 | 51,2 | 58,1 | 12,20 | 0,637 |
| 25 | 4,958 | 52,0 | 58,9 | 12,15 | 0,635 |
| 30 | 4,940 | 52,8 | 59,7 | 12,09 | 0,633 |
| 40 | 4,904 | 54,4 | 61,3 | 11,98 | 0,629 |

Thay đổi trong 20–30 °C < 3 % → có thể bỏ qua.

b) Tự nóng (Qm và driver ở nhiệt độ phòng, BD139/BD140 nóng theo công suất, Tj = Tamb + RθJA·P):

| Tamb | RθJA | Tj BD139 | Ic nghỉ | P mỗi BD |
|---|---|---|---|---|
| 20 °C | 100 (không tản) | 92 °C | **180 mA** | 0,72 W |
| 20 °C | 50 | 35 °C | 75 mA | 0,30 W |
| 20 °C | 25 | 26 °C | 60 mA | 0,24 W |
| 30 °C | 100 | 106 °C | **190 mA** | 0,77 W |
| 30 °C | 50 | 46 °C | 78 mA | 0,32 W |
| 30 °C | 25 | 36 °C | 62 mA | 0,25 W |

Vòng lặp ổn định (hệ số vòng ≈0,7) nhưng dòng nghỉ tăng ~3,5× nếu BD139/140 để trần; Qm không gắn nhiệt với các BD nên không bù. **Khuyến nghị**: tản nhiệt nhỏ (RθJA ≤ 50 °C/W) và/hoặc gắn Qm sát thân BD139, tăng RE3/RE4.
