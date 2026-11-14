# Detektionspilot – technischer Bericht vom 14.11.2026

## Repository-Stand

- Repository: `TroBo2026/Schild-Pilot-`
- Branch: `main`
- Vorheriger Stand: `81a2bef6ea35009abc0d9781d6e7db282cdd1b38`
- Es wurden keine anderen Repositories oder Projekte verändert.

## Datensatz und Rechte

TrafficSigns-Raw 0.2.0 aus *Object-Centric Low-Data Datasets*, Zenodo DOI 10.5281/zenodo.22052437. Zenodo nennt Vasile Marian, Yong-Bin Kang und Alexander Buddery als Urheber und CC BY 4.0 für die direkt veröffentlichten TrafficSigns-Daten. Die datensatzspezifische Lizenznotiz im Archiv bestätigt diese Lizenz und verlangt Attribution.

Archiv-SHA-256 vor Extraktion geprüft: `e1e162d114cfe14b209ab7614511524b0c558db72935d3e32c096f87150aff86`.

| Split | Bilder | Boxen |
|---|---:|---:|
| Train | 3.167 | 6.557 |
| Val | 628 | 1.063 |
| Test | 390 | 629 |
| Gesamt | 4.185 | 8.249 |

Nur TrafficSigns-Raw und die zugehörige Lizenznotiz wurden in den temporären CI-Runner extrahiert. Es wurden keine Bilder oder Gewichte ins Repository übernommen; Cityscapes- und COCO-Unterdaten wurden nicht verwendet. Die geografische Abdeckung ist nicht als global belegt. Die zwei Klassen `Traffic Sign` und `Damaged Traffic Sign` sind keine nationale oder globale Zeichenklassifikation.

## Erster Detektionslauf

GitHub Actions: [Run 43492476620](https://github.com/TroBo2026/Schild-Pilot-/actions/runs/43492476620).

- COCO-Audit: 0 Fehler, 0 Warnungen, 0 exakte Duplikate über die Splits.
- Modell: Faster R-CNN MobileNetV3 320, zufällige Initialisierung, 3 CPU-Epochen.
- Metrik: greedy 1:1-Matching, IoU 0,5, damalige feste Score-Schwelle 0,25.
- Val: in allen drei Epochen 0 TP und F1 0; FP stiegen von 207 über 526 auf 622; FN blieben 1.063.
- Train-Loss stieg von 0,2597 auf 0,3529.
- Testsplit wurde nicht ausgewertet.

Der Workflow war prozessseitig erfolgreich, das Modell fachlich nicht. Das frühere Skript hatte keine Qualitätsschranke und meldete deshalb `success`, obwohl keine einzige korrekte Detektion gefunden wurde.

## Änderungen in diesem Entwicklungslauf

- `training/detection_metrics.py`: dependency-freie IoU- und 1:1-Matching-Funktionen sowie Score-Schwellen-Sweep.
- `tests/test_detection_metrics.py`: Tests für IoU, Klassengleichheit, 1:1-Matching, Schwellenwertauswahl und ungültige Eingaben.
- `training/train_detector.py`: Schwellenwertauswahl nur auf Val; Test wird nur nach positiver Val-Detektion ausgewertet und nutzt die auf Val gewählte Schwelle. Null-TP auf Val oder Test beendet den Lauf mit Fehlerstatus.
- `.github/workflows/real-image-detector.yml`: CPU-Training ist bis zur Prüfung manuell auslösbar; Upload umfasst nur Berichte, Audit und Lizenznotiz, keine Modellgewichte.
- `README.md`, `training/README.md`, `docs/ROADMAP.md`, `docs/INTERNATIONAL_DATA_STRATEGY.md`: Status, Lizenz, Attribution, echte Ergebnisse und Grenzen aktualisiert.

## Noch offene Fragen

1. Warum erzeugt die zufällig initialisierte Faster-R-CNN-Baseline trotz Training keine korrekten Boxen?
2. Sind Bild-/Box-Skalierung, Klassenverteilung und Annotationsqualität durch Stichproben visuell plausibel?
3. Lässt sich mit einem kleineren, gezielten Trainingslauf eine positive Val-Detektion erreichen, ohne den CPU-Budgetrahmen erneut auszureizen?
4. Vortrainierte Gewichte werden nicht genutzt, bis deren konkrete Lizenz- und Trainingsdatenbedingungen geklärt sind.

## Nächster sinnvoller Schritt

Zuerst Metrik- und Konvertierungstests ausführen und die Boxen anhand weniger, lizenzierter Beispielbilder visuell prüfen. Erst danach einen bewusst begrenzten manuellen Trainingslauf starten. Keine Testdaten zur Schwellenwert- oder Modellwahl verwenden.

Schild Pilot bleibt ein Lern- und Forschungsprototyp, keine Fahrassistenz. Keine Fahrzeugsteuerung; keine Nutzerbilder ohne ausdrückliche Zustimmung hochladen.
