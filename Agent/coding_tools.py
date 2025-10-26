# ==============================================================================
# agent/tools/coding_tools.py
# Werkzeuge für den Dateisystemzugriff im Arbeitsbereich des Agenten.
# ==============================================================================
from agent.tools.execution_tools import execute_python_code_in_sandbox
from agent.tools.coding_tools import list_files, read_file, write_file
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferMemory
from langchain.agents import AgentExecutor, create_openai_functions_agent
import docker
import time
import os

from langchain.tools import tool

# Definieren des sicheren Arbeitsverzeichnisses für den Agenten.
# Alle Dateioperationen sind auf dieses Verzeichnis beschränkt.
AGENT_WORKSPACE = "agent_workspace"

# Sicherstellen, dass das Arbeitsverzeichnis existiert.
if not os.path.exists(AGENT_WORKSPACE):
    os.makedirs(AGENT_WORKSPACE)


@tool
def write_file(path: str, content: str) -> str:
    """
    Schreibt den angegebenen Inhalt in eine Datei unter dem angegebenen Pfad.
    Erstellt die Datei, falls sie nicht existiert, und alle notwendigen Verzeichnisse.
    Überschreibt die Datei, wenn sie bereits existiert.
    """
    try:
        # Sicherheitsüberprüfung: Verhindern, dass der Agent aus dem
        # Arbeitsbereich ausbricht.
        full_path = os.path.join(AGENT_WORKSPACE, path)
        if not os.path.abspath(full_path).startswith(
                os.path.abspath(AGENT_WORKSPACE)):
            return "Fehler: Der Versuch, außerhalb des Arbeitsverzeichnisses zu schreiben, ist nicht erlaubt."

        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Datei erfolgreich nach '{path}' geschrieben."
    except Exception as e:
        return f"Fehler beim Schreiben der Datei: {e}"


