# Core

Hier liegen modellunabhängige Komponenten. `decision.py` erzwingt eine konservative Enthaltungsregel: Wenn der höchste Modellscore zu niedrig ist oder die zwei besten Klassen zu ähnlich liegen, wird kein finales Label ausgegeben.

Die Grenzwerte sind vorläufige Entwicklungsparameter. Sie müssen anhand eines unabhängigen Validierungsdatensatzes geprüft und später kalibriert werden. Softmax-Scores sind nicht automatisch verlässliche Wahrscheinlichkeiten.
