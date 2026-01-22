from io import BytesIO
from pathlib import Path

import pandas as pd

from src.rules import label_and_weight


def main():
    cases = pd.read_csv("data/casos_dificeis.csv")
    preds = [label_and_weight(t)[0] for t in cases["text"]]
    cases["label_pred"] = preds
    acc = (cases["label_expected"] == cases["label_pred"]).mean()
    print(f"Acuracia regras em casos_dificeis: {acc:.2f}")

    mismatch = cases[cases["label_expected"] != cases["label_pred"]]
    print(f"Mismatches: {len(mismatch)}")
    if len(mismatch) > 0:
        print(mismatch[["id", "text", "label_expected", "label_pred", "notes"]].head(20))

    # Gera relatorios em reports/
    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)
    txt_path = reports_dir / "regras_casos_dificeis_relatorio.txt"
    xlsx_path = reports_dir / "regras_casos_dificeis_relatorio.xlsx"

    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(f"Acuracia regras em casos_dificeis: {acc:.2f}\n")
        f.write(f"Mismatches: {len(mismatch)}\n\n")
        f.write(cases.to_csv(index=False))

    # Salva XLSX
    cases.to_excel(xlsx_path, index=False)


if __name__ == "__main__":
    main()