@tool
def read_file(path: str) -> str:
    """
    Liest den Inhalt einer Datei unter dem angegebenen Pfad und gibt ihn zurück.
    """
    try:
        # Sicherheitsüberprüfung
        full_path = os.path.join(AGENT_WORKSPACE, path)
        if not os.path.abspath(full_path).startswith(
                os.path.abspath(AGENT_WORKSPACE)):
            return "Fehler: Der Versuch, außerhalb des Arbeitsverzeichnisses zu lesen, ist nicht erlaubt."

        with open(full_path, encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return f"Fehler: Datei unter '{path}' nicht gefunden."
    except Exception as e:
        return f"Fehler beim Lesen der Datei: {e}"


@tool
def list_files(path: str = ".") -> str:
    """
    Listet alle Dateien und Verzeichnisse unter dem angegebenen Pfad im Arbeitsbereich auf.
    """
    try:
        # Sicherheitsüberprüfung
        full_path = os.path.join(AGENT_WORKSPACE, path)
        if not os.path.abspath(full_path).startswith(
                os.path.abspath(AGENT_WORKSPACE)):
            return "Fehler: Der Versuch, außerhalb des Arbeitsverzeichnisses aufzulisten, ist nicht erlaubt."

        if not os.path.exists(full_path):
            return f"Fehler: Verzeichnis '{path}' nicht gefunden."

        files = os.listdir(full_path)
        if not files:
            return f"Das Verzeichnis '{path}' ist leer."
        return "\n".join(files)
    except Exception as e:
        return f"Fehler beim Auflisten der Dateien: {e}"


# ==============================================================================
# agent/tools/execution_tools.py
# Werkzeug zur Ausführung von Python-Code in der sicheren Docker-Sandbox.
# ==============================================================================


@tool
def execute_python_code_in_sandbox(code: str) -> str:
    """
    Führt ein Python-Code-Snippet in einer isolierten Docker-Sandbox aus.
    Gibt die kombinierte Ausgabe (stdout und stderr) zurück.
    Startet einen neuen Container für jede Ausführung, um die Isolation zu gewährleisten.
    """
    client = docker.from_env()
    container_name = f"kai-sandbox-{int(time.time())}"

    try:
        print(
            f"INFO: Erstelle und starte Sandbox-Container '{container_name}'...")
        # 'kai_agent-sandbox' ist der Name, den wir dem Image beim Bauen geben werden.
        container = client.containers.run(
            "kai_agent-sandbox",
            command=["python", "-c", code],
            name=container_name,
            detach=True,
            # Netzwerkzugriff für den Anfang deaktivieren (höchste Sicherheit)
            network_disabled=True,
        )

        # Warten, bis der Container seine Arbeit beendet hat (mit einem
        # Timeout)
        result = container.wait(timeout=30)

        # Ausgabe und Fehler aus dem Container holen
        stdout = container.logs(stdout=True, stderr=False).decode('utf-8')
        stderr = container.logs(stdout=False, stderr=True).decode('utf-8')

        print(
            f"INFO: Sandbox-Ausführung beendet. Exit Code: {result.get('StatusCode')}")

        output = ""
        if stdout:
            output += f"--- STDOUT ---\n{stdout}\n"
        if stderr:
            output += f"--- STDERR --- (Fehler)\n{stderr}\n"

        if not output:
            return "Code erfolgreich ohne Ausgabe ausgeführt."

        return output

    except docker.errors.ImageNotFound:
        return "Fehler: Docker-Image 'kai_agent-sandbox' nicht gefunden. Bitte baue es zuerst mit 'docker build -t kai_agent-sandbox . -f sandbox/Dockerfile'."
    except docker.errors.ContainerError as e:
        return f"Fehler innerhalb des Containers: {e}"
    except Exception as e:
        return f"Ein unerwarteter Docker-Fehler ist aufgetreten: {e}"
    finally:
        # Aufräumen: Container stoppen und entfernen, um Ressourcen
        # freizugeben.
        try:
            running_container = client.containers.get(container_name)
            running_container.stop()
            running_container.remove()
            print(
                f"INFO: Sandbox-Container '{container_name}' erfolgreich aufgeräumt.")
        except docker.errors.NotFound:
            # Container wurde bereits entfernt oder konnte nicht gestartet
            # werden.
            pass
        except Exception as e:
            print(
                f"WARNUNG: Fehler beim Aufräumen des Containers '{container_name}': {e}")


# ==============================================================================
# agent/agent_core.py
# Die Kernlogik des Agenten, die das LLM, die Werkzeuge und die ReAct-Schleife verbindet.
# ==============================================================================


# Importieren der von uns definierten Werkzeuge


class AgentCore:
    def __init__(self):
        # API-Schlüssel aus der .env-Datei holen.
        # Wenn nicht vorhanden, wird LangChain versuchen, ihn aus den
        # Umgebungsvariablen zu lesen.
        if not os.getenv("OPENAI_API_KEY"):
            print("WARNUNG: OPENAI_API_KEY nicht in .env gefunden. Stelle sicher, dass er in der Umgebung gesetzt ist.")

        # 1. Das "Gehirn" des Agenten definieren (LLM)
        # Wir verwenden hier ein leistungsfähiges Modell, das für "Function
        # Calling" optimiert ist.
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0)

        # 2. Die "Hände" des Agenten definieren (Werkzeuge)
        self.tools = [
            write_file,
            read_file,
            list_files,
            execute_python_code_in_sandbox,
        ]

        # 3. Das Prompt-Template definieren
        # Dies gibt dem Agenten seine Persönlichkeit, Anweisungen und den
        # Arbeitsbereich.
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """
            Du bist KAI, ein hochkompetenter, autonomer KI-Softwareentwickler.
            Dein Ziel ist es, die Aufgaben des Benutzers nach bestem Wissen und Gewissen zu erfüllen.

            VERHALTENSREGELN:
            - Du musst Aufgaben in kleinere, logische Schritte zerlegen.
            - Denke bei jedem Schritt nach (Gedanke), bevor du eine Aktion (Aktion) ausführst.
            - Du hast Zugriff auf ein sicheres Dateisystem im Verzeichnis './agent_workspace/'. Verwende die Werkzeuge 'list_files', 'write_file' und 'read_file', um damit zu interagieren.
            - Du kannst Python-Code mit dem Werkzeug 'execute_python_code_in_sandbox' ausführen. Dieser Code wird in einer isolierten Umgebung ausgeführt.
            - Nach jeder Aktion erhältst du eine Beobachtung. Nutze sie, um deinen nächsten Schritt zu planen.
            - Wenn du einen Fehler erhältst, versuche ihn zu debuggen. Analysiere die Fehlermeldung und korrigiere deinen Code oder Ansatz.
            - Wenn du fertig bist, antworte mit dem finalen Ergebnis oder der fertigen Datei.
            """),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

        # 4. Den Agenten erstellen
        # Wir verbinden LLM, Prompt und Werkzeuge.
        agent = create_openai_functions_agent(
            self.llm, self.tools, self.prompt)

        # 5. Den Agent Executor erstellen
        # Dies ist die Laufzeitumgebung, die die ReAct-Schleife (Gedanke -> Aktion -> Beobachtung) ausführt.
        # `verbose=True` ist entscheidend, um den Denkprozess des Agenten zu sehen.
        self.agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            # Wir fügen ein Gedächtnis hinzu, damit der Agent sich an den
            # Gesprächsverlauf erinnert.
            memory=ConversationBufferMemory(
                memory_key="chat_history", return_messages=True)
        )

    def run(self, user_input: str):
        """Startet den Agenten mit einer anfänglichen Aufgabe."""
        print(f"\n--- KAI Agent startet mit der Aufgabe: '{user_input}' ---")
        response = self.agent_executor.invoke({"input": user_input})
        print("\n--- KAI Agent hat die Aufgabe beendet. Finale Antwort: ---")
        print(response["output"])
