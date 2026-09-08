# -*- coding: utf-8 -*-
"""
两新宇宙 GitHub 样本切片器（同源切片，seed=42 可复现）
产出：
  sample_data_cyber/     网络安全：100 端点（94 normal + 6 类风险各 1，教学富集）
  sample_data_insurance/ 保险：100 保单（93 normal + 7 类欺诈各 1，教学富集）
与金融仓库同口径：样本列名与完整版一致，代码可直接迁移。
"""
import csv
import os
import random

random.seed(42)

CYBER_SRC = r"D:/MILIYA/syndata/cyber_module/data"
INS_SRC = r"D:/MILIYA/syndata/insurance_module/data"
OUT_BASE = os.path.join(os.path.dirname(__file__), "..")

def read_csv(path):
    with open(path, encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))

def write_csv(path, fieldnames, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)

# ---------- 网络切片 ----------
def slice_cyber():
    ds = read_csv(os.path.join(CYBER_SRC, "cyber_dataset.csv"))
    ev = read_csv(os.path.join(CYBER_SRC, "cyber_events.csv"))
    g = read_csv(os.path.join(CYBER_SRC, "cyber_graph.csv"))
    normal = [r for r in ds if r["risk_label"] == "normal"]
    pick = random.sample(normal, 94)
    pick_ids = {r["host_id"] for r in pick}
    types = ["phishing", "malware", "brute_force", "exfil", "insider_collusion"]
    seen = set()
    for t in types:
        candidates = [r for r in ds if r["risk_label"] == t]
        if candidates:
            c = random.choice(candidates)
            pick.append(c)
            pick_ids.add(c["host_id"])
            seen.add(t)
    pick.sort(key=lambda r: r["host_id"])
    out = os.path.join(OUT_BASE, "sample_data_cyber")
    write_csv(os.path.join(out, "cyber_dataset_sample.csv"), list(ds[0].keys()), pick)
    ev_pick = [r for r in ev if r["host_id"] in pick_ids]
    write_csv(os.path.join(out, "cyber_events_sample.csv"), list(ev[0].keys()), ev_pick)
    g_pick = [r for r in g if r["source"] in pick_ids]
    write_csv(os.path.join(out, "cyber_graph_sample.csv"), list(g[0].keys()), g_pick)
    labels = {}
    for r in pick:
        labels[r["risk_label"]] = labels.get(r["risk_label"], 0) + 1
    print(f"网络样本: {len(pick)} 端点 | {len(ev_pick)} 事件 | 标签分布 {labels}")

# ---------- 保险切片 ----------
def slice_insurance():
    ds = read_csv(os.path.join(INS_SRC, "insurance_dataset.csv"))
    ev = read_csv(os.path.join(INS_SRC, "insurance_events.csv"))
    g = read_csv(os.path.join(INS_SRC, "insurance_graph.csv"))
    normal = [r for r in ds if r["risk_label"] == "normal"]
    pick = random.sample(normal, 93)
    pick_ids = {r["policyholder_id"] for r in pick}
    types = ["staged_accident", "falsified_docs", "exaggeration",
             "ghost_claim", "policy_abuse", "organized_fraud"]
    for t in types:
        candidates = [r for r in ds if r["risk_label"] == t]
        if candidates:
            c = random.choice(candidates)
            pick.append(c)
            pick_ids.add(c["policyholder_id"])
    pick.sort(key=lambda r: r["policyholder_id"])
    out = os.path.join(OUT_BASE, "sample_data_insurance")
    write_csv(os.path.join(out, "insurance_dataset_sample.csv"), list(ds[0].keys()), pick)
    ev_pick = [r for r in ev if r["policyholder_id"] in pick_ids]
    write_csv(os.path.join(out, "insurance_events_sample.csv"), list(ev[0].keys()), ev_pick)
    g_pick = [r for r in g if r["source"] in pick_ids]
    write_csv(os.path.join(out, "insurance_graph_sample.csv"), list(g[0].keys()), g_pick)
    labels = {}
    for r in pick:
        labels[r["risk_label"]] = labels.get(r["risk_label"], 0) + 1
    print(f"保险样本: {len(pick)} 保单 | {len(ev_pick)} 事件 | 标签分布 {labels}")

if __name__ == "__main__":
    slice_cyber()
    slice_insurance()
