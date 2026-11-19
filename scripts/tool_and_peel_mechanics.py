"""
NewGripper 力学与几何可行性预校核计算器
====================================================================
覆盖三大核心物理校核（在画 SolidWorks 与下单前先算出精确力学边界）：
  1. 薄钢弹性撬片 / 铲刀悬臂弯曲校核：
     - 末端等效弯曲刚度 k_tip (N/mm) & MuJoCo 根部铰链等效扭转刚度 k_theta (N·m/rad)
     - 典型 2.0 N 贴屏/贴桌下压力下的弹性挠度 delta (mm) 与抗塑性屈服安全系数 SF
  2. 脆性贴膜 / 实验室脆硅片最小安全弯曲半径校核（断裂力学硬约束）：
     - 基于薄板纯弯表面最大拉应力 sigma = E * h / (2 * R)，推算临界折断半径 R_min = E * h / (2 * sigma_f)
     - 给出 2 倍安全系数下的工程剥离弯曲半径下限 R_safe，直接指导揭膜剥离角控制与仿真判据！
  3. 贴屏/贴桌倾角几何避碰快速估算（检查电爪机身与 GelSight Mini 外壳是否早于撬片磕碰屏幕）

运行：
  python scripts/tool_and_peel_mechanics.py
"""

from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass
class BladeCandidate:
    name: str
    material: str
    youngs_modulus_gpa: float
    yield_strength_mpa: float
    width_mm: float
    free_length_mm: float
    thickness_mm: float


@dataclass
class SheetTarget:
    name: str
    thickness_mm: float
    youngs_modulus_gpa: float
    fracture_or_yield_mpa: float
    note: str


def analyze_cantilever_blade(c: BladeCandidate, load_n: float = 2.0) -> dict[str, float | str]:
    """Euler-Bernoulli rectangular cantilever beam under normal tip load F."""
    E = c.youngs_modulus_gpa * 1e9  # Pa
    b = c.width_mm * 1e-3           # m
    L = c.free_length_mm * 1e-3     # m
    t = c.thickness_mm * 1e-3       # m

    I = b * (t ** 3) / 12.0                      # m^4
    k_tip_n_per_mm = (3.0 * E * I / (L ** 3)) / 1000.0
    k_theta_nm_per_rad = 3.0 * E * I / L         # MuJoCo/Isaac root revolute stiffness

    deflection_mm = load_n / k_tip_n_per_mm
    sigma_max_mpa = (6.0 * load_n * L / (b * (t ** 2))) / 1e6
    sf = c.yield_strength_mpa / sigma_max_mpa

    if sf < 2.0:
        verdict = "FAIL (屈服风险/易永久弯折)"
    elif deflection_mm < 0.20:
        verdict = "STIFF (偏硬，贴屏 Z 轴容错小)"
    elif deflection_mm > 1.20:
        verdict = "SOFT (偏软，易弯折难进 0.2mm 缝)"
    else:
        verdict = "PASS (黄金区间，推荐优先建模)"

    return {
        "k_tip_n_per_mm": k_tip_n_per_mm,
        "k_theta_nm_per_rad": k_theta_nm_per_rad,
        "delta_2n_mm": deflection_mm,
        "sigma_2n_mpa": sigma_max_mpa,
        "sf_2n": sf,
        "verdict": verdict,
    }


def analyze_brittle_bending(s: SheetTarget, safety_factor: float = 2.0) -> dict[str, float]:
    """
    Minimum bending radius before flexural fracture/yielding:
      sigma_max = E * h / (2 * R)  =>  R_min = E * h / (2 * sigma_f)
    """
    E_mpa = s.youngs_modulus_gpa * 1000.0
    r_min_mm = (E_mpa * s.thickness_mm) / (2.0 * s.fracture_or_yield_mpa)
    r_safe_mm = r_min_mm * safety_factor
    return {"r_min_mm": r_min_mm, "r_safe_mm": r_safe_mm}


def check_screen_clearance(
    label: str,
    finger_length_mm: float,
    housing_offset_mm: float,
    tilt_angles_deg: tuple[float, ...] = (15.0, 20.0, 25.0, 30.0, 35.0, 40.0),
) -> None:
    """
    当工作刃口贴在手机玻璃屏 z = 0，整指纵轴与屏幕呈倾角 alpha 时，
    距离刃口 L_f 处、向下探出偏置为 r_h 的刚性外壳最低棱边离屏高度：
      h_clear = L_f * sin(alpha) - r_h * cos(alpha)
    """
    print(f"\n=== 贴屏倾角避碰估算：{label} ===")
    print(f"参数: L_f = {finger_length_mm:.1f} mm, r_h = {housing_offset_mm:.1f} mm")
    print(f"{'整指倾角 alpha':>14} | {'最低点离屏间隙 h_clear (mm)':>26} | {'判定 (需 >= 5.0 mm)'}")
    print("-" * 70)
    for deg in tilt_angles_deg:
        rad = math.radians(deg)
        h_clear = finger_length_mm * math.sin(rad) - housing_offset_mm * math.cos(rad)
        status = "PASS" if h_clear >= 5.0 else ("WARN (余量紧张)" if h_clear > 0 else "FAIL (磕碰手机屏!)")
        print(f"{deg:>13.1f}° | {h_clear:>26.2f} | {status}")


