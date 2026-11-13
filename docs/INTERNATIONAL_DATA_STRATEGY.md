# Internationale Datenstrategie

## Ziel
Schild Pilot soll Verkehrszeichen aus unterschiedlichen Ländern erkennen. Ein globales Modell darf nationale Unterschiede nicht zu einer einzigen, scheinbar universellen Bedeutung zusammenfassen.

## Drei getrennte Ebenen
1. **Visuelle Klasse:** Was ist auf dem Schild zu sehen (Form, Symbol, Farbe, Text)?
2. **Regulatorische Zuordnung:** Welche nationale oder regionale Vorschrift beschreibt das Schild?
3. **Kontextuelle Bedeutung:** Welche Einschränkungen, Ausnahmen oder Zusatztafeln gelten?

Die KI darf zunächst eine visuelle Klasse vorschlagen. Eine rechtliche Bedeutung darf nur mit einer versionierten, überprüften Länder-Taxonomie verknüpft werden.

## Datenfreigabe-Gate
Vor jedem Datensatzimport müssen dokumentiert sein:
- Rechteinhaber und offizielle Bezugsquelle
- Lizenz/Vertrag, erlaubte Trainingsnutzung und kommerzielle Nutzung
- Bedingungen für abgeleitete Modelle und Modellgewichte
- Attributions-, Weitergabe- und geografische Einschränkungen
- Datenschutz- und Personenbezug
- Annotationstyp, Klassenmapping und bekannte Verzerrungen

Ein Datensatz, der nur akademische Forschung erlaubt oder dessen Lizenz unklar ist, darf nicht als Trainingsgrundlage für ein später kommerzielles GEPARD-Produkt freigegeben werden. Er kann allenfalls nach gesonderter Prüfung in einer isolierten Lernstudie verwendet werden.

## Kandidaten – noch keine automatische Freigabe
- **GTSRB:** deutscher Klassifikationsbenchmark; gut für einen ersten Lernversuch. Die offizielle Seite nennt freie Nutzung und verlangt eine Zitierung, aber keine eindeutige Datensatzlizenz. Keine pauschale kommerzielle Freigabe ableiten.
- **GTSDB:** deutsche Vollbild-Detektion mit Bounding Boxes; nur 900 Bilder und drei grobe Kategorien. Gut als Einstieg in die Detektionspipeline, nicht als globale Abdeckung.
- **Mapillary Traffic Sign Dataset (MTSD):** global ausgerichtet, 105.000 Straßenbilder und 400 annotierte Klassen. Die begleitende Veröffentlichung beschreibt die Verfügbarkeit für akademische Forschung. Vor Nutzung für GEPARD müssen die aktuellen Dataset-Bedingungen und kommerziellen Rechte separat geklärt werden.

## Evaluationsanforderungen
Berichte müssen Ergebnisse nach Land/Region, Klasse, Tageszeit, Wetter und Bildqualität aufschlüsseln. Ein hoher Gesamtwert darf schlechte Leistung in einzelnen Ländern oder seltenen Klassen nicht verdecken. Physische Szenen und zusammengehörige Bildsequenzen dürfen nicht zwischen Training und Test aufgeteilt werden.

## Quellen
- GTSRB: https://benchmark.ini.rub.de/gtsrb_dataset.html
- GTSDB: https://benchmark.ini.rub.de/gtsdb_dataset.html
- MTSD-Publikation: https://www.ecva.net/papers/eccv_2020/papers_ECCV/html/4217_ECCV_2020_paper.php


## Öffentliche Datensatz-Kandidaten – Recherche-Stand 13.11.2026

Diese Prüfung ist eine Vorauswahl, keine Freigabe zum Download, Training oder kommerziellen Einsatz:

| Kandidat | Aufgabe / Abdeckung | öffentlich auffindbare Nutzungsangaben | Entscheidung |
|---|---|---|---|
| GTSRB | zugeschnittene deutsche Schilder, 43 Klassen | Offizielle Benchmark-Seite; keine eindeutige pauschale kommerzielle Lizenz in den hier geprüften Angaben festgestellt | Nicht importieren, bis Originalbedingungen geklärt sind |
| GTSDB | deutsche Vollbild-Detektion | Offizielle Benchmark-Seite; Nutzungsbedingungen separat prüfen | Potenziell relevant für einen kleinen Detektions-Prototyp, derzeit nicht freigegeben |
| TT100K | chinesische Vollbilder, 221 Klassen und Bounding Boxes | Die geprüfte Ultralytics-Dokumentation nennt CC BY-NC 2.0 und rund 18 GB Download | Nicht für eine spätere kommerzielle GEPARD-Nutzung; großer Download unnötig |
| GTSIGN-220 | 220 deutsche StVO-nahe Klassen | Dataset-Karte nennt CC BY-SA 4.0; Bildherkunft verweist auf Mapillary | Vor Import Herkunft und Rechtekette der abgeleiteten Bilder prüfen |
| Mapillary Traffic Sign Dataset | internationale Vollbilder, rund 400 Klassen | Veröffentlichung beschreibt wissenschaftliche/akademische Verfügbarkeit; aktuelle Nutzungsbedingungen gesondert prüfen | Nicht als kommerziell freigegeben behandeln |

Für TT100K nennt die Dokumentation 6.105 Trainings-, 7.641 Validierungs- und 3.071 Testbilder, jedoch auch einen Downloadumfang von ungefähr 18 GB. Das ist für den aktuellen kostenlosen CPU-Pilot unnötig groß und wegen der nicht-kommerziellen Lizenz keine passende Grundlage für eine spätere kommerzielle Fahrzeuganwendung.

GTSRB/GTSDB und Mapillary bleiben bis zur Prüfung der jeweiligen Originalbedingungen gesperrt. Es wurden in dieser Recherche keine Bilddateien heruntergeladen, keine Nutzerfotos verwendet und keine Datensätze ins Repository aufgenommen.

Quellen der Vorprüfung:
- GTSRB/GTSDB Projektseite: https://github.com/houbensebastian/GermanTrafficSignBenchmarks
- TT100K-Dokumentation und Lizenzhinweis: https://docs.ultralytics.com/datasets/detect/tt100k
- GTSIGN-220 Dataset-Karte: https://huggingface.co/datasets/miriamcarnot/GTSIGN-220
- Mapillary-/Datensatz-Lizenzübersicht als Sekundärquelle: https://zenodo.org/records/23527395

Sekundärquellen ersetzen nicht die Original-Lizenztexte. Vor jeder tatsächlichen Nutzung sind die aktuellen Bedingungen beim jeweiligen Rechteinhaber zu prüfen.
