from flask import render_template, request, jsonify, flash, redirect, url_for
from app import app
from app.utils.telechargement_cours import telecharger_cours, sauvegarder_donnees
from app.utils.visualisation import generer_graphique
import pandas as pd
from datetime import datetime
import os

# ... (garder les routes existantes)

@app.route('/visualiser/<crypto>/<interval>')
def visualiser(crypto, interval):
    # Trouver le fichier CSV le plus récent pour cette crypto et cet intervalle
    pattern = f"{crypto}USDT_{interval}_*.csv"
    files = sorted(
        [f for f in os.listdir(app.config['DATA_DIR']) if f.startswith(f"{crypto}USDT_{interval}_")],
        key=lambda x: os.path.getmtime(os.path.join(app.config['DATA_DIR'], x)),
        reverse=True
    )
    
    if not files:
        flash("Aucune donnée disponible pour cette crypto et cet intervalle.", "error")
        return redirect(url_for('index'))
    
    filename = files[0]
    filepath = os.path.join(app.config['DATA_DIR'], filename)
    
    df = pd.read_csv(filepath, index_col='timestamp', parse_dates=True)
    graphique_json = generer_graphique(df)
    
    return render_template('visualiser.html', graphique_json=graphique_json, crypto=crypto, interval=interval)