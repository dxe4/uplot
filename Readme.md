```python
UPlot(df).sankey(
    'month','origin', 'distance',
    add_filters=True
).size(
    width=500, height=500
).render()
```

![Alt Text](https://github.com/dxe4/uplot/raw/master/gif/Peek%202019-05-12%2014-34.gif)

```python
UPlot(df).time_series(
    'iso_date', ['dep_delay', 'arr_delay']
).slider(
    "x", start_pct=30, end_pct=60, 
).tooltip().size(width=1000, height=500).render()
```
![Alt Text](https://github.com/dxe4/uplot/raw/master/gif/Peek%202019-05-12%2014-50.gif)

```python
UPlot(df).calendar_heatmap(
    'iso_date', 'cnt', filter_type='piecewise'
).size(width=800, height=300).render()
```
![Alt Text](https://github.com/dxe4/uplot/raw/master/gif/Peek%202019-05-12%2014-51.gif)

```python
UPlot(df).scatter_plot(
     "distance", "avg_speed", symbol_size=2
).slider('x', start_pct=0, end_pct=30).size(width=500, height=500).render()
```
![Alt Text](https://github.com/dxe4/uplot/raw/master/gif/Peek%202019-05-12%2015-00.gif)
