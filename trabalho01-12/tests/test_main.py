# tests/test_main.py
# tests/test_main.py

import sys
import os

# Adiciona explicitamente o caminho da pasta raiz do projeto (FACUL/)
# Isso permite que o Python encontre 'src.main' a partir de 'tests/'
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
from httpx import AsyncClient
from src.main import app 

# O AsyncClient permite simular requisições HTTP para a sua API sem rodar o uvicorn separadamente.

# ----------------------------------------
# 1. TESTES DE RECOMENDAÇÃO (GET)
# ----------------------------------------

@pytest.mark.asyncio
async def test_home_endpoint():
    """Testa se o endpoint raiz está operacional."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/")
    assert response.status_code == 200
    assert "operacional" in response.json()["message"]

@pytest.mark.asyncio
async def test_recommendation_item_success():
    """Testa se o endpoint Item-Based retorna a estrutura correta."""
    # Usando um filme conhecido no MovieLens 100K
    test_movie = "Toy Story (1995)"
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get(f"/recommend/item/{test_movie}")
    
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0
    assert "title" in response.json()[0]
    assert "similarity_score" in response.json()[0]

@pytest.mark.asyncio
async def test_recommendation_item_not_found():
    """Testa se o endpoint Item-Based retorna 404 para filme inexistente."""
    test_movie = "Filme Inexistente (9999)"
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get(f"/recommend/item/{test_movie}")
    
    assert response.status_code == 404
    assert "não encontrado" in response.json()["detail"]

@pytest.mark.asyncio
async def test_recommendation_user_success():
    """Testa se o endpoint User-Based retorna recomendações para um usuário válido (e.g., ID 1)."""
    # Usuário ID 1 é um usuário ativo no MovieLens 100K
    test_user_id = 1 
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get(f"/recommend/user/{test_user_id}")
    
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0
    assert "title" in response.json()[0]

# ----------------------------------------
# 2. TESTES DE CRUD SIMULADO (POST/PUT)
# ----------------------------------------

@pytest.mark.asyncio
async def test_update_preferences_put():
    """Testa o endpoint de atualização de preferências (PUT)."""
    payload = {"user_id": 9999, "item_id": 100, "rating": 5.0}
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.put("/user/preferences", json=payload)
    
    assert response.status_code == 200
    assert "Simulação" in response.json()["message"]

@pytest.mark.asyncio
async def test_add_new_user_post():
    """Testa o endpoint de adição de novo usuário (POST)."""
    payload = {"user_id": 9999, "occupation": "Data Scientist"}
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/user/add", json=payload)
    
    assert response.status_code == 200
    assert "adicionado" in response.json()["message"]