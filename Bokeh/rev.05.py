# 모든 배치들의 분포를 한 번에 보여줌
# 현재까지 Best

import dataiku
from dataiku import pandasutils as pdu
from bokeh.io import curdoc, output_notebook, show
from bokeh.layouts import gridplot, column
from bokeh.plotting import figure
from bokeh.models import Div

# Dataiku에서 데이터셋 불러오기
df = dataiku.Dataset('df').get_dataframe()

# Dataiku 노트북 출력 설정
output_notebook()

# 주석 추가 (HTML 형식)
legend = Div(text="""
    <b>Legend:</b>
    <ul>
        <li style="color:purple;">Purple bar: PSD(mean)</li>
        <li style="color:green;">Green bar: Suspension</li>
    </ul>
    """, width=400, height=50)

# 모든 배치에 대해 공통 가로축(Diameter)과 세로축(Volume) 범위를 계산
global_x_range = (df['Diameter'].min(), df['Diameter'].max())
global_y_range = (df['Volume'].min(), df['Volume'].max())

# 모든 Batch에 대해 플롯을 저장할 리스트
plots = []

# 각 Batch에 대해 산점도 생성
for batch in df['Batch'].unique():
    filtered_df = df[df['Batch'] == batch]

    # Diameter vs Volume 산점도
    p = figure(title=f"{batch}: Diameter vs Volume",
               x_axis_label='Diameter',
               y_axis_label='Volume',
               x_range=global_x_range,
               y_range=global_y_range,
               width=300, height=250)

    p.circle(filtered_df['Diameter'], filtered_df['Volume'], size=8, color="navy", alpha=0.6)

    # Suspension과 PSD(mean) 가로 막대 그래프 추가
    max_value = max(df['suspension'].max(), df['PSD(mean)'].max())
    p_extra = figure(width=300, height=50, x_range=(0, 0.6 * max_value), y_range=(0, 1), toolbar_location=None)
    p_extra.xgrid.grid_line_color = None
    p_extra.ygrid.grid_line_color = None
    p_extra.axis.visible = False

    suspension_value = filtered_df['suspension'].mean()
    psd_value = filtered_df['PSD(mean)'].mean()

    # 각 막대의 좌측에 텍스트로 값 표시 (기본 위치)
    p_extra.text(x=[0], y=[0.25], text=[f"{suspension_value:.1f}"], text_align="left", text_baseline="middle", text_color="green")
    p_extra.text(x=[0], y=[0.75], text=[f"{psd_value:.1f}"], text_align="left", text_baseline="middle", text_color="purple")

    # 가로 막대 그래프 생성 (숫자 바로 오른쪽에서 일정하게 시작)
    start_position = 0.1 * max_value  # 막대가 시작하는 위치를 고정
    p_extra.hbar(y=0.25, height=0.2, left=start_position, right=start_position + suspension_value * 0.5, color="green")
    p_extra.hbar(y=0.75, height=0.2, left=start_position, right=start_position + psd_value * 0.5, color="purple")

    # 두 그래프를 결합하여 row로 추가
    combined_plot = column(p_extra, p)
    plots.append(combined_plot)

# 플롯을 5열 그리드로 배치
grid = gridplot(plots, ncols=5)

# 전체 레이아웃을 주석과 함께 결합
layout = column(legend, grid)

# 레이아웃 출력
curdoc().add_root(layout)
show(layout)

