Roadmap zur Stabilisierung der Streamlit-App
 Ziel: Die nachfolgenden Aufgaben beschreiben Schritt für Schritt, wie die Streamlit-Anwendung
 verbessert werden kann, um das „Springen“ zwischen Seiten zu verhindern, Eingaben persistent zu
 speichern und Re-Runs nur gezielt auf Knopfdruck durchzuführen. Jede Aufgabe enthält alle
 notwendigen Details (“Tipps & Tricks der Elite”) zur Umsetzung, sodass eine KI-Implementierung sie
 direkt verstehen und umsetzen kann.
Aufgabe 1: Robuste Sidebar-Navigation einrichten
 Beschreibung: Die App soll über eine Seitenleiste mit Navigationselementen (z.B. Buttons oder
 Auswahlmenü) verfügen, um zwischen den ~50 Bereichen der Anwendung zu wechseln. Diese
 Navigation muss so implementiert sein, dass der aktuell gewählte Bereich im Zustand (Session State)
 erhalten bleibt und nicht beim ersten Interagieren wieder umspringt.
 Vorgehen:
 •
•
Session-State-Variable für aktuelle Seite einführen: Anstatt nur sofortige Aktionen von
 st.sidebar.button zu verwenden, sollte der Seitenwechsel über eine Session-State-Variable
 gesteuert werden. Beispiel:
st.session_state["page"] speichert den aktuellen
 Seitenname. Die Sidebar-Buttons setzen lediglich diese Variable, woraufhin ein
 st.experimental_rerun() ausgelöst werden kann (falls nötig). Beim nächsten Lauf rendert
 das Script dann den entsprechenden Bereich basierend auf dem Wert in
 st.session_state["page"] . Dieses Vorgehen stellt sicher, dass die Auswahl persistiert und
 nicht verloren geht, wenn kein Button gedrückt ist (Buttons sind nur beim Klick-Event
danach wieder
False ).
True ,
 Alternative: Auswahl-Widget nutzen: Eine Alternative ist, statt vieler einzelner Buttons ein
 Auswahl-Widget wie
st.sidebar.radio oder
st.selectbox zu verwenden, das die
 Seitenauswahl enthält. Dadurch wird automatisch ein zusammenhängender Zustand für die
 Seitenwahl erzeugt (der ausgewählte Wert bleibt erhalten) und man vermeidet die Problematik,
 dass Buttons nur transient sind . Wichtig ist, jedem Auswahl-Widget einen eindeutigen
 1
 2
 key zu geben, damit dessen Zustand in
st.session_state gespeichert wird (siehe Aufgabe
 2).
•
Seiteninhalt bedingt rendern: Strukturieren Sie Ihren Code so, dass am Anfang (nach dem
 Sidebar-Menü) mittels if/elif-Blöcken oder einer Dispatch-Funktion der entsprechende
 Seiteninhalt gerendert wird, abhängig von
st.session_state["page"] . Beispiel:
if st.session_state.page == "Bedarfsanalyse":
 render_bedarfsanalyse()
 elif st.session_state.page == "Solarkalkulator":
 render_solarkalkulator()

# etc

 1
Dieses Muster stellt sicher, dass immer nur der aktive Bereich angezeigt wird.
 3
 3
 Warum? Ohne eine Session-Variable für die Seite kann ein unbeabsichtigter Rerun die App auf einen
 Default-Zustand zurückwerfen (z.B. wieder die Startseite anzeigen), was als „Springen“ wahrgenommen
 wird. Mit obiger Navigation bleibt die Auswahl stabil, weil Streamlit den Zustand der Widgets (Radio/
 Button) über den Session State trackt . Die Streamlit-Dokumentation betont, dass Widgets einen
 eindeutigen Identity-Key haben und dass Streamlit deren Zustand löscht, wenn sie in einem Run nicht
 gerendert werden . Daher ist es wichtig, selbst den aktuellen Seitenzustand zu verwalten, um das
 automatische Entfernen zu verhindern.
 Aufgabe 2: Eingabewerte im Session State persistent halten
 Beschreibung: Damit Eingaben in verschiedenen Bereichen (z.B. manuelle Texteingaben in der
 Bedarfsanalyse oder Produktauswahlen im Solarkalkulator) beim Zurückkehren noch vorhanden sind,
 müssen alle wichtigen Werte im
