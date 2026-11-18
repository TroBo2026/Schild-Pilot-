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


## Folgeprüfung und Metrik-Härtung vom 16.11.2026

Nach Prüfung des aktuellen `main`-Stands wurden die Eingabegrenzen der Detektionsmetriken weiter verschärft:

- Box-Koordinaten, Scores und Schwellenwerte akzeptieren nur echte numerische Werte; boolesche Werte, numerische Zeichenketten, fehlende Werte und nicht-endliche Zahlen werden abgewiesen.
- Klassen-IDs müssen nicht-negative ganze Zahlen sein; Dezimalwerte, Zeichenketten, boolesche und negative IDs werden nicht stillschweigend umgewandelt.
- Die vorhandene IoU-Grenze bleibt strikt im Bereich `(0, 1]`.

Dafür wurden `training/detection_metrics.py` und `tests/test_detection_metrics.py` geändert. GitHub Actions Run 70 auf `main` (Commit `fd41389334005d2af590a80a72bd7756864d8228`) führte die Python-Kompilierungsprüfung und **36 Unit-Tests erfolgreich** aus: https://github.com/TroBo2026/Schild-Pilot-/actions/runs/43928494962

In diesem Lauf wurde kein Datensatz heruntergeladen, kein Modell trainiert und kein Modellgewicht hochgeladen. Die Metrik bleibt ein diagnostisches greedy 1:1-IoU-Verfahren und ist kein COCO-mAP-Ersatz. Die reale Detektionsleistung ist weiterhin nicht nachgewiesen; vor einem neuen Training müssen Box-Skalierung, Klassenmapping und Annotationen anhand lizenzierter Beispiele geprüft werden.

## Folgeprüfung und Detektionsdaten-Audit vom 17.11.2026

Der COCO-Intake-Audit wurde gehärtet, damit fehlerhafte JSON-Typen nicht erst im DataLoader oder in TorchVision auffallen:

- Kategorie-, Bild- und Annotations-IDs müssen positive JSON-Ganzzahlen sein; boolesche, negative, dezimale, textuelle und nicht-hashbare Werte werden mit Auditfehlern abgewiesen.
- Bildbreite und -höhe müssen positive Ganzzahlen sein. Boolesche Werte, Fließkommawerte, Null und nicht-endliche Werte werden nicht akzeptiert.
- Boolesche Bounding-Box-Koordinaten werden nicht mehr als Zahlen durchgelassen.
- Der Auditbericht enthält jetzt Annotationen je Kategorie, Bilder ohne gültige Annotationen sowie Minimum/Median/Maximum des Bounding-Box-Flächenanteils am jeweiligen Bild. Diese Kennzahlen helfen bei der späteren Prüfung von Klassenverteilung und Box-Skalierung; sie ersetzen keine visuelle Stichprobe.

Die vorhandenen Mini-Fixtures wurden um ungültige ID-/Dimensionsfälle erweitert. Die Tests verwenden ausschließlich synthetische Testbilder; der reale TrafficSigns-Raw-Datensatz wurde in dieser Runde nicht erneut heruntergeladen oder verarbeitet.

Der Null-TP-Trainingslauf ist damit noch nicht erklärt. Der nächste diagnostische Schritt bleibt die visuelle Stichprobe der Original-Boxen und der Vergleich von Klassenverteilung und Box-Flächenanteilen aus dem erweiterten Audit. Kein Training wurde gestartet.

### CI-Nachkorrektur zum Audit (17.11.2026)

Der erste Lauf nach der Audit-Erweiterung (GitHub Actions Run 72) kompilierte alle Module, führte 40 Tests aus und fand einen Assertion-Fehler: Die neue Boolean-Box-Prüfung erkannte den ungültigen Wert korrekt, aber der Meldungstext enthielt nicht die vom Test erwartete Formulierung „Bounding Box“. Die fachliche Validierung war aktiv; die Abweichung lag im Fehlertext. Der Meldungstext wurde präzisiert. Der Korrekturlauf muss noch erfolgreich abgeschlossen werden, bevor die Änderung als vollständig verifiziert gilt.

### Ergebnis der CI-Nachkorrektur

Der Meldungstext wurde in Commit `80a1bffed3ad698e774c60bba6349acca81919fe` präzisiert. GitHub Actions Run 73 auf `main` war erfolgreich: Python-Kompilierung bestanden und **40 Unit-Tests bestanden**. Die ursprüngliche Assertion-Abweichung ist damit behoben. Link: https://github.com/TroBo2026/Schild-Pilot-/actions/runs/44152462092


## Visuelle Stichprobenprüfung der Detektions-Annotationen (18.11.2026)

Zur Vorbereitung der noch ausstehenden Sichtprüfung wurde `training.preview_detection_annotations` ergänzt. Das Werkzeug wählt aus einem lokalen COCO-Split deterministisch bis zu 12 annotierte Bilder aus, zeichnet die Ground-Truth-Bounding-Boxes samt Klassennamen ein und erstellt eine statische Offline-Ansicht (`index.html`) sowie `report.json`.

- Eingaben: lokaler Datensatzordner und expliziter Split (Standard: `val`).
- Sicherheitsprüfungen: Bildpfade müssen innerhalb des jeweiligen Bildordners liegen; IDs, Klassenreferenzen, Box-Grenzen und tatsächliche Bilddimensionen werden geprüft.
- Datenschutz: keine Netzwerkzugriffe, keine Uploads, keine Änderung der Quelldateien. Vorschau-Ausgaben liegen unter `artifacts/`, das in `.gitignore` ausgeschlossen ist.
- Reproduzierbarkeit: feste Seed-Auswahl; die ausgewählten Bild-IDs stehen im JSON-Bericht.
- Abhängigkeiten: ausschließlich Pillow, bereits in `requirements.txt` und im Test-Workflow vorhanden.

GitHub Actions [Run 75](https://github.com/TroBo2026/Schild-Pilot-/actions/runs/44373580395) auf `main`, Commit `08ba23de8175f7124e7e1e1404b7314aa261fd9c`: Python-Kompilierung erfolgreich, **45 Unit-Tests bestanden**. Die fünf neuen Tests prüfen die Offline-Erstellung, HTML-Escaping, reproduzierbare Auswahl, Pfad-Traversal-Abwehr, Box-Grenzen und Bildmaß-Konsistenz.

**Wichtige Einschränkung:** Die Vorschaufunktion wurde in CI ausschließlich mit synthetischen Mini-Bildern getestet. Der reale TrafficSigns-Raw-Datensatz liegt nicht im Repository und wurde in diesem Lauf nicht erneut heruntergeladen. Deshalb wurden noch keine echten Datensatzbilder visuell geprüft und keine Ursache für die Null-TP-Detektion bestätigt. Vor einem Training muss die Vorschau lokal auf dem bereits rechtmäßig bezogenen Datensatz ausgeführt und stichprobenartig kontrolliert werden.

In diesem Lauf wurde kein Modell trainiert, kein Datensatz heruntergeladen und kein Modellgewicht hochgeladen.
