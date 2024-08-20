# 모든 데이터를 한 눈에 배치함

import dataiku
from dataiku import pandasutils as pdu
from bokeh.io import curdoc, output_notebook, show
from bokeh.layouts import gridplot, column
from bokeh.plotting import figure
import numpy as np

# Dataiku에서 데이터셋 불러오기
df = dataiku.Dataset('df').get_dataframe()

# Dataiku 노트북 출력 설정
output_notebook()

# 모든 배치에 대해 공통 가로축(Diameter)과 세로축(Volume) 범위를 계산
global_x_range = (df['Diameter'].min(), df['Diameter'].max())
global_y_range = (df['Volume'].min(), df['Volume'].max())

# 모든 Batch에 대해 플롯을 저장할 리스트
plots = []

# 각 Batch에 대해 산점도 생성
for batch in df['Batch'].unique():
    filtered_df = df[df['Batch'] == batch]

    # Bokeh plot 초기화
    p = figure(title=f"{batch}: Diameter vs Volume",
               x_axis_label='Diameter',
               y_axis_label='Volume',
               x_range=global_x_range,
               y_range=global_y_range,
               width=250, height=250)

    # Diameter vs Volume
    p.circle(filtered_df['Diameter'], filtered_df['Volume'], size=8, color="navy", alpha=0.6)

    # 플롯 추가
    plots.append(p)

# 플롯을 5열 그리드로 배치
grid = gridplot(plots, ncols=5)

# PSD(mean) 및 suspension의 별도 시각화를 위한 코드
psd_plots = []
suspension_plots = []

for batch in df['Batch'].unique():
    filtered_df = df[df['Batch'] == batch]

    # PSD(mean) 플롯
    p_psd = figure(title=f"{batch}: Diameter vs PSD(mean)",
                   x_axis_label='Diameter',
                   y_axis_label='PSD(mean)',
                   x_range=global_x_range,
                   width=250, height=250)
    p_psd.circle(filtered_df['Diameter'], filtered_df['PSD(mean)'], size=8, color="orange", alpha=0.6)
    psd_plots.append(p_psd)

    # suspension 플롯
    p_suspension = figure(title=f"{batch}: Diameter vs Suspension",
                          x_axis_label='Diameter',
                          y_axis_label='Suspension',
                          x_range=global_x_range,
                          width=250, height=250)
    p_suspension.circle(filtered_df['Diameter'], filtered_df['suspension'], size=8, color="green", alpha=0.6)
    suspension_plots.append(p_suspension)

# PSD(mean) 및 suspension 플롯들을 각각 그리드로 배치
psd_grid = gridplot(psd_plots, ncols=5)
suspension_grid = gridplot(suspension_plots, ncols=5)

# 레이아웃을 수직으로 결합
layout = column(grid, psd_grid, suspension_grid)

# 레이아웃 출력
curdoc().add_root(layout)
show(layout)