st.session_state zwischengespeichert werden. So gehen sie bei
 einem Seitenwechsel oder Rerun nicht verloren und die Felder behalten ihre zuletzt eingegebenen
 Werte.
 Vorgehen:
 •
•
Initialisierung einmalig vornehmen: Definieren Sie für jede relevante Eingabe einen
 eindeutigen Schlüssel (
 key ) und initialisieren Sie deren Default-Wert beim ersten Laden der
 App. Zum Beispiel:
if "bedarf_text" not in st.session_state:
 st.session_state.bedarf_text = ""
 Dadurch wird ein leerer Text für ein Eingabefeld Bedarfsanalyse nur gesetzt, wenn noch kein Wert
 vorhanden ist. Wichtig: Diese Initialisierung sollte vor dem Rendern der Widgets erfolgen, damit
 die Widgets den richtigen Startwert aus dem Session State bekommen.
 Widgets mit Keys versehen: Verwenden Sie bei jedem
st.selectbox etc. den Parameter
st.text_input ,
st.number_input ,
 key=... , um sie direkt mit einem Session-State-Wert zu
 verknüpfen
 4
 5
 . Beispiel:
eingabe = st.text_input("Eingabe", key="bedarf_text")
 In diesem Fall speichert Streamlit den Inhalt automatisch unter
st.session_state["bedarf_text"] . Gleiches gilt für Dropdowns:
auswahl = st.selectbox("Produkt", options=produkte_liste,
 key="ausgewähltes_produkt")
 Hierdurch bleibt die Auswahl erhalten, selbst wenn man die Seite wechselt – sofern die Keys
 nicht “bereinigt” werden (siehe unten).
 2
•
Manuelles Zwischenspeichern bei besonderen Widgets: Manche Widgets (z.B. File-Uploader
 oder Buttons) behalten ihren Zustand nicht automatisch. In solchen Fällen kann man den Wert
 manuell auf einen Session-State-Schlüssel spiegeln. Ein Beispiel aus der Community: Beim
 Hochladen einer PDF-Datei mit
st.file_uploader geht die Referenz verloren, sobald man
 die Seite wechselt, es sei denn man speichert sie in
st.session_state :
pdf_file = st.file_uploader("PDF hochladen", type=["pdf"],
 key="pdf_upload")
 if pdf_file:
 st.session_state.pdf_data = pdf_file.getvalue()
 Dadurch bleibt
pdf_data erhalten und kann auf anderen Seiten verwendet werden, auch
 wenn
pdf_file als Widget nicht mehr sichtbar ist .
 4
 5
 Warum? Normalerweise verwirft Streamlit Widget-Werte, wenn der Widget-Aufruf im nächsten Run
 fehlt – das ist der sogenannte Widget Cleanup Process. Beim Seitenwechsel werden die Keys von
 Widgets, die auf der neuen Seite nicht vorhanden sind, aus
st.session_state gelöscht . Um das
 zu verhindern, müssen wir die Werte unabhängig vom Widget speichern. Durch die eindeutigen Keys
 und Session-State-Nutzung bleiben die Daten in der laufenden Nutzersession vorhanden .
6
 7
 Aufgabe 3: Widget-Cleanup verhindern (Werte über Seiten
 hinweg halten)
 Beschreibung: Um den oben genannten Effekt – dass Werte beim Seitenwechsel verschwinden
komplett auszuschalten, wenden wir einen Trick an, den erfahrene Streamlit-Entwickler nutzen. Es gibt
 zwei Ansätze, um den Widget-Cleanup zu umgehen:
 Vorgehen (Option A – Hacky Trick):
 •
Werte an sich selbst zuweisen: Fügen Sie am Anfang jeder Seite (bzw. in jedem Seitenmodul)
 eine Schleife ein, die alle aktuell im Session State befindlichen Werte einmal sich selbst zuweist.
 Zum Beispiel:
for key in st.session_state.keys():
 st.session_state[key] = st.session_state[key]
 Oder gezielter:
st.session_state["bedarf_text"] = st.session_state["bedarf_text"]
 st.session_state["ausgewähltes_produkt"] =
 st.session_state["ausgewähltes_produkt"]

