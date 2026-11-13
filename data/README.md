# Datenordner

Trainingsbilder werden nicht ins Git-Repository hochgeladen. Der Ordner ist lokal vorgesehen und durch `.gitignore` ausgeschlossen.

## Klassifikation

Für das erste Klassifikationsmodell wird folgende Struktur erwartet:

```
data/signs/
  train/
    class_001/
      image_a.jpg
  val/
    class_001/
      image_b.jpg
  test/
    class_001/
      image_c.jpg
```

Jeder Klassenordnername ist ein Label. Alle Splits müssen dieselben Klassen enthalten. Der Testsplit bleibt bis zur finalen Auswertung unangetastet.

## Detektion in vollständigen Straßenbildern

Die vorbereitete Prüf-Pipeline erwartet COCO-artige Annotationen:

```
data/detection/
  train/
    images/
    annotations.json
  val/
    images/
    annotations.json
  test/
    images/
    annotations.json
```

Jede `annotations.json` enthält die COCO-Listen `images`, `annotations` und `categories`. Bounding Boxes müssen als `[x, y, width, height]` in Pixeln angegeben sein. Bild-IDs und Kategorie-IDs müssen innerhalb des jeweiligen Splits eindeutig beziehungsweise gültig sein. Alle drei Splits müssen dieselbe Kategorienliste verwenden.

Vor dem Training ausführen:

```bash
python -m training.audit_detection_dataset --data data/detection
```

Das Audit prüft fehlende Dateien, Annotation-Referenzen, Kategorien, Bildabmessungen, Bounding-Box-Grenzen und identische Bilddateien über Splits hinweg. Es erkennt keine nahezu identischen Bilder, gemeinsamen Video-/Szenenursprung oder falschen Labels; dafür ist zusätzlich eine gruppenbasierte Aufteilung und manuelle Stichprobenprüfung nötig.

## Freigabe vor jedem Import

1. Lizenz und Nutzungsbedingungen beim ursprünglichen Rechteinhaber prüfen.
2. Quelle, Version, Abrufdatum, Rechtekette und erlaubte Trainings-/Modellnutzung dokumentieren.
3. Länderabdeckung, Klassenmapping und Annotationstyp prüfen.
4. Personenbezogene Daten und unnötige Kennzeichen/Gesichter vermeiden.
5. Szenen- oder Sequenzgruppen vollständig einem Split zuordnen; keine Bildfolgen desselben Ortes über Train/Val/Test verteilen.
6. Keine zufälligen Internetbilder ohne nachvollziehbare Nutzungsrechte übernehmen.

Ein erfolgreiches Audit bestätigt nur die technische Datenintegrität, nicht die Lizenz oder die inhaltliche Richtigkeit der Annotationen.
