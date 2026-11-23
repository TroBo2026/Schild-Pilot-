# iPhone- und Außentest-Freigabe – Schild Pilot

Stand: 23.11.2026  
Repository: `TroBo2026/Schild-Pilot-`  
Gültiger Entwicklungsbranch: `main`

## Aktueller Freigabestatus

**NICHT FREIGEGEBEN für einen Erkennungstest auf öffentlichen Straßen.**

Die vorhandene Weboberfläche kann die Kamera-Quelle des Browsers anfordern bzw. ein Foto auswählen und es lokal anzeigen. Die Fotoeingabe prüft Bildtyp und Dateigröße (maximal 25 MB), gibt ersetzte Vorschau-Objekt-URLs frei und entfernt eine fehlerhafte Vorschau. Der Button für die Erkennung bleibt deaktiviert, solange kein echtes Modell integriert ist. Es findet keine Modellinferenz statt.

Der Detektor hat in seinem ersten Realbild-Versuch auf der Validierung null True Positives erreicht. Der Klassifikator wurde bislang nur mit synthetischen deutschen Szenen geprüft. Es gibt kein nachgewiesenes, kombiniertes Detektions-/Klassifikationssystem und keinen iPhone-Offline-Build.

Daher darf die aktuelle Oberfläche nicht als Verkehrszeichen-Erkennung oder als verlässliche Aussage über reale Schilder verstanden werden. Ein Kamerabild aufzunehmen ist möglich; ein fachlich sinnvoller Erkennungstest ist es noch nicht.

## Freigabestufen

### Stufe A – Fotoeingabe ohne KI (Demo, teilweise geprüft)

- [x] Foto auswählen oder Kamera-Quelle des Browsers anfordern
- [x] Bildvorschau lokal anzeigen
- [x] Bildtyp und Dateigröße prüfen; Dateien über 25 MB ablehnen
- [x] Vorschau-Objekt-URLs beim Ersetzen/Entfernen freigeben
- [x] Erkennungsbutton deaktiviert halten, bis echte Modellinferenz vorhanden ist
- [x] Keine Erkennung vortäuschen; fehlende Modellinferenz klar anzeigen
- [ ] iPhone-/Safari-Verhalten auf unterstützten Geräten dokumentieren
- [ ] Prüfen, dass Bilddaten nicht übertragen werden (Netzwerk-Inspektion auf einem eigenen Testgerät)

Diese Stufe testet nur die Bedienoberfläche, nicht die Verkehrszeichenerkennung. Die JavaScript-Logik wird mit Node-Unit-Tests geprüft; das ersetzt keinen Test auf einem echten iPhone.

### Stufe B – Lokale Modellinferenz (noch offen)

Vor einem Test mit echten Verkehrszeichen müssen alle Punkte erfüllt sein:

- [ ] Detektor hat auf einem unveränderten, unabhängigen Realbild-Testsplit positive und reproduzierbare Ergebnisse.
- [ ] Bericht enthält mindestens Precision, Recall, F1 und IoU-basierte Auswertung; Ergebnisse werden zusätzlich nach kleinen/großen Boxen und Klassen aufgeschlüsselt.
- [ ] Keine Schwellenwerte oder Modellentscheidungen wurden anhand des Test-Splits ausgewählt.
- [ ] Detektor und Klassifikator bleiben getrennt evaluierbar und ihre Schnittstelle ist getestet.
- [ ] Unbekannte, mehrdeutige oder schwache Ergebnisse führen sichtbar zu „Nicht sicher erkannt“ statt zu einer geratenen Klasse.
- [ ] Modell-Lizenz, Gewichtsherkunft und sämtliche verwendeten Datensatzlizenzen sind dokumentiert.
- [ ] Modell wird in ein unterstütztes lokales Format exportiert (z. B. Core ML oder ONNX); Export wird numerisch gegen die Referenz-Inferenz verglichen.
- [ ] Laufzeit, RAM-/Speicherbedarf und Energieverbrauch werden auf dem tatsächlichen iPhone gemessen.
- [ ] Inferenz funktioniert im Flugmodus; keine Cloud- oder kostenpflichtige API ist erforderlich.
- [ ] Bilddaten bleiben auf dem Gerät; kein Upload und keine Telemetrie mit Bildinhalten.

