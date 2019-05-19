from __future__ import absolute_import, division, print_function
import json
from IPython.core.display import HTML
from jinja2 import Template
import uuid
import attr

import copy
from functools import singledispatch

try:
  basestring
except NameError:
  basestring = str


def sankey_filter_checkbox(labels, onclick_name):
    uid = uuid.uuid4().hex
    filter_checkbox_html = '''
        <style>
        .switch {
          position: relative;
          display: inline-block;
          width: 30px;
          height: 17px;
        }

        .switch input { 
          opacity: 0;
          width: 0;
          height: 0;
        }

        .slider {
          position: absolute;
          cursor: pointer;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background-color: #ccc;
          -webkit-transition: .4s;
          transition: .4s;
        }

        .slider:before {
          position: absolute;
          content: "";
          height: 13px;
          width: 13px;
          left: 2px;
          bottom: 2px;
          background-color: white;
          -webkit-transition: .4s;
          transition: .4s;
        }

        input:checked + .slider {
          background-color: #2196F3;
        }

        input:focus + .slider {
          box-shadow: 0 0 1px #2196F3;
        }

        input:checked + .slider:before {
          -webkit-transform: translateX(13px);
          -ms-transform: translateX(13px);
          transform: translateX(13px);
        }

        /* Rounded sliders */
        .slider.round {
          border-radius: 17px;
        }

        .slider.round:before {
          border-radius: 50%;
        }
        </style>
        </head>
        <body>

        <div id='{{uid}}' style='display:block; float:left; margin-top:40px;'>
            <dl>
            {% for label in labels %}
            <dd>
                <label class="switch">
                  <input data-labelname='{{label}}' type="checkbox" onclick='{{onclick_name}}(this, "{{label}}");' checked>
                  <span class="slider round"></span>
                </label>
                {{label}}
                 </dd>
            {% endfor %}
            </dl>
        </div>

    '''
    filter_checkbox_html = Template(filter_checkbox_html)
    return filter_checkbox_html.render(
        labels=labels, onclick_name=onclick_name, uid=uid
    ), uid

def sankey_filter_js(filter_uid):
    js_template = '''
        function itemChecked(event, name) {
            var elms = document.getElementById('{{filter_uid}}').querySelectorAll('input');
            var checked = [];
            var unchecked = [];
            elms.forEach(function(i) {
                if (i.checked) {
                    checked.push(i.dataset.labelname);
                } else {
                    unchecked.push(i.dataset.labelname);
                }
            });

            var newData = [];
            var newLinks = [];
            originalData.forEach(function(i) {
                if (unchecked.indexOf(i.name) <0) {
                    newData.push(i);
                }
            })
            originalLinks.forEach(function(i) {
                if (unchecked.indexOf(i.source) <0 & unchecked.indexOf(i.target) <0) {
                    newLinks.push(i);
                }
            })
            setOption(newData, newLinks);
        };
    '''
    js_template = Template(js_template)
    return js_template.render(
        filter_uid=filter_uid
    )

def get_html():
    templates = []
    for fname in ['echarts.js', "echartsgl.js"]:
        with open(fname, "r") as f:
            template = '''
            <script>{}</script>
            '''.format(f.read())
            templates.append(template)
    result = " ".join(templates)
    return HTML(result)


@singledispatch
def to_serializable(val):
    return json.dumps(val)


class _Base():

    def to_json(self):
        _dict = attr.asdict(self)
        return json.dumps({k: v for k, v in _dict.items() if v is not None})


@to_serializable.register(_Base)
def ts_datetime(val):
    return val.to_json()


@attr.s
class TextStyle(_Base):
    color = attr.ib('#333')
    fontSize = attr.ib(18)


@attr.s
class Title(_Base):
    show = attr.ib(default=True)
    text = attr.ib(default="title")
    x = attr.ib(default="center")
    top = attr.ib(default=None)
    textStyle = TextStyle()


@attr.s
class ToolBox(_Base):
    feature = attr.ib(default={
        'restore': {},
        'saveAsImage': {},
        'dataZoom': {
            'yAxisIndex': 'none'
        },
    })


