"""
NewGripper 仿生弹性悬臂指甲 —— 固体力学与贴桌几何避碰校核脚本
====================================================================
用途：
  1. 在 SolidWorks / Fusion360 建模和下单买弹片之前，解析校核不同材料与厚度的悬臂指甲：
     - 末端等效弯曲刚度 k_tip (N/mm)
     - 导出至 MuJoCo / Isaac Lab 铰链的等效扭转刚度 k_theta (N·m/rad)
     - 典型贴桌法向载荷 (1N / 2N / 3N) 下的弹性挠度 delta (mm)
     - 根部最大弯曲应力 sigma_max (MPa) 与抗塑性屈服安全系数 SF
  2. 校核在不同贴桌倾角 alpha 下，右指视触觉传感器外壳（如 GelSight Mini）或夹爪本体是否会先磕碰桌面。

运行：
  python scripts/nail_mechanics_check.py
"""

from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass
class NailCandidate:
    name: str
    material: str
    youngs_modulus_gpa: float
    yield_strength_mpa: float
    width_mm: float
    free_length_mm: float
    thickness_mm: float


def analyze_cantilever(c: NailCandidate, load_n: float = 2.0) -> dict[str, float | str]:
    """Euler-Bernoulli rectangular cantilever beam subjected to tip normal load F."""
    E = c.youngs_modulus_gpa * 1e9  # Pa
    b = c.width_mm * 1e-3           # m
    L = c.free_length_mm * 1e-3     # m
    t = c.thickness_mm * 1e-3       # m

    I = b * (t ** 3) / 12.0                      # m^4
    k_tip_n_per_m = 3.0 * E * I / (L ** 3)       # N/m
    k_tip_n_per_mm = k_tip_n_per_m / 1000.0      # N/mm
    # Equivalent lumped revolute joint stiffness at nail root for MuJoCo/Isaac Lab:
    # tau = F * L, theta ~= delta / L => k_theta = tau / theta = k_tip * L^2 = 3*E*I / L
    k_theta_nm_per_rad = 3.0 * E * I / L         # N*m/rad

    deflection_mm = load_n / k_tip_n_per_mm      # mm
    sigma_max_mpa = (6.0 * load_n * L / (b * (t ** 2))) / 1e6
    safety_factor = c.yield_strength_mpa / sigma_max_mpa

    # Engineering feasibility heuristics for thin-sheet nail-wedge picking:
    # - Under F = 2N, desired elastic compliance in [0.25, 1.00] mm to absorb Z-error cleanly
    # - Safety factor >= 2.0 so 1000+ rubs never plastically bend the blade
    if safety_factor < 2.0:
        verdict = "FAIL (屈服风险/易永久弯折)"
    elif deflection_mm < 0.20:
        verdict = "STIFF (偏硬，适合硬卡但贴桌容错小)"
    elif deflection_mm > 1.20:
        verdict = "SOFT (偏软，易弯折打滑)"
    else:
        verdict = "PASS (黄金区间，推荐优先建模)"

    return {
        "k_tip_n_per_mm": k_tip_n_per_mm,
        "k_theta_nm_per_rad": k_theta_nm_per_rad,
        "delta_1n_mm": 1.0 / k_tip_n_per_mm,
        "delta_2n_mm": deflection_mm,
        "delta_3n_mm": 3.0 / k_tip_n_per_mm,
        "sigma_2n_mpa": sigma_max_mpa,
        "sf_2n": safety_factor,
        "verdict": verdict,
    }


