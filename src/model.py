from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
from sklearn.model_selection import StratifiedKFold, train_test_split


def train_and_evaluate(df):
    # Separa textos, rotulos e pesos (quando existirem)
    X = df["text"]
    y = df["label"]
    w = df["weight"] if "weight" in df.columns else None

    # Split para evitar avaliar no mesmo conjunto do treino
    stratify = y if y.nunique() > 1 else None
    if w is not None:
        X_train, X_test, y_train, y_test, w_train, w_test = train_test_split(
            X, y, w, test_size=0.2, random_state=42, stratify=stratify
        )
    else:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=stratify
        )
        w_train = None

    # Vetorizacao TF-IDF com n-gramas
    vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=2, max_df=0.9)
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)

    # Classificador linear com balanceamento de classes
    model = LogisticRegression(class_weight="balanced", max_iter=1000, random_state=42)
    if w_train is not None:
        model.fit(X_train_vec, y_train, sample_weight=w_train)
    else:
        model.fit(X_train_vec, y_train)

    # Predicao no conjunto de teste
    preds = model.predict(X_test_vec)

    # Cabecalho do relatorio
    header = "\nRelatório de Classificação (validação holdout):"

    labels = ["non_public", "public"]
    # Metricas por classe
    precision, recall, f1, support = precision_recall_fscore_support(
        y_test, preds, labels=labels, zero_division=0
    )
    acc = accuracy_score(y_test, preds)

    # Validacao cruzada configuravel
    cv_text = ""
    n_splits = 5
    min_samples = 5
    class_counts = y.value_counts()
    min_class = class_counts.min() if len(class_counts) > 0 else 0
    can_cv = y.nunique() > 1 and len(y) >= min_samples and min_class >= n_splits
    if can_cv:
        # Calcula metricas medias em 5 folds
        cv_f1 = []
        cv_acc = []
        skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)
        for train_idx, test_idx in skf.split(X, y):
            X_tr = X.iloc[train_idx]
            X_te = X.iloc[test_idx]
            y_tr = y.iloc[train_idx]
            y_te = y.iloc[test_idx]
            w_tr = w.iloc[train_idx] if w is not None else None

            # Vetorizacao e treino por fold
            vec = TfidfVectorizer(ngram_range=(1, 2), min_df=2, max_df=0.9)
            X_tr_vec = vec.fit_transform(X_tr)
            X_te_vec = vec.transform(X_te)
            clf = LogisticRegression(class_weight="balanced", max_iter=1000, random_state=42)
            if w_tr is not None:
                clf.fit(X_tr_vec, y_tr, sample_weight=w_tr)
            else:
                clf.fit(X_tr_vec, y_tr)

            # Predicao e metricas do fold
            preds_cv = clf.predict(X_te_vec)
            p_cv, r_cv, f1_cv, _ = precision_recall_fscore_support(
                y_te, preds_cv, labels=labels, zero_division=0
            )
            cv_f1.append(f1_cv[0])
            cv_acc.append(accuracy_score(y_te, preds_cv))

        cv_text = (
            f"\nValidacao cruzada ({n_splits}-fold):\n"
            f"P1 medio (F1 non_public): {sum(cv_f1) / len(cv_f1):.4f}\n"
            f"Acuracia media: {sum(cv_acc) / len(cv_acc):.4f}\n"
        )

    # Monta relatorio em texto
    col1 = 36
    report_lines = [
        header,
        f"{'classe (significado)':<{col1}}  precisão  recall  f1-score  suporte",
        f"{'non_public (contém dados pessoais)':<{col1}}  {precision[0]:.2f}      {recall[0]:.2f}        {f1[0]:.2f}        {support[0]}",
        f"{'public (não contém dados pessoais)':<{col1}}  {precision[1]:.2f}      {recall[1]:.2f}        {f1[1]:.2f}        {support[1]}",
        "",
        f"acurácia     {acc:.2f}",
    ]

    # P1 é equivalente ao F1 para a classe positiva (non_public)
    p1 = f1[0]
    p1_line = f"P1 (F1 para non_public): {p1:.4f}"
    # Junta relatorio e imprime
    report_text = "\n".join(report_lines + [p1_line, ""]) + cv_text
    print(report_text, end="")

    # Retorna texto e objetos treinados para persistencia
    return report_text, model, vectorizer
