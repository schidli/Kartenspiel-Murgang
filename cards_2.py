import pygame
import random
import os
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import gumbel_r
import tkinter as tk
from tkinter import simpledialog, messagebox
#############################################################################################################
# Initialisiere das Kartenspiel
pygame.init()

# Hier die Fenstergröße definieren
width, height = 480, 750
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Kartenspiel")

# Verzeichnis der Kartenbilder
image_dir = 'images'

# Lade die Kartenbilder
card_images = []
for i in range(0, 9):
    image_path = os.path.join(image_dir, f'card_{i}.png')
    if os.path.exists(image_path):
        image = pygame.image.load(image_path)
        card_images.append(image)
    else:
        print(f"Datei nicht gefunden: {image_path}")

# Definiere den Kartenstapel mit der angegebenen Häufigkeit
#Anzahl Schnapskarten:
#card_deck = [1] * 22 + [2] * 17 + [3] * 13 + [4] * 7 + [5] * 2 + [6] * 2 + [7] * 1 + [8] * 1 + [9] * 1
#Anzahl willkürlich:
card_deck = [1] * 100 + [2] * 80 + [3] * 60 + [4] * 30 + [5] * 15 + [6] * 8 + [7] * 6 + [8] * 3+ [9] * 1
# Liste, um die gezogenen Karten zu speichern
drawn_cards = []
# Magnituden der Karten
magnitudes = [0, 1000, 3000, 5000, 8000, 10000, 50000, 100000, 1000000]
#############################################################################################################
# Funktionen der einzelnen Ergebnissplots der gezogenen Karten
# Funktion, um den Frequenzplot anzuzeigen
def show_frequency_plot(drawn_cards):
    years = list(range(1, len(drawn_cards) + 1))
    magnitudes_drawn = [magnitudes[i-1] for i in drawn_cards]
    
    colors = ['tab:gray', 'tab:blue', 'tab:green', 'tab:orange', 'tab:red', 'tab:purple', 'tab:brown', 'tab:pink', 'tab:cyan']
    
    plt.figure(figsize=(10, 6))
    for year, magnitude in zip(years, magnitudes_drawn):
        if magnitude > 0:
            plt.plot([year, year], [0, magnitude], marker='o', color=colors[drawn_cards[year-1]-1])
    
    plt.xscale('linear')
    plt.yscale('log')
    plt.xlabel('Jahr')
    plt.ylabel('Magnitude (m³)')
    plt.title('Frequenzplot der gezogenen Karten')
    plt.xticks(years)
    plt.savefig('frequency_plot.png')
    plt.show()
    plt.close()
# Funktion, um den Wahrscheinlichkeitsplot (CDF) zu erstellen
def plot_cdf(drawn_cards):
    # Magnituden der gezogenen Karten extrahieren (ohne Magnitude = 0)
    drawn_magnitudes = [magnitudes[i-1] for i in drawn_cards if magnitudes[i-1] > 0]
    
    if len(drawn_magnitudes) == 0:
        print("Keine gültigen Magnituden vorhanden, um die Gumbel-Verteilung zu schätzen.")
        return
    
    # Gumbel-Verteilung anpassen
    gumbel_params = gumbel_r.fit(drawn_magnitudes)
    print(f"Geschätzte Gumbel-Parameter: Lage (mu) = {gumbel_params[0]:.2f}, Skala (sigma) = {gumbel_params[1]:.2f}")
    
    # Empirische kumulative Verteilung
    sorted_data = np.sort(drawn_magnitudes)
    empirical_cdf = np.arange(1, len(sorted_data) + 1) / len(sorted_data)
    
    # Angepasste Gumbel-CDF
    x = np.linspace(min(drawn_magnitudes), max(drawn_magnitudes), 1000)
    gumbel_cdf = gumbel_r.cdf(x, *gumbel_params)
    
    # Visualisierung
    plt.figure(figsize=(10, 6))
    plt.step(sorted_data, empirical_cdf, where='post', label='Empirische CDF', color='skyblue')
    plt.plot(x, gumbel_cdf, 'r-', label='Angepasste Gumbel-CDF')
    
    # Beispiel:  100, 50-, 5-jährliches Wiederkehrintervall
    return_period = 100  # Jährlichkeit
    exceedance_probability = 1 - (1 / return_period)
    water_level_100_years = gumbel_r.ppf(exceedance_probability, *gumbel_params)
    plt.axvline(water_level_100_years, color='purple', linestyle='--', label=f'100-jährliches Volumen ({water_level_100_years:.0f} m³)')
    
    return_period = 30  # Jährlichkeit
    exceedance_probability = 1 - (1 / return_period)
    water_level_30_years = gumbel_r.ppf(exceedance_probability, *gumbel_params)
    plt.axvline(water_level_30_years, color='green', linestyle='--', label=f'30-jährliches Volumen ({water_level_30_years:.0f} m³)')
    
    return_period = 5  # Jährlichkeit
    exceedance_probability = 1 - (1 / return_period)
    water_level_5_years = gumbel_r.ppf(exceedance_probability, *gumbel_params)
    plt.axvline(water_level_5_years, color='blue', linestyle='--', label=f'5-jährliches Volumen ({water_level_5_years:.0f} m³)')
    
    # Diagramm beschriften
    plt.xlabel('Magnitude (m³)')
    plt.ylabel('Kumulative Wahrscheinlichkeit')
    plt.title('Wahrscheinlichkeitsplot (CDF) der gezogenen Karten')
    plt.legend()
    plt.grid()
    plt.savefig('cdf_plot.png')
    plt.show()
