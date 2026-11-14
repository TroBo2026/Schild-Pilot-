# Training und Datensätze

## Leitlinie

Wir verwenden nur Datensätze, deren Herkunft und Nutzungsbedingungen dokumentiert sind. Öffentlich sichtbare Bilder sind nicht automatisch für Training oder Weitergabe freigegeben.

Für jede Quelle dokumentieren wir Lizenz, zulässige Nutzung, geografische Abdeckung, Klassen und Annotationstypen sowie die Aufteilung in Training, Validierung und Test.

## Klassifikation und Detektion

Klassifikation beantwortet: Was ist dieses bereits zugeschnittene Schild? Detektion lokalisiert Schilder in vollständigen Straßenbildern und kann mehrere Schilder pro Bild finden. Das sind getrennte Aufgaben mit unterschiedlichen Daten und Metriken.

## Datenquellen und Lizenzprüfung

GTSRB ist ein deutscher Benchmark für zugeschnittene Verkehrszeichenbilder. GTSDB ist ein separater deutscher Detektionsbenchmark mit natürlichen Straßenbildern. Vor kommerzieller Nutzung oder Weitergabe müssen die Bedingungen der konkret bezogenen Bilddateien geprüft werden.

Quellen:
- https://benchmark.ini.rub.de/gtsrb_dataset.html
- https://benchmark.ini.rub.de/about.html

## Öffentliche synthetische Pilotdaten: Fraunhofer Synset Signset Germany

- Quelle: https://huggingface.co/datasets/FraunhoferIOSB/Synset-Signset-Germany
- Auf der Dataset-Seite angegebene Lizenz: CC BY 4.0
- Veröffentlichter Umfang: 105.500 synthetisch gerenderte Bilder, 211 deutsche Verkehrszeichenklassen
- Verwendete Konfiguration: `Cycles`
- Verfügbare Quell-Splits in dieser Konfiguration: `train` und `validation`
- Aktuelle Pilot-Stichprobe: 80 Train-, 10 Val- und 10 Testbilder je Klasse
- Val und Test werden disjunkt aus dem Quell-Split `validation` gezogen. Es gibt in dieser Konfiguration keinen separat veröffentlichten offiziellen Test-Split.

**Wichtige Grenzen:** Die Bilder sind synthetisch gerenderte Szenen und keine echten Kameraaufnahmen. Der Testsplit ist eine abgeleitete Teilmenge des Quell-Validation-Splits und kein unabhängiger offizieller Benchmark-Test. Die Daten decken deutsche Zeichen ab, nicht die internationale Taxonomie. Gute Ergebnisse hier belegen keine Erkennung auf realen Straßen.

## Trainingsverfahren

Der kostenlose GitHub-Actions-CPU-Pilot verwendet ein vortrainiertes ResNet18. Der finale Residualblock (`layer4`) und Klassifikationskopf werden feinabgestimmt; frühere Merkmalsextraktionsblöcke bleiben eingefroren. Train-Augmentationen, AdamW, Cosine-Lernratenplan und Early Stopping sind aktiviert. Das beste Modell wird anhand der Validierungsgenauigkeit ausgewählt; der Testsplit bleibt bis zur finalen Evaluation unangetastet.

Lokaler Ablauf:

```bash
python -m training.prepare_synset_dataset --per-class-train 80 --per-class-val 10 --per-class-test 10
python -m training.audit_dataset --data data/signs
python -m training.train_classifier --data data/signs --epochs 8 --batch-size 32 --image-size 160 --workers 2 --patience 3
python -m training.evaluate_classifier --data data/signs/test
```

Die Auswertung enthält Top-1-, Top-5- und Macro-Top-1-Genauigkeit, Abdeckung der akzeptierten Vorhersagen, Genauigkeit auf akzeptierten Vorhersagen, Konfusionsmatrix und Kennzahlen je Klasse. Modell-Scores sind keine kalibrierten Sicherheitswahrscheinlichkeiten.

