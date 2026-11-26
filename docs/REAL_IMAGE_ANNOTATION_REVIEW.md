# Visuelle Prüfung echter Detektions-Annotationen

## Zweck

Die manuelle GitHub-Actions-Workflowdatei
`.github/workflows/annotation-preview.yml` erzeugt eine kleine, lokale Sichtprobe
der Ground-Truth-Bounding-Boxes aus dem Validierungssplit von TrafficSigns-Raw
0.2.0. Der Workflow ist bewusst von jedem Trainingsworkflow getrennt.

Er führt **keine Modellinferenz und kein Training** aus.

## Workflow ausführen

1. Im Repository `TroBo2026/Schild-Pilot-` den Tab **Actions** öffnen.
2. **Real-image annotation preview (no training)** auswählen.
3. **Run workflow** auf dem Branch `main` starten.
4. Eine Stichprobengröße zwischen 1 und 24 angeben; Standard ist 12.
5. Nach erfolgreichem Abschluss das Artefakt
   `schild-pilot-traffic-signs-annotation-preview` herunterladen.
6. `index.html` lokal im Browser öffnen und die Bilder mit den eingezeichneten
   Ground-Truth-Boxen prüfen. Zusätzlich `report.json` und
   `detection_audit.json` lesen.

Der Workflow verwendet ausschließlich den Validierungssplit für die Vorschau.
Der Testsplit wird weder für die Stichprobenauswahl noch für Modell- oder
Schwellenwertentscheidungen verwendet.

## Datenherkunft und Rechte

- Datensatz: TrafficSigns-Raw 0.2.0
- Quelle: https://doi.org/10.5281/zenodo.22052437
- Urheber: Vasile Marian, Yong-Bin Kang und Alexander Buddery
- Lizenz laut Datensatzseite und datensatzspezifischer Archivnotiz:
  Creative Commons Attribution 4.0 International (CC BY 4.0)
- Lizenztext und Attribution werden im Vorschauartefakt als
  `ATTRIBUTION.txt` mitgeliefert.
- Das Archiv wird vor der Extraktion anhand der dokumentierten SHA-256-Prüfsumme
  geprüft. Extrahiert werden nur TrafficSigns-Raw und seine Lizenznotiz.

## Umfang und Datenschutz

Der temporäre GitHub-Runner verarbeitet den versionierten Datensatz und erzeugt
eine kleine Vorschau. Hochgeladen werden ausschließlich:

- bis zu 24 verkleinerte Vorschau-JPEGs aus dem Validierungssplit;
- `index.html` und `report.json`;
- das technische Datensatz-Audit und das Intake-Manifest.

Das vollständige Archiv, der vollständige Datensatz und Modellgewichte werden
nicht als Workflow-Artefakt hochgeladen. Die Vorschau wird nach sieben Tagen
automatisch entfernt. Nutzerfotos werden von diesem Workflow nicht verwendet.

## Was die Sichtprüfung beantworten soll

- Liegt jede Box sichtbar auf dem annotierten Schild?
- Sind Boxen auffällig verschoben, zu groß, zu klein oder abgeschnitten?
- Passen die zwei Quellklassen `Traffic Sign` und `Damaged Traffic Sign` zum
  sichtbaren Inhalt?
- Gibt es mehrere Schilder im Bild, von denen nur einige annotiert sind?
- Sind Bildausrichtung und Koordinatenskalierung plausibel?

Das JSON-Reporting zeigt, welche Kategorien die Stichprobe abdeckt und welche
Kategorien fehlen. Es kann keine semantisch falschen Labels oder fehlenden
Annotationen automatisch erkennen. Dafür ist die manuelle Sichtprüfung nötig.

## Grenzen

TrafficSigns-Raw enthält nur zwei allgemeine Detektionsklassen und seine
geografische Abdeckung ist nicht als global belegt. Ein korrekt gezeichneter
Ground-Truth-Rahmen beweist keine Modellleistung. Die Ergebnisse sind kein
Verkehrszeichen-Klassifikator und keine Fahrassistenz.

Erst nach dokumentierter Sichtprüfung sollten Bild-/Box-Skalierung und
Klassenmapping weiter diagnostiziert werden. Ein neuer Trainingslauf bleibt
bis dahin gesperrt bzw. wird nicht gestartet.