# ... etc für alle wichtigen Keys

 Dieser Code bewirkt, dass Streamlit denkt, die Widgets seien weiterhin „aktiv“. Es unterbricht
 den Widget-Cleanup-Prozess, sodass die Keys nicht gelöscht werden, obwohl die zugehörigen
 Widgets nicht gerendert werden
 7
 . Wichtig: Dieser Code muss auf jeder Seite ausgeführt
 3
8
 werden, wenn man von einer anderen Seite kommt (also idealerweise ganz oben in jedem
 Seiten-Skript), damit die Werte erhalten bleiben .
Hinweis: Mit diesem Hack sollte man vorsichtig sein bei speziellen Widgets wie Buttons oder File
 Uploadern (diese könnten unerwartete Effekte haben, wenn man sie manuell zuweist ). Für normale
 Eingabe-Widgets funktioniert es aber gut.
 Vorgehen (Option B – Saubere Methode mit getrennten Keys):
 •
9
 Permanente vs. temporäre Keys nutzen: Ein eleganterer Ansatz ist, für jedes Widget zwei Keys
 zu verwenden – einen temporären Widget-Key (der mit
_prefix z.B.
"_bedarf_text" heißt)
 und einen permanenten Wert-Key (z.B.
•
•
"bedarf_text" ). Der Ablauf ist dann:
 Wenn die Seite gerendert wird, lesen Sie den permanenten Wert in den Widget-Key ein
 (Initialisierung der Eingabe).
 Nach Nutzer-Eingaben synchronisieren Sie den Widget-Key zurück auf den permanenten Wert.
 Konkret:

# Beim Laden der Seite (falls noch nicht geschehen)

 if "bedarf_text" not in st.session_state:
 st.session_state.bedarf_text = ""

# Temp. Wert dem Widget-Key zuweisen

 st.session_state["_bedarf_text"] = st.session_state.bedarf_text

# Widget mit dem Widget-Key anzeigen

 st.text_input("Bedarf", key="_bedarf_text", on_change=lambda:
 st.session_state.update(bedarf_text=st.session_state["_bedarf_text"]))
 Hier wird mittels
on_change Callback die Eingabe direkt in den permanenten Key zurückgeschrieben,
 sobald der User etwas ändert
 10
 11
 . Der Clou: Der permanente Key
bedarf_text bleibt immer in
st.session_state erhalten, auch wenn das Widget verschwindet, und beim nächsten Aufruf setzen
 wir den Widget (mit
_bedarf_text ) wieder auf diesen Wert.
•
Apply für alle relevanten Felder: Dies erfordert pro Widget etwas Code, lässt sich aber
 verallgemeinern. In dem zitierten Beispiel aus der Community wurde eine Funktion
verwendet, um den Wert zu übertragen
 10
 12
 keep(key)
 . Diese Methode verhindert Datenverlust zuverlässig
 und umgeht die interne Löschlogik von Streamlit auf saubere Weise .
 Warum? Option A funktioniert, ist aber ein Hack. Option B orientiert sich an bewährten Mustern: Man
 trennt den Zustand des Widgets vom eigentlichen Anwendungszustand. Streamlit löscht nur die Widget
gebundenen Keys (z.B.
6
 _bedarf_text ), nicht aber unsere eigenen persistenten Keys (z.B.
 bedarf_text ) . Somit bleibt der Wert erhalten. Dieser Trick ist inoffiziell, aber effektiv – genau das
 „geheime Zeug“, das nur erfahrene Entwickler kennen. Die offizielle Empfehlung der Streamlit
Entwickler geht ebenfalls in diese Richtung, nämlich Widget-Keys von den zu speichernden Werten zu
 entkoppeln .
 12
 Aufgabe 4: Widget-Update-Bug (doppelte Eingabe nötig) beheben
 Beschreibung: Ein beobachtetes Problem ist, dass Änderungen an bestimmten Eingabefeldern erst
 beim zweiten Versuch greifen. Beispiel: Man wählt ein Produkt aus einer Dropdown-Liste aus. Beim
 4
ersten Wechsel zur neuen Auswahl springt das Feld zurück zur vorherigen Auswahl; erst beim zweiten
 Mal bleibt der neue Wert. Das gleiche wurde für manuelle Eingaben (Textfelder oder Zahlen) berichtet.
 Dieses Verhalten ist ein bekannter Bug in Streamlit, der u.a.
