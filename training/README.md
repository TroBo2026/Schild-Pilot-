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

Für vollständige Straßenbilder ist eine getrennte COCO-artige Datenstruktur vorbereitet. `training.audit_detection_dataset` prüft die drei Splits auf fehlende Dateien, ungültige IDs/Referenzen, abweichende Kategorien, fehlerhafte Bildmaße, Bounding Boxes außerhalb des Bildes sowie byte-identische Bilder über Split-Grenzen. Das Audit ist ein technischer Vorabcheck, kein Nachweis für korrekte Labels, Szenen-Unabhängigkeit oder Nutzungsrechte. Die Tests verwenden synthetische Mini-Fixtures; es wurden keine echten Straßendatensätze importiert.

### Kandidatenprüfung (13.11.2026)

- **GTSDB:** 900 natürliche Straßenbilder, 600 Training und 300 Evaluation; Bounding-Box-Annotationen und 0–6 Schilder pro Bild. Die offizielle Benchmark-Seite beschreibt Umfang und Aufgabe, nennt auf der geprüften Seite aber keine eindeutige kommerzielle Bildlizenz. Daher vorerst nicht importieren. Quelle: https://benchmark.ini.rub.de/gtsdb_dataset.html
- **Mapillary-Bilder:** Mapillary erklärt, dass Nutzerbilder unter CC BY-SA geteilt werden. Das kann Attribution und Share-Alike-Pflichten auslösen; zusätzlich sind aktuelle Nutzungsbedingungen und die konkrete Modellnutzung zu prüfen. Nicht automatisch für ein proprietäres kommerzielles Modell freigegeben. Quelle: https://help.mapillary.com/hc/en-us/articles/115001770409-CC-BY-SA-license-for-open-data
- **BDD100K:** Die Datenlizenz erlaubt kommerzielle Nutzung laut Lizenztext nur BDD-/BAIR-Commons-Mitgliedern und deren Affiliates; das ist keine allgemeine kommerzielle Freigabe. Außerdem ist der Gesamtdatensatz groß. Daher keine Übernahme ohne geklärte Berechtigung. Quelle: https://github.com/bdd100k/bdd100k/blob/master/doc/source/download.rst
- **TT100K:** Die offizielle Projektseite nennt CC BY-NC. Wegen der Nicht-kommerziell-Bedingung nicht als Grundlage für ein späteres kommerzielles GEPARD-Produkt geeignet. Quelle: https://cg.cs.tsinghua.edu.cn/traffic-sign/

**Entscheidung:** Noch kein realer Detektionsdatensatz wird heruntergeladen oder ins Repository übernommen. GTSDB bleibt ein möglicher kleiner Forschungskandidat, bis die Originalbedingungen belastbar geklärt sind. Sekundäre Lizenzübersichten sind keine Rechtsfreigabe.
