# Training und Datensätze

## Leitlinie
Wir verwenden nur Datensätze, deren Herkunft und Nutzungsbedingungen dokumentiert sind. Öffentlich sichtbare Bilder sind nicht automatisch für Training oder Weitergabe freigegeben.

Für jede Quelle dokumentieren wir:
- Lizenz und erlaubte Nutzung (Training, Bearbeitung, Weitergabe)
- Länder- und Regionenabdeckung
- Klassen und Annotationstypen
- Aufteilung in Training, Validierung und unabhängigen Test

## Klassifikation und Detektion
Ein Klassifikationsdatensatz enthält oft bereits ausgeschnittene Schilder. Das beantwortet „Was ist dieses Schild?“, aber nicht „Wo ist das Schild im gesamten Straßenfoto?“. Für die zweite Aufgabe benötigen wir einen Datensatz mit Bounding Boxes oder Segmentierungen.

## Erste Lernstrategie
Transfer Learning: ein vortrainiertes Bildmodell wird an unsere Schildklassen angepasst. Das ist üblicherweise effizienter als Training von Grund auf. Die offizielle PyTorch-Anleitung erklärt Fine-Tuning und das Einfrieren vortrainierter Netzwerkschichten:
https://docs.pytorch.org/tutorials/beginner/transfer_learning_tutorial.html

## Datensatzprüfung
GTSRB ist ein bekannter deutscher Klassifikationsbenchmark, aber nicht global und nicht automatisch eine Freigabe für jede Nutzung. Vor Integration müssen wir Lizenz und konkrete Bereitstellungsbedingungen prüfen. GTSRB allein ersetzt keinen Detektor für vollständige Straßenbilder.

## Keine automatische Web-Bildersammlung
Wir aktivieren kein wahlloses Scraping. Bilder werden erst nach Lizenzprüfung und sauberer Kennzeichnung aufgenommen.
