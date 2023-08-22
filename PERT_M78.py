#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul  7 11:59:43 2022

@author: anthony
"""

import csv
import networkx as nx
import matplotlib.pyplot as plt
import datetime

def load_PERT_CSV (G, filename):
    G.clear()
    
    G.add_node('0',duration=0, early=-1, late=99999, critical = False, group = '')
    G.add_node('*',duration=0, early=-1, late=99999, critical = False, group = '')
    
    try: 
        with open(filename, newline='') as csvfile:
            reader=csv.reader(csvfile)
            next(reader)
            for row in reader:
                nodes = row[3].split(' ')
                print('got nodes = {} duration = {} group ={} neighbors ={}'.format(row[0], row[1], row[2], nodes))
    
                #ajoute le sommet lu dans la ligne
                G.add_node(row[0], duration = int(row[1]), early=-1, late=99999, critical = False, group = row[2])
                
                #ajoute les dépendances lues dans la ligne
                for node in nodes:
                    if node =='NONE':
                        G.add_edge('0',row[0])
                    else:
                        G.add_edge(node,row[0])
    except:
        return -1
    
    #pour les sommets sans successeur, les connecter au sommet fictif de fin 
    for i in G.nodes():
        if G.out_degree(i)==0 and i !='*':
            G.add_edge(i,'*')
    print(G.nodes)
    
    
    
    
        
    #Dessine le graphe
    options = {
        'node_color' : 'white',
        'node_size' : 550,
        'edge_color' : 'tab:grey',
        'with_labels': True
        }
    
    nx.draw(G,**options)
    plt.show   
    
def date_by_adding_business_days(from_date, add_days):
    business_days_to_add = add_days
    current_date = from_date
    while business_days_to_add > 0:
        current_date += datetime.timedelta(days=1)
        weekday = current_date.weekday()
        if weekday >= 5: # sunday = 6
            continue
        business_days_to_add -= 1
    return current_date
    
def dates_plus_tot (G):
    # initialise les dates au plus tôt
    for i in G.nodes():
        G.nodes[i]['early']=-1
        G.nodes[i]['cpt']=G.in_degree(i) #le champ compteur est le nombre de prédécesseur non-traité
    G.nodes['0']['early']=0
    queue=['0']
    print(G.nodes.data())
    
    #calcule les dates au plus tôt : early(i)=max
    while len(queue)>0:
        cur = queue.pop(0)
        curr_end=G.nodes[cur]['early']+G.nodes[cur]['duration']
        for i in G.successors(cur):
            G.nodes[i]['early']=max(G.nodes[i]['early'], curr_end)
            G.nodes[i]['cpt']-=1
            if G.nodes[i]['cpt']==0:
                queue.append(i)
    print(G.nodes.data())  
    
def dates_plus_tard (G):
    # initialise les dates au plus tôt
    for i in G.nodes():
        G.nodes[i]['late']=G.nodes['*']['early']
        G.nodes[i]['cpt']=G.out_degree(i) #le champ compteur est le nombre de successeur non-traité
    G.nodes['*']['late']=G.nodes['*']['early']
    queue=['*']
    print(G.nodes.data())
    
    #calcule les dates au plus tard : early(i)=max
    while len(queue)>0:
        cur = queue.pop(0)
        for i in G.predecessors(cur):
            G.nodes[i]['late']=min(G.nodes[i]['late'], G.nodes[cur]['late']-G.nodes[i]['duration'])
            G.nodes[i]['cpt']-=1
            if G.nodes[i]['cpt']==0:
                queue.append(i)
    print(G.nodes.data())

def taches_critiques (G):
    for i in G.nodes:
        if G.nodes[i]['early']==G.nodes[i]['late']:
            G.nodes[i]['critical']=True
    print(G.nodes.data())

def affiche_GANTT_jour_critique (G): #si durée en jour en commençant à une date donnée
    import plotly.express as px
    import pandas as pd
    import datetime

    import plotly.io as pio
    #pio.renderers.default = 'svg'
    pio.renderers.default = 'browser'
    
    start_date = '15/08/2022' #date de début du projet
    start_date_r = datetime.datetime.strptime(start_date, "%d/%m/%Y")

    # initialise data
    data = {'Task': [], 'Start': [], 'Finish': [], 'Critical': []}
    #print(G.nodes.data())

    # remplit data avec les infos des sommets
    for node in G.nodes(data=True) :
        if node[0] not in {'0','*'}:
            
            # cle d'accès au sommet
            key = node[0]
        
        # durée de la tâche (sommet)
            duration = G.nodes[key]['duration']
        
        # date de début au plus tôt de la tâche
            start_r = date_by_adding_business_days(start_date_r, G.nodes[key]['early'])

        # date de fin au plus tôt de la tâche
            stop_r = date_by_adding_business_days(start_r, duration)

        # update data
            data['Task'].append(key)
            data['Start'].append(start_r)
            data['Finish'].append(stop_r)
            data['Critical'].append(G.nodes[key]['critical'])
    #print(data)
    
    df = pd.DataFrame(data)
    color={True:'rgb(238,114,3)',False:'rgb(60,60,59)'}
    fig = px.timeline(df, x_start="Start", x_end="Finish", y="Task" ,color='Critical',
                      color_discrete_map=color)
    fig.update_yaxes(autorange="reversed")#,categoryorder='category ascending') # pour afficher les tâches du haut vers le bas
    fig.update_layout(
    title={
        'text': "Diagramme de GANTT",
        'y':0.95,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'})
    fig.show()
    
def affiche_GANTT_jour_groupe (G): #si durée en jour en commençant à une date donnée
    import plotly.express as px
    import pandas as pd
    import datetime

    import plotly.io as pio
    #pio.renderers.default = 'svg'
    pio.renderers.default = 'browser'
    
    start_date = '15/08/2022' #date de début du projet
    start_date_r = datetime.datetime.strptime(start_date, "%d/%m/%Y")

    # initialise data
    data = {'Task': [], 'Start': [], 'Finish': [], 'Critical': [], 'group': []}
    #print(G.nodes.data())

    # remplit data avec les infos des sommets
    for node in G.nodes(data=True) :
        if node[0] not in {'0','*'}:
            
            # cle d'accès au sommet
            key = node[0]
        
        # durée de la tâche (sommet)
            duration = G.nodes[key]['duration']
        
        # date de début au plus tôt de la tâche
            start_r = date_by_adding_business_days(start_date_r, G.nodes[key]['early'])

        # date de fin au plus tôt de la tâche
            stop_r = date_by_adding_business_days(start_r, duration)

        # update data
            data['Task'].append(key)
            data['Start'].append(start_r)
            data['Finish'].append(stop_r)
            data['Critical'].append(G.nodes[key]['critical'])
            data['group'].append(G.nodes[key]['group'])
    #print(data)
    
    df = pd.DataFrame(data)
    color={'État_de_l_art':'rgb(238,114,3)',
           'Plan_de_production':'rgb(125,161,119)',
           'Chantier_manuel': 'rgb(99,177,188)',
           'Organisation_Peak_période': 'rgb(206,184,136)',
           'Bilan_mission': 'rgb(255,203,5)'}
    fig = px.timeline(df, x_start="Start", x_end="Finish", y="Task" ,color='group',
                      color_discrete_map=color)
    fig.update_yaxes(autorange="reversed")#,categoryorder='category ascending') # pour afficher les tâches du haut vers le bas
    fig.update_layout(
    title={
        'text': "Diagramme de GANTT",
        'y':0.95,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'})
    fig.show()

if __name__ == '__main__':
    G = nx.DiGraph()
    #create_PERT(G)
    load_PERT_CSV(G, 'taches_M78_groupe.csv')
    # print(G.nodes())
    dates_plus_tot(G)
    dates_plus_tard(G)
    taches_critiques(G)
    affiche_GANTT_jour_critique(G)
    affiche_GANTT_jour_groupe(G)
    
    
    