# Funktion, um das Häufigkeitsdiagramm anzuzeigen
def show_histogram(magnitudes, drawn_cards):
    # Zähle die Häufigkeit jeder Karte
    card_counts = [drawn_cards.count(i) for i in range(1, 10)]
    
    fig, ax = plt.subplots()
    ax.figsize = (8, 8)
   
    bar_labels = ['red', 'blue', '_red', 'orange', 'red', 'blue', '_red', 'orange', 'orange']
    bar_colors = ['tab:red', 'tab:blue', 'tab:red', 'tab:orange', 'tab:red', 'tab:blue', 'tab:red', 'tab:orange', 'tab:orange']

    ax.bar([str(m) for m in magnitudes], card_counts, label=bar_labels, color=bar_colors)
    ax.set_xlabel('Magnitude (m³)')
    ax.set_ylabel('Häufigkeit')
    ax.set_title('Häufigkeit der gezogenen Karten')
    plt.savefig('histogram.png')
    plt.show()
    plt.close()

# Funktion, um die kumulierte empirische Wahrscheinlichkeitsfunktion anzuzeigen
def show_cumulative_empirical_probability(drawn_cards):
    # Zähle die Häufigkeit jeder Karte
    card_counts = [drawn_cards.count(i) for i in range(1, 10)]
    total_draws = len(drawn_cards)
    
    # Magnituden und Wahrscheinlichkeiten filtern (Ereignisse ohne Magnitude ausschließen)
    magnitudes_filtered = [magnitudes[i] for i in range(1, 10) if magnitudes[i] > 0]
    probabilities_filtered = [card_counts[i-1] / total_draws for i in range(1, 10) if magnitudes[i] > 0]
    cumulative_probabilities = np.cumsum(probabilities_filtered)
    
    # Erstelle das Diagramm
    plt.figure(figsize=(8, 6))
    plt.plot(magnitudes_filtered, cumulative_probabilities, marker='o', label='Empirische Wahrscheinlichkeit')
    
    # Gumbel-Grenzwertverteilung basierend auf den gezogenen Magnituden
    drawn_magnitudes = [magnitudes[i-1] for i in drawn_cards if magnitudes[i-1] > 0]
    magnitudes_numeric = np.linspace(1, 1000000, 1000)  # Kontinuierlicher Bereich von Magnituden
    gumbel_params = gumbel_r.fit(drawn_magnitudes)
    gumbel_cdf = gumbel_r.cdf(magnitudes_numeric, *gumbel_params)
    
    plt.plot(magnitudes_numeric, gumbel_cdf, linestyle='--', label='Gumbel-Grenzwertverteilung')
    
    plt.xscale('log')  # Setze die x-Achse auf eine logarithmische Skala
    plt.xlabel('Magnitude (m³)')
    plt.ylabel('Kumulative Wahrscheinlichkeit')
    plt.title('Kumulative Wahrscheinlichkeitsfunktion (logarithmisch)')
    plt.ylim(0, 1)
    plt.legend()
    plt.savefig('cumulative_empirical_probability_log.png')
    plt.show()
    plt.close()

    return gumbel_params