def main() -> None:
    blades = [
        BladeCandidate("301钢-0.10mm(偏薄)", "301全硬不锈钢", 193.0, 900.0, 12.0, 12.0, 0.10),
        BladeCandidate("301钢-0.15mm-短刃", "301全硬不锈钢", 193.0, 900.0, 12.0, 10.0, 0.15),
        BladeCandidate("301钢-0.20mm-主力", "301全硬不锈钢", 193.0, 900.0, 12.0, 12.0, 0.20),
        BladeCandidate("301钢-0.25mm-偏硬", "301全硬不锈钢", 193.0, 900.0, 12.0, 12.0, 0.25),
        BladeCandidate("301钢-0.30mm-强撬", "301全硬不锈钢", 193.0, 900.0, 12.0, 12.0, 0.30),
        BladeCandidate("碳纤片-0.30mm", "准各向同性碳纤", 70.0, 450.0, 12.0, 12.0, 0.30),
        BladeCandidate("PEEK-0.60mm-防划", "PEEK削尖片", 3.8, 95.0, 12.0, 10.0, 0.60),
    ]

    print("=== 1. 薄钢弹性撬片 / 刮刀悬臂力学与仿真参数校核 (测试载荷 F = 2.0 N) ===")
    print(
        f"{'方案':<18} | {'b×L×t (mm)':<12} | {'k_tip(N/mm)':>11} | {'k_theta(Nm/rad)':>15} | "
        f"{'δ@2N(mm)':>8} | {'σ@2N(MPa)':>9} | {'SF':>5} | 结论"
    )
    print("-" * 118)
    for b in blades:
        res = analyze_cantilever_blade(b, load_n=2.0)
        dims = f"{b.width_mm:.0f}×{b.free_length_mm:.0f}×{b.thickness_mm:.2f}"
        print(
            f"{b.name:<18} | {dims:<12} | "
            f"{res['k_tip_n_per_mm']:>11.2f} | "
            f"{res['k_theta_nm_per_rad']:>15.3f} | "
            f"{res['delta_2n_mm']:>8.2f} | "
            f"{res['sigma_2n_mpa']:>9.0f} | "
            f"{res['sf_2n']:>5.2f} | {res['verdict']}"
        )

    sheets = [
        SheetTarget("PET 软贴膜", 0.15, 3.0, 60.0, "可大角度剥离，主要防起皱/拉飞手机"),
        SheetTarget("0.30mm 钢化玻璃膜", 0.30, 70.0, 300.0, "典型化学钢化膜，剥离过急必裂成蜘蛛网"),
        SheetTarget("0.20mm 普通薄玻片", 0.20, 70.0, 70.0, "非钢化极脆，需极平缓托起"),
        SheetTarget("0.20mm 减薄脆硅片", 0.20, 160.0, 150.0, "实验室薄硅片，几乎不可弯曲，必须平铲托运"),
        SheetTarget("0.50mm 标准脆硅片", 0.50, 160.0, 150.0, "实验室标准硅片，严禁单边硬撬"),
    ]

    print("\n=== 2. 贴膜与脆硅片防折断最小弯曲半径估算 (断裂力学约束，安全系数 SF = 2.0) ===")
    print(f"{'目标薄片':<18} | {'厚 h(mm)':>8} | {'E(GPa)':>7} | {'σ_f(MPa)':>8} | {'临界 R_min':>11} | {'安全 R_safe':>11} | 工程策略含义")
    print("-" * 118)
    for s in sheets:
        br = analyze_brittle_bending(s, safety_factor=2.0)
        print(
            f"{s.name:<18} | {s.thickness_mm:>8.2f} | {s.youngs_modulus_gpa:>7.1f} | "
            f"{s.fracture_or_yield_mpa:>8.0f} | {br['r_min_mm']:>9.1f}mm | {br['r_safe_mm']:>9.1f}mm | {s.note}"
        )

    check_screen_clearance(
        "方案A - GelSight Mini 未优化直装 (L_f=26mm, r_h=15mm)",
        finger_length_mm=26.0,
        housing_offset_mm=15.0,
    )
    check_screen_clearance(
        "方案B - GelSight Mini 内收斜切优化 (L_f=26mm, r_h=6mm)",
        finger_length_mm=26.0,
        housing_offset_mm=6.0,
    )
    check_screen_clearance(
        "工业电爪主体机身 (L_f=85mm, r_h=25mm)",
        finger_length_mm=85.0,
        housing_offset_mm=25.0,
    )


if __name__ == "__main__":
    main()
