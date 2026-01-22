import pandas as pd

def load_data(path: str) -> pd.DataFrame:
    # Le planilha e valida formato esperado
    df = pd.read_excel(path)
    if {"id", "text"}.issubset(df.columns):
        # Dataset supervisionado ja vem com nomes padrao
        df = df.rename(columns={"id": "id", "text": "text"})
    else:
        required_cols = {"ID", "Texto Mascarado"}
        missing = required_cols.difference(df.columns)
        if missing:
            missing_list = ", ".join(sorted(missing))
            raise ValueError(
                "Colunas obrigatorias ausentes: "
                f"{missing_list}. Esperado: ID e Texto Mascarado, "
                "ou id e text."
            )
        # Dataset do edital precisa ser renomeado
        df = df.rename(columns={"Texto Mascarado": "text", "ID": "id"})

    base_cols = ["id", "text"]
    if "label" in df.columns:
        # Preserva rótulo se existir
        base_cols.append("label")
    df = df[base_cols]
    # Normaliza texto
    df["text"] = df["text"].astype(str).str.strip()
    return df
