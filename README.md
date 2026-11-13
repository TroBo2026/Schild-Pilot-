# Schild Pilot

Kostenlos entwickelter Prototyp zur Erkennung von Verkehrszeichen.

## Ziel
Schild Pilot soll Verkehrszeichen zunächst auf einzelnen Bildern erkennen. Später wird die Erkennung auf einem Smartphone getestet. Das Projekt ist ein Lern- und Forschungsprototyp und **keine sicherheitskritische Fahrassistenz**.

## Architektur
1. Bildaufnahme oder Bildauswahl
2. Detektion: Position(en) der Schilder im Gesamtbild finden
3. Klassifikation: jedes gefundene Schild einer Klasse zuordnen
4. Unsicherheit behandeln: bei geringer Sicherheit keine definitive Aussage
5. Evaluation auf getrennten, bisher ungesehenen Testbildern

## Projektstatus
**Phase 0:** mobiles Foto-Frontend und Projektstruktur abgeschlossen.
**Phase 1:** konservative Unsicherheitsentscheidung und Unit-Tests ergänzt; Modelltraining noch nicht ausgeführt.
**Phase 2:** Detektion mehrerer Schilder in vollständigen Straßenfotos.
**Phase 3:** Optimierung für Smartphone und Offline-Tests.

## Daten und Lizenzen
Öffentlich sichtbare Bilder sind nicht automatisch frei für Training oder Weitergabe. Für jeden Datensatz dokumentieren wir Herkunft, Lizenz, erlaubte Nutzung, Länderabdeckung und Klassen. Siehe [training/README.md](training/README.md).

## Technik
- Web-Prototyp: HTML, CSS, JavaScript
- Training und Evaluation: Python, PyTorch, Pillow
- spätere mobile Laufzeit: ONNX oder Core ML, nach Messungen und Kompatibilitätsprüfung

## Tests

Die modellunabhängigen Tests benötigen nur die Python-Standardbibliothek:

```bash
python -m unittest discover -s tests -v
```

GitHub Actions führt diese Tests bei Änderungen an `main` und bei Pull Requests automatisch aus.

## Web-Prototyp starten
Die Dateien liegen in `web/`. Für Kamerazugriff im Browser ist üblicherweise HTTPS und eine ausdrückliche Berechtigung nötig. Auf GitHub kann die Oberfläche später mit GitHub Pages veröffentlicht werden.

## Sicherheit
Nur im Stand testen. Das Smartphone während der Fahrt nicht bedienen. Ergebnisse können falsch oder unvollständig sein und dürfen nicht zur Steuerung eines Fahrzeugs oder für sicherheitskritische Entscheidungen verwendet werden.
