# 数据字典 · Data Dictionary

> 本仓库为**公开免费样本**（100 客户），从银行级消费金融反欺诈仿真成品
> **《080-万象-综合欺诈》**（10 万客户 · 167.6 万行为事件 · 20.3 万关系边）**同源切片**。
>
> 样本与完整版**同字段、同口径、同一生成体系**——在样本上验证的代码与特征工程可直接迁移到完整版。
>
> 100% 合成数据，无任何真实个人信息。切片脚本见 `../scripts/make_samples.py`（seed=42，可复现）。

---

## 一、文件清单

| 文件 | 行数（含表头） | 说明 |
|---|---|---|
| `transactions_sample.csv` | 1,681 | 行为事件流水（客户全生命周期序列，命名沿用交易流水语义） |
| `users_sample.csv` | 100 | 客户画像表（含欺诈标签 `risk_label`） |
| `devices_sample.csv` | 100 | 设备汇总表（申请设备 + 事件流设备） |

> 注：仓库文件命名沿用早期版本的三表约定（transactions/users/devices），实际为「事件流水/客户表/设备表」，
> 各列名与完整版源表完全一致。完整版另含 33 列原始全量表、18 维申请时点特征宽表与关系图。

## 二、表关系

```
users.customer_id (1) ──< transactions_sample: 该客户全部行为事件（注册→申请→放款→还款/违约）
users.customer_id (1) ──< devices_sample: 设备（主设备 1 台，即申请设备）
```

## 三、字段详解

### 3.1 users_sample.csv · 客户表（源：customers.csv，16 列）

| 字段 | 类型 | 说明 |
|---|---|---|
| `customer_id` | str | 客户编号，`C000001` 格式，全局唯一 |
| `age` | int | 年龄 |
| `monthly_income` | float | 月收入（元/月，合成分布） |
| `loan_amount` | float | 申请借款金额（元） |
| `credit_score` | int | 信用评分（300–850 量纲） |
| `device_id` | str | **申请设备**（主设备）编号 |
| `device_age_days` | int | 申请设备已使用天数 |
| `is_emulator` | int | 是否模拟器设备（0/1） |
| `is_rooted` | int | 是否越狱/root 设备（0/1） |
| `ip_address` | str | 申请 IP（脱敏：保留网段三段） |
| `ip_net_type` | enum | IP 网络类型：`residential` 住宅 / `mobile` 移动 / `datacenter` 机房 |
| `declared_city` | str | 申报常住城市 |
| `ip_city` | str | IP 归属城市 |
| `is_address_match` | int | 申报地与 IP 地是否一致（0/1） |
| `apply_hour` | int | 申请时刻（0–23 时） |
| `risk_label` | enum | **欺诈标签（核心）**：`normal` 正常 / 5 类欺诈（见 §四） |

### 3.2 transactions_sample.csv · 行为事件流水（源：fraud_behavior_events.csv，8 列）

| 字段 | 类型 | 说明 |
|---|---|---|
| `customer_id` | str | 客户编号，关联 users_sample.csv |
| `event_time` | datetime | 事件时间 `YYYY-MM-DD HH:MM:SS` |
| `event_type` | enum | 事件类型（见 §五 枚举表） |
| `device_id` | str | 该事件使用的设备 |
| `ip_address` | str | 事件 IP（脱敏网段） |
| `location` | str | 事件发生城市 |
| `action` | str | 中文行为描述（如「登录（第 2 次）」「提现至银行卡」） |
| `from_account` / `to_account` | str | 转账/归集类事件的对手账户（脱敏），其他事件为空 |

### 3.3 devices_sample.csv · 设备表（customers 主设备 + 事件流构造）

| 字段 | 类型 | 说明 |
|---|---|---|
| `device_id` | str | 设备编号 |
| `customer_id` | str | 关联客户 |
| `is_primary` | int | 是否申请设备（主设备）=1；事件流中出现的其他设备=0 |
| `device_age_days` / `is_emulator` / `is_rooted` | — | 设备指纹。**仅主设备在申请环节采集**（完整版同样如此）；非主设备为 `空`，这是采集现实而非缺失错误 |
| `first_seen_time` / `last_seen_time` | datetime | 该设备在事件流中首/末次出现时间 |
| `event_count` | int | 该设备事件总数 |

## 四、风险标签语义（risk_label）

| 标签 | 中文 | 行为画像（样本中真实存在） |
|---|---|---|
| `normal` | 正常 | 95 名，常规借贷与还款节奏 |
| `identity_fraud` | 身份冒用 | 冒用他人身份申请 → 放款后 **6 笔集中提现（cashout）** |
| `loan_fraud` | 包装贷/骗贷 | 虚假资质申请，放款后快速套现并逾期 |
| `first_party_fraud` | 第一方违约 | 本人申请但无还款意愿（贷后集中 cashout，无 repay） |
| `gang_fraud` | 团伙欺诈 | 团伙批量操作特征（设备/IP 关联，完整版有图结构可挖） |
| `synthetic_identity` | 合成身份 | 虚构身份申请，放款后 **6 笔集中提现** 并失联 |

> 欺诈客户共同标志：`放款(disburse)后短时间多笔 cashout 集中套现`——样本中可直接观察。
> **样本富集**：5 类欺诈各 1 名（欺诈率 5%），便于演示与教学；完整版为真实分布（欺诈率 2.85%）。

## 五、事件类型枚举（event_type）

`register` 注册 · `login` 登录 · `browse` 浏览产品 · `profile_fill` 填资料 ·
`apply` 提交申请 · `approve` 审批通过 · `disburse` 放款 ·
`cashout` 提现/套现 · `repay` 还款 · `default` 违约标记

## 六、建模入口（样本即可跑通）

1. **申请反欺诈二分类**：users 表 16 列直接训练（`risk_label` 二值化：normal=0 / 其余=1）
2. **序列建模**：按客户聚合事件流 → 时序特征 → LightGBM/Transformer（与完整版 features.csv 18 维宽表同源）
3. **设备/团伙异常检测**：devices 表 + IP 城市一致性（`is_address_match`）做无监督

## 七、与完整版的关系

| 维度 | 本样本 | 完整版（¥999 试水价） |
|---|---|---|
| 规模 | 100 客户 · 1,681 事件 | **10 万客户 · 167.6 万事件 · 20.3 万关系边** |
| 欺诈覆盖 | 5 类各 1 名（富集 5%） | 5 类全量（真实 2.85% 分布） |
| 形态 | 三表原始序列 | 客户表 + 33 列原始全量 + **18 维申请时点特征宽表** + 事件流 + **关系图** |
| 附赠 | — | 数据字典 + 质量报告 + LightGBM 基线（时间切分 AUC 0.8395） |

另有同体系单类型成品（合成身份 / 包装贷 / 团伙洗钱 / 全伪装 / 嵌套欺诈，各 10 万客户级）可单独选购。

## 八、复现与合规

```bash
cd scripts && python make_samples.py   # 从成品《080-万象》切片，seed=42，任意机器结果一致
```

- 本数据集 100% 程序合成：身份画像 Faker + 业务分布 CTGAN（基于 Lending Club 公开数据 CC0 校准）+ 欺诈行为规则仿真。
  不包含任何真实个人信息、真实商户或真实交易。
- 许可：CC BY-NC 4.0（署名—非商业性使用）。
