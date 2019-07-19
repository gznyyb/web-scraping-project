# import necessary packages for web scraping
from bs4 import BeautifulSoup
import requests

# import other useful packages
import pandas as pd
from time import sleep, time
from IPython.core.display import clear_output
import numpy as np

import matplotlib.pyplot as plt
import seaborn as sns

class AnimeListScraper(object):
	'''
	Methods for scraping https://myanimelist.net/ for information related to animes

	anime_scraper: method to scrape a list of animes
	save_to_file: save the resulting pandas dataframe to file
	'''
    
    def __init__(self):
        
        self.df_ = pd.DataFrame()
    
    def anime_scraper(self, tot_page_num, pause_sec, is_clear_output=True):
    	'''
    	Method to scrape a list of animes

    	Arguments:
    	tot_page_num: total number of pages to scrape
    	pause_sec: number of seconds to pause before going to the next page
    	is_clear_output: whether to clear output
    	'''

    	# address of the page to start scraping
        start_site_string = 'https://myanimelist.net/topanime.php'
        
        # initialize some variable
        start_time = time()
        num_request = 0
        page_num = 1
        anime_num = 0

        # initialize the dataframe with column names
        anime_dataset_columns = ['anime', 'score', 'popularity',
                                 'season_start', 'year_start', 'season_end', 'year_end',
                                 'num_episodes', 'anime_type']
        self.df_ = pd.DataFrame(columns=anime_dataset_columns)

        # request the initial page
        source = requests.get(start_site_string).text
        soup = BeautifulSoup(source, 'lxml')

        # update number of requests
        num_request += 1

        # pause for the number of second specified so as not to overburden the website
        sleep(pause_sec)

        # loop until some specified condition
        while True:

        	# loop through each animes on the page
            for anime in soup.find_all('tr', class_='ranking-list'):

                # get information about the anime
                info_list = anime.find('div', class_='information di-ib mt4').text.strip().split()

                # get the information only if the information is stored in a nice format
                if len(info_list) == 10:

                    # get the title of the anime
                    anime_code = anime.find('a', class_='hoverinfo_trigger fl-l fs14 fw-b')
                    anime_name = anime_code.text if anime_code is not None else np.nan

                    # get the anime score
                    score_code = anime.find('span', class_='text on')
                    score = score_code.text if score_code is not None else np.nan

                    # get the type of the anime
                    anime_type = info_list[0]

                    # get the number of episodes and replace the missing values with -500
                    num_episodes = int(info_list[1].split('(')[-1].replace('?', '-500'))

                    # get the months when the animes started and ended
                    season_start, season_end = info_list[3], info_list[6]

                    # get the years when the animes started and ended
                    year_start, year_end = int(info_list[4]), int(info_list[7])

                    # get the popularity of the animes
                    popularity = int(info_list[-2].replace(',', ''))

                    # store the above information into a list and append it to the dataframe
                    all_info_list = [anime_name, score, popularity,
                                     season_start, year_start, season_end, year_end,
                                     num_episodes, anime_type]
                    info_dict = {column_name: info for column_name, info in zip(anime_dataset_columns, all_info_list)}
                    self.df_ = self.df_.append(info_dict, ignore_index=True)

                else:
                    continue

            # get the time elapsed and print the number of requests per second
            time_elapsed = time() - start_time
            print('processed {0:.3f} requests/s'.format(num_request/time_elapsed))

            # print the number of pages processed
            print('{}/{} pages processed'.format(page_num, tot_page_num))

            # break the while loop if the specified number of pages has reached
            if page_num == tot_page_num:
                print('terminated because total page specified reached')
                break

            # request the next page and break if it failed, meaning the scraper has reached the maximum possible
            # number of pages
            try: 
                next_code = soup.find('a', class_='link-blue-box next')
                source = requests.get(start_site_string + next_code['href']).text
                soup = BeautifulSoup(source, 'lxml')

            except TypeError: 
                print('terminated because no more pages can be accessed from the website')
                break

            # update the number of requests and pause for number of seconds specified
            num_request += 1
            sleep(pause_sec)

            # clear output
            if is_clear_output:
                clear_output(wait=True)

            # update the page number
            page_num += 1

    def save_to_file(self, path):
    	'''
    	Method to save the resulting pandas dataframe to file

    	Arguments:
    	path: path to where the dataframe will be saved
    	'''

    	self.df_.to_csv(path)
            
