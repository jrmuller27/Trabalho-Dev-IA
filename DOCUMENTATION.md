**DOCUMENTAÇÃO: Configurar e Executar a Aplicação de Recomendação de Filmes**

Versão: 1.0
Data: 2025-11-30

Sumário
- Introdução
- Arquitetura do Projeto
- Dados e Pré-processamento
- Descrição do Modelo de Recomendação
- Decisões de Design
- Artefatos Salvos
- Como Executar Localmente (venv)
- Como Executar com Docker
- Como Testar a API
- Como Re-treinar / Reproduzir o Modelo
- Troubleshooting & FAQs
- Conversão para PDF

---

Introdução
=========

Esta documentação descreve como configurar, executar e entender a aplicação "Sistema de Recomendação de Filmes" incluída neste repositório. A aplicação fornece recomendações a partir do dataset MovieLens 100K e entrega uma API FastAPI com endpoints item-based e user-based (simulado).

Arquitetura do Projeto
======================

Estrutura relevante de arquivos:

- `src/main.py` - API FastAPI e lógica de recomendação.
- `models/` - artefatos treinados (ex.: `knn_model.pkl`, `movie_matrix.pkl`).
- `data/` - arquivos do MovieLens 100K (`u.data`, `u.item`, etc.).
- `Dockerfile` - imagem para executar a API via Docker.
- `README_DOCKER.md` - instruções focadas em Docker e WSL.
- `DOCUMENTATION.md` - este arquivo.

Dados e Pré-processamento
=========================

Fonte: MovieLens 100K (arquivos `data/u.data` e `data/u.item` incluídos).

- `u.data`: contém avaliações no formato `user_id\titem_id\trating\ttimestamp`.
- `u.item`: contém metadados dos filmes; usamos `item_id` e `title`.

Pré-processamento realizado (atuação no código):

- Carregamento dos ratings em `df_ratings`.
- Carregamento dos títulos em `df_items` (encoding `latin-1`).
- Merge para formar `DF_FULL` (ratings + título) usado para informações do usuário.
- A matriz `MOVIE_MATRIX` (índice = título do filme) contém features por filme utilizadas no KNN (pré-computada durante o treinamento).

Descrição do Modelo de Recomendação
==================================

Resumo técnico:

- Tipo: Filtragem Colaborativa baseada em item (Item-Based Collaborative Filtering).
- Implementação: `scikit-learn` KNN (NearestNeighbors) aplicado sobre uma representação vetorial de filmes. O arquivo `models/knn_model.pkl` contém o modelo KNN treinado; `models/movie_matrix.pkl` contém a matriz de características indexada por título.
- Similaridade: o sistema usa distância (provavelmente distância de cosseno) retornada pelo KNN; o código converte distância em similaridade fazendo `similarity = 1 - distance`.

Fluxo de recomendação (Item-Based)

1. O cliente solicita recomendações para um título (ex: `/recommend/item/Toy%20Story%20(1995)`).
2. A API localiza o índice do filme em `MOVIE_MATRIX`.
3. O KNN consulta os `k` vizinhos mais próximos do vetor do filme de entrada.
4. O resultado é retornado com um `similarity_score` (0..1)

User-Based (simulado)
----------------------

Além do endpoint item-based, há um endpoint `GET /recommend/user/{user_id}` que implementa uma estratégia simples:

1. Busca os filmes mais bem avaliados pelo usuário (top 5).
2. Para cada um, gera recomendações item-based.
3. Agrega as recomendações (soma das similaridades) e remove filmes já vistos.
4. Retorna as top-K recomendações agregadas.

Esta abordagem é de fácil implementação e funciona bem como um proxy rápido de User-Based sem treinar um modelo user-based separado.

Decisões de Design
===================

Motivações e trade-offs:

- Escolha Item-Based (KNN) em vez de matrix factorization ou modelos mais complexos: 
  - Racional: interpretable, rápido para gerar recomendações em datasets menores (MovieLens 100K), e permite reuso imediato com vetores de conteúdo/atributos.
  - Trade-off: KNN não escala tão bem para datasets muito grandes sem indexação especializada (ex: FAISS) e pode ter performance inferior a factorization em alguns cenários.

- Pré-computar `MOVIE_MATRIX` e treinar `KNN_MODEL` offline:
  - Racional: tempo de resposta menor no serviço; evita treinar/inicializar o KNN em tempo de execução.
  - Trade-off: precisa re-treinar/atualizar artefatos se novos dados chegarem.

- Simulação de operações CRUD (adicionar usuário/item, atualizar preferências):
  - Racional: requisitos acadêmicos exigiam endpoints; a implementação atual apenas registra/printa a ação em vez de persistir em DB.
  - Caminho real: conectar a um banco (Postgres, Redis) e acionar pipelines de retreinamento/incremental.

- API com FastAPI e Pydantic:
  - Racional: validação automática, geração de OpenAPI e docs (`/docs`) convenientemente disponíveis.

Escalabilidade e produção (considerações):

