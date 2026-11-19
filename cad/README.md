# CAD 真实装配与干涉校核目录

请将下载的**开源母版与商用现成件 STEP 模型**以及自制共用实体指尖/听诊盒放于本目录，建议结构如下：

```text
cad/
├── vendor_steps/
│   ├── yubi_hw/               # 从 https://github.com/toyota/yubi-hw 下载的 YUBI 手持端/电爪端原始 STEP
│   ├── actuated_umi_v2/       # 从 https://github.com/actuated-umi/actuated-umi-gripper 抽取的 GelSight Mini 托架 STEP
│   └── commercial/            # 工业电爪（大寰 PGE/AG）、RealSense D405、腕部六维力、GelSight Mini 官方 STEP
├── custom_parts/              # 自制 CNC 零件（ISO 转接法兰、双端定位销快换背板、声振听诊耦合钳口、隔振垫、遮手挡板）
└── assemblies/                # 总装配体（YUBI 手持采数总装 + 机械臂部署总装，含手机屏幕 z=0 参考平面与 15°~40° 避碰检查）
```

> 建模验收清单参见 [`docs/01_hardware_design_and_bom.md`](../docs/01_hardware_design_and_bom.md) 第 4、5 节。
