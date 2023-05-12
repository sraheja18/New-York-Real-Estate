from bokeh.plotting import figure, output_file, show
from bokeh.models import ColumnDataSource
from bokeh.models.tools import HoverTool
from bokeh.io import output_notebook, show, output_file
from bokeh.plotting import figure, ColumnDataSource
from bokeh.tile_providers import get_provider, Vendors
from bokeh.palettes import Category10, Category20, Category20b, Category20c
from bokeh.palettes import PRGn, RdYlGn
from bokeh.transform import linear_cmap,factor_cmap
from bokeh.layouts import row, column
from bokeh.models import GeoJSONDataSource, LinearColorMapper, ColorBar, NumeralTickFormatter
from bokeh.embed import components
from bokeh.resources import CDN

import pandas as pd




from bokeh.models import WheelZoomTool
from bokeh.palettes import RdBu
def plot_bokeh_smalldf(dataframe): 
    """ 
    Plots the circle map of listings based on users inputs. 
    :param dataframe: dataframe filtered by users inputs 
    :type dataframe: pandas DataFrame 
    :return: rendered bokeh circle map 
    :rtype: bokeh map objects 
    """ 

    if len(dataframe) > 500: 
        fs = dataframe.head(500)
        
    else: 
        fs = dataframe.copy()
    df = fs
    chosentile = get_provider(Vendors.OSM)
    palette = RdBu[7]
    source = ColumnDataSource(data=df)
    # Define color mapper - which column will define the colour of the data points
    color_mapper = linear_cmap(field_name = 'price', palette = palette, low = df['price'].min(), high = df['price'].max())

    # Set tooltips - these appear when we hover over a data point in our map, very nifty and very useful
    tooltips = [("Price","@price"), ("Region","@neighbourhood"), ("Keywords","@title_split"), ("Number of Reviews", "@number_of_reviews")]
    # Create figure
    p = figure( 
               x_axis_type = "mercator", 
               y_axis_type = "mercator", 
               x_axis_label = 'Longitude', 
               y_axis_label = 'Latitude', 
               tooltips = tooltips,
               plot_width = 1050, plot_height = 600, tools = ["pan", "reset", "save", "wheel_zoom"])
    # Add map tile
    p.add_tile(chosentile)

    # Add points using mercator coordinates
    sz = 7
    line_width = 1.2
    if (len(fs) < 70) or (fs["neighbourhood"].nunique() == 1): 
        sz = 12.7
        line_width = 2.7
    p.circle(x = 'mercator_x', y = 'mercator_y', color = color_mapper, source = source, size = sz, fill_alpha = 0.7, line_width = line_width, line_color = "black")
    # Defines color bar
    color_bar = ColorBar(color_mapper=color_mapper['transform'], 
                         formatter = NumeralTickFormatter(format='0.0[0000]'), 
                         label_standoff = 13, width=8, location=(0,0), title = "price")
    p.add_layout(color_bar, 'right')
    p.xgrid.grid_line_color = None
    p.ygrid.grid_line_color = None
    p.axis.visible = False
    p.title.align = "right"
    p.toolbar.active_scroll = p.select_one(WheelZoomTool)
    p.toolbar.logo = None
    script1, div1 = components(p)
    cdn_js = CDN.js_files[0]
    
    return script1, div1, cdn_js


    
def sort_keys(ls, df):
    """ 
    Sorts the dataframe based on input key
    :param ls: keys for sorting 
    :type ls: list 
    :param df: dataframe to sort
    :type df: pandas DataFrame 
    :return: sorted dataframe 
    
    :rtype: pandas DataFrame 
    """ 

    return df

def viz_key_df(ls, df): 
    """ 
    Visualize the listings based on users input using the plot_bokeh_smalldf() 
    :param ls: keys for sorting 
    :type ls: list 
    :param df: dataframe to visualize 
    :type df: pandas DataFrame 
    :return: rendered map 
    :rtype: bokeh map objects 
    """ 
    
    
    key_df=sort_keys(ls, df)

    
    
    return plot_bokeh_smalldf(key_df)