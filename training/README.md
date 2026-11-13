# Training und Datensätze

## Leitlinie
Wir verwenden nur Datensätze, deren Herkunft und Nutzungsbedingungen dokumentiert sind. Öffentlich sichtbare Bilder sind nicht automatisch für Training oder Weitergabe freigegeben.

Für jede Quelle dokumentieren wir:
- Lizenz und erlaubte Nutzung (Training, Bearbeitung, Weitergabe)
- Länder- und Regionenabdeckung
- Klassen und Annotationstypen
- Aufteilung in Training, Validierung und unabhängigen Test

## Erster deutscher Benchmark: GTSRB
Die offizielle Benchmark-Seite beschreibt GTSRB als deutschen Klassifikationsdatensatz mit 43 Klassen und mehr als 50.000 Bildern. Sie sagt, dass die Daten frei genutzt werden können und bittet um Zitierung der Originalveröffentlichung. Die dort erwähnte GPLv2-Angabe bezieht sich auf die Ergebnisanalyse-Software, nicht pauschal auf die Bilddaten.

Quellen:
- Offizielle Datensatzseite: https://benchmark.ini.rub.de/gtsrb_dataset.html
- Benchmark-Übersicht: https://benchmark.ini.rub.de/about.html
- Originalarbeit: Stallkamp et al., IJCNN 2011, Seiten 1453–1460.

Für den ersten lokalen Lernversuch ist GTSRB damit ein sinnvoller Kandidat, sofern wir die offiziellen Hinweise und die Herkunft der konkret bezogenen Dateien beibehalten. Vor kommerzieller Nutzung, Weitergabe oder Einbau der Bilder in eine veröffentlichte App müssen die Bedingungen erneut geprüft werden. Der Datensatz deckt nur deutsche Verkehrszeichen ab.

## Klassifikation und Detektion
GTSRB enthält bereits zugeschnittene Schilder. Es beantwortet „Was ist dieses Schild?“, aber nicht allein „Wo ist das Schild im gesamten Straßenfoto?“.

Für Detektion gibt es separat GTSDB, einen Benchmark mit natürlichen Vollbildern, in denen die Position von Schildern lokalisiert werden soll. Die offizielle Benchmark-Übersicht beschreibt GTSDB als Detection-Aufgabe. Seine kleine Größe macht ihn zu einem Einstiegspunkt, nicht zu einer ausreichenden globalen Trainingsbasis.

## Erste Lernstrategie
Transfer Learning: Ein vortrainiertes Bildmodell wird an unsere Schildklassen angepasst. Das ist üblicherweise effizienter als Training von Grund auf. Die offizielle PyTorch-Anleitung erklärt Fine-Tuning und das Einfrieren vortrainierter Netzwerkschichten:
https://docs.pytorch.org/tutorials/beginner/transfer_learning_tutorial.html

## Globale Abdeckung
Nach dem deutschen Prototyp brauchen wir weitere Datensätze mit sauber dokumentierten Nutzungsbedingungen und unterschiedlichen nationalen Verkehrszeichen-Taxonomien. Klassen dürfen nicht allein aufgrund ähnlicher Symbole zusammengelegt werden: Bedeutung und rechtliche Zuordnung können je Land abweichen.

## Lokale Datenprüfung und Evaluation

Vor dem Training die Datenstruktur prüfen:

```bash
python -m training.audit_dataset --data data/signs
```

Der Audit prüft fehlende Splits/Klassen, leere Klassen und identische Dateien über mehrere Splits hinweg. Er erkennt keine nahezu identischen Bilder oder zusammengehörigen Videoframes; dafür ist zusätzlich eine szenen- bzw. trackbasierte Trennung nötig.

Nach dem Training ausschließlich den separaten Testsplit auswerten:

```bash
python -m training.evaluate_classifier --data data/signs/test
```

Erzeugt werden `artifacts/evaluation/metrics.json` und `confusion_matrix.csv`. Die Kennzahlen sind Forschungsmetriken, keine Sicherheitsfreigabe.

## Keine automatische Web-Bildersammlung
Wir aktivieren kein wahlloses Scraping. Bilder werden erst nach Lizenzprüfung und sauberer Kennzeichnung aufgenommen.

## Öffentliche Pilotdaten: Fraunhofer Synset Signset Germany

Für einen reproduzierbaren ersten Trainingslauf ist jetzt ein begrenzter, klassenbalancierter Import vorbereitet:
- Quelle: https://huggingface.co/datasets/FraunhoferIOSB/Synset-Signset-Germany
- Angegebene Lizenz auf der Dataset-Seite: CC BY 4.0
- Umfang der Quelle: 105.500 synthetisch gerenderte Bilder, 211 deutsche Verkehrszeichenklassen
- Verwendete Konfiguration: Cycles
- Pilot-Stichprobe: 20 Train-, 5 Val- und 5 Testbilder je Klasse (sofern in allen Quell-Splits vorhanden)
- Der Testsplit stammt getrennt aus dem veröffentlichten Quell-Testsplit.

Wichtig: Das sind **synthetisch gerenderte Szenen und keine echten Kameraaufnahmen**. Sie eignen sich für einen technischen Pipeline-Pilot, belegen aber keine Erkennungsleistung auf realen Straßenbildern. Die Daten decken deutsche Zeichen ab und bilden keine internationale Taxonomie. Die Dataset-Veröffentlichung warnt ausdrücklich vor sicherheitskritischen Einsätzen ohne zusätzliche Eignungsprüfung.

Vorbereitung lokal:

```bash
python -m pip install -r requirements.txt
python -m training.prepare_synset_dataset --per-class-train 20 --per-class-val 5 --per-class-test 5
python -m training.audit_dataset --data data/signs
python -m training.train_classifier --data data/signs --epochs 2 --batch-size 32 --image-size 128
python -m training.evaluate_classifier --data data/signs/test
```

Ein GitHub-Actions-Workflow führt denselben begrenzten CPU-Pilotlauf aus und veröffentlicht Modell, Kennzahlen und Quellenmanifest als kurzlebiges Artefakt. Die Gewichte werden nicht ins Repository eingecheckt. Ein erfolgreicher Workflow ist erst nach Abschluss und Prüfung seiner Logs bestätigt.
