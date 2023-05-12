# Serve model as a flask application
import time
import pickle
from flask import Flask, request, render_template
import pandas as pd
from pred.predict import data_transform, predict, parse_request

from bokeh.tile_providers import get_provider, Vendors
from bokeh.palettes import Category20c
from bokeh.transform import linear_cmap
from bokeh.plotting import figure, ColumnDataSource
from bokeh.models import ColorBar, NumeralTickFormatter
from bokeh.embed import components
from bokeh.resources import CDN
from bokeh.palettes import RdBu

from viz_FilterbyText.pipeline_new_1 import viz_key_df
from viz_FilterbyText.pipeline_new import visualize_count, visualize_price, donut

model = None                    # model for prediction
df = None                       # global DataFrame object
application = Flask(__name__)   # Flask application




def select(df_selected, attributes, ranges):
    """ 
    Selects data according to the parsed attributes and ranges. 
   
    :param df_selected: DataFrame to select from 
    :type df_selected: Pandas DataFrame 

    :param attributes: list of attributes to select
    :type attributes: list 

    :param ranges: list of ranges of attributes
    :type ranges: list 
    
    :return: the selected DataFrame
    :rtype: Pandas DataFrame
    """
    assert isinstance(df_selected, pd.DataFrame)
    assert isinstance(attributes, list)
    assert isinstance(ranges, list)
    assert len(attributes) == len(ranges)

    df_selected = df_selected.copy(deep=True)
    for i, attribute in enumerate(attributes):
        if isinstance(ranges[i], list):
            df_selected = df_selected[df_selected[attribute].isin(ranges[i])]
        else:
            df_selected = df_selected[df_selected[attribute] > ranges[i]]

    return df_selected


def get_ng_dict(df):
    """
    Get the dictionary of neighbourhoods based on the input regions. 
    
    :param df: DataFrame to select from. 
    :type df: Pandas DataFrame 
    
    
    :return:  the dictionary of neighbourhoods in the selected regions. 
    :rtype: dictionary 
    """

    return df.groupby("neighbourhood_group")["neighbourhood"].unique().to_dict()


def load_model():
    """
    Loads the Decision Tree Regressor model we trained. 
    
    :return: None 
    :rtype: None 
    """
    global model

    # model variable refers to the global variable
    with open('pred/model.pkl', 'rb') as f:
        model = pickle.load(f)


def get_pd_df(path):
    """
    Read the CSV files into a Pandas DataFrame. 
    
    :param path: path of the csv files. 
    :type path: str 

    :return: a Pandas DataFrame of the inputed files. 
    :rtype: Pandas DataFrame 
    """
    return pd.read_csv(path)


def parse_price_range(priceRangeStr):
    """
    Parse the user inputed strings to get price range
    
    :param priceRangeStr: Range of Price 
    :type priceRangeStr: string 

    :return: list of price range 
    :rtype: list 
    """

    loStr, hiStr = priceRangeStr.split('-')
    if hiStr == '':
        hiStr = '20000'
    if loStr == '':
        loStr = '0'
    priceRangeList = list(range(int(loStr), int(hiStr)))
    return priceRangeList


def select_from_request(df_selected, request_form, notfound=False):
    """
    Selects data according to the html request.  

    :param df_selected: DataFrame to select
    :type df_selected: pandas DataFrame 

    :param request_form: the HTML request
    :type request_form: iterable 

    
    :return: the selected DataFrame 
    :rtype: pandas DataFrame 
    """

    global df
    attributes = []
    ranges = []

    roomTypeList = request_form.getlist('roomType')
    if roomTypeList != []:
        attributes.append('room_type')
        ranges.append(roomTypeList)

    neighbourhoodGroupList = request_form.getlist('neighbourhoodGroup')
    if neighbourhoodGroupList != []:
        attributes.append('neighbourhood_group')
        ranges.append(neighbourhoodGroupList)

    neighbourhoodList = request_form.getlist('neighbourhood')
    if neighbourhoodList != []:
        attributes.append('neighbourhood')
        ranges.append(neighbourhoodList)
    priceRange = '-'
    min_price = request_form.get('minPrice')
    max_price = request_form.get('maxPrice')
    if min_price or max_price:
        if min_price:
            priceRange = min_price + priceRange
        else:
            priceRange = '0' + priceRange
        if max_price:
            priceRange = priceRange + max_price

        attributes.append('price')
        ranges.append(parse_price_range(priceRange))

    min_nights = request_form.get('minNight')
    if min_nights:
        attributes.append('minimum_nights')
        ranges.append(int(min_nights))

    min_reviews = request_form.get('minReview')
    if min_reviews:
        attributes.append('number_of_reviews')
        ranges.append(int(min_reviews))

    return select(df_selected, attributes, ranges)