st.text_input ,
st.number_input ,
st.text_area betrifft
 13
 . Wir implementieren einen Workaround, um das sofort zu beheben.
 Ursache: Der Fehler tritt oft auf, wenn der Widget-Wert im gleichen Run noch einmal
 programmgesteuert gesetzt wird, insbesondere über den
value Parameter und anschließendes
 Überschreiben im Session State. Dadurch kommt es zu einem Konflikt zwischen altem und neuem Wert,
 so dass die erste Änderung verworfen wird . (Eine offizielle Behebung dieses Bugs ist im
 14
 15
 September 2025 in Arbeit, wobei
st.number_input künftig eindeutiger über den
wird
 16
 – bis das verfügbar ist, sollten wir den Workaround nutzen.)
 Vorgehen zur Behebung:
 •
key identifiziert
 Kein unmittelbares Überschreiben nach Input: Stellen Sie sicher, dass Sie nicht so codieren:
val = st.text_input("Eingabe", value=st.session_state.val)
 st.session_state.val = val
 14
 Dieser Ansatz führt zum beschriebenen Problem . Vermeiden Sie es, den Session State direkt
 nach dem Widget wieder zu überschreiben.
 •
Session State direkt nutzen (empfohlen): Besser ist es, dem Widget einen
nicht den
value-Parameter jedes Mal manuell aus
st.text_input("Eingabe", key="meine_eingabe")
 key zu geben und
 session_state zu setzen. Zum Beispiel:
Hier kümmert sich Streamlit selbst darum,
st.session_state["meine_eingabe"] zu
 aktualisieren, ohne dass wir eingreifen. Wenn man vorher
st.session_state["meine_eingabe"] initialisiert hat (siehe Aufgabe 2), wird dieser Wert
 als Default angezeigt und anschließend bei Änderungen automatisch aktualisiert. So bleibt der
 Wert konsistent.
 •
Alternative mit Callback: Sollte es nötig sein, den
value Parameter zu nutzen oder
 komplexere Logik durchzuführen, verwenden Sie die
on_change Callback-Funktion des
 Widgets. Beispielsweise kann man bei einem Textfeld folgendes machen:
def update_val():
 st.session_state.val = st.session_state.temp_val
 st.text_input("Eingabe", key="temp_val", value=st.session_state.val,
 on_change=update_val)
 Dabei ist
temp_val ein separater Widget-Key, der beim Ändern den Callback
update_val
 triggert, welcher den Wert in den eigentlichen State
val übernimmt
 17
 18
 . Diese Methode
 stellt sicher, dass Streamlit die Eingabe vollständig registriert. Laut Community-Berichten
 funktioniert dieser Ansatz zuverlässig und umgeht den „jeder zweite Input“-Bug .
 19
 5
Warum? Durch diese Änderungen verhindern wir, dass der Streamlit-Renderloop durcheinanderkommt.
 Der Bug entsteht durch Timing-Probleme in der internen Abfolge (Wert setzen vs. Rendern). Die
 on_change-Methode oder konsequente Nutzung von
key isoliert die Benutzeränderung, so dass sie
 beim ersten Mal angenommen wird. Zusammen mit Aufgabe 2 und 3 (Session State richtig einsetzen)
 erreicht man so, dass z.B. ein Dropdown-Wechsel sofort wirkt und nicht mehr zurückspringt. Tatsächlich
 wurde dieser Workaround in Foren empfohlen und bestätigt .
20
 18
 Aufgabe 5: Steuerung von Reruns mit Formularen (gezielte
 Neuberechnung)
 Beschreibung: Standardmäßig führt jede Änderung eines Eingabewertes in Streamlit einen sofortigen
 Re-Run des gesamten Skripts aus. Bei einer komplexen App (z.B. mit umfangreichen Berechnungen
 oder PDF-Generierung) kann das zu spürbaren Verzögerungen oder dem „Springen“ führen, wenn z.B.
 bei jedem Tastendruck der Output-Bereich neu gerendert wird. Wir möchten erreichen, dass
 Interaktionen gebündelt und nur auf Knopfdruck berechnet werden.
 Vorgehen:
 •
Forms einsetzen: Streamlit bietet mit
st.form die Möglichkeit, mehrere Eingabefelder zu
 einem Formular zusammenzufassen. Innerhalb eines
