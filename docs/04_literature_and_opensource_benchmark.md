# 04. 2023–2026 顶会文献查重与开源软硬件横向评测

> 核查日期：2026-11-19。本表汇总项目选型阶段系统核查的无本体采集、触觉/力觉/声振工具操作与薄片/剥离仿真开源工作，作为**CAD 选型依据**与**论文 Related Work / Baselines 对标基准**。

---

## 1. 赛道一：无本体采集、手指贴合与触觉/力觉 UMI 生态

| 项目名 & 年份/会议 | 开源仓库 / 主页 | 开源资产 | 主动 DOF | 无本体追踪与传感方案 | 对 NewGripper 的采用结论 |
| :--- | :--- | :--- | :---: | :--- | :--- |
| **YUBI** · CoRL 2026 *(Toyota / AIRoA)* | [yubi-hw](https://github.com/toyota/yubi-hw) · [yubi-sw](https://github.com/airoa-org/yubi-sw) | 完整本地 STEP/STL、BOM CSV、法兰、ROS 2 栈 | 1 | Meta Quest VR 6-DOF 追踪 + ESP32-C6 + AS5601 磁编码器；顺应手指贴合驱动；衍生工作 *YUBI in the Dark* 已验触觉 | **【核心母版】** 首选复刻魔改骨架：抗玻璃屏反光追踪稳、原生 ROS 2 易同步 20 kHz 声振与触觉、物料 < \$200 |
| **FARM / Actuated UMI v2** · 2025 | [主页](https://tactile-farm.github.io/) · [硬件 GitHub](https://github.com/actuated-umi/actuated-umi-gripper) | `actuated-UMI-v2-assy.step`、STL、BOM | 1 | D405 + OptiTrack；单侧 GelSight Mini + 匹配软垫 | **【托架母版】** 仅抽取 GelSight Mini 托架与 USB 防拉保护，不搬整套电机皮带 |
| **Specialist** · UC Berkeley | [项目页](https://specialist-ai.github.io/) | Onshape CAD、`specialist_description`、`specialist_sim` (MuJoCo) | 1 | Insta360 离线视觉 SLAM；TPU 95A 细指尖；Feetech STS3215 低成本舵机 | **【Baseline & 仿真参考】** 离线 SLAM 面对反光手机屏易漂移且难同步 20 kHz 声振，不选为硬件底盘；借鉴其 MuJoCo 资产结构，并将细 TPU + 纯视觉设为头号对照 Baseline |
| **Flash ALOHA** · Stanford | [GitHub](https://github.com/JohnYao93/flash-aloha) | 录制、平滑、Visual Masking 代码 | 1 | 轻臂（ARX）拖动示教（非无本体） | **【技巧借鉴】** 高减速比工业臂无法拖动示教，但借鉴其 **Visual Masking / 遮手挡板** 解决手指贴合采数的近景露手问题 |
| **HandUMI** · CoRL 2026 Workshop | [handumi-hw](https://github.com/murobotics-ai/handumi-hw) · [handumi-sw](https://github.com/murobotics-ai/handumi-sw) | STEP/STL、BOM、快换指尖 | 1 | Quest/PICO + 腕相机 + 开度编码器 | 备选指驱骨架参考，其定位销快换指尖盒思路已吸收 |
| **UMI-FT** · ICRA 2026 | [GitHub](https://github.com/real-stanford/UMI-FT) | CoinFT 采集、异步对时、部署代码 | 1 | iPhone ARKit + 左右指 CoinFT 六维力（独立 MCU 串口对齐） | **【架构借鉴】** 借鉴传感器坐标变换、去零、异步时延对齐，以及“指尖局部力与腕部外力解耦”原则 |
| **FreeTacMan** · ICRA 2026 | [GitHub](https://github.com/OpenDriveLab/FreeTacMan) | 组装指南、训练代码与数据 | 1 | NOKOV 240 Hz 光学动捕 + 双指视触觉 | 固定台架触觉同步流程参考 |
| **TacUMI** · ICRA 2026 | [项目页](https://tac-umi.github.io/TacUMI/) | 3D 打印模型与论文 | 1 | Vive Tracker + 工具侧六维 F/T + 视触觉 | 参考外部接触力与手指驱动力机械解耦思路 |
| **UMI / FastUMI / iPhUMI** · 2024–2026 | [UMI](https://github.com/real-stanford/universal_manipulation_interface) · [iPhUMI](https://github.com/real-stanford/iPhUMI) | 完整工具链与数据格式 | 1 | GoPro SLAM / iPhone ARKit | 复用工具坐标与时延标定方法论 |

---

## 2. 赛道二：隔物工具操控、高频声振感知与脆性/剥离相关先例（查重防撞车）

| 项目 / 方向 & 年份 | 核心内容与局限 | NewGripper 的核心差异化突破 |
| :--- | :--- | :--- |
| **SimToolReal / REGRIND / HiFun** · CoRL 2026 | 多指手或通用臂的粗放工具操控（铲菜翻锅、大螺丝、剪刀），依赖视觉与常规位控 | 我们直击**亚毫米透明缝隙与毫秒级脆性断裂/Snap-Through 失稳**（钢化膜撬边不碎、脆硅片无损铲取、暗卡扣防捅碎） |
| **Reactive Diffusion Policy (RSS 2025) & Adaptive Compliance Policy** | 引入高频触觉/力反馈实现柔顺反应控制，但主要基于**直接接触物体**的视触觉或腕部低频力 | 我们解决**隔着刚性工具（薄钢撬片/刮板/撬棒）直触视触觉失效**的难题，引入 **20 kHz 接触声振 + 工具传递函数 $H_{\text{tool}}(\omega)$ 自辨识** |
| **uSkin Tactile Fingernail (ICRA 2026 W) / GET Gripper / 5-DOF Gripper (IROS 2024) / PLATO Hand (RA-L 2026)** | 均已探索“指甲+软指腹”或桌面卡片拾取 | 明确**不把“发明指甲”作为硬件首创主张**；转而将创新锚定在**无本体实体指尖/听诊盒共用 + 光学全盲贴膜/揭膜与脆硅片的高频物理闭环** |
| **RoboAcoustics (ICRA) / 实验室刮擦与魔术贴剥离（Velcro Peeling / LCD 面板剥离）** | 已有零散的声学纹理分类、固定治具 LCD 面板剥离或魔术贴纯力控剥离 | **目前尚未见到**集“无本体同构采集 + 工具零改装声振听诊 + 全透明手机贴膜/赶泡/0.2 mm 撬边/防脆断揭膜 + 脆硅片跨材质泛化”于一体的通用闭环系统 |

---

## 3. 赛道三：仿真与控制代码基线参考

- **MuJoCo 3.x**（本机已安装 `mujoco-3.10.0`）：参考 `flex/drape.xml` 与 `specialist_sim`，用于 Stage 1 真实 CAD 贴屏避碰、弹性撬片集中参数模型与剥离弯曲半径约束验证；
- **Isaac Lab 3.0**：参考 `Isaac-Lift-Cloth-Franka` 与并行刚柔接触配置，用于多卡 A100 Stage 2 并行试错；
- **ThinShellLab (ICLR 2024, [`Genesis-Embodied-AI/ThinShellLab`](https://github.com/Genesis-Embodied-AI/ThinShellLab))**：Taichi 可微薄壳求解器，可作单一薄片滑移/起拱失效机理的对照参考；
- **Flipbot (ICRA 2023, [`RobotLL/Flipbot`](https://github.com/RobotLL/Flipbot))**：粗定位 $\rightarrow$ 力觉寻边接触控制思路的经典基线参考；
- **Roller Rings (IROS 2025, [`Rice-RobotPI-Lab/Roller-Rings`](https://github.com/Rice-RobotPI-Lab/Roller-Rings))**：保留为后续若实测确需升级第 2 主动 DOF（独立切向送料）时的开源滚轮盒参考。
