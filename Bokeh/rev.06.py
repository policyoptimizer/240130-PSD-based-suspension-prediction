# 단일 그래프와 전체 개별 그래프를 합쳤음
# 현재까지 Best

import dataiku
from dataiku import pandasutils as pdu
from bokeh.io import curdoc, output_notebook, show
from bokeh.layouts import gridplot, column, row, Spacer
from bokeh.models import Select, ColumnDataSource, CustomJS, Div
from bokeh.plotting import figure
import numpy as np

# Dataiku에서 데이터셋 불러오기
dataset = dataiku.Dataset('df')
df = dataset.get_dataframe()

# Dataiku 노트북 출력 설정
output_notebook()

# 드롭다운을 통해 배치 선택하고, 히스토그램을 보여주는 부분
p_histogram = figure(title="Histogram of Volume by Diameter",
                     x_axis_label='Diameter',
                     y_axis_label='Volume',
                     tools='pan,box_zoom,reset,save', width=600)

initial_batch = df['Batch'].unique()[0]
filtered_df = df[df['Batch'] == initial_batch]

hist, edges = np.histogram(filtered_df['Diameter'], bins=30, weights=filtered_df['Volume'])
source = ColumnDataSource(data=dict(top=hist, left=edges[:-1], right=edges[1:], bottom=[0]*len(hist)))

p_histogram.quad(top='top', bottom='bottom', left='left', right='right', source=source,
                 fill_color="navy", line_color="white", alpha=0.7)

batch_select = Select(title="Select Batch:", value=initial_batch, options=list(df['Batch'].unique()))

callback = CustomJS(args=dict(source=source, batch_select=batch_select, df=df.to_dict(orient='records')), code="""
    var data = source.data;
    var batch = batch_select.value;
    var filtered_df = df.filter(row => row['Batch'] === batch);

    var hist_data = [];
    var edges_data = [];

    var hist = [];
    var edges = [];

    var weights = filtered_df.map(row => row['Volume']);
    var diameter = filtered_df.map(row => row['Diameter']);

    var bin_count = 30;
    var min_diameter = Math.min(...diameter);
    var max_diameter = Math.max(...diameter);
    var bin_width = (max_diameter - min_diameter) / bin_count;

    for (var i = 0; i < bin_count; i++) {
        edges.push(min_diameter + i * bin_width);
        hist.push(0);
    }
    edges.push(max_diameter);

    for (var i = 0; i < diameter.length; i++) {
        var bin = Math.floor((diameter[i] - min_diameter) / bin_width);
        hist[bin] += weights[i];
    }

    data['top'] = hist;
    data['left'] = edges.slice(0, -1);
    data['right'] = edges.slice(1);
    data['bottom'] = Array(hist.length).fill(0);

    source.change.emit();
""")

batch_select.js_on_change('value', callback)

# 주석 추가 (HTML 형식)
legend = Div(text="""
    <ul>
        <li style="color:purple;">Purple bar: PSD(mean)</li>
        <li style="color:green;">Green bar: Suspension</li>        
    </ul>
    """, width=400, height=50)

# 모든 배치에 대한 플롯 생성
global_x_range = (0, 250)
global_y_range = (df['Volume'].min(), df['Volume'].max())
plots = []

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

    combined_plot = column(p_extra, p)
    plots.append(combined_plot)

# 플롯을 5열 그리드로 배치
grid = gridplot(plots, ncols=5)

# 단일 배치 히스토그램과 드롭다운 배치, legend를 우측에 배치
top_layout = row(Spacer(width=450), column(batch_select, p_histogram))

# 전체 레이아웃을 상단의 단일 그래프, 우측의 legend, 전체 배치 플롯과 함께 결합
layout = column(top_layout, row(Spacer(width=1300), column(legend)), grid)

# 레이아웃 출력
curdoc().add_root(layout)
show(layout)

