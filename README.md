# Schild Pilot

Kostenlos entwickelter Lern- und Forschungsprototyp zur Verkehrszeichenerkennung.

## Ziel und Grenzen

Schild Pilot entwickelt zunächst die Klassifikation bereits zugeschnittener Verkehrszeichen. Danach folgen Detektion in vollständigen Straßenfotos und eine lokale Smartphone-Laufzeit. Das Projekt ist **keine Fahrassistenz** und wird nicht mit Fahrzeugsteuerungen verbunden.

## Architektur

1. Bildauswahl oder spätere Fotoaufnahme
2. **Detektion:** Schilderpositionen im Gesamtbild finden; ein experimenteller Detektor existiert, hat aber noch keine brauchbaren Treffer nachgewiesen
3. **Klassifikation:** einen zugeschnittenen Schild-Ausschnitt einer Klasse zuordnen
4. **Unsicherheit:** bei schwachen oder mehrdeutigen Ergebnissen keine definitive Aussage
5. **Evaluation:** getrennte Daten-Splits, Kennzahlen je Klasse und Konfusionsmatrix

## Projektstatus

**Phase 0:** mobiles Foto-Frontend, Bildvorschau und Grundstruktur vorhanden. Die Oberfläche führt noch keine Modellinferenz aus.

**Phase 1:** ein ResNet18-Klassifikationspilot wurde erfolgreich trainiert und ausgewertet. Der aktuelle Pilot umfasst 211 deutsche Verkehrszeichenklassen aus synthetisch gerenderten Bildern. Das Modell klassifiziert zugeschnittene Schilder, es erkennt noch keine Schilder in vollständigen Fotos.

**Letzter erfolgreicher Trainingslauf:** 13. November 2026, GitHub Actions [Run 43472419845](https://github.com/TroBo2026/Schild-Pilot-/actions/runs/43472419845), Trainingscode-Commit `d65909aff7c8b2816ca2d536036954c3f3498929`. Der aktuelle Branch `main` enthält zusätzlich die nachfolgende Korrektur der Split-Provenienz.

| Kennzahl | Ergebnis |
|---|---:|
| Klassen | 211 |
| Training | 16.880 Bilder (80 je Klasse) |
| Validierung | 2.110 Bilder (10 je Klasse) |
| Test | 2.110 Bilder (10 je Klasse) |
| Test Top-1 | 87,54 % |
| Test Top-5 | 96,68 % |
| Abdeckung der akzeptierten Vorhersagen | 88,20 % |
| Genauigkeit unter akzeptierten Vorhersagen | 93,93 % |

Die Enthaltungsregel hat 249 von 2.110 Testbildern als unsicher zurückgewiesen. Die Scores sind nicht kalibrierte Sicherheitswahrscheinlichkeiten.

**Wichtige Einschränkung der Evaluation:** Die Quelle veröffentlicht in der verwendeten Konfiguration keinen offiziellen Test-Split. Validierung und Test wurden als disjunkte Teilmengen aus dem Quell-Split `validation` gezogen. Die Werte sind daher ein reproduzierbarer interner Pilotvergleich, kein unabhängiger Benchmark-Nachweis.

**Phase 2:** Die COCO-Intake- und Audit-Pipeline ist implementiert. TrafficSigns-Raw 0.2.0 wurde in einem isolierten GitHub-Actions-Lauf mit SHA-256 und CC-BY-4.0-Lizenznotiz geprüft; der Datensatz wurde nur im temporären Runner-Arbeitsbereich verarbeitet und nicht ins Repository übernommen. Der erste Faster-R-CNN-CPU-Versuch lief technisch durch, erreichte auf der Validierung aber in allen drei Epochen 0 True Positives. Das ist keine brauchbare Detektions-Baseline. Die neue Auswertung sweeped Score-Schwellen auf Val und lässt Test nur nach positivem Val-Ergebnis zu.

**Phase 3:** lokale Smartphone-/iPhone-Laufzeit und Offline-Tests; noch offen.

## Daten und Lizenzen

Verwendete Pilotquelle: [Fraunhofer IOSB Synset Signset Germany](https://huggingface.co/datasets/FraunhoferIOSB/Synset-Signset-Germany), Konfiguration `Cycles`, auf der Dataset-Seite mit CC BY 4.0 angegeben. Sie enthält synthetisch gerenderte Szenen, keine echten Kameraaufnahmen. Die Quelle deckt deutsche Verkehrszeichen ab und ist keine globale Taxonomie.

Öffentlich sichtbare Bilder sind nicht automatisch frei für Training oder Weitergabe. TrafficSigns-Raw 0.2.0 ist laut Zenodo-Datensatzseite und beigefügter Lizenznotiz unter CC BY 4.0 veröffentlicht; die erforderliche Attribution ist in [training/README.md](training/README.md) dokumentiert. Die geografische Abdeckung der Quelle ist für unseren Pilot noch nicht ausreichend charakterisiert. Eine gesonderte rechtliche Prüfung für eine kommerzielle GEPARD-Anwendung ist nicht erfolgt. Weitere Quellen bleiben bis zur Prüfung ihrer Originalbedingungen gesperrt.

## Technik

- Web-Prototyp: HTML, CSS, JavaScript
- Training und Evaluation: Python, PyTorch, torchvision, Pillow
- aktueller Klassifikator: ResNet18, Feinabstimmung von `layer4` und Klassifikationskopf
- spätere lokale Laufzeit: ONNX oder Core ML nach Kompatibilitäts- und Laufzeitmessungen

## Tests

Die Tests verwenden die Python-Standardbibliothek und Pillow; der CI-Workflow installiert Pillow automatisch:

```bash
python -m unittest discover -s tests -v
```

GitHub Actions führt diese Tests bei Änderungen an `main` und bei Pull Requests automatisch aus. Trainingsläufe sind separat und werden in den jeweiligen Workflow-Ergebnissen dokumentiert.

## Web-Prototyp starten

Die Dateien liegen in `web/`. Für Kamerazugriff im Browser sind üblicherweise HTTPS und eine ausdrückliche Berechtigung nötig. Die aktuelle Oberfläche ist eine Foto-/Vorschau-Demo, keine verbundene KI-Inferenz.

## Sicherheit und Datenschutz

- Smartphone-Tests ausschließlich im Stand; Gerät während der Fahrt nicht bedienen.
- Keine Fahrzeugsteuerung und keine sicherheitskritischen Entscheidungen.
- Ergebnisse können falsch oder unvollständig sein.
- Nutzerbilder werden nicht ohne ausdrückliche Zustimmung hochgeladen.


## Aktueller Detektionsbericht

Der erste Realbild-Detektionslauf (GitHub Actions [Run 43492476620](https://github.com/TroBo2026/Schild-Pilot-/actions/runs/43492476620)) verarbeitete 3.167 Trainings-, 628 Validierungs- und 390 Testbilder. Das technische Audit fand keine Fehler, Warnungen oder byte-identischen Duplikate über die Splits. Der damalige Detektor erzielte auf Val bei IoU 0,5 und Score 0,25 jedoch 0 True Positives in allen drei Epochen. Der Job war technisch erfolgreich, das Modell fachlich nicht brauchbar. Der Testsplit wurde in diesem Lauf nicht ausgewertet. Details und Korrekturmaßnahmen: [Detektionsbericht](docs/DETECTION_PILOT_REPORT.md).

Das CPU-Training ist bis zur Überprüfung der neuen Metrik- und Qualitätsschranke manuell auslösbar, nicht mehr bei jedem Push. Keine Modellgewichte werden automatisch in Git oder CI-Berichte hochgeladen.
