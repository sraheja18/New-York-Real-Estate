from pred import predict
from application import *
from viz_FilterbyText.pipeline_new_1 import *
from viz_FilterbyText.pipeline_new import *
import pytest
import pandas as pd
import numpy as np
from flask import Flask, request, render_template
from werkzeug.datastructures import MultiDict

class TestCases:
    ##### Chang #####
    def test_predict(self):
        '''
        Test predict(model_path, encoded_input) fucntion in pred/predict.py. The function takes the path
        of the regressor model and the encoded input data as parameters, and should give a float value as
        the output.
        '''
        request_form = {
            'roomType': 'Entire home/apt',
            'neighbourhoodGroup': 'Bronx', 
            'neighbourhood': 'Claremont Village',
            'minNight': '1'
        }
        model_path = './pred/model.pkl'
        encoded_input = data_transform(get_pd_df('./data/final_dataframe.csv'), request_form)
        y_pred = predict(model_path=model_path, encoded_input=encoded_input)
        assert isinstance(y_pred, np.float64)

    def test_get_ng_dict(self):
        '''
        Test get_ng_dict(df) function in application.py. The function takes the df with pd.DataFrame type
        and output an dictionary with the neighbourhood groups as keys, and the contained neighbourhoods 
        as values.
        '''
        df = get_pd_df('./data/final_dataframe.csv')
        ng_dict = get_ng_dict(df)
        assert isinstance(ng_dict, dict)
        assert 'Chinatown' in ng_dict.get('Manhattan')

    def test_get_pd_df(self):
        '''
        Test get_pd_df(path) function in application.py. The function takes the path of the dataset csv
        as input, and output the loaded pd.DataFrame object.
        '''
        df = get_pd_df('./data/final_dataframe.csv')
        assert isinstance(df, pd.DataFrame)
    ##### Chang #####


    ##### Kexin #####
    

    def test_plot_bokeh_map_new(self):
        ''' 
        Tests plot_bokeh_map_new() fucntion in application.py. The plot_bokeh_map_new() function 
        is used to filter room_lists that help plot bokeh figure.
        The plot_bokeh_map_new function input should be a structured dataframe and returns a function 
        called viz_key_df with passed in params: room_list and df.
        '''
        rm_ls=['bedroom', 'bedrooms', 'bed',
                 'beds', 'bdrs', 'bdr', 'room', 'rooms',
                 'apt', 'apartment', 'studio', 'loft', 'townhouse',
                 'bath', 'baths']   
        csv_path='./viz_FilterbyText/final_dataframe.csv'
        full_df=pd.read_csv(csv_path, index_col=0)
        random_df=full_df.sample(n=10) # randomly select 10 rows from full_df
        assert type(random_df) == pd.DataFrame
        output1,output2,output3 = plot_bokeh_map_new(random_df)
        assert isinstance(output1, str) 
        assert isinstance(output2, str)
        assert isinstance(output3, str)


    def test_plot_bokeh_smalldf(self):
        '''
        Tests plot_bokeh_smalldf() fucntion in viz_FilterbyText.pipeline_new_1.py. The plot_bokeh_smalldf() function 
        is used to create an auto-generated bokeh figure from the final_dataframe.csv.
        The plot_bokeh_smalldf function input should be a structured dataframe and returns a bokeh plot based on it.
        '''
        csv_path='./viz_FilterbyText/final_dataframe.csv'
        full_df=pd.read_csv(csv_path, index_col=0)
        random_df=full_df.sample(n=10) # randomly select 10 rows from full_df
        col_name_check=['id','name','host_id','host_name','neighbourhood_group','neighbourhood',
                        'latitude','longitude','room_type','price','minimum_nights','number_of_reviews','coordinates',
                        'mercator','mercator_x','mercator_y','title_split']
            
        assert all(i in col_name_check for i in random_df.columns.tolist())  == True
        # self.assertEqual(str(type(p)),"<class 'bokeh.plotting.figure.Figure'>") # comment out as return object is not a bokeh fig
        script1, div1, cdn_js=plot_bokeh_smalldf(random_df)
        assert isinstance(cdn_js, str) 
        assert isinstance(script1, str)
        assert isinstance(div1, str)
    ##### Kexin #####


    ##### bittan #####
    def test_parse_price_range(self):
        ''' Test cases for parse_price-range function in application.py '''
        assert type(parse_price_range('20-30'))==list, 'output should be a list'
        assert parse_price_range('20-30')==[i for i in range(20,30)]
        assert parse_price_range('''-''')==[i for i in range(0,20000)]

    def test_select_from_request(self):
        ''' Test cases for select from request function in application.py'''
        csv_path='./viz_FilterbyText/final_dataframe.csv'
        full_df=pd.read_csv(csv_path, index_col=0)
        request_form=MultiDict([('roomType', 'Entire home/apt'), ('neighbourhoodGroup', 'Brooklyn'), ('neighbourhood', 'Cypress Hills'), ('minPrice', '10'), ('maxPrice', '1000'), ('minNight', '1')])
        assert type(select_from_request(full_df,request_form
            ,notfound=False))==pd.DataFrame
        assert isinstance(select_from_request(full_df, request_form, notfound = True), pd.DataFrame)
        assert len(select_from_request(full_df, request_form, notfound = False)) >= 0
        
        
        
        
        request_form = MultiDict([('roomType', 'Entire home/apt'), ('neighbourhoodGroup', 'Brooklyn'), ('neighbourhood', 'Cypress Hills'), ('maxPrice', '1000'), ("minReview", "0")])
        assert isinstance(select_from_request(full_df, request_form), pd.DataFrame)

    def test_sort_keys(self):
        ''' Test cases for sort_keys function in ./viz_FilterbyText/pipeline_new_1.py'''
        csv_path='./viz_FilterbyText/final_dataframe.csv'
        full_df=pd.read_csv(csv_path, index_col=0)
        assert type(sort_keys([],full_df))==pd.DataFrame
        

    def test_viz_key_df(self):
        ''' Test cases for viz_key_df function in ./viz_FilterbyText.pipeline_new_1.py'''
        csv_path='./viz_FilterbyText/final_dataframe.csv'
        full_df=pd.read_csv(csv_path, index_col=0)
        script1, div1, cdn_js=viz_key_df([],full_df)
        assert isinstance(cdn_js, str)
        assert isinstance(script1, str)
        assert isinstance(div1, str)
    ##### bittan #####


    ##### Zhexu ##### 
    def test_load_model(self): 
        """ 
        Test the load_model() in application.py

        """ 

        assert load_model() == None 

    
    def test_actual_app(self): 
        """ 
        Test the actual application renders 

        """ 
        assert actual_app() == None # Will not return anything if there is no user input 

    def test_visualize_count(self): 
        """ 
        Test the hexbin map for visualizing counts. 

        """ 

        csv_path = './viz_FilterbyText/final_dataframe.csv'

        fs = pd.read_csv(csv_path)

        script1, div1, cdn_js, title = visualize_count(fs)

        assert isinstance(script1, str)
        assert isinstance(div1, str)
        assert isinstance(cdn_js, str)
        assert isinstance(title, str)

        rq = MultiDict([('roomType', 'Entire home/apt'), ('neighbourhoodGroup', 'Brooklyn'), ('neighbourhood', 'Cypress Hills')])
        df_selected = select_from_request(fs, rq)
        script1, div1, cdn_js, title = visualize_count(df_selected)


        assert isinstance(script1, str)
        assert isinstance(div1, str)
        assert isinstance(cdn_js, str)
        assert isinstance(title, str)

    def test_visualize_price(self): 
        """ 
        Test the hexbin map for visualizing price. 

        """ 

        csv_path = './viz_FilterbyText/final_dataframe.csv'

        fs = pd.read_csv(csv_path)

        script1, div1, cdn_js, title = visualize_price(fs)

        assert isinstance(script1, str)
        assert isinstance(div1, str)
        assert isinstance(cdn_js, str)
        assert isinstance(title, str)

        rq = MultiDict([('roomType', 'Entire home/apt'), ('neighbourhoodGroup', 'Brooklyn'), ('neighbourhood', 'Cypress Hills')])
        df_selected = select_from_request(fs, rq)
        script1, div1, cdn_js, title = visualize_price(df_selected)


        assert isinstance(script1, str)
        assert isinstance(div1, str)
        assert isinstance(cdn_js, str)
        assert isinstance(title, str)

    def test_donut(self): 
        """ 
        Test the dount() which generates the donut chart. 

        """ 

        csv_path = './viz_FilterbyText/final_dataframe.csv'
        fs = pd.read_csv(csv_path)
        img = donut(fs)

        
        assert isinstance(img, str)
       