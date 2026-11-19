# 仿真资产目录（URDF / MJCF / Meshes）

本目录用于存放从真实 CAD 导出的仿真模型，供 Stage 1（MuJoCo 单机精密接触验证）与 Stage 2（多卡 A100 Isaac Lab / MJX 大规模训练）共享：

```text
assets/
├── urdf/                  # 导出的 NewGripper URDF（含机械臂末端或独立 6-DOF 浮动末端）
├── mjcf/                  # 面向 MuJoCo 3.x 精细接触优化的 XML（含弹性指甲铰链与多段屈曲薄片）
└── meshes/
    ├── visual/            # 外观网格（STL/OBJ）
    └── collision/         # 凸包分解后的防碰网格（注意：指甲刃口必须使用参数化薄板原语，严禁粗糙凸包）
```

> 详细导出规范参见 [`docs/03_simulation_modeling_spec.md`](../docs/03_simulation_modeling_spec.md)。
