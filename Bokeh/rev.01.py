# 각 배치별로 입자 분포 등 확인 가능함

import dataiku
from dataiku import pandasutils as pdu
from bokeh.io import curdoc, output_notebook
from bokeh.layouts import column
from bokeh.models import Select, ColumnDataSource, CustomJS
from bokeh.plotting import figure, show
import numpy as np

# Dataiku에서 데이터셋 불러오기 (예: 'your_dataset_name'은 Dataiku 프로젝트 내의 데이터셋 이름)
dataset = dataiku.Dataset('df')
df = dataset.get_dataframe()

# 초기화
output_notebook()

# Bokeh plot 초기화
p = figure(title="Histogram of Volume by Diameter",
           x_axis_label='Diameter',
           y_axis_label='Volume',
           tools='pan,box_zoom,reset,save')

# 초기 Batch 설정
initial_batch = df['Batch'].unique()[0]
filtered_df = df[df['Batch'] == initial_batch]

# 히스토그램 데이터 생성
hist, edges = np.histogram(filtered_df['Diameter'], bins=30, weights=filtered_df['Volume'])
source = ColumnDataSource(data=dict(top=hist, left=edges[:-1], right=edges[1:], bottom=[0]*len(hist)))

# 히스토그램 그리기
p.quad(top='top', bottom='bottom', left='left', right='right', source=source,
       fill_color="navy", line_color="white", alpha=0.7)

# Batch 선택 위젯 생성
batch_select = Select(title="Select Batch:", value=initial_batch, options=list(df['Batch'].unique()))

# JavaScript 콜백 함수
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

# 레이아웃 정의
layout = column(batch_select, p)

# 레이아웃 출력
curdoc().add_root(layout)

