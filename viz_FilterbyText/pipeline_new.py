from bokeh.palettes import GnBu
from bokeh.transform import cumsum
import matplotlib.pyplot as plt
from bokeh.palettes import Blues
from bokeh.models import HoverTool
from bokeh.plotting import figure, show, output_file
import numpy as np
from bokeh.plotting import figure, output_file, show
from bokeh.models import ColumnDataSource
from bokeh.models.tools import HoverTool
from bokeh.io import output_notebook, show, output_file
from bokeh.plotting import figure, ColumnDataSource
from bokeh.tile_providers import get_provider, Vendors
from bokeh.palettes import Category10, Category20, Category20b, Category20c
from bokeh.palettes import PRGn, RdYlGn
from bokeh.transform import linear_cmap, factor_cmap
from bokeh.layouts import row, column
from bokeh.models import GeoJSONDataSource, LinearColorMapper, ColorBar, NumeralTickFormatter
from bokeh.embed import components
from bokeh.resources import CDN
import pandas as pd
from io import BytesIO
import base64



from bokeh.models import WheelZoomTool
from bokeh.palettes import RdBu



def visualize_count(filtered_dataset): 
    """ 
    Visualize the count of listings based on the user inputs, using hexbin map. 

    :param filtered_dataset: filtered dataset for mapping 
    :type filtered_dataset: pandas DataFrame 

    :return: a rendered bokeh hexbin map based on inputs 
    :rtype: bokeh map objects 
    """ 
    fs = filtered_dataset.copy()


    def wgs84_to_web_mercator(df, lon = "longitude", lat = "latitude"): 
        """ 
        Transforms the longitude and latitude to web mercators for hexbin mapping. 

        
        :param df: dataframe to transform 
        :type df: pandas DataFrame 

        :param lon: name of the longitude column 
        :type lon: str 

        :param lat: name of the latitude column 
        :type lat: str 

        :return: transformed dataframe 
        :rtype: pandas DataFrame 
        """ 
        k = 6378137
        df["x"] = df[lon] * (k * np.pi / 180.0)
        df["y"] = np.log(np.tan((90 + df[lat]) * np.pi / 360.0)) * k
        return df

    # Transforms the dataset for hexbin mapping later 
    CDMXhex = wgs84_to_web_mercator(fs) 
    x = CDMXhex['x']
    y = CDMXhex['y']
    tile_provider = get_provider(Vendors.OSM)

    palette = list(reversed(Blues[7]))

    # Setting up titles 
    title = "Number of Airbnb Listings in "
    if fs["neighbourhood"].nunique() == 1:
        title = title + fs["neighbourhood"].iloc[0] + ", "
    for i in fs["neighbourhood_group"].unique():
        title = title + i + ", "
    title = title + "NYC"

    p = figure(match_aspect = False, tools = ["pan", "reset", "save", "wheel_zoom"], 
               x_axis_type="mercator", y_axis_type="mercator",plot_width=1050,plot_height=600)

    p.grid.visible = True

    # Adjust size of the hexbin for better visualization
    sz = 1000
    if fs["neighbourhood_group"].nunique() == 1:
        sz = 500
    if fs["neighbourhood"].nunique() == 1:
        sz = 127 

    r, bins = p.hexbin(x, y, size=sz,
                       line_color="white", line_alpha=0.2,
                       palette=palette, hover_color="pink", alpha=0.7, hover_alpha=0.2)

    # Adjust the map layout for better visualization
    p.add_tools(HoverTool(
        tooltips=[("Count", "@c")],
        show_arrow=True, mode="mouse", point_policy="follow_mouse", renderers=[r]))

    r = p.add_tile(tile_provider)
    r.level = "underlay" 

    color_mapper = linear_cmap(field_name='price', palette=palette,
                               low=bins["counts"].min(), high=bins["counts"].max() + 1)

    color_bar = ColorBar(color_mapper=color_mapper['transform'],
                         formatter=NumeralTickFormatter(format='0.0[0000]'),
                         label_standoff=13, width=8, location=(0, 0), title = "Number of Listings")

    
    p.add_layout(color_bar, 'right')
    p.xgrid.grid_line_color = None
    p.ygrid.grid_line_color = None
    p.axis.visible = False
    p.title.align = "right"
    p.toolbar.active_scroll = p.select_one(WheelZoomTool)
    p.toolbar.logo = None

    script1, div1 = components(p)
    cdn_js = CDN.js_files[0]

    
    return script1, div1, cdn_js, title


