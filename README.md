# Schild Pilot

Schild Pilot ist ein kostenloser, modularer Lern- und Forschungsprototyp zur Verkehrszeichenerkennung. Der Einstieg ist bewusst auf deutsche Verkehrszeichen begrenzt; die langfristige Architektur soll weitere Länder und Zeichensysteme unterstützen.

## Aktueller Funktionsumfang

- Deutscher Lernmodus mit einer ersten Auswahl von acht häufigen Verkehrszeichen.
- Ablauf pro Zeichen: Schild und Bedeutung lernen → Quizfrage zum selben Schild → Antwortfeedback und Erklärung → nächstes Zeichen.
- Fotoauswahl und lokale Bildvorschau.
- Die Foto-KI ist noch nicht mit dem Web-Prototyp verbunden. Bei eigenen Fotos wird deshalb kein Erkennungsergebnis vorgetäuscht.
- **Internationale Taxonomie ist noch nicht implementiert.** Die geplante Trennung von visueller Zeichenklasse und landesspezifischer rechtlicher Bedeutung ist in [docs/INTERNATIONAL_TAXONOMY.md](docs/INTERNATIONAL_TAXONOMY.md) beschrieben.

## KI-Trainingsstand

Der Klassifikator ist ein ResNet18 für 211 deutsche Verkehrszeichenklassen aus dem Datensatz [Fraunhofer IOSB Synset Signset Germany](https://huggingface.co/datasets/FraunhoferIOSB/Synset-Signset-Germany), Konfiguration `Cycles`. Der Datensatz enthält synthetisch gerenderte Szenen, keine echten Kameraaufnahmen.

### Bisheriger Pilot vom 13.11.2026
- 16.880 Trainings-, 2.110 Validierungs- und 2.110 Testbilder
- Test Top-1: 87,54 %
- Test Top-5: 96,68 %
- Abdeckung der akzeptierten Vorhersagen: 88,20 %
- Genauigkeit auf akzeptierten Vorhersagen: 93,93 %

### Erweiterter Pilot vom 21.11.2026
GitHub Actions: [Run 44921927981](https://github.com/TroBo2026/Schild-Pilot-/actions/runs/44921927981)

- 73.850 Trainings-, 10.550 Validierungs- und 10.550 Testbilder (211 Klassen; 94.950 Bilder insgesamt)
- Zwei CPU-Trainingsepochen; bestes Validierungsergebnis: 89,95 %
- Test Top-1: 89,77 %
- Test Top-5: 97,85 %
- Test-Macro-Top-1: 89,77 %
- Enthaltungsregel: 8.473 akzeptierte und 2.077 zurückgewiesene Testvorhersagen
- Testabdeckung: 80,31 %
- Genauigkeit auf akzeptierten Testvorhersagen: 98,61 %
- Datensatz-Audit: 0 Fehler, 0 Warnungen

**Interpretation:** Der Testsplit besteht aus einer disjunkten Teilmenge des Quell-Splits `validation`; die Datenquelle veröffentlicht in dieser Konfiguration keinen unabhängigen offiziellen Testsplit. Alle Bilder sind synthetisch und die Taxonomie ist deutsch. Die Kennzahlen belegen weder globale Abdeckung noch Erkennung realer Kameraaufnahmen oder Sicherheit im Straßenverkehr. Die Modell-Scores sind keine kalibrierten Sicherheitswahrscheinlichkeiten.

Der Trainingslauf erzeugte ein temporäres CI-Artefakt von 41.922.682 Bytes, das auch Modellgewichte enthielt. Dieses Artefakt ist laut GitHub bis zum 28.11.2026 aufbewahrt. Die Workflow-Konfiguration wurde danach geändert: zukünftige Trainingsläufe starten nicht automatisch bei Pushes, benötigen eine explizite manuelle Bestätigung und laden nur Auswertungsdateien sowie das Datenquellenmanifest hoch – keine Modellgewichte.

## Architektur und nächste Schritte

1. **Internationale Taxonomie:** visuelle Klasse und landesspezifische Regel/Erklärung getrennt modellieren; derzeit nur Konzeptdokumentation.
2. **Lernmodus:** geprüfte deutsche Zeichen und verständliche Erklärungen.
3. **Klassifikation:** einen bereits ausgeschnittenen Schildbereich einer der 211 Klassen zuordnen.
4. **Detektion:** Schilder in vollständigen Fotos finden. Der bisherige Realbild-Pilot hatte keine brauchbaren Validierungstreffer; diese Pipeline bleibt ein offener Entwicklungsbereich.
5. **Integration:** Klassifikator und Detektor verbinden, Unsicherheit sauber behandeln und erst danach die Foto-KI im Frontend aktivieren.
6. **iPhone:** spätere lokale Laufzeit und Offlinebetrieb, erst nach technischen Tests.

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

---