# Jährlichkeit für eine gegebene Magnitude berechnen
def calculate_probability_and_frequency(magnitude, gumbel_params):
    probability = gumbel_r.cdf(magnitude, *gumbel_params)
    frequency = 1 / (1-probability)
    return probability, frequency
#  Magnitude für eine gegebene Jährlichkeit berechnen
def calculate_magnitude_for_probability(T, gumbel_params):
    probability=1-(1/T)
    magnitude = gumbel_r.ppf(probability, *gumbel_params)
    return magnitude
# Funktion, um den Jährlichkeits-zu-Magnituden-Plot anzuzeigen
# Funktion, um die kumulierte empirische Wahrscheinlichkeitsfunktion anzuzeigen
def show_cumulative_empirical_probability(drawn_cards):
    # Zähle die Häufigkeit jeder Karte
    card_counts = [drawn_cards.count(i) for i in range(1, 10)]
    total_draws = len(drawn_cards)
    
    # Magnituden und Wahrscheinlichkeiten filtern (Ereignisse ohne Magnitude ausschließen)
    magnitudes_filtered = [magnitudes[i] for i in range(1, len(magnitudes)) if magnitudes[i] > 0]
    probabilities_filtered = [card_counts[i-1] / total_draws for i in range(1, len(magnitudes)) if magnitudes[i] > 0]
    cumulative_probabilities = np.cumsum(probabilities_filtered)
    
    # Erstelle das Diagramm
    plt.figure(figsize=(8, 6))
    plt.plot(magnitudes_filtered, cumulative_probabilities, marker='o', label='Empirische Wahrscheinlichkeit')
    
    # Gumbel-Grenzwertverteilung basierend auf den gezogenen Magnituden
    drawn_magnitudes = [magnitudes[i-1] for i in drawn_cards if magnitudes[i-1] > 0]
    magnitudes_numeric = np.linspace(1, 1000000, 1000)  # Kontinuierlicher Bereich von Magnituden
    gumbel_params = gumbel_r.fit(drawn_magnitudes)
    gumbel_cdf = gumbel_r.cdf(magnitudes_numeric, *gumbel_params)
    
    plt.plot(magnitudes_numeric, gumbel_cdf, linestyle='--', label='Gumbel-Grenzwertverteilung')
    
    plt.xscale('log')  # Setze die x-Achse auf eine logarithmische Skala
    plt.xlabel('Magnitude (m³)')
    plt.ylabel('Kumulative Wahrscheinlichkeit')
    plt.title('Kumulative Wahrscheinlichkeitsfunktion (logarithmisch)')
    plt.ylim(0, 1)
    plt.legend()
    plt.savefig('cumulative_empirical_probability_log.png')
    plt.show()
    plt.close()

    return gumbel_params