## Verifizierter Trainingslauf vom 13.11.2026

GitHub Actions: https://github.com/TroBo2026/Schild-Pilot-/actions/runs/43472419845

- Datenumfang: 16.880 Training-, 2.110 Validierungs- und 2.110 Testbilder
- 211 Klassen, 8 Epochen, bestes Validierungsergebnis: 88,72 %
- Test Top-1: 87,54 %
- Test Top-5: 96,68 %
- Enthaltungsregel: 1.861 akzeptierte und 249 zurückgewiesene Vorhersagen
- Abdeckung: 88,20 %
- Genauigkeit auf akzeptierten Vorhersagen: 93,93 %
- Dataset-Audit: keine Fehler und keine Warnungen

Diese Werte beschreiben ausschließlich diesen synthetischen Pilotlauf. Val und Test stammen aus disjunkten Teilmengen des Quell-Splits `validation`; es ist kein unabhängiger realer Foto-Benchmark. Die Modell-Scores sind nicht kalibriert. Das Ergebnis darf nicht als reale Straßen- oder Sicherheitsleistung interpretiert werden.

## Keine automatische Web-Bildersammlung

Wir aktivieren kein wahlloses Scraping. Weitere echte Bilddaten werden erst nach Prüfung von Lizenz, Herkunft, Annotationen und zulässiger Nutzung aufgenommen. Keine privaten Nutzerbilder ohne ausdrückliche Zustimmung.

## Sicherheitsgrenzen

Schild Pilot ist ein Forschungs- und Lernprototyp. Keine Fahrzeugsteuerung, keine Fahrerassistenzfreigabe und keine Tests während der Fahrt. Für eine spätere reale Anwendung wären unabhängige, geografisch getrennte reale Testdaten, Detektion, robuste Unsicherheitsbehandlung, Kalibrierung und umfangreiche Sicherheitsvalidierung erforderlich.


## Validierungsbasierte Schwellenwertwahl

Das neue Skript `training.calibrate_thresholds` liest ausschließlich den Validierungs-Split und wählt ein Paar aus Mindestscore und Abstand zur zweitbesten Klasse. Eine feste Schwellenwert-Suche in 0,05-Schritten maximiert die Genauigkeit der akzeptierten Vorhersagen unter der Nebenbedingung einer Mindestabdeckung von standardmäßig 80 %. Die resultierenden Werte werden in `artifacts/sign_classifier/calibrated_thresholds.json` gespeichert und von der anschließenden Testauswertung automatisch verwendet.

Die Kalibrierung ist eine Auswahl eines Betriebspunkts auf Validierungsdaten, keine statistische Wahrscheinlichkeitskalibrierung. Sie garantiert keine Fehlerfreiheit. Die Testdaten werden weder zur Schwellenwertwahl noch zur Modellauswahl verwendet. Der Testbericht dokumentiert die tatsächlich verwendete Schwellenwertquelle.


## Detektionsdaten: Intake-Audit und Lizenz-Screening

Für vollständige Straßenbilder ist eine getrennte COCO-artige Datenstruktur vorbereitet. `training.audit_detection_dataset` prüft die drei Splits auf fehlende Dateien, ungültige IDs/Referenzen, abweichende Kategorien, fehlerhafte Bildmaße, Bounding Boxes außerhalb des Bildes sowie byte-identische Bilder über Split-Grenzen. Das Audit ist ein technischer Vorabcheck, kein Nachweis für korrekte Labels, Szenen-Unabhängigkeit oder Nutzungsrechte. Die Unit-Tests verwenden synthetische Mini-Fixtures. Der echte Datensatz wurde erst im separaten CI-Intake vom 14.11.2026 temporär verarbeitet; die Bilder wurden nicht ins Git-Repository übernommen.

### Kandidatenprüfung (13.11.2026)

