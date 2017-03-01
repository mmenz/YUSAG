#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 24 22:28:56 2017

@author: matthewrobinson
"""
###Code to do parsing excluding the tiebreaks games

import pickle
import hashlib
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
#matplotlib notebook

import re

matches = pd.read_csv("/Users/matthewrobinson/Documents/1701/Tennis/tennis_archive_matches_ATP_no_tiebreaks.csv")
matches = matches[['pbp_id','tny_name','server1','server2','winner','pbp','score','adf_flag','wh_minutes']]

#create new dataframe to store data
game_df = pd.DataFrame(np.zeros((100000,15)),\
columns = ['match_id','server','returner','match_winner','set_winner','game_winner',\
           'pt1','pt2','pt3','pt4','pt5','pt6','deuce','ad_in','ad_out'])

#loop over matches
#for index, row in df.iterrows():
row_index = 0
for match_index in range(3800):
    
    #note in this example also need to split on '.' that denotes the end of a set
    #should check if len() = number of games played as indicated by score
    match_pbp = matches.at[match_index,'pbp']
    sets = match_pbp.split('.')
    #games = match_pbp.replace('.',';').split(';')
    
    #compute total number of games from the score
    score = matches.at[match_index,'score']
    #score = re.sub('\(\w\)',"",score) #getting rid of the tiebreak score in parens
    score = score.split(' ')

    total_games = 0

    st_games_arr = np.zeros(5) #keeps track of number of games in each set
    st_index = 0
    for st in score:
        for st_games in st.split('-'):
            total_games = total_games + float(st_games)
            st_games_arr[st_index] = st_games_arr[st_index] + float(st_games)
        st_index = st_index + 1

    st_games_arr = st_games_arr.astype(int)
    
    server1 = matches.at[match_index,'server1']
    server2 = matches.at[match_index,'server2']
    
    server1_sets = 0
    server2_sets = 0

    server1_games = 0
    server2_games = 0
    st_winner = 0

    server1_pts = 0
    server2_pts = 0

    #row_index = 0
    server1_serve = True
    st_index = 0
    st_start_game = 0
    
    
    for st in sets:
        
        games = st.split(';')
        first_row_st = row_index
        
        
        for game in games:

            pt_num = 1
            pt_column = 'pt' + str(pt_num)

            server1_pts = 0
            server2_pts = 0

            if server1_serve:
                game_df.at[row_index,'server'] = 1
                game_df.at[row_index,'returner'] = 2
            elif not(server1_serve):
                game_df.at[row_index,'server'] = 2
                game_df.at[row_index,'returner'] = 1

            server_last_pt = False #keeps track of who won last point

            for pt in game:

                if (pt == 'S' or pt == 'A'): #if server wins point or ace
                    server_last_pt = True
                    if (server1_serve): #server 1 is serving
                        server1_pts = server1_pts + 1 #need to check if game is won here maybe
                        game_df.at[row_index,pt_column] = game_df.at[row_index,pt_column] + 1 #set column to 1 because won point
                    else: #server2 is serving
                        server2_pts = server2_pts + 1
                        game_df.at[row_index,pt_column] = game_df.at[row_index,pt_column] + 1 #because won point and on serve
                else: #If the returner wins the point
                    server_last_pt = False
                    if (server1_serve):
                        server2_pts = server2_pts + 1
                        game_df.at[row_index,pt_column] = game_df.at[row_index,pt_column] - 1
                    else:
                        server1_pts = server1_pts + 1
                        game_df.at[row_index,pt_column] = game_df.at[row_index,pt_column] - 1


                #assign the right column for the next point

                if (pt_num >= 6) and (pt_num % 2 == 0):
                    pt_column = 'deuce'
                    pt_num = pt_num + 1
                elif ((pt_num >= 6) and (server_last_pt)): #this is wrong, could be less points
                    pt_column = 'ad_in'
                    pt_num = pt_num + 1
                    #print(pt_column,pt_num)
                elif ((pt_num >= 6) and (not(server_last_pt))):    
                    pt_column = 'ad_out'
                    pt_num = pt_num + 1
                    #print(pt_column, pt_num)
                else:
                    pt_num = pt_num + 1
                    pt_column = 'pt' + str(pt_num)


            #see who won the game
            if (server1_pts > server2_pts): #if server1 wins
                game_df.at[row_index,'game_winner'] = 1
                server1_games = server1_games + 1
            elif (server2_pts > server1_pts):
                game_df.at[row_index,'game_winner'] = 2
                server2_games = server2_games + 1

            server1_serve = not(server1_serve)
            row_index = row_index + 1

        #test who won the set
        if server1_games > server2_games:
            st_winner = 1
        else:
            st_winner = 2

        #fill the df with the setwinner
        game_df.loc[first_row_st : first_row_st + len(st)-1,'set_winner'] = st_winner

        #will need to fill match with match winner later
        game_df.loc[first_row_st : first_row_st + len(st)-1,'match_winner'] = matches.at[match_index,'winner']
        game_df.loc[first_row_st : first_row_st + len(st)-1,'match_id'] = matches.at[match_index,'pbp_id']

        #st_start_game = st_games_arr[st_index]
        #st_index = st_index + 1
