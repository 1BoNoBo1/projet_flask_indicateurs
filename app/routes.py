from flask import render_template, request, jsonify, flash, redirect, url_for
from app import app
from app.utils.telechargement_cours import telecharger_cours, sauvegarder_donnees
from app.utils.strategie_trading import appliquer_strategie
from app.utils.evaluation_strategie import calculer_metriques
from app.utils.visualisation import generer_graphique, generer_graphique_strategie, generer_graphique_comparaison
import pandas as pd
import json
import os
from datetime import datetime, timedelta


def get_available_data():
    data_dir = app.config['DATA_DIR']
    available_data = []
    for filename in os.listdir(data_dir):
        if filename.endswith('.csv'):
            parts = filename.split('_')
            if len(parts) >= 2:
                symbol = parts[0].replace('USDT', '')  # Supprime 'USDT' du symbole
                interval = parts[1]
                available_data.append((symbol, interval))
    return list(set(available_data))  # Supprime les doublons

@app.route('/')
def index():
    available_data = get_available_data()
    return render_template('index.html', available_data=available_data)


@app.route('/telecharger', methods=['GET', 'POST'])
def telecharger():
    if request.method == 'POST':
        crypto = request.form['crypto']
        interval = request.form['interval']
        start_date = request.form['start_date']
        end_date = request.form['end_date'] or datetime.now().strftime('%Y-%m-%d')

        try:
            df = telecharger_cours(crypto, interval, start_date, end_date)
            csv_path, json_path = sauvegarder_donnees(df, crypto, interval, start_date, end_date)
            flash(f'Données téléchargées et sauvegardées avec succès: {csv_path}, {json_path}', 'success')
        except Exception as e:
            flash(f'Erreur lors du téléchargement des données: {str(e)}', 'error')

        return redirect(url_for('index'))

    # Préparer les options pour le formulaire
    cryptos = ['BTC', 'ETH', 'XRP', 'LTC', 'BCH', 'ADA']
    intervals = [('1m', '1 minute'), ('5m', '5 minutes'), ('15m', '15 minutes'), ('30m', '30 minutes'),
                 ('1h', '1 heure'), ('4h', '4 heures'), ('1d', '1 jour'), ('1w', '1 semaine')]
    default_start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    
    return render_template('telecharger.html', cryptos=cryptos, intervals=intervals, default_start_date=default_start_date)

@app.route('/visualiser/<crypto>/<interval>')
def visualiser(crypto, interval):
    # Trouver le fichier le plus récent pour cette crypto et cet intervalle
    files = sorted(
        [f for f in os.listdir(app.config['DATA_DIR']) if f.startswith(f"{crypto}USDT_{interval}_") and (f.endswith('.csv') or f.endswith('.json'))],
        key=lambda x: os.path.getmtime(os.path.join(app.config['DATA_DIR'], x)),
        reverse=True
    )
    
    if not files:
        flash("Aucune donnée disponible pour cette crypto et cet intervalle.", "error")
        return redirect(url_for('index'))
    
    filename = files[0]
    filepath = os.path.join(app.config['DATA_DIR'], filename)
    
    print(f"Tentative de lecture du fichier : {filepath}")
    
    try:
        if filename.endswith('.csv'):
            df = pd.read_csv(filepath, index_col='timestamp', parse_dates=True)
        elif filename.endswith('.json'):
            with open(filepath, 'r') as f:
                data = json.load(f)
            df = pd.DataFrame(data['data'], columns=data['columns'])
            
            # Essayer d'abord avec des millisecondes, puis avec des nanosecondes si ça échoue
            try:
                df.index = pd.to_datetime(data['index'], unit='ms')
            except ValueError:
                df.index = pd.to_datetime(pd.to_numeric(data['index']), unit='ns')
        else:
            raise ValueError("Format de fichier non supporté")
        
        print("Colonnes du DataFrame:")
        print(df.columns)
        print("\nTypes des colonnes:")
        print(df.dtypes)
        print("\nPremières lignes du DataFrame:")
        print(df.head())
        
        # Vérifier les colonnes et ajuster si nécessaire
        required_columns = ['open', 'high', 'low', 'close', 'volume']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Colonnes manquantes dans les données: {', '.join(missing_columns)}")
        
        # Essayer de générer le graphique
        graphique_json = generer_graphique(df)
        
        print("Contenu de graphique_json:", graphique_json) #debug  
        print("Contenu de graphique_json:", graphique_json[:500])  # Imprime les 500 premiers caractères
        print("Aperçu du DataFrame:")
        print(df.head())
        print("Types des colonnes:")
        print(df.dtypes)
        return render_template('visualiser.html', graphique_json=graphique_json, crypto=crypto, interval=interval)
    
    except Exception as e:
        print(f"Erreur complète : {str(e)}")
        flash(f"Erreur lors de la visualisation des données : {str(e)}", "error")
        return redirect(url_for('index'))