def check_table_clearance(
    label: str,
    finger_length_mm: float = 85.0,
    housing_half_thickness_mm: float = 16.0,
    tilt_angles_deg: tuple[float, ...] = (15.0, 20.0, 25.0, 30.0, 35.0, 40.0),
) -> None:
    """
    简单几何校核：当指尖接触桌面 z = 0，整指纵轴与桌面呈倾角 alpha 时，
    距离指尖 L_f 处、向下探出偏置为 r_h 的外壳最低棱边距离桌面的垂直高度：
      h_clear = L_f * sin(alpha) - r_h * cos(alpha)
    (适用于快速估算电爪主体/视触觉外壳底部是否会磕桌)
    """
    print(f"\n=== 贴桌倾角几何避碰估算：{label} ===")
    print(
        f"假设条件: 外壳关键棱边距指尖 L_f = {finger_length_mm:.1f} mm, "
        f"向下探出偏置 r_h = {housing_half_thickness_mm:.1f} mm"
    )
    print(f"{'整指倾角 alpha':>14} | {'最低点离桌间隙 h_clear (mm)':>26} | {'判定 (需 >= 5.0 mm)'}")
    print("-" * 70)
    for deg in tilt_angles_deg:
        rad = math.radians(deg)
        h_clear = finger_length_mm * math.sin(rad) - housing_half_thickness_mm * math.cos(rad)
        status = "PASS" if h_clear >= 5.0 else ("WARN (余量紧张)" if h_clear > 0 else "FAIL (磕碰桌面!)")
        print(f"{deg:>13.1f}° | {h_clear:>26.2f} | {status}")


def main() -> None:
    candidates = [
        NailCandidate("301钢-0.10mm(偏薄)", "301全硬不锈钢", 193.0, 900.0, 12.0, 12.0, 0.10),
        NailCandidate("301钢-0.15mm-短刃", "301全硬不锈钢", 193.0, 900.0, 12.0, 10.0, 0.15),
        NailCandidate("301钢-0.20mm-主力", "301全硬不锈钢", 193.0, 900.0, 12.0, 12.0, 0.20),
        NailCandidate("301钢-0.25mm-偏硬", "301全硬不锈钢", 193.0, 900.0, 12.0, 12.0, 0.25),
        NailCandidate("301钢-0.30mm-硬卡", "301全硬不锈钢", 193.0, 900.0, 12.0, 12.0, 0.30),
        NailCandidate("碳纤片-0.30mm", "准各向同性碳纤", 70.0, 450.0, 12.0, 12.0, 0.30),
        NailCandidate("PEEK-0.60mm-绝缘", "PEEK削尖片", 3.8, 95.0, 12.0, 10.0, 0.60),
    ]

    print("=== 1. 仿生弹性悬臂指甲力学与仿真参数校核 (测试载荷 F = 2.0 N) ===")
    header = (
        f"{'方案':<18} | {'b×L×t (mm)':<12} | {'k_tip(N/mm)':>11} | {'k_theta(Nm/rad)':>15} | "
        f"{'δ@2N(mm)':>8} | {'σ@2N(MPa)':>9} | {'SF':>5} | 结论"
    )
    print(header)
    print("-" * 118)
    for c in candidates:
        res = analyze_cantilever(c, load_n=2.0)
        dims = f"{c.width_mm:.0f}×{c.free_length_mm:.0f}×{c.thickness_mm:.2f}"
        print(
            f"{c.name:<18} | {dims:<12} | "
            f"{res['k_tip_n_per_mm']:>11.2f} | "
            f"{res['k_theta_nm_per_rad']:>15.3f} | "
            f"{res['delta_2n_mm']:>8.2f} | "
            f"{res['sigma_2n_mpa']:>9.0f} | "
            f"{res['sf_2n']:>5.2f} | {res['verdict']}"
        )
    print("\n注：k_theta (N·m/rad) 可直接作为 MuJoCo/Isaac Lab 指甲根部旋转铰链刚度初值。")

    # 校核 A：若视触觉直装（未做内收/高倾角避让），底部下探 15 mm -> 低倾角会直接磕桌！
    check_table_clearance(
        "方案对比A - 视触觉外凸直装 (L_f=26mm, r_h=15mm)",
        finger_length_mm=26.0,
        housing_half_thickness_mm=15.0,
    )
    # 校核 B：优化为内收斜切指座（r_h 压至 6 mm）或采用“手腕40°高倾角 + 指甲弯折成18°浅楔角”
    check_table_clearance(
        "方案对比B - 视触觉内收斜切优化 (L_f=26mm, r_h=6mm)",
        finger_length_mm=26.0,
        housing_half_thickness_mm=6.0,
    )
    # 校核 C：电爪主体（距指尖约 85 mm，半厚约 25 mm）
    check_table_clearance(
        "电爪主体机身 (L_f=85mm, r_h=25mm)",
        finger_length_mm=85.0,
        housing_half_thickness_mm=25.0,
    )


if __name__ == "__main__":
    main()
