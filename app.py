import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import pandas as pd

# ページ設定
st.set_page_config(page_title="Skill CT Timeline", layout="wide")

# スキルリスト（例）
skills = [
    {"Name": "ワンワンボンバー", "CT": 3.45, "Effect Time": 2.0},
    {"Name": "ブリザード", "CT": 4.5, "Effect Time": None},
    {"Name": "プロテクション", "CT": 3.9, "Effect Time": 1.5},
    {"Name": "ラグナロク", "CT": 3.0, "Effect Time": None},
    {"Name": "マンドレイク爆弾", "CT": 4.85, "Effect Time": 2.5},
    {"Name": "ピアシングソード", "CT": 3.25, "Effect Time": None},
    {"Name": "自然の力", "CT": 3.75, "Effect Time": 2},
    {"Name": "ポイズンフィールド", "CT": 4.95, "Effect Time": 2.5},
    {"Name": "地獄火", "CT": 4.5, "Effect Time": None},
    {"Name": "精霊地震", "CT": 3.5, "Effect Time": None},
    {"Name": "炎の鞭", "CT": 3.95, "Effect Time": 2.0},
    {"Name": "亡者の堕落", "CT": 3.0, "Effect Time": None},
    {"Name": "キングスライム召喚", "CT": 3.35, "Effect Time": None},
    {"Name": "ドラゴンスレイヤーランス", "CT": 3.75, "Effect Time": 2},
    {"Name": "猫の足跡", "CT": 5, "Effect Time": None},
    {"Name": "月光斬り", "CT": 4.0, "Effect Time": None},
    {"Name": "ゴッドフィスト", "CT": 4.5, "Effect Time": None},
    {"Name": "火山爆発", "CT": 4.45, "Effect Time": 2.5},
    {"Name": "デスサイズ", "CT": 4.7, "Effect Time": 2.5},
    {"Name": "ベヒモス召喚", "CT": 3.9, "Effect Time": None},
    {"Name": "ドラゴンブレス", "CT": 3.85, "Effect Time": None},
    {"Name": "フェニックス召喚", "CT": 4.3, "Effect Time": 2.0},
    {"Name": "アルマゲドン", "CT": 4.75, "Effect Time": None}
]
# UI
mode = st.radio("Mode:", ["ranking event", "normal stage"])
total_time = st.selectbox("Total Time:", [30, 40])
names = [s["Name"] for s in skills]
selected = st.multiselect("Select skills:", names, default=names[:2])

if not selected:
    st.info("Please select at least one skill.")
    st.stop()

# フィルタ処理
skills = [s for s in skills if s["Name"] in selected]

# イベント計算
timeline = []
for idx, s in enumerate(skills):
    t = 0
    while t <= total_time:
        start = t + s["CT"] if mode == "ranking event" else t
        end = start + s["Effect Time"]
        if start > total_time:
            break
        timeline.append({
            "name": s["Name"], "start": start, "end": end, "et": s["Effect Time"], "idx": idx
        })
        t += s["CT"]

# 重複チェック関数
def is_overlapping(a, b):
    return not (a["end"] <= b["start"] or b["end"] <= a["start"])

for ev in timeline:
    ev["overlap"] = any(
        ev["Name"] != other["Name"] and
        ev["Effect Time"] > 0 and other["Effect Time"] > 0 and
        is_overlapping(ev, other)
        for other in timeline
    )

# 描画
fig, ax = plt.subplots(figsize=(14, 6))
for ev in timeline:
    y = ev["idx"]
    if ev["Effect Time"] > 0:
        # 効果時間あり：バー
        color = 'red' if ev["overlap"] else 'skyblue'
        rect = patches.Rectangle((ev["start"], y-0.3), ev["Effect Time"], 0.6,
                                 facecolor=color, edgecolor='black', alpha=0.6)
        ax.add_patch(rect)
    else:
        # 即時型：縦線、重複時点線
        overlap_with_et = any(
            other["Name"] != ev["Name"] and other["Effect Time"] > 0 and
            ev["start"] >= other["start"] and ev["start"] <= other["end"]
            for other in timeline
        )
        style = ':' if overlap_with_et else '-'
        ax.plot([ev["start"], ev["start"]], [y-0.3, y+0.3],
                color='blue', linestyle=style, linewidth=2)

# 軸設定
ax.set_yticks(range(len(skills)))
ax.set_yticklabels([s["Name"] for s in skills])
ax.set_xlim(0, total_time)
ax.set_xlabel("時間（秒）")
ax.set_title(f"スキルCTタイムライン ({mode})")
ax.grid(axis='x', linestyle='--', alpha=0.5)

st.pyplot(fig, use_container_width=True)

# Legend mapping
st.markdown("**Legend mapping:**")
for i, s in enumerate(skills):
    st.markdown(f"- **Skill {i+1}** = {s['name']}")
