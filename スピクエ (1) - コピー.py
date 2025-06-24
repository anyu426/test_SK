import gradio as gr
import pandas as pd
import altair as alt
import numpy as np

# 元スキル定義
ORIGINAL =[
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

def plot_skills_gr(mode, total_time, selected_names):
    skills = [s for s in ORIGINAL if s["Name"] in selected_names]
    rows = []
    for idx, s in enumerate(skills):
        alias = f"Skill {idx+1}"
        ct, et = s["CT"], s.get("Effect Time") or 0
        t = 0
        while t <= total_time:
            start = t + ct if mode == "ranking event" else t
            end = start + et
            if start > total_time:
                break
            rows.append({"alias": alias, "start": start, "end": end, "et": et})
            t += ct

    df = pd.DataFrame(rows)
    df["dup"] = df.apply(
        lambda r: ((df.start < r["end"]) & (df.end > r["start"]) & (df.alias != r["alias"])).any()
        if r["et"] > 0 else False, axis=1
    )
    inst = [
        {"alias": r["alias"], "t": round(r["start"], 2), "dup": ((df.start < r["start"]) & (df.end > r["start"]) & (df.alias != r["alias"])).any()}
        for r in rows if r["et"] == 0
    ]
    df_inst = pd.DataFrame(inst)

    base = alt.Chart(df).encode(
        y=alt.Y('alias:N', sort=list(df['alias'].unique()))
    )
    bars = base.mark_bar(opacity=0.6).encode(
        x='start:Q', x2='end:Q',
        color=alt.condition('datum.dup', alt.value('red'), alt.value('steelblue'))
    )
    rules = alt.Chart(df_inst).mark_rule(strokeWidth=2).encode(
        x='t:Q', y=alt.Y('alias:N', sort=list(df_inst['alias'].unique())),
        color=alt.condition('datum.dup', alt.value('red'), alt.value('steelblue')),
        strokeDash=alt.condition('datum.dup', alt.value([4,2]), alt.value([1,0]))
    )
    chart = (bars + rules).properties(width=700, height=50*len(skills))
    alias_map = "\n".join([f"{alias} = {s['Name']}" for alias, s in zip(df.alias.unique(), skills)])
    return chart, alias_map

# Gradio UI
with gr.Blocks() as demo:
    gr.Markdown("## Skill CT Timeline Visualizer")
    with gr.Row():
        with gr.Column(scale=1):
            mode = gr.Radio(["ranking event", "normal stage"], label="Mode")
            total_time = gr.Dropdown([30, 40], label="Total Time (sec)", value=30)
            options = [s["Name"] for s in ORIGINAL]
            selected = gr.CheckboxGroup(options, label="Select Skills", value=options[:2])
            run = gr.Button("Draw")
        with gr.Column(scale=3):
            plot = gr.Plot()
            legend = gr.Textbox(label="Alias Mapping")
    run.click(plot_skills_gr, inputs=[mode, total_time, selected], outputs=[plot, legend])

if __name__ == "__main__":
    demo.launch()