- **GTSDB:** 900 natürliche Straßenbilder, 600 Training und 300 Evaluation; Bounding-Box-Annotationen und 0–6 Schilder pro Bild. Die offizielle Benchmark-Seite beschreibt Umfang und Aufgabe, nennt auf der geprüften Seite aber keine eindeutige kommerzielle Bildlizenz. Daher vorerst nicht importieren. Quelle: https://benchmark.ini.rub.de/gtsdb_dataset.html
- **Mapillary-Bilder:** Mapillary erklärt, dass Nutzerbilder unter CC BY-SA geteilt werden. Das kann Attribution und Share-Alike-Pflichten auslösen; zusätzlich sind aktuelle Nutzungsbedingungen und die konkrete Modellnutzung zu prüfen. Nicht automatisch für ein proprietäres kommerzielles Modell freigegeben. Quelle: https://help.mapillary.com/hc/en-us/articles/115001770409-CC-BY-SA-license-for-open-data
- **BDD100K:** Die Datenlizenz erlaubt kommerzielle Nutzung laut Lizenztext nur BDD-/BAIR-Commons-Mitgliedern und deren Affiliates; das ist keine allgemeine kommerzielle Freigabe. Außerdem ist der Gesamtdatensatz groß. Daher keine Übernahme ohne geklärte Berechtigung. Quelle: https://github.com/bdd100k/bdd100k/blob/master/doc/source/download.rst
- **TT100K:** Die offizielle Projektseite nennt CC BY-NC. Wegen der Nicht-kommerziell-Bedingung nicht als Grundlage für ein späteres kommerzielles GEPARD-Produkt geeignet. Quelle: https://cg.cs.tsinghua.edu.cn/traffic-sign/

**Entscheidung:** Noch kein realer Detektionsdatensatz wird heruntergeladen oder ins Repository übernommen. GTSDB bleibt ein möglicher kleiner Forschungskandidat, bis die Originalbedingungen belastbar geklärt sind. Sekundäre Lizenzübersichten sind keine Rechtsfreigabe.


### Neuer Kandidat für einen ersten Realbild-Detektionspilot

**TrafficSigns-Raw** aus *Object-Centric Low-Data Datasets*, Version 0.2.0 (Zenodo, veröffentlicht am 22.08.2026), ist der derzeit stärkste geprüfte Kandidat für einen kleinen echten Bildpilot:

- 4.185 variable Straßenbild-Aufnahmen, 8.249 manuell überprüfte Bounding Boxes
- 3.167 Train-, 628 Val- und 390 Testbilder
- zwei Klassen: „Traffic Sign“ und „Damaged Traffic Sign“
- Direkte Veröffentlichung der TrafficSigns-Raw-Bilder; nicht mit den separat behandelten Cityscapes-/COCO-Teildatensätzen verwechseln
- Zenodo nennt CC BY 4.0 für die direkt veröffentlichten TrafficSigns-Daten; die zugehörige Arbeit beschreibt die Bildquelle als autoreneigene Straßenbilder und die Boxen als detector-vorgeschlagen und manuell überprüft

Quellen:
- Zenodo-Version 0.2.0: https://zenodo.org/records/22052437
- Begleit-Repository und Release-Dokumentation: https://github.com/Latzi/object-centric-low-data-datasets
- Begleitpublikation: https://arxiv.org/abs/2606.21113

**Entscheidung:** Für einen begrenzten, nicht sicherheitskritischen Forschungs-Pilot geeignet, vorbehaltlich erneuter Prüfung der mitgelieferten Lizenzdatei, Attribution, Datenschutz-/Bildinhalte und Prüfsummen beim konkreten Download. Die zwei Klassen sind nur eine grobe Schilder-/Zustandsdetektion; sie ersetzen keine 211-Klassen-Schilderklassifikation und bilden keine internationale Taxonomie ab. Der Datensatz ist relativ klein und visuell eher sauber; Ergebnisse müssen entsprechend eingeordnet werden. Vor jeder Produkt- oder GEPARD-Nutzung ist eine gesonderte Rechte- und Datenschutzprüfung erforderlich.

