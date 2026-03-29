import pandas as pd
from pathlib import Path
import json
from datetime import datetime
import logging

# ------------------- Config Logging -------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# ------------------- Paths -------------------
BASE_DIR = Path(__file__).parent.parent / "data"
BRONZE_PATH = BASE_DIR / "bronze"
SILVER_PATH = BASE_DIR / "silver"
SILVER_PATH.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = SILVER_PATH / f"cars_silver_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

# Mapeamento de renomeação
rename_map = {
    "version": "versao",
    "old_price": "preco_antigo",
    "new_price": "novo_preco"
}

# ------------------- Funções -------------------

def clean_price(df, col) -> pd.DataFrame:
    """Limpa coluna de preços: remove 'R$', pontos e converte para float."""
    df[col] = df[col].fillna("")
    df[col] = df[col].str.replace(r"[R$\.\*]", "", regex=True)
    df[col] = df[col].str.replace(",", ".")
    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)
    logging.info(f"Coluna {col} limpa e convertida para float")
    return df

def parse_parcela(df, col="parcela") -> pd.DataFrame:
    """Extrai apenas o valor numérico da parcela e converte para float."""
    df[col] = df[col].str.extract(r"(\d+)")  
    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)
    logging.info(f"Coluna {col} tratada com sucesso")
    return df

def parse_details(df, col="details") -> pd.DataFrame:
    """Extrai ano_modelo, km, cidade e estado da coluna 'details'."""
    parts = df[col].str.split("•", expand=True)
    df["ano_modelo"] = parts[0].str.replace("Ano/Modelo", "").str.strip()
    df["km"] = parts[1].str.replace(r"[^\d]", "", regex=True).astype(float)
    cidade_estado = parts[2].str.strip().str.rsplit(",", n=1, expand=True)
    df["cidade"] = cidade_estado[0].str.strip()
    df["estado"] = cidade_estado[1].str.strip()
    logging.info("Coluna details parseada em ano_modelo, km, cidade e estado")
    return df

def parse_title(df, col="title") -> pd.DataFrame:
    """Separa a coluna 'title' em 'marca' e 'modelo'."""
    parts = df[col].str.split(n=1, expand=True)
    df["marca"] = parts[0]
    df["modelo"] = parts[1]
    logging.info("Coluna title parseada em marca e modelo")
    return df

def rename_columns(df: pd.DataFrame, colunas: dict) -> pd.DataFrame:
    """Renomeia colunas do DataFrame com base em um dicionário."""
    logging.info("Renomeando colunas restantes")
    return df.rename(columns=colunas)

# Ordem final das colunas
col_order = [
    "id",
    "marca",
    "modelo",
    "versao",
    "ano_modelo",
    "km",
    "preco_antigo",
    "novo_preco",
    "parcela",
    "cidade",
    "estado",
    "link",
    "data_extracao"
]


def data_transformation() -> pd.DataFrame:
    """Lê todos os JSONs da pasta bronze, limpa, transforma e evita duplicados na Silver."""
    
    # 1️⃣ Lê arquivos da Bronze
    all_files = list(BRONZE_PATH.glob("*.json"))
    df_list = []
    for file in all_files:
        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)
        df_list.append(pd.DataFrame(data))
    
    if not df_list:
        logging.info("Nenhum arquivo bronze encontrado")
        return pd.DataFrame(columns=col_order)
    
    df = pd.concat(df_list, ignore_index=True)
    
    # Adiciona ID temporário
    df["id"] = range(1, len(df)+1)
    
    # 2️⃣ Limpeza e parsing
    df = clean_price(df, "old_price")
    df = clean_price(df, "new_price")
    df = parse_parcela(df, "parcela")
    df = parse_details(df, "details")
    df = df.drop(columns=["details"])
    df = parse_title(df, "title")
    df["data_extracao"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    df = rename_columns(df, rename_map)
    
    # 3️⃣ Evita duplicados com Silver existente
    existing_links = set()
    silver_files = list(SILVER_PATH.glob("*.csv"))
    for f in silver_files:
        existing_links.update(pd.read_csv(f, usecols=["link"])["link"].tolist())
    
    df = df[~df["link"].isin(existing_links)]
    
    # 4️⃣ Reordena colunas
    df = df[col_order]
    logging.info(f"Transformações concluídas, {len(df)} novos carros a salvar")
    
    return df



def save_transform_data():
    """Salva os dados transformados na pasta silver"""
    df = data_transformation()
    df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")
    print(f"Silver salvo em: {OUTPUT_FILE}")




