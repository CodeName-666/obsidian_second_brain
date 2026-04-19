# Vault Context

Dieses Vault ist das zentrale zweite Gehirn fuer Entwicklungs-, Planungs- und Wissensarbeit. Es sammelt Projektwissen, technische Referenzen, Daily Notes, Skill-Dokumentation und dauerhafte Arbeitsregeln. Persoenliche Profildaten gehoeren in `00 Kontext/` und werden ueber die Zeit ausgebaut.

## Ueber mich

Persoenlicher Kontext (Rolle, Arbeitsschwerpunkte, bevorzugte Tools, Schreib- und Kommunikationsstil) wird in `00 Kontext/` gepflegt. Die kanonische Einstiegsdatei ist `00 Kontext/Ueber mich.md`. Diese Datei wird beim Setup nicht vorab befuellt; sie entsteht mit der Zeit und wird vom Skill als erste Referenz fuer inhaltliche Aufgaben gelesen.

## Vault-Struktur

- `00 Kontext/`: Persoenliches Kontext-Profil. Typische Eintraege sind `Ueber mich.md`, `ICP.md`, `Angebot.md`, `Schreibstil.md`, `Branding.md`. Diese Dateien sind die erste Referenz fuer inhaltliche Aufgaben.
- `01 Inbox/`: Schnelle Gedanken, Brain Dumps und unverarbeitete Notizen.
- `02 Projekte/`: Aktive Projekte mit klarem Ziel und Ende. Projekte starten als einzelne `.md`-Datei. Wenn ein Projekt waechst, wird die Hauptnotiz nach `02 Projekte/<Projektname>/<Projektname>.md` verschoben; dort koennen weitere Unternotizen entstehen.
- `03 Bereiche/`: Laufende Verantwortungsbereiche ohne Enddatum. Der Ordner wird bei Bedarf angelegt, sobald erstmals dauerhafte Bereichsnotizen entstehen.
- `04 Ressourcen/`: Wissen, Referenzmaterial und thematische Sammlungen. Themen liegen in eigenen Ordnern. Skill-Dokumentation lebt hier unter `04 Ressourcen/Skills/`.
- `05 Daily Notes/`: Tagesnotizen im Format `YYYY-MM-DD.md`.
- `06 Archive/`: Abgeschlossene oder inaktive Inhalte.
- `07 Anhänge/`: Bilder, PDFs und andere eingefuegte Dateien.

## Vault-Physik & Einbindung in Repos

Das physische Vault ist ein eigenstaendiges Verzeichnis mit eigener `.obsidian`-Konfiguration. Der Pfad wird beim Setup in die `config.json` des installierten Skills geschrieben und dort zentral gepflegt. Projekt-Repos koennen dieses Vault ueber die Mount-Namen `obsidian`, `obsidian_brain` oder `.obsidian_brain` einbinden, solange dort das Vault-Root mit `Brain.md` sichtbar ist. Der Resolver des Skills `obsidian-second-brain` erkennt diese Mount-Namen automatisch.

Das bedeutet: es existiert nur **eine** physische Kopie jeder Notiz, unabhaengig davon, ueber welches Projekt-Repo gerade darauf zugegriffen wird. Aenderungen im Vault werden ausschliesslich im Vault-Repo versioniert, nicht in den verlinkten Projekt-Repos.

Praktische Konsequenzen beim Arbeiten:

- **Git-Commits fuer Vault-Inhalte** gehoeren in das Vault-Repo, nicht in die nutzenden Projekt-Repos. Projekt-Repos ignorieren den Mount bzw. sehen ihn als unverfolgte Referenz.
- **Notizen muessen aus jedem verlinkten Projekt heraus sinnvoll bleiben.** Projektspezifische Inhalte kommen nach `02 Projekte/`; groessere Projekte werden unter `02 Projekte/<Projektname>/` gebuendelt, nicht am Vault-Root.
- **Relative Links aus dem Vault heraus** auf Code oder Dateien ausserhalb des Vaults treffen je nach Zugriffs-Repo auf andere Dateibaeume. Wenn eine Notiz hart an einen bestimmten Repo-Kontext gebunden ist, im Frontmatter oder Fliesstext explizit darauf hinweisen.
- **Wikilinks innerhalb des Vaults** sind der bevorzugte Verknuepfungsweg, weil sie vom physischen Mount-Pfad unabhaengig sind. Dafuer auch Heading- und Block-Anchors nutzen, z. B. `[[Notizname#Abschnitt]]`.
- **Fuer Dateien ausserhalb des Vaults** (Code, Status-Markdowns, Configs) relative Markdown-Links setzen statt Wikilinks, weil diese Dateien nicht Teil des Obsidian-Index sind.
- **Bei Vault-Aufgaben zuerst `Brain.md` lesen.** Es ist der Einstiegspunkt fuer Struktur, Routing-Regeln und dauerhafte Ablagekonventionen.

## Technische Referenzdokumente

Projektspezifische Referenzdokumente (Architektur, Datenbankschema, Feature-Analysen, Design-Vergleiche usw.) werden in der jeweiligen Projektnotiz unter `02 Projekte/<Projektname>/` verlinkt. Hier in `Brain.md` steht nur dann ein Verweis, wenn ein Dokument projektuebergreifend Autoritaet besitzt.

Sobald das erste Projekt solche Referenzen braucht, wird dieser Abschnitt mit projektweiten Einstiegspunkten befuellt. Solange er leer bleibt, ist die erste Anlaufstelle fuer technische Fragen die Hauptnotiz des jeweiligen Projekts.

## Projektkontext zwischen Sessions

Es gibt bewusst **kein** globales `memory/`-Verzeichnis. Fuer wiederaufnahmefaehigen Projektkontext gilt ein Drei-Stufen-Modell:

