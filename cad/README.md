# CAD 真实装配与干涉校核目录

请将下载的**商用现成件官方 3D 模型（`.step` / `.stp`）**以及自制指座的装配体放在本目录下，建议按如下子目录组织：

```text
cad/
├── vendor_steps/          # 外购商用件官方 STEP 模型（大寰电爪、GelSight Mini/DIGIT、RealSense D405、Dynamixel XL330、腕部六维力）
├── custom_parts/          # 自制 CNC 零件（ISO 转接法兰、左指斜角指甲快换座、右指避碰指座、手持 UMI 采数手柄）
└── assemblies/            # 总装配体（部署端总装 + 手持 UMI 总装，带 15°/25° 贴桌参考平面用于干涉检查）
```

> 建模完成后请对照 [`docs/01_hardware_design_and_bom.md`](../docs/01_hardware_design_and_bom.md) 第 3 节的 **8 项 CAD 可行性死穴清单**逐项验收。