Planungsstand vor dem CI-Intake: Der Datensatz war noch nicht ins Repository geladen. Diese Planung wurde am 14.11.2026 im isolierten CI-Runner umgesetzt; siehe den nachfolgenden Ergebnisbericht. Der Datensatz bleibt weiterhin außerhalb des Git-Repositories. Die gelieferten Train/Val/Test-Splits wurden unverändert übernommen; der erste Trainingsversuch verwendete Train und Val, der Testsplit blieb unberührt.



## Verbesserter synthetischer Klassifikationslauf #6 (13.11.2026)

GitHub Actions: https://github.com/TroBo2026/Schild-Pilot-/actions/runs/43483453551

- 211 Klassen; 16.880 Trainings-, 2.110 Validierungs- und 2.110 abgeleitete Testbilder
- Bestes Validierungsergebnis: 88,34 % (Epoche 8); Trainingsgenauigkeit am Ende: 96,39 %
- Test Top-1: 87,39 %; Top-5: 96,73 %
- Auf Validierungsdaten gewählter Betriebspunkt: Mindestscore 0,60, Mindestabstand 0,35; Validierungsabdeckung 80,24 %, Genauigkeit der akzeptierten Vorhersagen 97,05 %
- Auf dem Testsplit: 1.660 akzeptierte und 450 zurückgewiesene Vorhersagen; Abdeckung 78,67 %; Genauigkeit auf akzeptierten Vorhersagen 97,17 %

Gegenüber Lauf #4 ist Top-1 geringfügig niedriger (87,39 % statt 87,54 %), Top-5 geringfügig höher (96,73 % statt 96,68 %). Die hohe Genauigkeit der akzeptierten Vorhersagen geht mit einer Enthaltung bei 21,33 % der Testbilder einher. Die auf Validierungsdaten angestrebte Mindestabdeckung von 80 % wurde im Test nicht ganz erreicht. Es handelt sich weiterhin um synthetische, zugeschnittene deutsche Schilderbilder; kein realer Straßen-Benchmark und keine Sicherheitsvalidierung.

Hinweis zur Auswertung: Die Schwellenwerte wurden ausschließlich auf dem Val-Split gewählt und aus artifacts/sign_classifier/calibrated_thresholds.json übernommen. threshold_source=model_dir_default bezeichnet den regulären Datei-Ladepfad, nicht die Verwendung der festen CLI-Standardwerte.

## Realbild-Detektionspilot: TrafficSigns-Raw 0.2.0

