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
card_deck = [1] * 100 + [2] * 80 + [3] * 60 + [4] * 30 + [5] * 15 + [6] * 10 + [7] * 5 + [8] * 3+ [9] * 1
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
    
    #plt.figure(figsize=(15.75, 8.86))
    plt.figure(figsize=(12, 6.75))
    for year, magnitude in zip(years, magnitudes_drawn):
        if magnitude > 0:
            plt.plot([year, year], [0, magnitude], marker='o', color=colors[drawn_cards[year-1]-1])
    
    plt.xscale('linear')
    plt.yscale('log')
    plt.xlabel('Jahr', fontsize=14)
    plt.ylabel('Magnitude (m³)', fontsize=14)
    plt.title('Frequenzplot der gezogenen Karten', fontsize=14)
    plt.xticks(years, fontsize=12)  # Schriftgröße für die x-Achsenticks
    plt.yticks(fontsize=12)
    plt.savefig('frequency_plot.png')
    plt.show()
    plt.close()

def plot_empirical(drawn_cards):
    # Magnituden der gezogenen Karten extrahieren (ohne Magnitude = 0)
    drawn_magnitudes = [magnitudes[i-1] for i in drawn_cards if magnitudes[i-1] > 0]
    
    if len(drawn_magnitudes) == 0:
        print("Keine gültigen Magnituden vorhanden, um die empirische Verteilung zu erstellen.")
        return
    
    # Empirische kumulative Verteilung
    sorted_data = np.sort(drawn_magnitudes)
    empirical_cdf = np.arange(1, len(sorted_data) + 1) / len(sorted_data)
    
    # Visualisierung
    plt.figure(figsize=(12, 6.75))
    plt.step(sorted_data, empirical_cdf, where='post', label='Empirische CDF', color='skyblue', linewidth=2)
    
    # 5-, 30- und 100-jährliche Wiederkehrintervalle
    for return_period, color in zip([5, 30, 100], ['#000000', '#4d4d4d', '#bfbfbf']):
        exceedance_probability = 1 - (1 / return_period)
        if len(sorted_data) > 0:
            # Näherung: Volumen für die gegebene Wahrscheinlichkeit aus den Daten schätzen
            water_level = np.percentile(sorted_data, exceedance_probability * 100)
            
            # Vertikale Linie nur bis zur Kurve
            plt.plot([water_level, water_level], [0, exceedance_probability], color=color, linestyle='--', linewidth=1, alpha=0.7)
            
            # Horizontale Linie nur bis zur Kurve
            #plt.plot([min(sorted_data), water_level], [exceedance_probability, exceedance_probability], color=color, linestyle='--', linewidth=1, alpha=0.7)
            plt.plot([0, water_level], [exceedance_probability, exceedance_probability], color=color, linestyle='--', linewidth=1, alpha=0.7)
            # Beschriftung oberhalb der horizontalen Linie
            #plt.text(water_level, exceedance_probability + 0.02, f'{return_period}-jährlich', 
            #         color=color, fontsize=10, verticalalignment='center', horizontalalignment='center')
            
            # Volumenswerte in der Legende
            plt.plot([], [], color=color, linestyle='--', label=f'{return_period}-jährlich: {water_level:.0f} m³')
    # Achsenlimits setzen, um den Ursprung (0, 0) in die linke untere Ecke zu bringen
    plt.xlim(0, max(sorted_data) * 1.1)  # x-Achse beginnt bei 0
    plt.ylim(0, 1.1)  # y-Achse beginnt bei 0
    # Diagramm beschriften
    plt.xlabel('Magnitude (m³)', fontsize=14)
    plt.ylabel('Kumulative Wahrscheinlichkeit', fontsize=14)
    plt.title('Empirische Wahrscheinlichkeitsverteilung', fontsize=14)
    plt.yticks(fontsize=12)
    plt.xticks(fontsize=12)
    
    # Legende rechts unten positionieren
    plt.legend(fontsize=12, loc='lower right')
    plt.grid(color='lightgray', linestyle='-', linewidth=0.5, alpha=0.7)
    plt.savefig('empiric_plot.png')
    plt.show()
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
    plt.figure(figsize=(12, 6.75))
    plt.step(sorted_data, empirical_cdf, where='post', label='Empirische CDF', color='skyblue', linewidth=2)
    plt.plot(x, gumbel_cdf, 'r-', label='Angepasste Gumbel-CDF', linewidth=2)
    
    # 5-, 30- und 100-jährliche Wiederkehrintervalle
    for return_period, color in zip([5, 30, 100], ['#000000', '#4d4d4d', '#bfbfbf']):
        exceedance_probability = 1 - (1 / return_period)
        water_level = gumbel_r.ppf(exceedance_probability, *gumbel_params)
        
        # Vertikale Linie nur bis zur Gumbel-Kurve
        plt.plot([water_level, water_level], [0, exceedance_probability], color=color, linestyle='--', linewidth=1, alpha=0.7)
        
        # Horizontale Linie nur bis zur Gumbel-Kurve
        #plt.plot([min(x), water_level], [exceedance_probability, exceedance_probability], color=color, linestyle='--', linewidth=1, alpha=0.7)
        plt.plot([0, water_level], [exceedance_probability, exceedance_probability], color=color, linestyle='--', linewidth=1, alpha=0.7)
        # Beschriftung oberhalb der horizontalen Linie
        #plt.text(water_level, exceedance_probability + 0.02, f'{return_period}-jährlich', 
        #         color='black', fontsize=10, verticalalignment='center', horizontalalignment='center')
        
        # Volumenswerte in der Legende
        plt.plot([], [], color=color, linestyle='--', label=f'{return_period}-jährlich: {water_level:.0f} m³')
    # Achsenlimits setzen, um den Ursprung (0, 0) in die linke untere Ecke zu bringen
    plt.xlim(0, max(x) * 1.1)  # x-Achse beginnt bei 0
    plt.ylim(0, 1.1)  # y-Achse beginnt bei 0
    
    # Diagramm beschriften
    plt.xlabel('Magnitude (m³)', fontsize=14)
    plt.ylabel('Kumulative Wahrscheinlichkeit', fontsize=14)
    plt.title('Wahrscheinlichkeitsplot (CDF) der gezogenen Karten', fontsize=14)
    plt.yticks(fontsize=12)
    plt.xticks(fontsize=12)
    
    # Legende rechts unten positionieren
    plt.legend(fontsize=12, loc='lower right')
    plt.grid(color='lightgray', linestyle='-', linewidth=0.5, alpha=0.7)
    plt.savefig('cdf_plot.png')
    plt.show()
