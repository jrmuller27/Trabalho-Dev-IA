# src/main.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import pandas as pd
import numpy as np

# --- 1. Inicialização e Carregamento do Modelo e Dados ---
app = FastAPI(
    title="Sistema de Recomendação de Filmes",
    description="API que fornece recomendações usando Filtragem Colaborativa Baseada em Item do MovieLens 100K, com endpoints de Usuário e CRUD simulado.",
    version="1.0.0"
)

# Carregamento dos artefatos de Machine Learning e Dados para Lógica de Usuário
try:
    # 1. Carregamento dos Modelos e Matriz
    KNN_MODEL = joblib.load('models/knn_model.pkl')
    MOVIE_MATRIX = joblib.load('models/movie_matrix.pkl')

    # 2. Carregamento e Merge do DataFrame Completo (necessário para a lógica de usuário)
    # Garante que os arquivos u.data e u.item estejam na pasta 'data/'
    
    # Colunas para u.data (ratings)
    df_ratings = pd.read_csv('data/u.data', sep='\t', names=['user_id', 'item_id', 'rating', 'timestamp'])
    
    # Colunas para u.item (títulos) - Apenas item_id e title são necessários
    i_cols = ['item_id', 'title'] + [str(i) for i in range(22)]
    df_items = pd.read_csv(
        'data/u.item', 
        sep='|', 
        encoding='latin-1', 
        names=i_cols,
        usecols=[0, 1]
    )

    # DataFrame completo (ratings + títulos)
    DF_FULL = pd.merge(df_ratings, df_items, on='item_id')

except FileNotFoundError as e:
    raise FileNotFoundError(f"Erro Crítico: Arquivo necessário não encontrado. Certifique-se de que os modelos estão em 'models/' e os dados em 'data/'. Detalhe: {e}")

# --- 2. Definição do Esquema de Dados (Pydantic) ---

# Define a estrutura de dados que a API vai retornar para cada recomendação
class Recommendation(BaseModel):
    title: str
    similarity_score: float

# Esquemas para os endpoints de CRUD/Atualização (Requisito do Professor)
class NewRating(BaseModel):
    user_id: int
    item_id: int # Usar item_id (do dataset)
    rating: float # Nota de 1.0 a 5.0

class NewUser(BaseModel):
    user_id: int
    occupation: str

class NewItem(BaseModel):
    item_id: int
    title: str
    
# --- 3. Função Core (Lógica de Recomendação Item-Based) ---

# A função generate_recommendations original (Item-Based) foi modificada para aceitar argumentos de modelo/matriz
# para que possa ser usada dentro da lógica de recomendação por usuário
def generate_recommendations(movie_title: str, k: int = 10):
    """Gera K recomendações para o título de filme fornecido, usando o modelo KNN (Item-Based)."""
    
    # 1. Tentar encontrar o índice do filme na matriz (linha)
    try:
        movie_index = MOVIE_MATRIX.index.get_loc(movie_title)
    except KeyError:
        return None # Filme não encontrado na nossa matriz
        
    # 2. Obter a linha de features do filme e remodelar para o KNN
    movie_features = MOVIE_MATRIX.loc[movie_title].values.reshape(1, -1)
    
    # 3. Encontrar os vizinhos mais próximos (k+1 para excluir o próprio filme)
    distances, indices = KNN_MODEL.kneighbors(movie_features, n_neighbors=k + 1)
    
    recommendations_list = []
    
    # 4. Formatar os resultados (começando em 1 para pular o filme de entrada)
    for i in range(1, len(distances.flatten())):
        recommended_title = MOVIE_MATRIX.index[indices.flatten()[i]]
        similarity_score = 1 - distances.flatten()[i] # Converte Distância de Cosseno em Similaridade
        
        recommendations_list.append(
            {"title": recommended_title, "similarity_score": round(similarity_score, 4)}
        )
            
    return recommendations_list

# --- 4. Nova Função Core (Lógica de Recomendação User-Based Simulado) ---