with st.form(...): Blocks platzierte
 Widgets lösen keinen sofortigen Re-Run aus, sondern nur ein einmaliger Re-Run erfolgt, wenn
 der Nutzer den Formular-Submit-Button klickt
 21
 22
 . Beispielsweise:
with st.form("bedarf_form"):
 eingabe1 = st.text_input("Eingabe 1", key="eing1")
 eingabe2 = st.number_input("Eingabe 2", key="eing2")
 submitted = st.form_submit_button("Berechnen")
 if submitted:

# nur ausgef\u00FChrt nach Klick auf "Berechnen"

 berechne_ergebnis(eingabe1, eingabe2)
 st.write("Ergebnis...", ...)
 Hier kann der Nutzer beide Felder ausfüllen oder ändern, ohne dass die App sofort neu läuft.
 Erst beim Klick auf Berechnen werden die Werte übernommen und die Berechnung gestartet.
•
•
Heavy Calculations/PDF-Erstellung an Submit koppeln: Verschieben Sie zeitintensive
 Operationen (Solarkalkulationen, PDF-Generierung) in solche Submit-Events. Auf diese Weise
 passiert die aufwändige Aktion nur, wenn der Nutzer es ausdrücklich anfordert, und nicht aus
 Versehen bei jeder kleinen Eingabeänderung. Dies macht die App responsiver und stabiler im
 Gefühl.
 Teilformulare pro Bereich: Sie können pro Bereich (Seite) ein eigenes Formular vorsehen. Z.B.
 in Bedarfsanalyse ein Formular für die Bedarfseingaben mit einem „Weiter“ oder „Speichern“
 Button, in Solarkalkulator ein Formular für die Produktauswahl und Parameter mit einem
 „Berechnen“ Button, etc. Achten Sie darauf, unterschiedliche
verwenden (z.B.
"bedarf_form" ,
key /Namen für die Forms zu
 "solar_form" ), damit sie sich nicht stören.
 6
22
 Warum? Durch Forms “batchen” wir die Interaktionen: „When you don’t want to rerun your script with
 each input made by a user, st.form is here to help! Forms make it easy to batch user input into a single rerun.”
 erklärt Streamlit in seinen Advanced Features . Für den Nutzer bedeutet das: die App springt nicht
 mehr bei jeder kleinen Änderung hin und her, sondern reagiert kontrolliert. Dies adressiert genau das
 Problem, dass z.B. beim Tippen oder einmaligen Dropdown-Wechsel alles neu gerendert wurde. Mit
 Formularen bleibt der aktuelle Bildschirm stehen, bis man auf "Submit" drückt – das macht die
 Anwendung wesentlich stabiler und benutzerfreundlicher.
 Aufgabe 6: Manuelle Reset-/Restart-Funktion einbauen
 Beschreibung: Die App soll nicht automatisch ihren Zustand verlieren, nur weil man zwischen Menüs
 wechselt. Stattdessen möchten wir, dass ein Reset/Leeren der Eingaben explizit vom Nutzer
 ausgelöst wird (z.B. nachdem ein Angebot fertig erstellt wurde und man einen neuen Durchlauf
 beginnen möchte). Hierfür bauen wir einen “Reset” oder “Neustart”-Button ein, der gezielt Session
State-Einträge löscht oder zurücksetzt.
 Vorgehen:
 •
Reset-Button in Sidebar oder Header: Platzieren Sie einen Button, z.B.
 st.sidebar.button("Neues Projekt starten") oder
st.button("Eingaben
zur\u00FCcksetzen") an geeigneter Stelle (etwa auf der PDF-Ergebnis-Seite oder global in
 der Navigation).
•
•
Callback zum Leeren definieren: Nutzen Sie entweder den Rückgabewert des Buttons oder
 on_click , um eine Funktion aufzurufen, die
st.session_state bereinigt. Beispiel:
def reset_state():
 for key in ["bedarf_text", "ausgewähltes_produkt", ...]: # alle
relevanten Keys
 st.session_state.pop(key, None)
 st.session_state.page = "Bedarfsanalyse"

# optional: zur Startseite wechseln

 st.sidebar.button("Neues Projekt", on_click=reset_state)
 Diese Funktion entfernt alle gespeicherten Eingabedaten und setzt die Seite zurück. Wichtig: Nur
 die Keys entfernen, die wirklich neu gestartet werden sollen – z.B. könnte man auch Ergebnisse
 oder Datei-Uploads zurücksetzen. Dadurch startet der Benutzer mit leerer Maske neu, aber nur
 wenn er es möchte.
 Bestätigung oder mehrstufiger Reset (optional): Falls gewünscht, kann man einen Confirm
