import pandas as pd
import joblib
from datetime import datetime

# Caricare il modello pre-addestrato
modello = joblib.load("modelli/rifiuti_predictor.pkl")

def prevedi_zone_critiche(data_oggi):
    """Prevede le zone con maggiore accumulo di rifiuti sulla base dei dati storici."""
    data_oggi = datetime.strptime(data_oggi, "%Y-%m-%d")

    # Simulazione di dati storici
    dati = pd.DataFrame({
        "mese": [data_oggi.month],
        "giorno_settimana": [data_oggi.weekday()],
        "ora": [12]  # Supponiamo un'analisi a mezzogiorno
    })

    probabilità = modello.predict_proba(dati)[0][1]  # Probabilità di criticità
    return f"Probabilità di accumulo rifiuti oggi: {probabilità * 100:.2f}%"