# Funktion, um das Häufigkeitsdiagramm anzuzeigen
def show_histogram(magnitudes, drawn_cards):
    # Zähle die Häufigkeit jeder Karte
    card_counts = [drawn_cards.count(i) for i in range(1, 10)]
    
    # Erstelle die Figur
    #plt.figure(figsize=(15.75, 8.86))
    plt.figure(figsize=(12, 6.75))
    # Farben und Labels für die Balken
    bar_colors =colors = ['tab:gray', 'tab:blue', 'tab:green', 'tab:orange', 'tab:red', 'tab:purple', 'tab:brown', 'tab:pink', 'tab:cyan']
    #bar_labels = ['red', 'blue', '_red', 'orange', 'red', 'blue', '_red', 'orange', 'orange']
    #bar_colors = ['tab:red', 'tab:blue', 'tab:red', 'tab:orange', 'tab:red', 'tab:blue', 'tab:red', 'tab:orange', 'tab:orange']
    
    # Erstelle das Balkendiagramm
    plt.bar([str(m) for m in magnitudes], card_counts, color=bar_colors)
    
    # Achsenbeschriftungen und Titel
    plt.xlabel('Magnitude (m³)', fontsize=14)
    plt.ylabel('Häufigkeit', fontsize=14)
    plt.title('Häufigkeit der gezogenen Karten', fontsize=14)
    
    # Achsenticks
    plt.yticks(fontsize=12)
    plt.xticks(fontsize=12)
    
    # Speichere und zeige das Diagramm
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
    probabilities_filtered = [probabilities[i] for i in range(len(probabilities)) if card_counts[i] > 0]
    
    # Farben für die Punkte
    colors = ['tab:gray', 'tab:blue', 'tab:green', 'tab:orange', 'tab:red', 'tab:purple', 'tab:brown', 'tab:pink', 'tab:cyan']
    point_colors = [colors[i] for i in range(len(card_counts)) if card_counts[i] > 0]
    
    # Erstelle das Diagramm
    plt.figure(figsize=(12, 6.75))
    
    # Punkte mit den entsprechenden Farben plotten
    for magnitude, probability, color in zip(magnitudes_filtered, probabilities_filtered, point_colors):
        plt.plot(magnitude, probability, marker='o', color=color, linestyle='', label=f'Magnitude: {magnitude}')
    
    # Verbindungslinie zwischen den Punkten (dünn und grau)
    plt.plot(magnitudes_filtered, probabilities_filtered, color='lightgray', linestyle='-', linewidth=1)
    
    # Füge eine Ausgleichsgerade hinzu (log-log-Skalierung), aber ohne Legendeneintrag
    log_magnitudes = np.log10(magnitudes_filtered)
    log_probabilities = np.log10(probabilities_filtered)
    coeffs = np.polyfit(log_magnitudes, log_probabilities, 1)  # Lineare Regression im log-log-Raum
    fit_line = np.poly1d(coeffs)
    plt.plot(magnitudes_filtered, 10**fit_line(log_magnitudes), linestyle='--', color='red')  # Kein Label für die Ausgleichsgerade
    
    # Achsen auf logarithmische Skala setzen
    plt.xscale('log')
    plt.yscale('log')
    
    # Achsenbeschriftungen und Titel
    plt.xlabel('Magnitude (m³)', fontsize=14)
    plt.ylabel('Frequenz', fontsize=14)
    plt.title('F/M Kurve (log-log)', fontsize=14)
    
    # Y-Achsen-Ticks anpassen
    y_ticks = [10**-2, 10**-1, 10**0]
    plt.yticks(y_ticks, [f"{tick:.0e}" for tick in y_ticks], fontsize=12)
    plt.xticks(fontsize=12)
    
    # Legende hinzufügen (rechts oben)
    plt.legend(fontsize=10, loc='upper right')
    
    # Diagramm speichern und anzeigen
    plt.savefig('return_period_plot_from_frequencies.png')
    plt.show()
    plt.close()
