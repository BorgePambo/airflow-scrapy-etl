# 🚗 Scrapy Analytics Pipeline

ETL completo para scraping e análise de veículos seminovos da Movida, utilizando **Airflow**, **Playwright**, **Pandas** e **DuckDB**.
<img width="1232" height="620" alt="scrapping_projeto325" src="https://github.com/user-attachments/assets/a1519788-e477-4264-861d-ee371d9ee66c" />

---

## 📋 Sobre o Projeto

Este pipeline automatiza a coleta, transformação e carga de dados de veículos seminovos do site da Movida. Os dados são processados em 3 camadas (Bronze, Silver, Gold) para garantir qualidade e facilitar análises no Power BI ou outras ferramentas.

---

## 🛠️ Tecnologias

| Tecnologia | Função |
|------------|--------|
| **Apache Airflow 3.x** | Orquestração de pipelines |
| **Playwright** | Web scraping com Chromium |
| **Pandas** | Transformação e limpeza de dados |
| **DuckDB** | Banco analítico para agregações |
| **Docker & Docker Compose** | Containerização |
| **Power BI** | Visualização e dashboards |

---

## 📊 Arquitetura do Pipeline

┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│ BRONZE │ ──→ │ SILVER │ ──→ │ GOLD │
│ (JSON) │ │ (CSV) │ │ (Parquet) │
│ Dados │ │ Dados │ │ Dados │
│ Brutos │ │ Limpos │ │ Agregados │
└─────────────┘ └─────────────┘ └─────────────┘
↑ ↑ ↑
Playwright Pandas DuckDB
Scraping Transform Analytics


---

## 🚀 Como Rodar

### Pré-requisitos
- Docker e Docker Compose instalados
- Git
- WSL 2 (se estiver no Windows)

### 1. Clone o repositório
```bash
git clone https://github.com/SEU_USER/scrapy-analytics.git
cd scrapy-analytics

2. Configure as variáveis de ambiente
docker compose up --build -d

4. Acesse o Airflow
URL: http://localhost:8080
Login: airflow / airflow

5. Execute o pipeline
Ative o DAG scrapy_analytics_pipeline
Clique em Trigger


📁 Estrutura do Projeto
scrapy-analytics/
├── docker/
│   ├── Dockerfile.airflow      # Imagem customizada com Playwright
│   ├── docker-compose.yml      # Orquestração dos containers
│   ├── dags/                   # DAGs do Airflow
│  
│   
│   
├── scripts/
│   ├── extract.py              # Scraping com Playwright
│   ├── transform.py            # Limpeza com Pandas
│   └── load.py                 # Carga com DuckDB
├── data/                       # Dados (não versionado)
│   ├── bronze/                 # JSONs brutos
│   ├── silver/                 # CSVs limpos
│   └── gold/                   # DuckDB + Parquet
├── .gitignore
└── README.md
