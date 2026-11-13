# Evaluation

Ein Modell darf nicht allein anhand seiner Trainingsgenauigkeit bewertet werden.

Mindestens zu erfassen:
- Top-1 Accuracy und pro-Klasse Precision/Recall
- Confusion Matrix, insbesondere für visuell ähnliche Schilder
- Anteil der Enthaltungen bei der Unsicherheitsregel
- Fehlerquote unter den akzeptierten Vorhersagen
- Ergebnisse auf getrennten, nicht zum Training verwendeten Testbildern
- Robustheit bei Unschärfe, Helligkeitswechsel, Perspektive, Verdeckung und Kompression

Bei Video- oder Serienbildern dürfen benachbarte Frames desselben physischen Schilds nicht über Training und Test verteilt werden. Sonst entsteht Datenleckage.

Eine hohe Benchmark-Genauigkeit ist kein Nachweis für Eignung im Straßenverkehr. Das Projekt bleibt ein nicht sicherheitskritischer Prototyp.
