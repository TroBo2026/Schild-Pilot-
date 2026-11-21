# Schild Pilot

Schild Pilot ist ein kostenloser Lern- und Forschungsprototyp für **deutsche Verkehrszeichen**. Der erste Produktfokus ist bewusst eng: deutsche StVO-Zeichen erkennen, korrekt benennen, ihre Bedeutung verständlich erklären und das Wissen anschließend mit kurzen Fragen abprüfen.

## Aktueller Funktionsumfang

- Deutscher Lernmodus mit einer ersten Auswahl von acht häufigen Verkehrszeichen.
- Ablauf pro Zeichen: Schild und Bedeutung lernen → Quizfrage zum selben Schild → Antwortfeedback und Erklärung → nächstes Zeichen.
- Fotoauswahl und lokale Bildvorschau.
- Die Foto-KI ist noch nicht mit dem Web-Prototyp verbunden. Bei eigenen Fotos wird deshalb kein Erkennungsergebnis vorgetäuscht.

## KI-Trainingsstand

Der Klassifikator ist ein ResNet18 für 211 deutsche Verkehrszeichenklassen aus dem Datensatz [Fraunhofer IOSB Synset Signset Germany](https://huggingface.co/datasets/FraunhoferIOSB/Synset-Signset-Germany), Konfiguration `Cycles`. Der Datensatz umfasst synthetisch gerenderte Bilder, keine echten Kameraaufnahmen.

Der bisherige Pilot nutzte 80 Trainings-, 10 Validierungs- und 10 Testbilder pro Klasse:
- 16.880 Trainingsbilder
- 2.110 Validierungsbilder
- 2.110 Testbilder
- Test Top-1: 87,54 %
- Test Top-5: 96,68 %

Diese Werte sind ein interner synthetischer Pilotvergleich. Val und Test stammen aus getrennten Teilmengen des Quell-Splits `validation`; es gibt in dieser Konfiguration keinen offiziellen Test-Split. Die Zahlen sind kein Nachweis für zuverlässige Erkennung realer Straßenfotos.

**Erweiterter Trainingslauf:** Die Datenvorbereitung und GitHub-Actions-Konfiguration sind jetzt auf 350 Trainings-, 50 Validierungs- und 50 Testbilder pro Klasse eingestellt. Zielumfang bei 211 Klassen:
- 73.850 Trainingsbilder
- 10.550 Validierungsbilder
- 10.550 Testbilder
- insgesamt 94.950 Bilder

Der erweiterte Lauf ist noch nicht als erfolgreich bestätigt. Seine Ergebnisse werden erst nach abgeschlossenem Training und Testauswertung veröffentlicht. Der Testsplit wird nicht zur Modellauswahl oder Schwellenwertkalibrierung verwendet.

## Architektur und nächste Schritte

1. **Lernmodus:** geprüfte deutsche Zeichen und verständliche Erklärungen.
2. **Klassifikation:** einen bereits ausgeschnittenen Schildbereich einer der 211 Klassen zuordnen.
3. **Detektion:** Schilder in vollständigen Fotos finden. Der bisherige Realbild-Pilot hatte keine brauchbaren Validierungstreffer; diese Pipeline bleibt ein offener Entwicklungsbereich.
4. **Integration:** Klassifikator und Detektor verbinden, Unsicherheit sauber behandeln und erst danach die Foto-KI im Frontend aktivieren.
5. **iPhone:** spätere lokale Laufzeit und Offlinebetrieb, erst nach technischen Tests.

## Quellen, Daten und Lizenz

- Fraunhofer IOSB Synset Signset Germany: [Datensatzseite](https://huggingface.co/datasets/FraunhoferIOSB/Synset-Signset-Germany), auf der Seite angegebene Lizenz CC BY 4.0.
- Verkehrszeichen-Namen und Bedeutungen im Lernmodus orientieren sich an der deutschen Straßenverkehrs-Ordnung: [StVO, Anlage 2](https://www.gesetze-im-internet.de/stvo_2013/anlage_2.html) und [Anlage 3](https://www.gesetze-im-internet.de/stvo_2013/anlage_3.html).

Öffentlich sichtbare Bilder sind nicht automatisch frei für Training oder Weitergabe. Weitere Datenquellen werden erst nach Prüfung ihrer Lizenz, Herkunft, Annotationen und Nutzungsbedingungen aufgenommen. Keine wahllose Bildersammlung.

## Technik und Tests

- Web-Prototyp: HTML, CSS, JavaScript
- Training und Evaluation: Python, PyTorch, torchvision, Pillow
- Klassifikator: ResNet18
- Tests: `python -m unittest discover -s tests -v`
- Trainingsworkflow: `.github/workflows/synthetic-training.yml`

## Sicherheitsgrenzen

Schild Pilot ist ein Lern- und Forschungsprototyp, keine Fahrassistenz. Keine Fahrzeugsteuerung und keine sicherheitskritischen Entscheidungen. Foto- und App-Tests nur im sicheren Stillstand; niemals während der Fahrt, beim Radfahren oder beim Überqueren einer Straße bedienen. Für reale Nutzung wären unabhängige echte Testdaten, eine funktionierende Detektion, robuste Unsicherheitsbehandlung und umfangreiche Sicherheitsvalidierung erforderlich.