Dialog vorschalten (derzeit unterstützt Streamlit einfache Modal-Dialoge nicht nativ, aber man
 könnte z.B. einen zweiten Button "Wirklich löschen?" einblenden oder eine kleine Checkbox zur
 Bestätigung einbauen).
 Warum? Dieses Feature gibt dem Anwender die Kontrolle. Ohne manuelle Reset-Funktion versucht
 man oft mit Seitenwechseln oder F5 die App neu zu laden, was aber alle Session-Daten verliert. Mit
 einem gut implementierten Reset-Button wird gezielt nur das gelöscht, was nötig ist (z.B.
 Eingabeformular leeren nach PDF-Erstellung), und es passiert nicht unbeabsichtigt beim Navigieren.
 7
In Kombination mit Aufgaben 2 und 3 (wo wir Persistenz eingebaut haben) ist so ein manueller Reset
 der definierte Weg, um einen frischen Zustand zu bekommen, anstatt dass die App an unpassenden
 Stellen selbst alles zurücksetzt.
 Aufgabe 7: Weitere Optimierungen und Best Practices
 Beschreibung: Über die obigen Kernmaßnahmen hinaus gibt es einige zusätzliche Tipps, um die App
 so robust wie möglich zu machen und bekannte Stolpersteine zu vermeiden:
 •
•
•
•
•
Caching für aufwändige Berechnungen verwenden: Falls bestimmte Berechnungen (z.B.
 Solarkalkulation) oder Datenbank-Abfragen immer wieder ausgeführt werden, nutzen Sie
 st.cache_data oder
st.cache_resource (je nach Anwendungsfall) um Ergebnisse zu
 cachen. So werden identische Berechnungen nicht mehrfach durchgeführt, was die Performance
 steigert. Vorsicht: Invalidate den Cache, wenn Eingabedaten wirklich geändert wurden. Durch
 Caching wird das Erlebnis flüssiger und verhindert möglicherweise auch Timing-Probleme, weil
 weniger oft neu gerechnet wird.
 Keine unnötigen globalen Variablen: Verwenden Sie den Session State anstelle globaler
 Variablen, um Daten zu teilen. Globale Variablen werden bei jedem Rerun neu initialisiert (es sei
 denn, sie sind in
st.session_state ). Mit Session State haben Sie pro Nutzer eine Art
 globalen Speicher, der über Reruns hinweg gleich bleibt . Dies stabilisiert die App, da Sie
 genau kontrollieren, was persistent ist.
 23
 Eindeutige Keys und keine Kollisionen: Stellen Sie sicher, dass alle Widgets in der gesamten
 App eindeutige Keys haben. Bei ~50 Seiten besteht die Gefahr, dass man z.B. zweimal
 key="submit_button" verwendet – das würde zu Konflikten oder unerwartetem Verhalten
 führen (Widgets beeinflussen sich gegenseitig). Am besten vergeben Sie präfixte Keys, z.B.
 "bedarf_submit" vs.
"solar_submit" , oder nutzen Sie die Seitennamen im Key.
 State zwischen Sessions nicht verwechseln: Bedenken Sie, dass
st.session_state pro
 User-Session getrennt ist. Aktionen eines Nutzers beeinflussen keinen anderen, was gut ist .
 Aber ein Refresh (F5) im Browser startet eine neue Session (alle Daten weg). Wenn persistente
 Speicherung über Sessions hinweg gewünscht ist, müsste man externe Speicherung
 (Datenbank, Datei) in Betracht ziehen – das geht aber über den normalen Anwendungsfall
 hinaus. Für eine stabile Laufzeit innerhalb einer Session haben wir mit den obigen Schritten
 bereits das Maximum herausgeholt.
 24
 Debugging-Hilfen einbauen: Während der Umsetzung kann es helfen, wichtige
 st.session_state Werte zeitweise anzuzeigen (z.B.
st.write(st.session_state) in
 der Sidebar) um zu beobachten, ob die State-Updates wie erwartet passieren. Entfernen Sie
 solche Debug-Outputs später für den Endnutzer.