@attr.s
class XAxis(_Base):
    type = attr.ib()
    data = attr.ib()
    boundaryGap = attr.ib(default=False)
    min = attr.ib(default=None)
    max = attr.ib(default=None)


@attr.s
class YAxis(_Base):
    type = attr.ib()
    data = attr.ib(default=None)
    name = attr.ib(default=None)
    min = attr.ib(default=None)
    max = attr.ib(default=None)


@attr.s
class DataZoom(_Base):
    show = attr.ib(default=True)
    realtime = attr.ib(default=True)
    start = attr.ib(default=40)
    end = attr.ib(default=60)
    type = attr.ib(default="slider")
    orient = attr.ib(default="horizontal")


@attr.s
class SymbolSize(_Base):
    size = attr.ib(default=20)
    z_multiplier = attr.ib(default=1)

    def render(self):
        t = '''
            function(data) {
                if (data.length == 3 ) {
                    return data[2] * {{z_multiplier}};
                } else {
                    return {{size}};
                }
            }
        '''
        t = Template(t)
        return t.render(size=self.size, z_multiplier=self.z_multiplier).replace("\n", "")


@attr.s
class ItemStyle(_Base):
    normal = attr.ib(default=None)
    opacity = attr.ib(default=None)


@attr.s
class VisualMap(_Base):
    min = attr.ib()
    max = attr.ib()
    type = attr.ib(default="piecewise")
    calculable = attr.ib(default=True)
    orient = attr.ib(default="horizontal")
    left = attr.ib(default=50)
    top = attr.ib(default=50)


@attr.s
class Calendar(_Base):
    range = attr.ib()
    top = attr.ib(default=50)
    left = attr.ib(default=50)
    right = attr.ib(default=50)
    cellSize = attr.ib(default=['auto', 15])
    itemStyle = attr.ib(default={
        'normal': {'borderWidth': 0.5}
    }),
    yearLabel = attr.ib(default={'show': False})


@attr.s
class Series(_Base):
    data = attr.ib()
    type = attr.ib()

    animation = attr.ib(default=True)
    areaStyle = attr.ib(default=None)
    name = attr.ib(default=None)
    coordinateSystem = attr.ib(default=None)
    symbolSize = attr.ib(default=SymbolSize())
    itemStyle = attr.ib(default=None)
    large = attr.ib(default=False)
    largeThreshold = attr.ib(default=True)

    def html(self):
        _dict = attr.asdict(self)
        _dict.pop('symbolSize')
        
        t = '''
            {
            {% for k, v in _dict.items() %}{% if v is not none %}{{k}}: {{v|tojson|safe}},{% endif %}
            {% endfor %} 'symbolSize': function(data) {
                    if (data.length == 3 ) {
                        return data[2] * {{z_multiplier}};
                    } else {
                        return {{size}};
                    }
                },
            }
        '''
        return Template(t).render(
            _dict=_dict,
            z_multiplier=self.symbolSize.z_multiplier,
            size=self.symbolSize.size,

        )

    def get_dict(self):
        _dict = attrs.asdict(self)
        r = self.symbolSize.render()
        json.dumps(_dict)
        return _dict


def default_cross_tooltip():
    return {
        'trigger': 'axis',
        'axisPointer': {
            'type': 'cross',
            'animation': False,
            'label': {
                'backgroundColor': '#505765'
            }
        }
    }


def default_legend(names):
    return {
        'data': [str(i) for i in names],
        'x': 'left',
    }


