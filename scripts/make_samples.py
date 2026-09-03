# -*- coding: utf-8 -*-
"""
credit-fraud-simulation-data · 开源样本切片器（100% 合成 · 同源切片）
===================================================================
样本切自成品数据集《080-万象-综合欺诈》（10 万客户 · 167.6 万事件 · 全类型综合）。
抽样策略：95 个 normal + 5 类欺诈各 1 个（identity/loan/first_party/gang/synthetic）
          → 样本欺诈率 5%（为演示富集；完整版为真实 2.85% 分布）。
产出（与源表同列名，样本代码可直接迁移完整版）：
  sample_data/users_sample.csv         客户画像表   （源：customers.csv）
  sample_data/transactions_sample.csv  行为事件流水 （源：fraud_behavior_events.csv）
  sample_data/devices_sample.csv       设备汇总表   （源：customers 主设备 + 事件流构造）
seed=42，可复现。
"""
import csv
import os
import random
from collections import defaultdict

random.seed(42)

SRC = r"D:/MILIYA/成品电影/080-万象-综合欺诈/data"
OUT = os.path.join(os.path.dirname(__file__), "..", "sample_data")
os.makedirs(OUT, exist_ok=True)

# ---------- 1. 读 customers，分层抽样 100 客户 ----------
customers = []
with open(os.path.join(SRC, "customers.csv"), encoding="utf-8-sig") as f:
    for r in csv.DictReader(f):
        customers.append(r)

fraud_types = ["identity_fraud", "loan_fraud", "first_party_fraud",
               "gang_fraud", "synthetic_identity"]
# 先抽 95 normal，再 5 类欺诈各 1 —— 顺序固定保证 seed=42 可复现
pool_normal = [r for r in customers if r["risk_label"] == "normal"]
pick_normal = set(random.sample([r["customer_id"] for r in pool_normal], 95))
picked = {}
for r in customers:
    if r["customer_id"] in pick_normal:
        picked[r["customer_id"]] = r
for ft in fraud_types:
    ft_pool = [r for r in customers if r["risk_label"] == ft]
    c = random.choice(ft_pool)
    picked[c["customer_id"]] = c

keep = set(picked.keys())
print(f"选定客户: {len(keep)}（normal 95 + 5 类欺诈各 1）")

# ---------- 2. 流式过滤 events ----------
ev_cols = None
event_rows = []
dev_agg = defaultdict(lambda: {"first": None, "last": None, "n": 0})
with open(os.path.join(SRC, "fraud_behavior_events.csv"), encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    ev_cols = reader.fieldnames
    for r in reader:
        cid = r["customer_id"]
        if cid not in keep:
            continue
        event_rows.append(r)
        did = r["device_id"]
        if not did:
            continue
        a = dev_agg[(cid, did)]
        a["n"] += 1
        t = r["event_time"]
        if a["first"] is None or t < a["first"]:
            a["first"] = t
        if a["last"] is None or t > a["last"]:
            a["last"] = t
print(f"事件流水: {len(event_rows)} 行 | 涉及设备组合: {len(dev_agg)}")

# ---------- 3. 构造 devices 表（主设备=customers.device_id，指纹仅主设备采集） ----------
dev_rows = []
for cid, c in picked.items():
    prim = c["device_id"]
    for (ccid, did), a in sorted(dev_agg.items()):
        if ccid != cid:
            continue
        if did == prim:
            dev_rows.append({
                "device_id": did, "customer_id": cid, "is_primary": 1,
                "device_age_days": c["device_age_days"],
                "is_emulator": c["is_emulator"], "is_rooted": c["is_rooted"],
                "first_seen_time": a["first"], "last_seen_time": a["last"],
                "event_count": a["n"],
            })
        else:
            dev_rows.append({
                "device_id": did, "customer_id": cid, "is_primary": 0,
                "device_age_days": "", "is_emulator": "", "is_rooted": "",
                "first_seen_time": a["first"], "last_seen_time": a["last"],
                "event_count": a["n"],
            })
print(f"设备汇总: {len(dev_rows)} 行")

# ---------- 4. 写文件（列名与源表一致） ----------
usr_cols = list(customers[0].keys())
with open(os.path.join(OUT, "users_sample.csv"), "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=usr_cols)
    w.writeheader()
    for cid in sorted(picked.keys()):
        w.writerow(picked[cid])

with open(os.path.join(OUT, "transactions_sample.csv"), "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=ev_cols)
    w.writeheader()
    w.writerows(sorted(event_rows, key=lambda r: (r["customer_id"], r["event_time"])))

dev_cols = ["device_id", "customer_id", "is_primary", "device_age_days",
            "is_emulator", "is_rooted", "first_seen_time", "last_seen_time", "event_count"]
with open(os.path.join(OUT, "devices_sample.csv"), "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=dev_cols)
    w.writeheader()
    w.writerows(dev_rows)

# ---------- 5. 统计 ----------
from collections import Counter
ts = [r["event_time"][:10] for r in event_rows]
print("输出: ", OUT)
print(f"users={len(picked)} | events={len(event_rows)} | devices={len(dev_rows)}")
print(f"风险标签分布: {dict(Counter(r['risk_label'] for r in picked.values()))}")
print(f"事件时间范围: {min(ts)} ~ {max(ts)}")
evt = Counter(r["event_type"] for r in event_rows)
print(f"事件类型: {dict(evt.most_common(10))}")