def get_user_recommendations(user_id: int, k: int = 10):
    """
    Simula a recomendação User-Based: 
    1. Encontra os 5 filmes mais bem avaliados pelo usuário.
    2. Gera recomendações Item-Based para cada um deles.
    3. Agrega os resultados e remove filmes já vistos.
    """
    
    # 1. Obter filmes avaliados pelo usuário
    movies_watched = DF_FULL[DF_FULL['user_id'] == user_id]
    
    if movies_watched.empty:
        return None # Usuário não encontrado ou não avaliou nada

    # 2. Pegar os 5 filmes com a maior nota (mais gostou)
    top_rated_movies = movies_watched.sort_values(by='rating', ascending=False)['title'].head(5)
    
    final_recommendations = {}

    # 3. Gerar Item-Based Recommendations para cada um desses top 5 filmes
    for movie_title in top_rated_movies:
        item_recs = generate_recommendations(movie_title, k=k)
        
        for rec in item_recs:
            title = rec['title']
            score = rec['similarity_score']
            
            # 4. Acumular a similaridade (dando mais peso se for recomendado por mais filmes)
            if title not in final_recommendations:
                final_recommendations[title] = score
            else:
                final_recommendations[title] += score

    # 5. Filtrar filmes que o usuário já viu
    watched_titles = set(movies_watched['title'].tolist())
    
    # 6. Ordenar e limitar o resultado
    sorted_recs = sorted(final_recommendations.items(), key=lambda item: item[1], reverse=True)
    
    output = []
    for title, score in sorted_recs:
        if title not in watched_titles:
            output.append(
                Recommendation(title=title, similarity_score=round(score, 4))
            )
            
    return output[:k]


# --- 5. Endpoints da API ---

@app.get("/")
async def home():
    """Endpoint básico para verificar se a API está de pé."""
    return {"message": "Sistema de Recomendação de Filmes (FastAPI) operacional!"}

# --- 5.1 Endpoints de Recomendação (Item-Based) ---

@app.get(
    "/recommend/item/{movie_title}", 
    response_model=list[Recommendation]
)
async def get_item_recommendations(
    movie_title: str,
    k: int = 10
):
    """
    Retorna as Top K recomendações para o título de filme fornecido (Item-Based).
    Use %20 para espaços no título (ex: /recommend/item/Toy%20Story%20(1995)).
    """
    
    movie_title = movie_title.replace('%20', ' ')
    
    recs = generate_recommendations(movie_title, k)
    
    if recs is None:
        raise HTTPException(status_code=404, detail=f"Filme '{movie_title}' não encontrado na base de dados.")
    
    # Converte o dicionário interno para o modelo Pydantic
    final_output = [Recommendation(**r) for r in recs]
    return final_output

# --- 5.2 Endpoints de Recomendação (User-Based) ---

@app.get("/recommend/user/{user_id}", response_model=list[Recommendation])
async def get_user_recs(user_id: int, k: int = 10):
    """
    Retorna recomendações para um usuário específico baseado em seus filmes mais bem avaliados (Simulado User-Based).
    IDs de usuário válidos vão de 1 a 943 no MovieLens 100K.
    """
    
    recs = get_user_recommendations(user_id, k)
    
    if not recs:
        raise HTTPException(status_code=404, detail=f"Usuário {user_id} não encontrado ou sem avaliações suficientes.")
    
    return recs

# --- 5.3 Endpoints de CRUD Simulado (Requisito do Professor) ---

@app.put("/user/preferences")
async def update_preferences(new_rating: NewRating):
    """
    Simula a atualização das preferências de um usuário (adição de nova avaliação).
    Requisito do professor: 'Atualizar as preferências de um usuário'.
    """
    # Na vida real, esta função acionaria o retreinamento ou a escrita em um DB.
    print(f"SIMULAÇÃO: Usuário {new_rating.user_id} avaliou item {new_rating.item_id} com {new_rating.rating}")
    return {"message": "Preferência atualizada com sucesso (Simulação).", "user_id": new_rating.user_id, "rating": new_rating.rating}

@app.post("/user/add")
async def add_new_user(user: NewUser):
    """
    Simula a adição de um novo usuário ao sistema.
    Requisito do professor: 'Adicionar novos usuários'.
    """
    # Apenas logamos a informação
    print(f"SIMULAÇÃO: Novo usuário adicionado: ID {user.user_id}, Ocupação: {user.occupation}")
    return {"message": "Novo usuário adicionado (Simulação).", "user_id": user.user_id}

@app.post("/item/add")
async def add_new_item(item: NewItem):
    """
    Simula a adição de um novo item (filme) ao catálogo.
    Requisito do professor: 'Adicionar novos itens'.
    """
    # Apenas logamos a informação
    print(f"SIMULAÇÃO: Novo item adicionado: ID {item.item_id} - {item.title}")
    return {"message": "Novo item adicionado (Simulação).", "item_id": item.item_id, "title": item.title}