Diese zusätzlichen Hinweise sorgen dafür, dass die App nicht nur das ursprüngliche Springen
 verhindert, sondern insgesamt stabil, performant und vorhersagbar läuft. Viele dieser Tipps
 stammen aus Community-Erfahrungen und offiziellen Best Practices und sind erfahrungsgemäß nicht
 allgemein bekannt, gehören aber zum „Elite-Wissen“, um komplexe Streamlit-Apps zu meistern.
 8
Fazit
 Durch die Umsetzung der obigen Aufgaben wird Ihre Streamlit-App deutlich robuster:
 •
•
•
•
Seitenwechsel führen nicht mehr zum Verlust der Eingaben oder ungewollten Sprüngen, da die
 Navigation mittels Session State stabil gehalten wird und alle Eingabefelder persistent sind
 (Aufgaben 1–3).
 Eingaben bleiben erhalten, und Änderungen greifen sofort korrekt beim ersten Mal (Aufgabe 4),
 was die Benutzererfahrung verbessert.
 Neuladevorgänge passieren nur noch gezielt: Entweder gebündelt auf Benutzeraktion hin
 (Form-Submit, Aufgabe 5) oder durch einen expliziten Reset (Aufgabe 6), nicht mehr bei jeder
 kleinen Interaktion.
 Zusatzoptimierungen (Aufgabe 7) runden das Ganze ab, indem Performance-Probleme und
 Wartungsrisiken minimiert werden.
 All diese Schritte zusammen stellen sicher, dass Ihre Streamlit-App stabil läuft, nicht hin- und
 herspringt, und dem Nutzer ein konsistentes Verhalten bietet. Die vorgeschlagenen Lösungen basieren
 auf gründlicher Recherche und dem Wissen erfahrener Entwickler – inklusive der „geheimen“ Tricks, die
 oft den Unterschied machen. Befolgen Sie diese Roadmap Schritt für Schritt, dann sollte Ihre App
 künftig genau so funktionieren, wie Sie es erwarten. Viel Erfolg!
3
 21
 Quellen: Die verwendeten Techniken und Erklärungen stützen sich auf die offiziellen Streamlit
Dokumentationen und Community-Beiträge, u.a. zur Session State Verwaltung , zum Widget
Lifecycle , bekannten Workarounds für Eingabebugs sowie Best Practices zum Einsatz von
 Forms . Diese Referenzen bieten weiterführende Details zu den hier beschriebenen „Patches“ und
 bestätigen die Wirksamkeit der vorgeschlagenen Maßnahmen.
6
 13
 18
 7
 1
 9
 Retain user input values in multipage app when changing pages - Using Streamlit - Streamlit
 <https://discuss.streamlit.io/t/retain-user-input-values-in-multipage-app-when-changing-pages/44714>
 2
 6
 7
 8
 10
 11
 12
 python - Session state is reset in Streamlit multipage app - Stack Overflow
 <https://stackoverflow.com/questions/74968179/session-state-is-reset-in-streamlit-multipage-app>
 3
 24
 Widget behavior - Streamlit Docs
 <https://docs.streamlit.io/library/advanced-features/widget-behavior>
 4
 5
 Display pdf in streamlit - Using Streamlit - Streamlit
 <https://discuss.streamlit.io/t/display-pdf-in-streamlit/62274>
 13
 After first input, st.number_input requires to input twice to get the right value returned if the
 widget's value parameter is assigned a class property which is stored in st.session_state · Issue #9657 ·
 streamlit/streamlit · GitHub
 <https://github.com/streamlit/streamlit/issues/9657>
 14
 15
 17
 18
 19
 20
 Text_input only getting set every other time? - Using Streamlit - Streamlit
 <https://discuss.streamlit.io/t/text-input-only-getting-set-every-other-time/50106>
 16
 Use `key` as main identity for `st.number_input` by lukasmasuch · Pull Request #12437 · streamlit/
 streamlit · GitHub
 <https://github.com/streamlit/streamlit/pull/12437>
 21
 22
 Using forms - Streamlit Docs
 <https://docs.streamlit.io/develop/concepts/architecture/forms>
 9
23
 Ultimate guide to the Streamlit library - Deepnote
 <https://deepnote.com/blog/ultimate-guide-to-the-streamlit-library>
 10