# Funktion, um den Jährlichkeits-zu-Magnituden-Plot anzuzeigen
def show_return_period_plot_from_frequencies(drawn_cards):
    # Zähle die Häufigkeit jeder Karte
    card_counts = [drawn_cards.count(i) for i in range(1, 10)]
    total_draws = len(drawn_cards)
    
    # Berechne die empirische Wahrscheinlichkeit und Jährlichkeit
    probabilities = [count / total_draws for count in card_counts]
    return_periods = [1 / prob if prob > 0 else np.inf for prob in probabilities]  # Jährlichkeit berechnen
    
    # Magnituden und zugehörige Jährlichkeiten filtern (nur gezogene Karten)
    magnitudes_filtered = [magnitudes[i] for i in range(1, 10) if card_counts[i-1] > 0]
    return_periods_filtered = [return_periods[i] for i in range(len(return_periods)) if card_counts[i] > 0]
    
    # Erstelle das Diagramm
    plt.figure(figsize=(8, 6))
    plt.plot(magnitudes_filtered, return_periods_filtered, marker='o', linestyle='-', label='Jährlichkeit')
    
    # Füge eine Ausgleichsgerade hinzu (log-log-Skalierung)
    log_magnitudes = np.log10(magnitudes_filtered)
    log_return_periods = np.log10(return_periods_filtered)
    coeffs = np.polyfit(log_magnitudes, log_return_periods, 1)  # Lineare Regression im log-log-Raum
    fit_line = np.poly1d(coeffs)
    plt.plot(magnitudes_filtered, 10**fit_line(log_magnitudes), linestyle='--', color='red', label='Ausgleichsgerade')
    
    plt.xscale('log')  # Setze die x-Achse auf eine logarithmische Skala
    plt.yscale('log')  # Setze die y-Achse auf eine logarithmische Skala
    plt.xlabel('Magnitude (m³)')
    plt.ylabel('Jährlichkeit (Jahre)')
    plt.title('Jährlichkeit zu Magnitude (log-log)')
    plt.legend()
    plt.savefig('return_period_plot_from_frequencies.png')
    plt.show()
    plt.close()
#############################################################################################################
# Hauptspiel-Schleife
running = True
show_hist = False
show_prob = False
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if show_hist:
                show_prob = True
                show_hist = False
            else:
                # Ziehe eine zufällige Karte aus dem Kartenstapel
                random_index = random.choice(card_deck)
                random_card = card_images[random_index]
                # Speichere die gezogene Karte
                drawn_cards.append(random_index)
                # Zeige die gezogene Karte an
                screen.fill((0, 0, 0))  # Bildschirm leeren
                screen.blit(random_card, (width // 2 - random_card.get_width() // 2, height // 2 - random_card.get_height() // 2))
                pygame.display.flip()
                pygame.time.wait(800)  # Warte 2 Sekunden

                # Zeige die Rückseite der Karte an
                screen.fill((0, 0, 0))  # Bildschirm leeren
                screen.blit(card_images[0], (width // 2 - card_images[0].get_width() // 2, height // 2 - card_images[0].get_height() // 2))
                pygame.display.flip()

    # Bildschirm aktualisieren
    pygame.display.update()

# Beende Pygame
pygame.quit()
#############################################################################################################
# Frequenzplot
show_frequency_plot(drawn_cards)

# Häufigkeitsdiagramm
show_histogram(magnitudes, drawn_cards)
# Jährlichkeits-zu-Magnituden-Plot basierend auf Häufigkeiten
show_return_period_plot_from_frequencies(drawn_cards)
#show_cumulative_empirical_probability(drawn_cards)
#gumbel_params = show_cumulative_empirical_probability(drawn_cards)
# Wahrscheinlichkeitsplot (CDF)
plot_cdf(drawn_cards)
""" 
#############################################################################################################
# GUI-Fenster zur Eingabe der Magnitude
root = tk.Tk()
root.withdraw()  

magnitudes_entered = []
frequencies_entered = []

while True:
    user_choice = simpledialog.askstring("Eingabe", "Geben Sie 'M' für Magnitude oder 'T' für Jährlichkeit ein:")
    if user_choice is None:
        break
    if user_choice.lower() == 'm':
        user_magnitude = simpledialog.askfloat("Magnitude Eingabe", "Bitte geben Sie eine Magnitude ein:")
        if user_magnitude is not None:
            probability, frequency = calculate_probability_and_frequency(user_magnitude, gumbel_params)
            messagebox.showinfo("Ergebnis", f"Überschreitungswahrscheinlichkeit der Magnitude {user_magnitude} m³: {probability:.4f}\nJährlichkeit der Magnitude {user_magnitude} m³: {frequency:.4f} Jahre")
    elif user_choice.lower() == 't':
        user_probability = simpledialog.askfloat("Jährlichkeit Eingabe", "Bitte geben Sie eine Jährlichkeit ein:")
        if user_probability is not None:
            magnitude = calculate_magnitude_for_probability(user_probability, gumbel_params)
            messagebox.showinfo("Ergebnis", f"Magnitude für die Jährlichkeit {user_probability:.4f}: {magnitude:.4f} m³") """