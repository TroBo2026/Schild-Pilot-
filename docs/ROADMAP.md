# Schild Pilot – Roadmap

## Phase 0 – Grundgerüst
- [x] Repository- und Projektstruktur
- [x] Mobile Fotoauswahl/-aufnahme im Browser (UI-Prototyp)
- [x] Bildvorschau und klare Statusanzeige
- [x] Modellunabhängige Enthaltungsregel und Unit-Tests
- [ ] Modell-Schnittstelle und Inferenz in der Oberfläche

## Phase 1 – Klassifikation zugeschnittener Schilder
- [x] Datensatzstruktur-Audit mit Split- und Hashprüfung
- [x] Lizenz- und Herkunftsdokumentation für den synthetischen Fraunhofer-Pilot
- [x] Klassenmapping für die 211 Pilotklassen
- [x] Reproduzierbarer, balancierter Trainingslauf mit Manifest
- [x] Modellmetadaten und Checkpoint-Erzeugung
- [x] Evaluation mit Top-1, Top-5, Macro-Top-1, Abdeckung und Genauigkeit akzeptierter Vorhersagen
- [x] Kennzahlen je Klasse und Konfusionsmatrix
- [x] Validierungsbasiertes Schwellenwert-Skript implementieren (Mindestabdeckung 80 %; Testsplit bleibt getrennt)
- [x] Kalibrierungs- und Testlauf mit validierungsbasierten Schwellenwerten abgeschlossen (Lauf #6; siehe Trainingsbericht)
- [ ] Unabhängigen realen Foto-Benchmark mit klaren Nutzungsrechten auswählen
- [ ] Fehlersammlung und gezielte Analyse schwieriger Klassen
- [ ] Lizenz-/Rechtsprüfung für eine mögliche kommerzielle GEPARD-Nutzung

### Verifizierter synthetischer Pilot vom 13.11.2026

- 211 deutsche Klassen; 80 Trainings-, 10 Validierungs- und 10 Testbilder je Klasse
- Test: 2.110 Bilder, Top-1 87,54 %, Top-5 96,68 %
- Enthaltungsregel: 88,20 % Abdeckung; 93,93 % Genauigkeit auf akzeptierten Vorhersagen
- Trainingslauf: [GitHub Actions 43472419845](https://github.com/TroBo2026/Schild-Pilot-/actions/runs/43472419845)

**Interpretation:** Das ist ein synthetischer Klassifikationspilot, kein Nachweis für reale Straßenleistung. Der Quell-Datensatz stellt in der verwendeten Konfiguration keinen offiziellen Test-Split bereit. Val und Test sind disjunkt aus dem Quell-Split `validation` gezogen. Die Kennzahlen sind nicht auf reale Kameraaufnahmen oder andere Länder übertragbar.

## Phase 2 – Detektion in vollständigen Straßenbildern
- [x] Technisches COCO-Detektionsdaten-Audit mit Bounding-Box-, Referenz-, Klassen- und Exact-Duplicate-Prüfung vorbereiten
- [x] Kleinen Realbild-Kandidaten TrafficSigns-Raw (CC BY 4.0, 4.185 Bilder, 8.249 geprüfte Boxen) identifizieren und Lizenz-/Provenienzprüfung dokumentieren
- [x] TrafficSigns-Raw-Archiv, Lizenzdatei und SHA-256-Prüfsumme im isolierten CI-Runner verifizieren
- [x] Datensatz-Intake, YOLO-zu-COCO-Konvertierung und technisches Audit im Detektor-Workflow implementieren
- [x] Ersten CPU-Detektionsversuch ausführen und Kennzahlen dokumentieren (0 True Positives; kein brauchbares Modell)
- [x] Score-Schwellen-Sweep ausschließlich auf Validierungsdaten implementieren
- [x] Testsplit nur nach positiver Validierung freigeben; Null-TP-Ergebnisse als fehlgeschlagen markieren
- [ ] Funktionierende Detektions-Baseline mit positiver Val- und Testleistung nachweisen
- [ ] Detektor getrennt von der Klassifikation evaluieren
- [ ] Mehrere Schilder pro Foto lokalisieren
- [ ] Kleine, verdeckte, teilweise sichtbare und unbekannte Schilder berücksichtigen
- [ ] Unsichere oder nicht unterstützte Klassen explizit kennzeichnen

### Realbild-Detektionsversuch vom 13./14.11.2026

- Datensatz: TrafficSigns-Raw 0.2.0, CC BY 4.0, DOI 10.5281/zenodo.22052437
- Train 3.167 Bilder / 6.557 Boxen; Val 628 / 1.063; Test 390 / 629
- Audit: 0 Fehler, 0 Warnungen, 0 exakte Duplikate über Splits
- Erster Lauf #43492476620: 3 Epochen, zufällige Initialisierung, Score 0,25 / IoU 0,5; Val jeweils 0 TP, F1 0, steigender FP-Zähler 207 → 526 → 622
- Der Lauf hat den Testsplit nicht ausgewertet. Ein erfolgreicher Workflow-Status bedeutete nur, dass der Prozess ohne Fehler beendet wurde, nicht dass der Detektor brauchbar war.
- CPU-Training ist bis zur Korrektur manuell; Berichtsartefakte enthalten keine Modellgewichte.

## Phase 3 – Smartphone und Offline-Fähigkeit
- [ ] Modell für eine lokale Browser- oder iOS-Laufzeit exportieren
- [ ] Fotoanalyse auf dem iPhone im Stand testen
- [ ] Laufzeit, Speicherbedarf, Energiebedarf und Offline-Fähigkeit messen
- [ ] Robustheit bei Schatten, Regen, Nacht, Unschärfe und Blickwinkeln untersuchen

## Qualitäts-, Datenschutz- und Sicherheitsregeln

- Klassifikation (zugeschnittener Ausschnitt) und Detektion (vollständiges Bild) bleiben getrennte Aufgaben.
- Testdaten bleiben vom Training getrennt; abgeleitete Test-Splits werden als solche gekennzeichnet.
- Keine erfundenen Erkennungen oder kalibriert dargestellten Modell-Scores.
- Bei geringer Sicherheit: „Nicht sicher erkannt“.
- Keine wahllose Bildersammlung oder ungeprüftes Scraping.
- Keine Nutzerbilder ohne ausdrückliche Zustimmung hochladen.
- Keine Verbindung zur Fahrzeugsteuerung und keine Fahrassistenzfreigabe.
- Smartphone-Tests ausschließlich im Stand.


Aktueller Detektor-Workflow: https://github.com/TroBo2026/Schild-Pilot-/actions/workflows/real-image-detector.yml