class DataCleaning(object):
	'''
	Methods to do data cleaning

	replace_drop_na_val: replace the -500 values with np.nan and drop them
	replace_months: replace the text month names with numeric values
	missing_val_examine: examine the columns for missing values
	'''
    
    def __init__(self, df):
        self.df_ = df
        
    def replace_drop_na_val(self):
    	'''replace the -500 values with np.nan and drop them'''

        self.df_.replace(-500, np.nan, inplace=True)
        self.df_.dropna(inplace=True)
        
    def replace_months(self, replace_dict):
    	'''
    	replace the text month names with numeric values

    	Arguments:
    	replace_dict: dict specify how the months values will be replaced
    	'''

        self.df_['season_start'] = self.df_.season_start.apply(lambda x: replace_dict.get(x))
        self.df_['season_end'] = self.df_.season_end.apply(lambda x: replace_dict.get(x))
        
    def missing_val_examine(self):
        '''
        examine the columns for missing values

        Returns: pandas series displaying each column and the number of missing values it has
        '''

        return self.df_.isna().apply('sum', axis=0)
        
class DataExamine(object):
	'''
	Methods to do some exploratory data analysis

	box_plot: Method to plot boxplots of the numeric columns
	score_pop_scatter_plot: Method to plot a scatter plot of score vs popularity
	bar_plot: Method to plot barplots of number of animes release vs months
	score_pop_ratio_examine: Method to further examine the relationship between score and popularity
	anime_type_over_time_plot: Method to plot various characteristics over time
	'''
    
    def __init__(self, df):
        self.df_ = df
    
    def box_plot(self, style='fivethirtyeight'):
    	'''
    	Method to plot boxplots of the numeric columns

    	Arguments:
    	style: style in which the plot will be created
    	'''
        
        plt.style.use('fivethirtyeight')

        fig, ax = plt.subplots(1, 3, figsize=(17,9))

        ax[0].boxplot(self.df_.score)
        ax[0].set_title('Boxplot for Score')

        ax[1].boxplot(self.df_.popularity)
        ax[1].set_title('Boxplot for Popularity')

        ax[2].boxplot(self.df_.num_episodes)
        ax[2].set_title('Boxplot for Episodes')
        plt.show()
        
    def score_pop_scatter_plot(self, style='fivethirtyeight'):
    	'''Method to plot a scatter plot of score vs popularity'''
        
        plt.style.use('fivethirtyeight')
        
        # plot a scatterplot of score vs popularity. Since they are in different scale, log scale for popularity is used. 
        ax = self.df_.plot.scatter('popularity', 'score', figsize=(11,9), logx=True, alpha=0.7)
        ax.set_title('Score vs Popularity Scatterplot')
        plt.show()
        
    def bar_plot(self, style='fivethirtyeight'):
    	'''Method to plot barplots of number of animes release vs months'''
        
        plt.style.use('fivethirtyeight')
        
        year_start_cat = self.df_.year_start.apply(lambda x: 'before 2000' if x <=2000 else 'after 2000')
        year_end_cat = self.df_.year_end.apply(lambda x: 'before 2000' if x <=2000 else 'after 2000')
        
        fig, ax = plt.subplots(2, 2, figsize=(13,13))

        sns.countplot(x=self.df_.season_start, ax=ax[0][0])
        ax[0][0].set(title='Month When Animes Start')

        sns.countplot(x=self.df_.season_end, ax=ax[0][1])
        ax[0][1].set(title='Month When Animes End')

        sns.countplot(x=self.df_.season_start, hue=year_start_cat, ax=ax[1][0])
        ax[1][0].set(title='Month When Animes Start')

        sns.countplot(x=self.df_.season_end, hue=year_end_cat, ax=ax[1][1])
        ax[1][1].set(title='Month When Animes End')
        ax[1][1].get_legend().remove()

        plt.show()


    def score_pop_ratio_examine(self, lower_threshold=8, upper_threshold=8.5, rows_showed=10, is_head=True):
    	'''
    	Method to further examine the relationship between score and popularity

    	Arguments:
    	lower_threshold: the score threshold under which animes which have lowest score pop ratios will be examined
    	upper_threshold: the score threshold above which animes which have highest score pop ratios will be examined
    	rows_showed: number of rows to show
    	is_head: True to examine the animes with lowest score popularity ratio and False otherwise

    	Returns: pandas dataframe that display animes that have high score pop disparity or low
    	'''

        self.df_['score_popularity_ratio'] = self.df_.score / self.df_.popularity

        if is_head:
            return self.df_[self.df_.score < lower_threshold].sort_values(by='score_popularity_ratio').head(rows_showed)

        else:
            return self.df_[self.df_.score > upper_threshold].sort_values(by='score_popularity_ratio').tail(rows_showed)
        
    def anime_type_over_time_plot(self):
    	'''Method to plot various characteristics over time'''

        year_TV_count = self.df_[self.df_.anime_type=='TV'].groupby(self.df_.year_start).count().drop([2019])
        year_Movie_count = self.df_[self.df_.anime_type=='Movie'].groupby(self.df_.year_start).count().drop([2019])
        year_OVA_count = self.df_[self.df_.anime_type=='OVA'].groupby(self.df_.year_start).count().drop([2019])

        year_TV_score_mean = self.df_[self.df_.anime_type=='TV'].groupby(self.df_.year_start).score.mean().drop([2019])
        year_Movie_score_mean = self.df_[self.df_.anime_type=='Movie'].groupby(self.df_.year_start).score.mean().drop([2019])
        year_OVA_score_mean = self.df_[self.df_.anime_type=='OVA'].groupby(self.df_.year_start).score.mean().drop([2019])

        year_TV_ep_mean = self.df_[self.df_.anime_type=='TV'].groupby(self.df_.year_start).num_episodes.mean().drop([2019])

        year_TV_pop_mean = self.df_[self.df_.anime_type=='TV'].groupby(self.df_.year_start).popularity.mean().drop([2019])
        year_Movie_pop_mean = self.df_[self.df_.anime_type=='Movie'].groupby(self.df_.year_start).popularity.mean().drop([2019])
        year_OVA_pop_mean = self.df_[self.df_.anime_type=='OVA'].groupby(self.df_.year_start).popularity.mean().drop([2019])

        fig, ax = plt.subplots(2, 2, figsize=(13, 13))

        ax[0][0].plot(year_TV_count, color='blue')
        ax[0][0].plot(year_Movie_count, color='green')
        ax[0][0].plot(year_OVA_count, color='red')
        ax[0][0].legend(['TV', 'Movie', 'OVA'], loc='upper left')
        ax[0][0].set_title('Count of Animes Over Time')
        ax[0][0].get_legend().remove()

        ax[0][1].plot(year_TV_score_mean, color='blue')
        ax[0][1].plot(year_Movie_score_mean, color='green')
        ax[0][1].plot(year_OVA_score_mean, color='red')
        ax[0][1].legend(['TV', 'Movie', 'OVA'], loc='upper left')
        ax[0][1].set_title('Mean Anime Score Over Time')

        ax[1][0].plot(year_TV_ep_mean)
        ax[1][0].set_title('Mean # of Episodes for Series Over Time')

        ax[1][1].plot(year_TV_pop_mean, color='blue')
        ax[1][1].plot(year_Movie_pop_mean, color='green')
        ax[1][1].plot(year_OVA_pop_mean, color='red')
        ax[1][1].legend(['TV', 'Movie', 'OVA'], loc='upper left')
        ax[1][1].set_title('Mean Popularity of Anime Made Over Time')
        ax[1][1].get_legend().remove()

        plt.show()
        