### Stufe C – Begrenzter, beaufsichtigter Außentest (noch offen)

Erst nach erfolgreicher Stufe B:

- [ ] Testplan und Einverständnis einer erziehungsberechtigten Person liegen vor.
- [ ] Tests finden ausschließlich bei sicherem Stillstand statt, auf einem sicheren Gehweg oder Privatgelände, mit Abstand zur Fahrbahn und ohne Betreten der Straße.
- [ ] Das Gerät wird niemals beim Fahren, Radfahren, Überqueren einer Straße oder beim Gehen durch unübersichtliche Bereiche bedient.
- [ ] Es wird nicht versucht, Verkehrsentscheidungen anhand der App zu treffen.
- [ ] Testbilder werden nur lokal ausgewertet. Eine Weitergabe oder ein Upload erfolgt nur nach ausdrücklicher Zustimmung und vorheriger Prüfung von Personen-/Kennzeichen-Daten sowie der Bildrechte.
- [ ] Fehler, Unsicherheit, Wetter, Licht und ungefähre Schildgröße werden protokolliert; private Standortdaten werden nicht unnötig gespeichert.

## Messbare Mindestkriterien für einen Forschungs-Pilot

Die folgenden Werte sind **Projekt-Gates**, keine gesetzlichen oder sicherheitstechnischen Standards. Sie sind vor einem Feldversuch anhand des konkreten Datensatzes festzulegen und dürfen nicht nachträglich passend zum Ergebnis verändert werden:

1. Unabhängiger, lizenzierter Realbild-Testsplit mit dokumentierter Herkunft und geografischer Abdeckung.
2. Mindestens 300 Testbilder aus mehreren Szenen; keine nahezu identischen Bilder desselben Aufnahmeortes in Train und Test.
3. Für die Detektion: IoU=0,5 Precision und Recall jeweils mindestens 0,80 auf dem festgelegten Pilot-Testsplit; zusätzlich Ergebnisse für kleine Objekte separat berichten.
4. Für Klassifikation: Genauigkeit und Abdeckung der akzeptierten Vorhersagen getrennt ausweisen; jede nicht unterstützte Klasse muss zur Enthaltung führen.
5. Keine ungeklärten Fehler in der Offline-Datenverarbeitung, im Bildpfad oder in der Modellkonvertierung.
6. Auf dem Ziel-iPhone: wiederholbare Inferenz im Flugmodus, dokumentierte Laufzeit und kein Upload von Testbildern.

Das Erreichen dieser Schwellen wäre nur eine Forschungs-Pilotfreigabe für beaufsichtigte, stationäre Tests – keine Fahrassistenzfreigabe und keine Garantie für zuverlässige Erkennung im Straßenverkehr.

## Was vor dem nächsten Außentest zu tun ist

1. Lokale Annotation-Vorschau mit dem lizenzierten TrafficSigns-Raw-Datensatz ausführen und Boxen visuell prüfen.
2. Bild-/Box-Skalierung und Klassenmapping in der Detektionspipeline nachweisen.
3. Null-TP-Ursache beheben und erst nach bestandenem Audit einen begrenzten Trainingslauf durchführen.
4. Auf einem unabhängigen Realbild-Testsplit evaluieren.
5. Detektor und Klassifikator integrieren, Unsicherheits-/Enthaltungsverhalten testen.
6. Lokalen iPhone-Export und Offlinebetrieb verifizieren.

## Sicherheits- und Datenschutzgrenze

Schild Pilot bleibt ein Lern- und Forschungsprototyp. Keine Fahrzeugsteuerung, keine Fahrassistenz, keine sicherheitskritischen Versprechen. Das Telefon wird niemals während der Fahrt oder beim Überqueren einer Straße bedient. Nutzerbilder werden ohne ausdrückliche Zustimmung weder hochgeladen noch anderweitig weitergegeben.
