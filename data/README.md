# Datenordner

Trainingsbilder werden nicht ins Git-Repository hochgeladen. Der Ordner ist lokal vorgesehen und durch `.gitignore` ausgeschlossen.

Für das erste Klassifikationsmodell wird folgende Struktur erwartet:

```
data/signs/
  train/
    class_001/
      image_a.jpg
  val/
    class_001/
      image_b.jpg
```

Jeder Klassenordnername ist ein Label. Train und Val müssen dieselben Klassen enthalten. Ein unabhängiger Testdatensatz wird zusätzlich separat gehalten und darf nicht zum Abstimmen des Modells verwendet werden.

Vor dem Import eines Datensatzes:
1. Lizenz und Nutzungsbedingungen prüfen.
2. Quelle, Version, Download-Datum und Länderabdeckung dokumentieren.
3. Klassenmapping und Annotationen prüfen.
4. Personenbezogene Daten und unnötige Kennzeichen/Gesichter vermeiden.
5. Keine zufälligen Internetbilder ohne nachvollziehbare Nutzungsrechte übernehmen.
