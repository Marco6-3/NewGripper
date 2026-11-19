# 仿真资产目录（URDF / MJCF / Meshes）

本目录用于存放从真实 CAD 导出的仿真模型，供 Stage 1（MuJoCo 3.x 精密贴屏避碰与剥离/失稳机理验证）与 Stage 2（多卡 A100 Isaac Lab / MJX 并行试错）共享：

```text
assets/
├── urdf/                  # 导出的 NewGripper（部署端与共用实体听诊/触觉盒）URDF
├── mjcf/                  # 面向 MuJoCo 3.x 优化的 XML（含集中参数弹性撬片铰链、脆性曲率约束贴膜、卡扣突跳台架）
└── meshes/
    ├── visual/            # 外观网格（STL/OBJ）
    └── collision/         # 凸包分解后的外壳碰撞体（注意：0.2mm 薄钢撬片刃口严禁粗糙凸包，必须用参数化薄板原语）
```

> 建模与导出规范参见 [`docs/03_simulation_modeling_spec.md`](../docs/03_simulation_modeling_spec.md)。