- `05 Daily Notes/`: Tagesbezogene Session-Deltas, Probleme, Entscheidungen und naechste Einstiege.
- `02 Projekte/<Projektname>/<Projektname>.md` oder `02 Projekte/<Projektname>.md`: kanonische Wahrheitsquelle fuer Projektrichtung, Status und dauerhafte Entscheidungen.
- `02 Projekte/<Projektname>/Projektkompass.md`: optionaler, abgeleiteter Cache fuer grosse migrierte Projekte. Diese Notiz ist nie die Wahrheitsquelle.

Ein `Projektkompass.md` kommt nur in Frage, wenn ein Projekt bereits nach `02 Projekte/<Projektname>/<Projektname>.md` migriert ist und zusaetzlich mindestens eine dieser Bedingungen erfuellt:

- die Hauptnotiz hat mehr als 300 nichtleere Zeilen
- das Projekt besitzt mehr als 3 fachliche Unternotizen ausserhalb von `Tasks/`

Wenn `Projektkompass.md` existiert, muss die Frontmatter ausdruecklich markieren, dass es ein Cache ist, zum Beispiel mit:

- `note_role: project_digest`
- `truth_source: false`
- `write_policy: consolidate_only`

Direkte Routine-Edits gehoeren **nicht** in den Projektkompass. Er wird nur durch einen bewussten Konsolidierungsschritt neu erzeugt.

## Regeln fuer dieses Vault

- Nutze Wikilinks wie `[[Notizname]]` fuer interne Verknuepfungen.
- Neue Notizen ohne klaren Platz kommen zunaechst in `01 Inbox/`.
- Halte Notizen moeglichst atomar. Eine Idee pro Notiz, ausser bei Daily Notes.
- Daily Notes werden als `YYYY-MM-DD.md` benannt.
- Nutze YAML Frontmatter mit mindestens `tags`. Wenn sinnvoll auch `status` und `date`.
- Dateinamen bleiben in normaler Schreibweise mit Leerzeichen und Grossbuchstaben.
- Neue Projekte bekommen zunaechst eine einzelne `.md`-Datei direkt unter `02 Projekte/`.
- Wenn ein Projekt mehrere zusammengehoerige Notizen bekommt, wird die Hauptnotiz nach `02 Projekte/<Projektname>/<Projektname>.md` verschoben. Diese Datei bleibt die kanonische Projektstartseite; eine zusaetzliche Root-Datei `02 Projekte/<Projektname>.md` bleibt dann nicht bestehen. Zugehoerige Tasks liegen im jeweiligen Projekt unter `Tasks/`.
- Wenn ein Projekt eigene `Tasks/`-Notizen hat, bleibt die Hauptprojektnotiz trotzdem die kanonische Status-Startseite. Feature- oder Phasen-Details werden in die passende Task-Notiz geschrieben und von der Projektstartseite aus verlinkt.
- Bereiche und Ressourcen sind Ordner, weil sie ueber die Zeit wachsen.
- Abgeschlossene Projekte werden nur auf Anweisung nach `06 Archive/` verschoben.
- Vor Loeschen oder Ueberschreiben bestehender Inhalte nachfragen.
- Wenn der Nutzer sagt "merk dir das" oder "speicher das", wird die Information thematisch passend abgelegt: Schreibregeln nach `00 Kontext/Schreibstil.md`, Projektinfos in die Projektdatei, technische Erkenntnisse nach `04 Ressourcen/`, Vault-Regeln in diese `Brain.md`.
- Session-Deltas gehoeren in `05 Daily Notes/`, nicht in eine globale `memory.md` oder in rohe Chat-Logs.
- Wenn ein `Projektkompass.md` existiert, bleibt trotzdem immer die kanonische Hauptnotiz die Wahrheitsquelle.
- Wenn die reale Vault-Struktur und diese Datei auseinanderlaufen, zuerst `Brain.md` korrigieren oder die Abweichung explizit markieren, bevor neue Inhalte an eine falsche Stelle geschrieben werden.

## Pflege von Brain.md

`Brain.md` wird aktualisiert, wenn mindestens einer dieser Faelle eintritt:

- Eine Top-Level-Struktur, ein Ordnername oder eine Ablageregel hat sich dauerhaft geaendert.
- Ein neues Repo bindet das Vault ueber einen anderen stabilen Mount-Pfad ein.
- Eine dauerhafte Regel fuer das Speichern, Verlinken oder Auffinden von Wissen hat sich etabliert.
- Der dokumentierte Hauptzweck des Vaults ist zu eng oder veraltet geworden.

## Session-Routinen

### Bei Session-Start

1. `01 Inbox/` auf neue Eintraege pruefen und das Einsortieren anbieten.
2. Bei Projektsessions zuerst die kanonische Hauptnotiz laden. Wenn vorhanden, `Projektkompass.md` als abgeleiteten Cache lesen und danach die Hauptnotiz bestaetigen.
3. Fuer aktuellen Verlauf die letzten relevanten Daily Notes der vergangenen 3-7 Tage heranziehen.

### Kontext bei Bedarf

Wenn der Nutzer nach dem aktuellen Stand fragt, zuerst die relevanten Projektdateien in `02 Projekte/`, bei Bedarf die letzten Daily Notes in `05 Daily Notes/` und zugehoerige Projekt-Tasks lesen.

### Bei Session-Ende

Wenn eine Session natuerlich endet, anbieten:

1. Einen Eintrag in `05 Daily Notes/` zu erstellen
2. Neue Erkenntnisse als Notizen zu speichern
3. Die kanonische Hauptprojektnotiz zu aktualisieren, falls sich dauerhafte Wahrheit geaendert hat
4. Die Inbox aufzuraeumen
