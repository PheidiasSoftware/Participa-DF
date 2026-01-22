from src.rules import label_and_weight

def apply_weak_labels(df):
    # Aplica regras e pesos de confianca para cada texto
    labels = df["text"].apply(label_and_weight)
    df["label"] = labels.apply(lambda x: x[0])
    df["weight"] = labels.apply(lambda x: x[1])
    return df
