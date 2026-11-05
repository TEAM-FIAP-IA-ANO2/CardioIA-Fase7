"""Carregamento e inferência do modelo de risco sintético."""

from functools import lru_cache
from pathlib import Path

import joblib
import pandas as pd

from .schemas import PatientData, RiskResult


MODEL_VERSION = "rf-synthetic-v1"


def classify_band(probability: float) -> str:
    if not 0 <= probability <= 1:
        raise ValueError("A probabilidade deve estar entre 0 e 1.")
    if probability < 0.30:
        return "BAIXO"
    if probability < 0.70:
        return "MODERADO"
    return "ALTO"


@lru_cache(maxsize=4)
def load_model(model_path: str):
    return joblib.load(model_path)


@lru_cache(maxsize=4)
def load_columns(columns_path: str):
    return joblib.load(columns_path)


def predict(patient: PatientData, artifacts_dir: Path) -> RiskResult:
    model_path = (artifacts_dir / "modelo_risco_cardiaco.joblib").resolve()
    columns_path = (artifacts_dir / "colunas_modelo.joblib").resolve()
    if not model_path.is_file() or not columns_path.is_file():
        raise FileNotFoundError(
            "Artefatos do modelo ausentes. Execute scripts/train_model.py antes do MVP."
        )

    model = load_model(str(model_path))
    columns = list(load_columns(str(columns_path)))
    payload = patient.model_dump()
    missing = [name for name in columns if name not in payload]
    if missing:
        raise ValueError(f"Colunas obrigatórias ausentes: {missing}")

    frame = pd.DataFrame([{name: payload[name] for name in columns}])
    probabilities = model.predict_proba(frame)[0]
    classes = list(getattr(model, "classes_", [0, 1]))
    if 1 not in classes or len(classes) != len(probabilities):
        raise ValueError("O modelo não expõe corretamente a classe positiva 1.")

    probability = float(probabilities[classes.index(1)])
    classifier = getattr(model, "named_steps", {}).get("classifier", model)
    return RiskResult(
        probability=round(probability, 6),
        predicted_class=int(probability >= 0.5),
        risk_band=classify_band(probability),
        model_name=type(classifier).__name__,
        model_version=MODEL_VERSION,
    )