Quelle: [Zenodo 22052437](https://zenodo.org/records/22052437), Version 0.2.0, DOI [10.5281/zenodo.22052437](https://doi.org/10.5281/zenodo.22052437). Urheber laut Zenodo: Vasile Marian, Yong-Bin Kang und Alexander Buddery. Die offizielle Datensatzseite und die beigefügte TrafficSigns-spezifische Lizenznotiz nennen CC BY 4.0 für die direkt veröffentlichten TrafficSigns-Raw-Bilder und YOLO-Annotationen. Die Lizenz verlangt Attribution zur begleitenden Arbeit, zum Repository-Release und zur DOI-Veröffentlichung.

- Archiv-SHA-256, vor Extraktion im CI geprüft: `e1e162d114cfe14b209ab7614511524b0c558db72935d3e32c096f87150aff86`
- Train: 3.167 Bilder / 6.557 Boxen
- Val: 628 Bilder / 1.063 Boxen
- Test: 390 Bilder / 629 Boxen
- Gesamt: 4.185 Bilder / 8.249 Boxen
- Klassen: `Traffic Sign`, `Damaged Traffic Sign`
- Nur `traffic_signs_raw/` und die passende Lizenznotiz wurden extrahiert. Andere Archivbestandteile, insbesondere Cityscapes- und COCO-Daten, wurden nicht verwendet.
- Die Bilder und Modellgewichte wurden nicht ins Git-Repository übernommen.

**Geografische Einschränkung:** Die offizielle Datensatzbeschreibung belegt keine globale Abdeckung. Zwei Objekt-/Zustandsklassen sind keine Verkehrszeichen-Taxonomie. Der Datensatz ist ein begrenzter Detektionspilot, keine globale Klassifikationsgrundlage.

### Erster CPU-Trainingslauf

GitHub Actions: https://github.com/TroBo2026/Schild-Pilot-/actions/runs/43492476620

Das technische Daten-Audit war sauber: 0 Fehler, 0 Warnungen und keine byte-identischen Bilder über Train/Val/Test. Der anschließende Faster-R-CNN-MobileNetV3-320-Lauf wurde mit zufälliger Initialisierung und drei CPU-Epochen ausgeführt. Er war prozessseitig erfolgreich, aber fachlich nicht brauchbar:

| Epoche | Train-Loss | TP | FP | FN | Precision | Recall | F1 |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 0,2597 | 0 | 207 | 1.063 | 0 % | 0 % | 0 |
| 2 | 0,2950 | 0 | 526 | 1.063 | 0 % | 0 % | 0 |
| 3 | 0,3529 | 0 | 622 | 1.063 | 0 % | 0 % | 0 |

Die alte Auswertung nutzte nur IoU 0,5 und Score 0,25. Der steigende False-Positive-Zähler und die fehlenden Treffer zeigen, dass der Lauf keine brauchbare Detektions-Baseline geliefert hat. Der offizielle Testsplit wurde in diesem Lauf nicht ausgewertet. Der frühere Workflow meldete trotzdem `success`, weil er nur den Prozessabschluss prüfte; das war kein Qualitätsnachweis.

### Korrektur im aktuellen Code

- `training/detection_metrics.py`: neue dependency-freie IoU-, 1:1-Matching- und Score-Schwellen-Sweep-Logik.
- `training/train_detector.py`: Vorhersagen werden einmal gesammelt; die Score-Schwelle wird ausschließlich auf Val anhand F1 ausgewählt. Der Testsplit wird nur nach mindestens einem echten Val-Treffer ausgewertet und verwendet unverändert die Val-Schwelle.
- Ein Lauf mit 0 True Positives auf Val oder Test wird als fehlgeschlagen beendet. Testdaten werden bei Null-TP auf Val nicht geöffnet.
- `.github/workflows/real-image-detector.yml`: der lange CPU-Lauf ist bis zur nächsten Prüfung nur manuell startbar. Berichtsartefakte enthalten JSON-Metriken und Lizenz-/Auditnachweise, keine Modellgewichte.

Es wurde in dieser Entwicklungsrunde kein neues Modelltraining gestartet. Die Ursache für den Null-TP-Lauf ist noch nicht abschließend geklärt. Vor einem weiteren langen CPU-Lauf müssen die neuen Metriktests und der Code-Review erfolgreich sein. Vortrainierte TorchVision-Gewichte werden nicht eingesetzt, solange ihre konkreten, gegebenenfalls aus den Trainingsdaten abgeleiteten Nutzungsbedingungen nicht für den Einsatzzweck geklärt sind.

## Keine automatische Web-Bildersammlung

Wir aktivieren kein wahlloses Scraping. Weitere echte Bilddaten werden erst nach Prüfung von Lizenz, Herkunft, Annotationen und zulässiger Nutzung aufgenommen. Keine privaten Nutzerbilder ohne ausdrückliche Zustimmung.

## Sicherheitsgrenzen

Schild Pilot ist ein Forschungs- und Lernprototyp. Keine Fahrzeugsteuerung, keine Fahrerassistenzfreigabe und keine Tests während der Fahrt. Für eine spätere reale Anwendung wären unabhängige, geografisch getrennte reale Testdaten, Detektion, robuste Unsicherheitsbehandlung, Kalibrierung und umfangreiche Sicherheitsvalidierung erforderlich.