def donut(dataset): 
    """ 
    Plot the donut chart to visualize the percentage of room types in the selected regions. 

    
    
    :param dataset: dataset to visualize 
    :type dataset: pandas DataFrame 

    :return: a donut chart visualizing the percentage of room types 
    :rtype: rendered image
    """ 

    # Renders the donut chart based on room types 
    fs = dataset.copy()
    fig, ax = plt.subplots(figsize=(11, 7), subplot_kw=dict(aspect="equal"))
    column_name = fs.columns[0]
    recipe = (fs.groupby("room_type").count()[
              column_name] / len(fs)).reset_index()["room_type"]
    data = (fs.groupby("room_type").count()[
            column_name] / len(fs)).reset_index()[column_name]
    wedges, texts = ax.pie(data, wedgeprops=dict(
        width=0.5, edgecolor="black"), startangle=-40)
    bbox_props = dict(boxstyle="square,pad=0.3", fc="w", ec="k", lw=0.72)
    kw = dict(arrowprops=dict(arrowstyle="-"),
              bbox=bbox_props, zorder=0, va="center") 
    
    # Add wedges connecting to pieces of the chart for better visualization 
    for i, p in enumerate(wedges):
        ang = (p.theta2 - p.theta1)/2. + p.theta1
        y = np.sin(np.deg2rad(ang))
        x = np.cos(np.deg2rad(ang))
        horizontalalignment = {-1: "right", 1: "left"}[int(np.sign(x))]
        connectionstyle = "angle,angleA=0,angleB={}".format(ang)
        kw["arrowprops"].update({"connectionstyle": connectionstyle})
        ax.annotate(recipe[i] + ": " + str(np.round(data[i] * 100, 1)) + "%", xy=(x, y), xytext=(1.35*np.sign(x), 1.4*y),
                    horizontalalignment=horizontalalignment, fontsize=12, **kw)

    # Renders the resulting chart to image for display 
    buffer = BytesIO()
    plt.savefig(buffer)
    plot_data = buffer.getvalue()
    imb = base64.b64encode(plot_data)
    ims = imb.decode()
    imd = "data:image/png;base64," + ims

    return imd



# 127 

def visualize_price(filtered_dataset): 
    """ 
    Visualize the average price of listings based on the user inputs, using hexbin map. 

    :param filtered_dataset: filtered dataset for mapping 
    :type filtered_dataset: pandas DataFrame 

    :return: a rendered bokeh hexbin map based on inputs 
    :rtype: bokeh map objects 
    """ 

    fs = filtered_dataset.copy()

    def wgs84_to_web_mercator(df, lon = "longitude", lat = "latitude"): 
        """ 
        Transforms the longitude and latitude to web mercators for hexbin mapping. 

        
        :param df: dataframe to transform 
        :type df: pandas DataFrame 

        :param lon: name of the longitude column 
        :type lon: str 

        :param lat: name of the latitude column 
        :type lat: str 

        :return: transformed dataframe 
        :rtype: pandas DataFrame 
        """ 
        k = 6378137
        df["x"] = df[lon] * (k * np.pi/180.0)
        df["y"] = np.log(np.tan((90 + df[lat]) * np.pi/360.0)) * k
        return df

    # Prepare the dataset for hexbin mapping later 
    CDMXhex = wgs84_to_web_mercator(fs)
    x = CDMXhex['x']
    y = CDMXhex['y']
    tile_provider = get_provider(Vendors.OSM)
    avg_price = CDMXhex.groupby("x")["price"].mean().round(0).values
    palette = RdBu[11]

    # Adjust map title based on user inputs 
    title = "Price of Airbnb Listings in "
    if fs["neighbourhood"].nunique() == 1:
        title = title + fs["neighbourhood"].iloc[0] + ", "
    for i in fs["neighbourhood_group"].unique():
        title = title + i + ", "
    title = title + "NYC"

    # Adjust the size of the hexbin for better visualization 
    sz = 1500
    if fs["neighbourhood_group"].nunique() == 1:
        sz = 800
    if fs["neighbourhood"].nunique() == 1:
        sz = 200

    # Plotting 
    p = figure(match_aspect=False, tools = ["pan", "reset", "save", "wheel_zoom"], 
               x_axis_type="mercator", y_axis_type="mercator",plot_width=1050,plot_height=600)

    p.grid.visible = True

    r, bins = p.hexbin(x, y, size = sz,
                       line_color="white", line_alpha=0.2,
                       palette=palette, hover_color="pink", alpha=0.7, hover_alpha=0.2)

    # Adjust the map layouts for better visualization 
    r = p.add_tile(tile_provider)
    r.level = "underlay"

    color_mapper = linear_cmap(
        field_name='price', palette=palette, low = min(avg_price), high = max(avg_price))

    color_bar = ColorBar(color_mapper=color_mapper['transform'], 
                         formatter=NumeralTickFormatter(format='0.0[0000]'),
                         label_standoff=13, width=8, location=(0, 0), title = "Average Price")

    p.add_layout(color_bar, 'right')
    output_notebook()
    p.xgrid.grid_line_color = None
    p.ygrid.grid_line_color = None
    p.axis.visible = False
    p.title.align = "right"
    p.toolbar.active_scroll = p.select_one(WheelZoomTool)
    p.toolbar.logo = None

    script1, div1 = components(p)
    cdn_js = CDN.js_files[0]
    return script1, div1, cdn_js, title