class UPlot():

    def __init__(self, df):
        self.uid = uuid.uuid4().hex
        self.df = df.copy(deep=True)
        self.height = 800
        self.width = 800
        self.template = None
        self.context = {}
        self._dict = {
            'toolbox': ToolBox(),
        }

    def size(self, height=800, width=800):
        self.height = height
        self.width = width
        return self

    def title(self, title, title_options=None):
        if not title_options:
            title_options = {}
        self._dict['title'] = Title(text=title, **title_options)
        return self

    def tooltip(self, tooltip=None):
        if tooltip is not None:
            self._dict['tooltip'] = tooltip
        else:
            self._dict['tooltip'] = default_cross_tooltip(),
        return self

    def slider(self, axis, start_pct=40, end_pct=60, realtime=True):
        self._dict['dataZoomJson'] = [
            attr.asdict(DataZoom(
                orient='horizontal' if axis == 'x' else 'vertical',
                start=start_pct,
                end=end_pct,
            )),
            attr.asdict(DataZoom(
                orient='horizontal' if axis == 'x' else 'vertical',
                start=start_pct,
                end=end_pct,
                type="inside",
            ))
        ]
        self._dict['dataZoomJson'] = json.dumps(self._dict['dataZoomJson'])
        return self

    def scatter_plot(self, x, y, z=None, segment=None, symbol_size=5, largeThreshold=None):
        all_cols, _df = self._all_cols_and_df(x, y, z=z, segment=segment)

        series = []
        legend_names = []

        if segment is None:
            
            sources = [{'df': _df, 'name': y}]
        else:
            sources = []
            segments = _df[segment].unique()
            for segment_val in segments:
                _temp = _df.loc[_df[segment] == segment_val].drop_duplicates()
                sources.append({
                    'df': _temp,
                    'name': segment_val
                })

        for source in sources:
            _data = {
                'name':source['name'],
                'type':'scatter',
                'animation':True,
                'areaStyle':{},
                'data':source['df'].as_matrix().tolist(),
                'symbolSize':SymbolSize(size=symbol_size)
            }
            if largeThreshold is not None:
                _data['large'] = True
                _data['largeThreshold'] = largeThreshold
            s = Series(**_data)
            legend_names.append(source['name'])
            series.append(s.html())

        self._dict['xAxis'] = {}
        self._dict['yAxis'] = YAxis(type="value", min="dataMin", max='dataMax')
        self._dict['series'] = series
        self._dict['legend'] = default_legend(legend_names)
        self.tooltip(tooltip={})
        return self

    def _ycols(self, y):
        if isinstance(y, basestring):
            y_cols = [y]
        else:
            y_cols = y

        return y_cols

    def _series_dfs(self, df,):
        if segment is None:
            return [{'df': df, 'name': y}]
        else:
            series = []
            segments = df[segment].unique()
            for segment_val in segments:
                _temp = _df.loc[_df[segment] == segment_val].drop_duplicates()
                segments.append({'df': df, 'name': segment_val})

    def _all_cols_and_df(self, x, y, z=None, segment=None):
        y_cols = self._ycols(y)

        all_cols = y_cols + [x]

        if segment:
            all_cols.append(segment)
        if z:
            all_cols.append(z)

        _df = self.df
        _df = _df[all_cols]
        _df = _df.drop_duplicates()
        _df = _df.dropna()
        return all_cols, _df

    def time_series(self, x, y, symbol_size=5):
        all_cols, _df = self._all_cols_and_df(x, y)

        series = []
        legend_names = []
        for col in self._ycols(y):
            s = Series(
                name=col, type='line',
                animation=True, areaStyle={},
                data=[i for i in _df[col]],
                symbolSize=SymbolSize(size=symbol_size)
            )
            legend_names.append(col)
            series.append(s.html())

        self._dict['xAxisJson'] = XAxis(type="category", data=[str(i) for i in _df[x]]).to_json()
        self._dict['yAxis'] = YAxis(type="value", min="dataMin", max='dataMax')
        self._dict['series'] = series
        self._dict['legend'] = default_legend(legend_names)
        return self

    def add_visual_map(self, min_, max_, **kwargs):
        self._dict['visualMapJson'] = VisualMap(
            min=min_,
            max=max_,
            top=50,
            **kwargs
        )
        self._dict['visualMapJson'] = json.dumps(attr.asdict(self._dict['visualMapJson']))
        return self

    def calendar_heatmap(self, iso_date_col, value_col, filter_type='piecewise'):

        _min = float(self.df[value_col].min())
        _max = float(self.df[value_col].max())

        _min_date = self.df[iso_date_col].min()
        _max_date = self.df[iso_date_col].max()

        data = self.df[[iso_date_col, value_col]].values.tolist()
        self.add_visual_map(_min, _max, type=filter_type)

        self._dict['calendarJson'] = Calendar(
            range=[_min_date, _max_date],
            top=120,
            left=30,
            right=30
        )
        self._dict['calendarJson'] = json.dumps(attr.asdict(self._dict['calendarJson']))
        series = Series(
            type="heatmap",
            coordinateSystem='calendar',
            data=data
        )
        self._dict['series'] = [series.html()]
        self.tooltip(tooltip={})
        return self

    def _render_normal_plot(self):
        option = {}

        # self._dict.as_dict = _as_dict
        
        series = self._dict.pop("series", None)
        data = {}
        for k, v in self._dict.items():
            if k.endswith("Json"):
                data[k.replace("Json", "")] = v
            else:
                try:
                    data[k] = {k:v for k, v in attr.asdict(v).items() if v is not None}
                except Exception as e:
                    # recurse
                    data[k] = json.dumps(v)

        template = '''
            <div id={{uid}} style="width: {{width}}px; height: {{height}}px;"></div>
            <script>
                var option =  {
                    {% for k, v in _dict.items() %}
                        {{k}}:{{v}},
                    {% endfor %}

                    {% if series %}
                        'series':[{% for k in series %}{{k}},{% endfor %}],
                    {% endif %}
                };

            var chart = echarts.init(document.getElementById('{{uid}}'));
            chart.setOption(option);
            </script>
        '''
        template = Template(template)
        result = template.render(
            uid=self.uid, width=self.width, height=self.height, _dict=data, series=series,
        )

        return HTML(result)

    def render(self):
        if self.template is None:
            result = self._render_normal_plot()
            return result
        else:
            template = self.template
            context = self.context
            context['width'] = self.width
            context['height'] = self.height
            result = HTML(template.render(context))
            return result

    def sankey(self, from_col, to_col, value_col, add_filters=True):
        t = '''
            {% if filter_html %}
                {{filter_html}}
            {% endif %}
            <div id='{{uid}}' style="width: {{width}}px; height: {{height}}px;display:block; float:left;"></div>
            <script>
            
            var originalData = {{nodes}};
            var originalLinks = {{links}};

            {% if filter_js %}
                {{filter_js}}
            {% endif %}

            function setOption(data, links) {

                var chart = echarts.init(document.getElementById('{{uid}}'));
                var option = {
                    animation: true,
                    title: {
                        text: 'Sankey Diagram'
                    },
                    tooltip: {
                        trigger: 'item',
                        triggerOn: 'mousemove'
                    },
                    series: [
                        {
                            type: 'sankey',
                            data: data,
                            links: links,
                            focusNodeAdjacency: 'allEdges',
                            itemStyle: {
                                normal: {
                                    borderWidth: 1,
                                    borderColor: '#aaa'
                                }
                            },
                            lineStyle: {
                                normal: {
                                    color: 'source',
                                    curveness: 0.5
                                }
                            }
                        }
                    ]
                }
                chart.setOption(option);
            }
            setOption(originalData, originalLinks);
            </script>
        '''

        _df = self.df
        _df = _df[[from_col, to_col, value_col]]
        _df = _df.groupby([from_col, to_col]).sum().reset_index()

        _df = _df.dropna()

        uid = uuid.uuid4().hex
        nodes = []
        for i in _df[from_col].unique():
            if {'name': str(i)} not in nodes:
                nodes.append({'name': str(i)})

        for i in _df[to_col].unique():
            if {'name': str(i)} not in nodes:
                nodes.append({'name': str(i)})

        links = []
        for row in _df.to_dict(orient="records"):
            _row = {
                'source': str(row[from_col]),
                'target': str(row[to_col]),
                'value': row[value_col],
            }
            links.append(_row)

        filter_js= None
        filter_html = None
        if add_filters:
            filter_html, filter_id = sankey_filter_checkbox([i['name'] for i in nodes], 'itemChecked')
            filter_js = sankey_filter_js(filter_id)

        self.template = Template(t)
        self.context = {
            'uid': uid,
            'nodes': nodes,
            'links': links,
            'filter_html': filter_html,
            'filter_js': filter_js
        }
        return self
