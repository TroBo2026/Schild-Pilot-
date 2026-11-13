# Schild Pilot – Roadmap

## Phase 0 – Grundgerüst
- [x] Repository und Projektstruktur
- [x] Mobile Fotoaufnahme/-auswahl im Browser
- [x] Bildvorschau und klare Statusanzeige
- [x] Modellunabhängige Enthaltungsregel und Unit-Tests
- [ ] Modell-Schnittstelle

## Phase 1 – Klassifikation
- [ ] Datensatz und Lizenz prüfen
- [ ] Klassenverzeichnis/Label-Mapping definieren
- [ ] Transfer-Learning-Trainingsskript
- [ ] Validierung, Konfusionsmatrix und Fehlersammlung
- [ ] Modellversion und Metadaten

## Phase 2 – Detektion
- [ ] Detektionsdatensatz mit Bounding Boxes auswählen
- [ ] Detektor evaluieren
- [ ] Mehrere Schilder pro Foto unterstützen
- [ ] Unbekannte und unsichere Schilder kennzeichnen

## Phase 3 – Smartphone
- [ ] Modell für Browser oder iOS exportieren
- [ ] Fotoanalyse auf iPhone testen
- [ ] Laufzeit, Speicherbedarf und Offline-Fähigkeit messen
- [ ] Robustheit bei Schatten, Regen, Nacht, Unschärfe und Blickwinkeln testen

## Qualitätsregeln
- Keine erfundenen Erkennungen oder Konfidenzwerte.
- Testdaten bleiben vom Training getrennt.
- Bei geringer Sicherheit: „Nicht sicher erkannt“.
- Keine Verbindung zur Fahrzeugsteuerung.
- Smartphone-Tests ausschließlich im Stand.
