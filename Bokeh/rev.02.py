# 모든 배치들을 나열함

import dataiku
from dataiku import pandasutils as pdu
from bokeh.io import curdoc, output_notebook, show
from bokeh.layouts import column
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure

# Dataiku에서 데이터셋 불러오기
dataset = dataiku.Dataset('df')
df = dataset.get_dataframe()

# Dataiku 노트북 출력 설정
output_notebook()

# Batch 리스트
batches = df['Batch'].unique()

# 모든 Batch에 대해 플롯을 저장할 리스트
plots = []

# 각 Batch에 대해 산점도 생성
for batch in batches:
    filtered_df = df[df['Batch'] == batch]

    # Bokeh plot 초기화
    p = figure(title=f"{batch}: Diameter vs Other Attributes",
               x_axis_label='Diameter',
               y_axis_label='Value',
               width=800, height=400)

    # Diameter vs Volume
    p.circle(filtered_df['Diameter'], filtered_df['Volume'], size=8, color="navy", alpha=0.6, legend_label="Volume")

    # Diameter vs suspension
    p.triangle(filtered_df['Diameter'], filtered_df['suspension'], size=8, color="green", alpha=0.6, legend_label="Suspension")

    # Diameter vs PSD(mean)
    p.square(filtered_df['Diameter'], filtered_df['PSD(mean)'], size=8, color="orange", alpha=0.6, legend_label="PSD(mean)")

    # 범례 설정
    p.legend.location = "top_left"
    p.legend.click_policy = "hide"

    # 플롯 추가
    plots.append(p)

# 모든 플롯을 수직으로 배치
layout = column(*plots)

# 레이아웃 출력
curdoc().add_root(layout)
show(layout)

