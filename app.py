import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

# ページ設定
st.set_page_config(page_title='Skill CT Timeline', page_icon=':hourglass_flowing_sand:')

# 📦 スキルデータ（例）
@st.cache_data
def load_skills():
    return pd.DataFrame([
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
])
skills_df = load_skills()

st.title("🏹 Skill CT Timeline")

# 🔧 ユーザー入力 UI
mode = st.radio("Mode", ["ranking event", "normal stage"])
total_time = st.select_slider("Total Time", options=[30,40], value=30)

selected = st.multiselect(
    "Select skills:",
    skills_df["Name"],
    default=skills_df["Name"].tolist()[:2]
)

# 🚫 選択がないとき
if not selected:
    st.warning("Please select at least one skill.")
    st.stop()

# データ生成
rows = []
for idx, row in skills_df[skills_df["Name"].isin(selected)].iterrows():
    alias = f"Skill {len(rows)}"  # 別の方法でもOK
    t=0
    while t <= total_time:
        start = t + (row.CT if mode=="ranking event" else 0)
        end = start + row["EffectTime"]
        if start > total_time: break
        rows.append({
            "alias": alias,
            "name": row.Name,
            "start": start,
            "end": end,
            "instant": row["EffectTime"] == 0
        })
        t += row.CT

df = pd.DataFrame(rows)
df["dup"] = df.apply(
    lambda r: ((df.alias != r.alias) & (df.start < r.end) & (df.end > r.start)).any(), axis=1
)

# 📊 プロット
bars = alt.Chart(df[~df.instant]).mark_bar().encode(
    x="start:Q", x2="end:Q", y=alt.Y("alias:N", sort=alt.EncodingSortField("alias")),
    color=alt.condition("dup", alt.value("red"), alt.value("steelblue"))
)
inst = alt.Chart(df[df.instant]).mark_rule(strokeWidth=2).encode(
    x="start:Q", y="alias:N",
    color=alt.condition("dup", alt.value("red"), alt.value("steelblue")),
    strokeDash=alt.condition("dup", alt.value([4,2]), alt.value([1,0]))
)

chart = (bars + inst).properties(width=700, height=50 * len(df["alias"].unique()))
st.altair_chart(chart)

# 📝 スキル対応表
st.markdown("### Legend mapping")
mapping = {f"Skill {i+1}": name for i, name in enumerate(selected)}
for alias, name in mapping.items():
    st.write(f"- **{alias}** = {name}")