- Para produção em escala, considerar:
  - Substituir KNN local por serviço de indexação (FAISS, Annoy) para latência menor e grande escalabilidade.
  - Armazenar artefatos em um object storage e carregar em memória no bootstrap do serviço.
  - Cache de recomendações populares e uso de Redis para respostas frequentes.

Artefatos Salvos
================

- `models/knn_model.pkl` - modelo KNN treinado com `scikit-learn`.
- `models/movie_matrix.pkl` - pandas DataFrame (index = título) com features por filme.

Como Executar Localmente (venv)
===============================

1) Criar e ativar venv (Windows PowerShell):

```powershell
# No diretório do projeto
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2) Rodar a API localmente (modo desenvolvimento):

```powershell
# Assegure que 'models/' e 'data/' estão presentes
python -m src.main
# ou usar uvicorn se preferir (com venv ativado):
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

3) Testar endpoints (PowerShell):

```powershell
Invoke-RestMethod -Uri http://localhost:8000
Invoke-RestMethod -Uri "http://localhost:8000/recommend/item/Toy%20Story%20(1995)?k=5"
Invoke-RestMethod -Uri "http://localhost:8000/recommend/user/1?k=10"
```

Como Executar com Docker
========================

Consulte `README_DOCKER.md` para passos detalhados. Resumo rápido:

```powershell
# Build
docker build -t trabalho01_api:latest .

# Run
docker run -d --name trabalho01_api -p 8000:8000 trabalho01_api:latest

# Logs
docker logs -f trabalho01_api
```

Como Testar a API (endpoints & exemplos)
=======================================

- Rota raiz: `GET /` — retorna mensagem de status.
- Item-Based: `GET /recommend/item/{movie_title}?k=10` — retorna lista de objetos `{title, similarity_score}`.
- User-Based (simulado): `GET /recommend/user/{user_id}?k=10`.
- CRUD simulados: `PUT /user/preferences`, `POST /user/add`, `POST /item/add` — todos retornam mensagens de simulação.

Exemplo com curl/PowerShell:

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/recommend/item/Toy%20Story%20(1995)?k=5"
Start-Process "http://localhost:8000/docs"
```

Como Re-treinar / Reproduzir o Modelo
=====================================

Um roteiro mínimo para reproduzir os artefatos (assumindo o processamento de features já conhecido):

1. Carregar ratings e itens (`data/u.data`, `data/u.item`).
2. Criar representação de filmes (ex.: matriz TF-IDF de gêneros ou features derivadas de ratings agregados — a forma exata usada para `MOVIE_MATRIX` não está em um script neste repositório, portanto você pode reproduzir um pipeline simples):

```python
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors
import joblib

# Exemplo simplificado (agrupando gêneros se existirem como texto)
df_items = pd.read_csv('data/u.item', sep='|', encoding='latin-1', names=[...])
# Montar um campo de texto e vectorizar
vectorizer = TfidfVectorizer()
movie_matrix = pd.DataFrame(vectorizer.fit_transform(df_items['genre_text']).toarray(), index=df_items['title'])

# Treinar KNN
knn = NearestNeighbors(metric='cosine')
knn.fit(movie_matrix.values)

# Salvar
joblib.dump(knn, 'models/knn_model.pkl')
joblib.dump(movie_matrix, 'models/movie_matrix.pkl')
```

Observação: o pipeline real pode usar agregações de ratings, normalizações e engenharia de features; o código principal supõe que `movie_matrix` e `knn_model` já existem.

Troubleshooting & FAQs
======================

- Erro: `Docker Desktop is unable to start` — ver `README_DOCKER.md` (WSL2 Integration). Logs mostram `wslUpdateRequired` se WSL2 não estiver ativo.
- Erro: `FileNotFoundError` ao iniciar `src.main` — verifique se `models/knn_model.pkl`, `models/movie_matrix.pkl` e os arquivos `data/*` estão presentes.
- Erro: `movie_title` não encontrado — verifique título exato; use `%20` para espaços na URL.

Conversão para PDF
==================

Opções para gerar PDF a partir deste arquivo Markdown:

1) Usando `pandoc` (recomendado):

```powershell
# Instalar pandoc (se necessário) e converter
# No Windows, baixe instalador ou use choco: choco install pandoc
pandoc DOCUMENTATION.md -o DOCUMENTATION.pdf --pdf-engine=xelatex
```

2) Usando `wkhtmltopdf` (renderiza HTML gerado a partir do Markdown):

```powershell
# Converter MD -> HTML (ex: grip, markdown-it-cli ou pandoc) e então:
wkhtmltopdf DOCUMENTATION.html DOCUMENTATION.pdf
```

3) Alternativa programática em Python (requer pacotes adicionais): `markdown` + `weasyprint` ou `pdfkit`.

Se quiser, posso tentar gerar `DOCUMENTATION.pdf` aqui automaticamente. Preciso de autorização para instalar/usar `pandoc` ou pacotes Python (posso tentar uma conversão simples, mas pode falhar se o ambiente não tiver as dependências). Diga se quer que eu tente agora.

---

FIM
