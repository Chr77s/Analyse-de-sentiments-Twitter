import tkinter as tk
import matplotlib.pyplot as plt
import tweepy
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import re
import time

# Configuration de notre API Tweepy pour le plan gratuit
bearer_token = 'AAAAAAAAAAAAAAAAAAAAAOSSyQEAAAAAGb4Xm0IYhfoKeqvHL1bbsE50zFM%3DE0ctRO5G1aXXPeiqxvOtlwDWfDgJcDSIRPla1TU9jeSfo3Kgcl'

client = tweepy.Client(bearer_token=bearer_token)

# Initialisation de l'analyseur de sentiments VADER
analyser = SentimentIntensityAnalyzer()

# Cache pour limiter les requêtes répétées
cache_tweets = {}

# Fonction pour nettoyer les tweets
def nettoyer_texte(tweet):
    tweet = re.sub(r"http\S+", "", tweet)  # Supprime les liens
    tweet = re.sub(r"@\S+", "", tweet)  # Supprime les mentions
    tweet = re.sub(r"#", "", tweet)  # Supprime les hashtags
    tweet = re.sub(r"\n", " ", tweet)  # Supprime les retours à la ligne
    return tweet.strip()

# Fonction pour rechercher les tweets en gérant les limites API
def rechercher_tweets(mots_cles):
    if mots_cles in cache_tweets:  
        return cache_tweets[mots_cles]  

    query = f"{mots_cles} lang:fr OR lang:en -is:retweet"
    
    try:
        tweets = []
        for response in tweepy.Paginator(client.search_recent_tweets, query=query, max_results=10, limit=2):
            if response.data:
                tweets.extend([nettoyer_texte(tweet.text) for tweet in response.data])

        cache_tweets[mots_cles] = tweets  # Stocker en cache
        time.sleep(2)  # Pause pour éviter d'être bloqué
        return tweets
    except tweepy.TooManyRequests:
        return ["Erreur : Trop de requêtes envoyées. Attendez un moment."]
    except Exception as e:
        return [f"Erreur : {e}"]

# Fonction  pour analyser les sentiments avec VADER
def analyser_sentiments(tweets):
    sentiments = {'Positif': 0, 'Négatif': 0, 'Neutre': 0}
    
    for tweet in tweets:
        score = analyser.polarity_scores(tweet)["compound"]
        if score > 0.05:
            sentiments['Positif'] += 1
        elif score < -0.05:
            sentiments['Négatif'] += 1
        else:
            sentiments['Neutre'] += 1
    
    return sentiments

# Interface graphique 
def creer_interface():
    fenetre = tk.Tk()
    fenetre.title("Analyse des Sentiments sur Twitter")

    tk.Label(fenetre, text="Mots-clés :", font=("Arial", 12)).pack()
    
    input_keywords = tk.Entry(fenetre, width=50)
    input_keywords.pack(pady=5)

    bouton_recherche = tk.Button(fenetre, text="Analyser", command=lambda: lancer_recherche(input_keywords, output_box))
    bouton_recherche.pack(pady=5)

    output_box = tk.Text(fenetre, height=10, width=60)
    output_box.pack(pady=10)

    fenetre.mainloop()

# Fonction pour gérer l'affichage et l'analyse
def lancer_recherche(input_keywords, output_box):
    mots_cles = input_keywords.get()
    output_box.delete(1.0, tk.END)
    output_box.insert(tk.END, "Recherche en cours...\n")

    tweets = rechercher_tweets(mots_cles)
    sentiments = analyser_sentiments(tweets)

    afficher_resultats(output_box, sentiments)
    visualiser_sentiments(sentiments)

# Fonction pour afficher les résultats dans l'interface
def afficher_resultats(output_box, sentiments):
    output_box.delete(1.0, tk.END)
    for sentiment, count in sentiments.items():
        output_box.insert(tk.END, f"{sentiment}: {count}\n")

# Fonction pour visualiser les sentiments sous forme de graphique
def visualiser_sentiments(sentiments):
    categories = list(sentiments.keys())
    valeurs = list(sentiments.values())

    plt.figure(figsize=(8, 5))
    plt.bar(categories, valeurs, color=['green', 'red', 'blue'])
    plt.xlabel('Catégories de Sentiments')
    plt.ylabel('Nombre')
    plt.title('Analyse des Sentiments sur Twitter')
    plt.show()

# Lancement de l'application
if __name__ == "__main__":
    creer_interface()
