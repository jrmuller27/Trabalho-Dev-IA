# Trabalho-Dev-IA


## 🧠 Detalhes do Modelo e Decisões de Design

* **Técnica Principal:** Filtragem Colaborativa Baseada em Item.
* **Algoritmo Utilizado:** **K-Nearest Neighbors (KNN)** com métrica de **Similaridade de Cosseno**.
* **Decisão de Design:** Escolhemos o KNN por sua eficácia em datasets esparsos como o MovieLens e por ser leve o suficiente para ser rapidamente carregado pelo FastAPI.
* **Simulação de Usuário:** O endpoint `/recommend/user/{user_id}` simula a recomendação ao agregar as sugestões de *Item-Based* dos **5 filmes mais bem avaliados** pelo usuário.
* **CRUD/Atualização:** As rotas `POST /user/add` e `PUT /user/preferences` são **simuladas** (apenas logando a transação) para cumprir o requisito, visto que o retreinamento do modelo em tempo real ou a conexão a um banco de dados estava fora do escopo deste desenvolvimento.

 ## APOS DOCKER TIVER ONLINE E IMAGEM ON ( VERIFICAR README_DOCKER PARA MAIS INFORMAÇÕES )
 ### RODAR NO POWERSHELL DENTRO DO DIRETORIO DO PROJETO
 # rota raiz (se implementada)
Invoke-RestMethod -Uri http://localhost:8000

# documentação interativa (abrir no browser)
Start-Process "http://localhost:8000/docs"

# openapi json
Invoke-RestMethod -Uri http://localhost:8000/openapi.json