def show_return_period_plot_with_threshold(drawn_cards, magnitudes, Q_T):
    """
    Plottet die Jährlichkeit (Return Period) basierend auf einem Schwellenwert Q_T.
    
    Parameters:
    - drawn_cards: Liste der gezogenen Karten (z. B. 1 bis 9).
    - magnitudes: Liste der Magnituden, die den Karten zugeordnet sind.
    - Q_T: Schwellenwert für die Magnitude.
    """
    import numpy as np
    import matplotlib.pyplot as plt

    # Zähle die Häufigkeit jeder Karte
    card_counts = [drawn_cards.count(i) for i in range(1, 10)]
    total_draws = len(drawn_cards)
    
    # Berechne die Magnituden, die den Schwellenwert Q_T überschreiten
    magnitudes_filtered = [magnitudes[i-1] for i in range(1, 10) if magnitudes[i-1] >= Q_T]
    counts_filtered = [card_counts[i-1] for i in range(1, 10) if magnitudes[i-1] >= Q_T]
    
    # Berechne die Überschreitungswahrscheinlichkeit und Jährlichkeit
    probabilities = [count / total_draws for count in counts_filtered]
    return_periods = [1 / prob if prob > 0 else np.inf for prob in probabilities]
    
    # Erstelle das Diagramm
    plt.figure(figsize=(15.75, 8.86))
    plt.plot(magnitudes_filtered, return_periods, marker='o', linestyle='-', label='Jährlichkeit')
    
    # Füge eine Ausgleichsgerade hinzu (log-log-Skalierung)
    log_magnitudes = np.log10(magnitudes_filtered)
    log_return_periods = np.log10(return_periods)
    coeffs = np.polyfit(log_magnitudes, log_return_periods, 1)  # Lineare Regression im log-log-Raum
    fit_line = np.poly1d(coeffs)
    plt.plot(magnitudes_filtered, 10**fit_line(log_magnitudes), linestyle='--', color='red')#, label='Ausgleichsgerade')
    
    plt.xscale('log')  # Setze die x-Achse auf eine logarithmische Skala
    plt.yscale('log')  # Setze die y-Achse auf eine logarithmische Skala
    plt.xlabel('Magnitude (m³)')
    plt.ylabel('Jährlichkeit (Jahre)')
    plt.title(f'Jährlichkeit zu Magnitude (Q_T = {Q_T}) (log-log)')
    plt.legend()
    plt.savefig('return_period_plot_with_threshold.png')
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
                pygame.time.wait(2000)  # Warte 2 Sekunden

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
#show_return_period_plot_with_threshold(drawn_cards,magnitudes, 2000)
#show_cumulative_empirical_probability(drawn_cards)
#gumbel_params = show_cumulative_empirical_probability(drawn_cards)
# Wahrscheinlichkeitsplot (CDF)
plot_empirical(drawn_cards)
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