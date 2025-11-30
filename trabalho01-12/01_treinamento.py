# 01_train.py
import pandas as pd
import joblib
from sklearn.neighbors import NearestNeighbors
import numpy as np
import os

# Garante que a pasta 'models/' exista
if not os.path.exists('models'):
    os.makedirs('models')

print("--- Iniciando o Treinamento do Modelo de Recomendação ---")

# 1. Carregar u.data (Avaliações) e u.item (Títulos)
try:
    print("1. Carregando dados do MovieLens...")
    column_names = ['user_id', 'item_id', 'rating', 'timestamp']
    df_ratings = pd.read_csv(
        'data/u.data', 
        sep='\t', 
        names=column_names
    )
    i_cols = ['item_id', 'title'] + [str(i) for i in range(22)] 
    df_items = pd.read_csv(
        'data/u.item',  
        sep='|', 
        names=i_cols, 
        encoding='latin-1', 
        usecols=[0, 1]      
    )
except FileNotFoundError:
    print("ERRO: Arquivos 'u.data' ou 'u.item' não encontrados. Verifique a pasta 'data/'.")
    exit()

df_full = pd.merge(df_ratings, df_items, on='item_id')

# 2. Criar a Matriz Item-Usuário (Pivot Table)
print("2. Criando Matriz Item-Usuário...")
movie_matrix = df_full.pivot_table(
    index='title',  
    columns='user_id', 
    values='rating'
).fillna(0)

# 3. Treinar o Modelo KNN
print("3. Treinando modelo KNN (Similaridade de Cosseno)...")
knn_model = NearestNeighbors(metric='cosine', algorithm='brute')
knn_model.fit(movie_matrix.values) 

# 4. Persistência dos Modelos
print("4. Salvando modelos para a API na pasta 'models/'...")
joblib.dump(knn_model, 'models/knn_model.pkl')
joblib.dump(movie_matrix, 'models/movie_matrix.pkl')

print("--- ✅ Treinamento concluído. Arquivos .pkl salvos com sucesso! ---")