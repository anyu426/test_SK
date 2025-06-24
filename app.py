# app.py
import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.colors import hsv_to_rgb
import numpy as np

# ページ設定
st.set_page_config(page_title="スキルCTタイムライン", layout="wide")

# サンプルスキルデータ（日本語OK）
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

# ユーザーインターフェース
mode = st.radio("Mode:", ["ranking event", "normal stage"])
total_time = st.select_slider("Total Time (seconds):", options=[30, 40], value=30)

names = [s["Name"] for s in skills]
selected = st.multiselect("Select skills:", names, default=names[:2])
skills = [s for s in skills if s["Name"] in selected]

if not skills:
    st.info("Select at least one skill.")
    st.stop()

# フォント日本語対応（ローカル環境にある日本語フォント名に変更してください）
# import matplotlib.font_manager as fm
# font_prop = fm.FontProperties(fname="/path/to/IPAexMincho.ttf")
# plt.rcParams['font.family'] = font_prop.get_name()

# 補助関数
def time_overlap(s1, e1, s2, e2):
    return max(0, min(e1, e2) - max(s1, s2))

def generate_distinct_colors(n):
    hues = np.linspace(0, 1, n + 1)[:-1]
    return [hsv_to_rgb((h, 0.6, 0.9)) for h in hues]

# プロット生成
fig, ax = plt.subplots(figsize=(14, 6))
colors = generate_distinct_colors(len(skills))
bar_height = 0.3
effect_ranges = [[] for _ in skills]
instant_times = {}

# CTイベントを収集
for i, skill in enumerate(skills):
    ct = float(skill["CT"])
    et = skill.get("Effect Time") or 0
    color = colors[i]
    t = 0
    while t <= total_time:
        start = t + ct if mode == "ranking event" else t
        end = start + et
        if start > total_time:
            break
        if et > 0:
            ax.add_patch(patches.Rectangle((start, i - bar_height/2), end - start, bar_height,
                                           color=color, alpha=0.6))
            effect_ranges[i].append((start, end))
        else:
            key = round(start, 2)
            instant_times.setdefault(key, []).append(i)
        t += ct

# 効果時間の重複部分を赤で描画
for i in range(len(skills)):
    for j in range(i+1, len(skills)):
        for si, ei in effect_ranges[i]:
            for sj, ej in effect_ranges[j]:
                if time_overlap(si, ei, sj, ej) > 0:
                    ov_s = max(si, sj); ov_e = min(ei, ej)
                    for y in [i, j]:
                        ax.add_patch(patches.Rectangle((ov_s, y-bar_height/2),
                                                       ov_e - ov_s, bar_height,
                                                       color='red', alpha=0.8))

# 即時スキルを縦線で描画（重複なら点線）
for t, idxs in instant_times.items():
    for i in idxs:
        overlaps_effect = any(
            j != i and any(s <= t <= e for s, e in effect_ranges[j])
            for j in range(len(skills))
        )
        color = 'red' if len(idxs) > 1 else 'blue'
        linestyle = ':' if overlaps_effect else '-'
        ax.plot([t, t], [i-bar_height/2, i+bar_height/2],
                color=color, linestyle=linestyle, linewidth=1.8, alpha=0.9)

# 軸設定
ax.set_xlim(0, total_time)
ax.set_ylim(-1, len(skills))
ax.set_yticks(range(len(skills)))
ax.set_yticklabels([s["Name"] for s in skills])
ax.set_xlabel("時間（秒）")
ax.set_title(f"スキルCTタイムライン（{mode}）")
ax.grid(axis='x', linestyle='--', alpha=0.6)
plt.tight_layout()

# 可視化
st.pyplot(fig, use_container_width=True)

# ログとしてスキル一覧を出力
st.markdown("### 📝 Selected skills info")
for s in skills:
    et = s.get("Effect Time")
    et_str = "即時" if not et else f"{et} 秒"
    st.write(f"- {s['Name']}: CT = {s['CT']} s, 効果時間 = {et_str}")
