import duckdb
import pandas as pd
from pathlib import Path
from datetime import datetime
import logging

# ------------------- Config Logging -------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# ------------------- Paths -------------------
BASE_DIR = Path(__file__).parent.parent / "data"

SILVER_PATH = BASE_DIR / "silver"
GOLD_PATH = BASE_DIR / "gold"
GOLD_PATH.mkdir(parents=True, exist_ok=True)

DUCKDB_PATH = GOLD_PATH / "cars_analytics.duckdb"
PARQUET_PATH = GOLD_PATH / "cars_gold.parquet"

# ------------------- Funções -------------------

def load_silver_data() -> pd.DataFrame:
    """Lê todos os CSVs da Silver e concatena em um DataFrame único."""
    files = list(SILVER_PATH.glob("*.csv"))
    if not files:
        logging.warning("Nenhum arquivo Silver encontrado!")
        return pd.DataFrame()
    
    df_list = [pd.read_csv(f) for f in files]
    df = pd.concat(df_list, ignore_index=True)
    logging.info(f"Dados Silver carregados: {len(df)} linhas")
    return df

def save_to_duckdb_and_parquet(df: pd.DataFrame):
    """Salva dados raw e Gold agregados no DuckDB e exporta Parquet para Gold."""
    
    con = duckdb.connect(DUCKDB_PATH)
    
    # ------------------ Raw ------------------
    con.execute("DROP TABLE IF EXISTS cars_raw")
    con.execute("CREATE TABLE cars_raw AS SELECT * FROM df")
    logging.info("Tabela cars_raw criada no DuckDB")

    # ------------------ Gold ------------------
    con.execute("""
    DROP TABLE IF EXISTS cars_gold;
    CREATE TABLE cars_gold AS
    SELECT
        marca,
        modelo,
        versao,
        estado,
        COUNT(*) AS total_carros,
        AVG(novo_preco) AS preco_medio,
        AVG(km) AS km_medio,
        SUM(CASE WHEN preco_antigo > novo_preco THEN 1 ELSE 0 END) AS total_carros_promocao
    FROM cars_raw
    GROUP BY marca, modelo, versao, estado
    """)
    logging.info("Tabela cars_gold criada no DuckDB com agregações")

    # Exporta Gold para Parquet
    con.execute(f"COPY cars_gold TO '{PARQUET_PATH}' (FORMAT PARQUET)")
    logging.info(f"Arquivo Gold exportado para Parquet: {PARQUET_PATH}")

    con.close()
    logging.info(f"Banco DuckDB salvo em: {DUCKDB_PATH}")

