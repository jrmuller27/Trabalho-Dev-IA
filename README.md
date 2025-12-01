# 🎬 Sistema de Recomendação de Filmes - MovieLens

Este repositório contém a implementação de um sistema de recomendação de filmes baseado em **Filtragem Colaborativa**. O projeto foi desenvolvido como parte da disciplina de Ciência de Dados / Inteligência Artificial, focando em práticas de **MLOps** (Machine Learning Operations) utilizando **FastAPI** para a interface de aplicação e **Docker** para containerização.

## 👨‍💻 Integrantes do Grupo

* **Douglas Soeiro**
* **Rodrigo Lins**
* **Vitor Nascimento**
* **José Muller**
* **Matheus Alves**

---

## 🎯 Objetivo do Projeto

O objetivo principal é entregar uma API funcional capaz de recomendar filmes com base na similaridade entre itens e no histórico de usuários, garantindo portabilidade e reprodutibilidade através de containers.

O sistema foi projetado para:
1.  Processar o dataset **MovieLens 100K**.
2.  Treinar um modelo de Machine Learning (KNN).
3.  Disponibilizar endpoints de recomendação via API RESTful.
4.  Garantir a execução em qualquer ambiente via Docker.

---

## 🛠️ Stack Tecnológica

* **Linguagem:** Python 3.10+
* **API Framework:** FastAPI
* **Servidor:** Uvicorn
* **Machine Learning:** Scikit-Learn (NearestNeighbors), Pandas, NumPy
* **Containerização:** Docker
* **Testes:** Pytest, HTTPX

---

## 🏗️ Arquitetura e Estrutura

O projeto segue uma estrutura modular para facilitar a manutenção e os testes:

<img width="3612" height="1880" alt="cmd-3" src="https://github.com/user-attachments/assets/0485bc36-3de3-48fa-ac24-c2793d197abe" />

---

## 🤖 Modelo de Recomendação e Decisões de Design

1. 📌 Filtragem Colaborativa Baseada em Itens (Item-Based)
Utilizamos o algoritmo K-Nearest Neighbors (KNN) para calcular a similaridade entre filmes.

Por quê?

Em sistemas de recomendação de filmes, os usuários tendem a gostar de obras similares às que já avaliaram positivamente.
A abordagem Item-Item apresenta vantagens importantes:

* **Mais estável em datasets esparsos (como o MovieLens 100K)**
* **Mais eficiente na inferência do que User-User**
* **Evita problemas de usuários com poucas avaliações**


---


2. 🎯 Métrica de Similaridade: Similaridade do Cosseno.

A métrica utilizada foi a Cosine Similarity.

Por quê?

A Similaridade de Cosseno:

* **É amplamente usada em sistemas de recomendação**
* **Funciona muito bem com matrizes esparsas**
* **Ignora a magnitude das notas e foca na orientação dos vetores**
* **Favorece recomendações baseadas em padrões de gosto, e não na nota absoluta**
  
---


3. 📦 Persistência do Modelo (.pkl)

O script `01_treinamento.py` processa os dados, treina o modelo e salva os artefatos em models/ usando joblib.

A API carrega o modelo apenas uma vez na inicialização.

Isso garante:

* **Baixa latência nas requisições**
* **Alta reprodutibilidade**
* **Menos carga computacional durante a execução**

---


## 🚀 Guia de Instalação e Execução

🔹Execução via Docker

1. Construir a imagem:

<img width="544" height="125" alt="cmd-4" src="https://github.com/user-attachments/assets/f02a032f-fd8e-4dfb-99a2-c04e9740a623" />

2. Rodar o container:
<img width="544" height="125" alt="cmd-5" src="https://github.com/user-attachments/assets/ac0e347a-74c0-47cf-9109-5083122e495d" />

A API estará disponível em: http://localhost:8000


---

## 🔌 Documentação da API (Endpoints)


## Resumo das Rotas
<img width="687" height="458" alt="ChatGPT Image 30 de nov  de 2025, 20_29_46" src="https://github.com/user-attachments/assets/f01d8cde-c802-4f1b-a680-3f6352f5e414" />


---




## 🧪 Testes Automatizados

O projeto inclui uma suíte de testes de integração para garantir a robustez da aplicação. 

<img width="544" height="125" alt="cmd-6" src="https://github.com/user-attachments/assets/f86c0b7c-0d78-487b-a85d-663a94e115d4" />