@app.route('/appliquer_strategie/<crypto>/<interval>', methods=['GET', 'POST'])
def appliquer_strategie_route(crypto, interval):
    if request.method == 'POST':
        longueurALMA = int(request.form.get('longueurALMA', 10))
        sigma = float(request.form.get('sigma', 6))
        offset = float(request.form.get('offset', 0.85))
        decalage = int(request.form.get('decalage', 3))
        
        # Charger les données les plus récentes
        files = [f for f in os.listdir(app.config['DATA_DIR']) if f.startswith(f"{crypto}USDT_{interval}_") and f.endswith('.csv')]
        
        if not files:
            flash(f"Aucune donnée disponible pour {crypto}/USDT ({interval}). Veuillez d'abord télécharger les données.", "error")
            return redirect(url_for('index'))
        
        filename = max(files, key=lambda x: os.path.getmtime(os.path.join(app.config['DATA_DIR'], x)))
        filepath = os.path.join(app.config['DATA_DIR'], filename)
        
        try:
            df = pd.read_csv(filepath, index_col='timestamp', parse_dates=True)
            df_strategie = appliquer_strategie(df, longueurALMA, sigma, offset, decalage)
            metriques = calculer_metriques(df_strategie)
            graphique_json = generer_graphique_strategie(df_strategie)
            print("Contenu de graphique_json:", graphique_json[:500])  # debug Imprime les 500 premiers caractères

            return render_template('resultats_strategie.html', 
                                   graphique_json=graphique_json, 
                                   crypto=crypto, 
                                   interval=interval,
                                   parametres={
                                       'longueurALMA': longueurALMA,
                                       'sigma': sigma,
                                       'offset': offset,
                                       'decalage': decalage
                                   },
                                   metriques=metriques)
        except Exception as e:
            print(f"Erreur lors de l'application de la stratégie : {str(e)}")
            flash(f"Erreur lors de l'application de la stratégie : {str(e)}", "error")
            return redirect(url_for('index'))
        
    return render_template('appliquer_strategie.html', crypto=crypto, interval=interval)

@app.route('/rapport/<crypto>/<interval>')
def rapport_performance(crypto, interval):
    files = [f for f in os.listdir(app.config['DATA_DIR']) if f.startswith(f"{crypto}USDT_{interval}_") and f.endswith('.json')]
    if not files:
        flash("Aucune donnée disponible pour cette crypto et cet intervalle.", "error")
        return redirect(url_for('index'))
    
    filename = max(files, key=lambda x: os.path.getmtime(os.path.join(app.config['DATA_DIR'], x)))
    filepath = os.path.join(app.config['DATA_DIR'], filename)
    
    with open(filepath, 'r') as f:
        data = json.load(f)
    df = pd.DataFrame(data['data'], columns=data['columns'])
    df.index = pd.to_datetime(data['index'], unit='ms')
    
    df_strategie = appliquer_strategie(df)
    metriques = calculer_metriques(df_strategie)
    graphique_json = generer_graphique_strategie(df_strategie)
    
    return render_template('rapport_performance.html', 
                           graphique_json=graphique_json, 
                           metriques=metriques, 
                           crypto=crypto, 
                           interval=interval)
    

@app.route('/comparer_strategies/<crypto>/<interval>', methods=['GET', 'POST'])
def comparer_strategies(crypto, interval):
    if request.method == 'POST':
        # Récupérer les paramètres des stratégies depuis le formulaire
        strategies = []
        for i in range(1, 3):  # Pour comparer 2 stratégies
            strategy = {
                'nom': request.form[f'nom_{i}'],
                'longueurALMA': int(request.form[f'longueurALMA_{i}']),
                'sigma': float(request.form[f'sigma_{i}']),
                'offset': float(request.form[f'offset_{i}']),
                'decalage': int(request.form[f'decalage_{i}'])
            }
            strategies.append(strategy)

        # Charger les données
        files = [f for f in os.listdir(app.config['DATA_DIR']) if f.startswith(f"{crypto}USDT_{interval}_") and f.endswith('.json')]
        if not files:
            flash("Aucune donnée disponible pour cette crypto et cet intervalle.", "error")
            return redirect(url_for('index'))
        
        filename = max(files, key=lambda x: os.path.getmtime(os.path.join(app.config['DATA_DIR'], x)))
        filepath = os.path.join(app.config['DATA_DIR'], filename)
        
        with open(filepath, 'r') as f:
            data = json.load(f)
        df = pd.DataFrame(data['data'], columns=data['columns'])
        df.index = pd.to_datetime(data['index'], unit='ms')

        # Appliquer les stratégies et calculer les métriques
        results = []
        for strategy in strategies:
            df_strategy = appliquer_strategie(df, strategy['longueurALMA'], strategy['sigma'], strategy['offset'], strategy['decalage'])
            metriques = calculer_metriques(df_strategy)
            results.append({
                'nom': strategy['nom'],
                'metriques': metriques,
                'df': df_strategy
            })

        # Générer le graphique de comparaison
        graphique_json = generer_graphique_comparaison(results)

        return render_template('comparaison_strategies.html',
                               graphique_json=graphique_json,
                               results=results,
                               crypto=crypto,
                               interval=interval)

    return render_template('formulaire_comparaison.html', crypto=crypto, interval=interval)