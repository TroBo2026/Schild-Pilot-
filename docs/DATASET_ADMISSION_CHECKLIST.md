# Datensatz-Freigabecheck – Schild Pilot

Dieses Dokument ist eine praktische Prüfliste vor dem Import, Training oder Export eines Datensatzes. Es ersetzt keine rechtliche Prüfung. Ein öffentlich auffindbarer Datensatz ist nicht automatisch für Modelltraining, kommerzielle Nutzung oder Weitergabe freigegeben.

## Entscheidungsregel

- **FREIGEGEBEN:** Alle Pflichtfelder sind anhand der Originalquelle belegt, die geplante Nutzung ist erlaubt, und technische Qualitätsprüfungen sind abgeschlossen.
- **HALT:** Mindestens eine Pflichtangabe fehlt, ist widersprüchlich oder muss noch geklärt werden. Bis dahin keine Daten herunterladen/importieren oder trainieren.
- **ABGELEHNT:** Die Bedingungen widersprechen der geplanten Nutzung, die Herkunft ist nicht ausreichend nachvollziehbar oder das Risiko ist nicht vertretbar.

Keine Freigabe durch bloße Sekundärquellen, Such-Snippets oder eine allgemeine Aussage wie „open data“.

## 1. Quellen- und Rechteprüfung

- [ ] Offizielle Bezugsquelle und Rechteinhaber identifiziert
- [ ] Exakte Version/Release und Veröffentlichungsdatum notiert
- [ ] Original-Lizenz bzw. aktuelle Nutzungsbedingungen lokal/als Link dokumentiert
- [ ] Training und Evaluation ausdrücklich von den Bedingungen gedeckt
- [ ] Kommerzielle Nutzung (falls später vorgesehen) geprüft, nicht aus Forschungsfreigabe abgeleitet
- [ ] Regeln für abgeleitete Modelle/Weights, Weitergabe und Veröffentlichung geprüft
- [ ] Attribution, Notice, Share-Alike, Nichtkommerziell oder weitere Auflagen vollständig notiert
- [ ] Bildrechte und Rechte an Annotationen getrennt geprüft
- [ ] Datenschutz, Personen, Kennzeichen, Gesichter und Standortdaten berücksichtigt
- [ ] Keine ungeprüften Unter-Datensätze oder Drittquellen aus einem Archiv mitübernommen

**Beleg:** Original-URL, Lizenztext/Version, Abrufdatum und kurze wörtliche Fundstelle oder Zusammenfassung.

## 2. Globale Abdeckung und Taxonomie

- [ ] Länder/Regionen und tatsächliche Aufnahmeorte sind belegt; „global“ nicht nur aus dem Namen ableiten
- [ ] Klassenliste und Annotation-Schema sind dokumentiert
- [ ] Visuelle Klasse (Form/Symbol/Text) ist von nationaler Rechtsbedeutung getrennt
- [ ] Regionale Varianten, Zusatztafeln, temporäre Zeichen und unbekannte Klassen sind beschrieben
- [ ] Klassenmapping ist nachvollziehbar und versioniert; keine stillschweigende Zusammenlegung unterschiedlicher Bedeutungen
- [ ] Fehlende Länder/Regionen und Klassen werden als Lücken ausgewiesen

## 3. Aufgaben- und Labelqualität

- [ ] Aufgabe eindeutig: zugeschnittener Schild (**Klassifikation**) oder Schild im Vollbild (**Detektion**)
- [ ] Annotationstyp, Koordinatensystem, Bildmaße und Label-Definitionen geprüft
- [ ] Stichprobe der Labels visuell kontrolliert; Fehler und Grenzfälle protokolliert
- [ ] Verdeckte, beschädigte, unscharfe, kleine und mehrere Schilder pro Bild berücksichtigt
- [ ] Klassenverteilung und Bildqualität (Licht, Wetter, Perspektive) untersucht
- [ ] Label-Mapping und Konvertierung mit kleinen Fixtures getestet

## 4. Split- und Leckageprüfung

- [ ] Original-Splits erhalten oder Abweichungen dokumentiert
- [ ] Train/Val/Test nach Szene, Standort oder Sequenz gruppiert, nicht zufällig über nahe Frames
- [ ] Exakte Duplikate und möglichst Near-Duplicates über Splits geprüft
- [ ] Testsplit bleibt unangetastet für finale Evaluation
- [ ] Geografische und zeitliche Verteilung je Split dokumentiert
- [ ] Evaluation berichtet Ergebnisse pro Region und Klasse; globale Mittelwerte verdecken keine Lücken

## 5. Reproduzierbarer, datensparsamer Intake

- [ ] Nur die benötigten Dateien und Splits herunterladen
- [ ] Downloadquelle, Version, Dateigröße und SHA-256 prüfen
- [ ] Lizenz-/Attributionsdateien zusammen mit dem Intake-Nachweis aufbewahren
- [ ] Rohbilder nicht ins Git-Repository committen
- [ ] Nutzerbilder nicht ohne ausdrückliche Zustimmung hochladen oder in Trainingsdaten übernehmen
- [ ] Keine automatische Web-Bildersammlung oder Scraping
- [ ] Kostenloses, lokal ausführbares Verfahren; keine neue kostenpflichtige API/Cloud-Abhängigkeit
- [ ] Speicher-, Rechen- und Downloadumfang vorab begrenzen

## 6. Eintrag für jeden Kandidaten

Kopiere diese Vorlage in den Quellenbericht, bevor ein Kandidat importiert wird:

- **Name / Version:**
- **Offizielle Quelle / Release:**
- **Rechteinhaber:**
- **Lizenz / Nutzungsbedingungen (Originalbeleg):**
- **Training / Evaluation erlaubt:**
- **Kommerzielle Nutzung:**
- **Modellgewichte / abgeleitete Werke / Weitergabe:**
- **Attribution / Auflagen:**
- **Geografische Abdeckung:**
- **Klassen / Annotationstyp:**
- **Split- und Szenenprovenienz:**
- **Datenschutz / Bildrechte:**
- **Downloadumfang / benötigte Teilmenge:**
- **Audit / Stichprobenprüfung:**
- **Entscheidung (FREIGEGEBEN / HALT / ABGELEHNT):**
- **Begründung / offene Punkte / Prüfdatum:**

## Forschungsgrenze

Selbst ein freigegebener und technisch sauberer Datensatz belegt keine Leistung im Straßenverkehr. Schild Pilot bleibt ein Lern- und Forschungsprototyp; keine Fahrzeugsteuerung, keine Fahrassistenz und keine sicherheitskritischen Entscheidungen.