def plot_bokeh_map_new(df_new):
    """
    Plot the map of offerings (points) using the updated visulization and NLP processed dataframe. 

    :param df_new: NLP processed dataframe to plots 
    :type df_new: Pandas DataFrame 

    :return: an interactive bokeh map of circles of offerings 
    :rtype: bokeh map ojects 
    """ 

    room_list = ['bedroom', 'bedrooms', 'bed',
                 'beds', 'bdrs', 'bdr', 'room', 'rooms',
                 'apt', 'apartment', 'studio', 'loft', 'townhouse',
                 'bath', 'baths']
    fs = df_new.copy()
    return viz_key_df(room_list, fs)


@application.route('/actual_app', methods=['POST', 'GET'])
def actual_app(): 
    """ 
    The actual application to generate analysis and render the pages. 


    :return: rendered webpages 
    :rtype: rendered html 
    """ 

    #import cProfile, pstats
    #profiler = cProfile.Profile()
    #profiler.enable()
    col_to_show = ['name', 'host_name', 'room_type', 'neighbourhood_group',
                   'neighbourhood',
                   'minimum_nights', 'number_of_reviews', "price"]
    global df
    df = get_pd_df('./data/final_dataframe.csv')

    df_selected = df.copy(deep=True).drop_duplicates(
        col_to_show).reset_index(drop=True)
    roomTypeSet = set(df['room_type'])
    neighbourhoodGroupSet = set(df['neighbourhood_group'])

    msg_pred = str(len(df_selected)) + " records found based on given inputs, Average Price is: $" + str(round(df_selected["price"].mean(
    ), 1)) + ", Median Price is: $" + str(round(df_selected["price"].median(), 1)) + ", displaying top 20 cheapest offerings: "
    anchor = "top"
    ng_dict = get_ng_dict(df)
    # select data according to the submitted form
    for i in ng_dict.keys():
        ng_dict[i] = list(sorted(ng_dict[i]))
    if not request: 
        return 
    if request.method == 'POST':
        err_message = False
        roomTypeList = request.form.getlist('roomType')
        if roomTypeList == []:
            err_message = True
        neighbourhoodGroupList = request.form.getlist('neighbourhoodGroup')
        if neighbourhoodGroupList == []:
            err_message = True
        neighbourhoodList = request.form.getlist('neighbourhood')
        if neighbourhoodList == []:
            err_message = True
        if err_message:
            err_message = "In order to generate analysis, Please select all the required inputs: Room Type, Region, Neighbourhood. "
            msg_pred = script1 = script1_count = err_message
            div1 = cdn_js = div1_count = cdn_js_count = script1_price = div1_price = cdn_js_price = ""

            # profiler.disable()
            #stats = pstats.Stats(profiler).sort_stats('cumtime')
            # stats.print_stats()
            return render_template('actual_app.html', anchor=anchor, request_form=request.form,
                                   selected_RT=request.form.getlist(
                                       'roomType'),
                                   selected_NG=request.form.getlist(
                                       'neighbourhoodGroup'),
                                   selected_NEI=request.form.get(
                                       'neighbourhood'),
                                   tables="",
                                   roomTypeSet=sorted(roomTypeSet),
                                   neighbourhoodGroupSet=sorted(
                                       neighbourhoodGroupSet),
                                   neighbourhoodSet="", ng_dict=ng_dict,
                                   script1=script1, div1=div1, cdn_js=cdn_js, msg_pred=msg_pred,
                                   script1_count=script1_count, div1_count=div1_count, cdn_js_count=cdn_js_count,
                                   script1_price=script1_price, div1_price=div1_price, cdn_js_price=cdn_js_price,
                                   img="")

        time.sleep(1)
        anchor = "finder"
        df_selected = select_from_request(df_selected, request.form).drop_duplicates(
            col_to_show).reset_index(drop=True)
        msg_pred = str(len(df_selected)) + " records found based on given inputs, Average Price is: $" + str(round(df_selected["price"].mean(
        ), 1)) + ", Median Price is: $" + str(round(df_selected["price"].median(), 1)) + ", displaying top 20 cheapest offerings: "
        if len(df_selected) == 0:
            encoded_input = data_transform(df, request.form)
            price_predicted = predict('pred/model.pkl', encoded_input)
            msg_pred = "We have no available record that match the input, but our model recommands a reasonable price based on the market trend"
            msg_pred = msg_pred + " for the given inputs is: " + \
                "$" + str(price_predicted) + ". "

        elif len(df_selected) < 20:
            encoded_input = data_transform(df, request.form)
            price_predicted = predict('pred/model.pkl', encoded_input)
            msg_pred = "Less than 20 records found based on the inputs, which may not be representative of the market. Based on our model, a resonable price recommended for the given inputs is: "
            msg_pred = msg_pred + "$" + str(price_predicted) + ". "

            msg_pred = msg_pred + " \n And the available listings found based on the inputs are: "

        else:
            msg_pred = str(len(df_selected)) + " records found based on given inputs, Average Price is: $" + str(round(df_selected["price"].mean(
            ), 1)) + ", Median Price is: $" + str(round(df_selected["price"].median(), 1)) + ", displaying top 20 cheapest offerings: "

    if (df_selected.empty):
        script1 = script1_count = "No result was found given the inputs. "
        map_title = ""
        div1 = cdn_js = div1_count = cdn_js_count = script1_price = div1_price = cdn_js_price = img = cs_title = pr_title = donut_title = ""

    else:
        if (len(df_selected) > 500):
            script1, div1, cdn_js = plot_bokeh_map_new(df_selected)
            map_title = "Too many records found, displaying top 500 cheapest listings. "

        else:
            map_title = ""
            script1, div1, cdn_js = plot_bokeh_map_new(df_selected)
        script1_count, div1_count, cdn_js_count, cs_title = visualize_count(
            df_selected)
        script1_price, div1_price, cdn_js_price, pr_title = visualize_price(
            df_selected)
        donut_title = "Percentage of Matching Room Types"

        img = donut(df_selected)
    if len(df_selected) >= 20:
        df_selected = df_selected.head(20)
    if len(df_selected) != 0:
        tables_shown = [df_selected[col_to_show].rename({"name": "Title", "host_name": "Host", "neighbourhood_group": "Region", "neighbourhood": "Neighbourhood", "room_type": "Room Type",
                                                        "minimum_nights": "Minimum Nights", "number_of_reviews": "Number of Reviews", "price": "Price Per Day"}, axis=1).to_html(classes='data', header='true')]
    else:
        tables_shown = ""
    return render_template('actual_app.html', anchor=anchor, request_form=request.form,
                           selected_RT=request.form.getlist('roomType'),
                           selected_NG=request.form.getlist(
                               'neighbourhoodGroup'),
                           selected_NEI=request.form.get('neighbourhood'),
                           tables=tables_shown,
                           roomTypeSet=sorted(roomTypeSet),
                           neighbourhoodGroupSet=sorted(neighbourhoodGroupSet),
                           neighbourhoodSet="", ng_dict=ng_dict, map_title=map_title,
                           script1=script1, div1=div1, cdn_js=cdn_js, msg_pred=msg_pred,
                           script1_count=script1_count, div1_count=div1_count, cdn_js_count=cdn_js_count, cs_title=cs_title,
                           script1_price=script1_price, div1_price=div1_price, cdn_js_price=cdn_js_price, pr_title=pr_title,
                           img=img, donut_title=donut_title)



@application.route('/', methods=['POST', 'GET'])
def home_endpoint():
    """ 
    Route for the flask backend. 

    :return: rendered index.html 
    :rtype: rendered webpages 
    """ 
    return render_template('index.html')


if __name__ == '__main__':
    load_model()  # load model at the beginning once only

    application.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)


