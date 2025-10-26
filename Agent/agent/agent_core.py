"""
Agent Core Module - KAI Agent Orchestration
============================================

Main agent orchestration using LangChain's ReAct pattern with GPT-4.
Implements dual-expertise system: renewable energy consulting and
software architecture.

Requirements: 2.1, 2.2, 2.4, 2.5, 10.1, 10.2, 10.4, 11.1, 11.2, 11.3
"""

import os
import time
from typing import Any

# Import error handling and logging
from agent.errors import (
    AgentError,
    APIError,
    ConfigurationError,
    ExecutionError,
    format_error_message,
    get_retry_delay,
    should_retry,
)
from agent.logging_config import get_logger, log_agent_reasoning
from agent.tools.search_tools import tavily_search
from agent.tools.telephony_tools import start_interactive_call, update_call_summary
from agent.tools.testing_tools import execute_pytest_in_sandbox
from langchain_classic.agents import AgentExecutor, create_openai_functions_agent
from langchain_classic.memory import ConversationBufferMemory

# LangChain 1.0+ Import-Updates
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI

# Import tool sets
from agent.tools.coding_tools import (
    generate_project_structure,
    list_files,
    read_file,
    write_file,
)
from agent.tools.execution_tools import (
    execute_python_code_in_sandbox,
    run_terminal_command_in_sandbox,
)
from agent.tools.knowledge_tools import knowledge_base_search


class AgentCore:
    """
    Main agent orchestration class using LangChain's ReAct pattern.

    The agent has dual expertise:
    1. Renewable Energy Consultant - Expert in photovoltaics and
       heat pumps
    2. Software Architect - Builds robust software following best
       practices

    Attributes:
        llm: ChatOpenAI instance (GPT-4)
        tools: List of available tools
        prompt: System prompt template with dual-expertise persona
        agent_executor: LangChain AgentExecutor for ReAct loop
        memory: Conversation buffer for context retention
        logger: Logger instance for tracking agent operations
        max_retries: Maximum number of retry attempts on failure

    Requirements: 2.1, 2.2, 2.4, 10.1, 10.2, 10.4
    """

    def __init__(
        self,
        vector_store,
        model: str = "gpt-4o",
        temperature: float = 0.7,
        max_retries: int = 2,
        verbose: bool = True
    ):
        """
        Initialize agent with knowledge base and configuration.

        Args:
            vector_store: FAISS vector store for knowledge retrieval
            model: OpenAI model name (default: gpt-4o)
            temperature: LLM temperature (0.0-1.0, default: 0.7)
            max_retries: Maximum retry attempts on failure (default: 2)
            verbose: Whether to show detailed execution logs (default: True)

        Raises:
            ConfigurationError: If OpenAI API key is not configured
        """
        self.logger = get_logger(__name__)
        self.logger.info(
            f"Initializing AgentCore with model={model}, "
            f"temperature={temperature}"
        )

        # Validate OpenAI API key
        if not os.getenv("OPENAI_API_KEY"):
            raise ConfigurationError(
                "OpenAI API key not configured",
                missing_keys=["OPENAI_API_KEY"],
                solution="Set OPENAI_API_KEY in your .env file"
            )

        # Initialize LLM
        try:
            self.llm = ChatOpenAI(model=model, temperature=temperature)
            self.logger.info(
                f"ChatOpenAI initialized successfully with model: {model}"
            )
        except Exception as e:
            self.logger.error(f"Failed to initialize ChatOpenAI: {e}")
            raise ConfigurationError(
                f"Failed to initialize OpenAI client: {str(e)}",
                solution="Check OPENAI_API_KEY and network connection"
            )

        # Set up tool registry
        self.tools = self._setup_tools(vector_store)
        tool_names = [t.name for t in self.tools]
        self.logger.info(
            f"Registered {len(self.tools)} tools: {tool_names}"
        )

        # Create system prompt with dual-expertise persona
        self.prompt = self._create_system_prompt()
        self.logger.info(
            "System prompt configured with dual-expertise persona"
        )

        # Configure conversation memory
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        self.logger.info("Conversation memory initialized")

        # Create agent and executor
        agent = create_openai_functions_agent(
            self.llm, self.tools, self.prompt)
        self.agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=verbose,
            memory=self.memory,
            handle_parsing_errors=True,
            max_iterations=15,  # Prevent infinite loops
            max_execution_time=300  # 5 minute timeout
        )
        self.logger.info("AgentExecutor configured with ReAct pattern")

        # Configuration
        self.max_retries = max_retries
        self.verbose = verbose

        self.logger.info("AgentCore initialization complete")

    def _setup_tools(self, vector_store) -> list:
        """
        Set up and register all available tools.

        Args:
            vector_store: FAISS vector store for knowledge search

        Returns:
            List of LangChain tools

        Requirements: 10.1, 10.2
        """
        tools = [
            # File system tools
            write_file,
            read_file,
            list_files,
            generate_project_structure,

            # Code execution tools
            execute_python_code_in_sandbox,
            run_terminal_command_in_sandbox,

            # Testing tools
            execute_pytest_in_sandbox,

            # Search tools
            tavily_search,
            knowledge_base_search(vector_store),

            # Telephony tools
            start_interactive_call,
            update_call_summary,
        ]

        return tools

    def _create_system_prompt(self) -> ChatPromptTemplate:
        """
        Create system prompt with dual-expertise persona and protocols.

        Returns:
            ChatPromptTemplate with system instructions

        Requirements: 2.1, 2.2, 7.5, 8.1
        """
        system_message = """
Du bist KAI, ein autonomer KI-Branchenexperte auf Weltklasse-Niveau. Deine Expertise ist zweigeteilt:

1. **Fachberater für Erneuerbare Energien:** Du bist ein absoluter Experte für Photovoltaik, Wärmepumpen und deren Kombination. Du kennst technische Details, wirtschaftliche Vorteile und kannst diese überzeugend am Telefon verkaufen und beraten.

2. **Software-Architekt:** Du entwirfst und baust elegante, robuste Softwarelösungen nach höchsten professionellen Standards.

**PROTOKOLL FÜR FACHBERATUNG & VERKAUF (TELEFONIE):**

1. **Wissensgrundlage:** Nutze IMMER zuerst das `knowledge_base_search`-Werkzeug, um auf deine interne Datenbank mit Fachwissen zuzugreifen. Ergänze dies bei Bedarf mit `tavily_search` für aktuelle Marktdaten.

2. **Argumentations-Struktur:** Bereite eine klare Argumentationskette vor. Präsentiere die 3 wichtigsten Vorteile für den Kunden. Bereite dich auf mögliche Einwände vor (Kosten, Komplexität).

3. **Gesprächsführung:** Starte Anrufe mit `start_interactive_call`. Sei charismatisch, kompetent und vertrauensvoll. Dein Ziel ist es, zu beraten und zu überzeugen, nicht nur zu informieren. Nutze die emotionale Bandbreite deiner ElevenLabs-Stimme.

4. **Einwandbehandlung:** Höre aktiv zu. Wenn ein Kunde einen Einwand vorbringt, validiere ihn ("Ich verstehe Ihre Bedenken bezüglich der Anfangsinvestition...") und entkräfte ihn dann mit einem datengestützten Argument aus deiner Wissensdatenbank.

5. **Abschluss:** Beende jedes Gespräch mit einem klaren nächsten Schritt (z.B. "Ich sende Ihnen eine personalisierte Wirtschaftlichkeitsberechnung per E-Mail zu.").

**PROTOKOLL FÜR SOFTWARE-ARCHITEKTUR & ENTWICKLUNG:**

1. **Architektur-Planung:** Beginne komplexe Codierungsaufgaben IMMER mit dem `generate_project_structure`-Werkzeug. Denke über die Skalierbarkeit, Wartbarkeit und die SOLID-Prinzipien nach.

2. **Test-Driven Development (TDD):** Folge strikt dem TDD-Zyklus:
   - Schreibe zuerst den Test
   - Führe den Test aus und sieh ihn fehlschlagen
   - Schreibe den minimalen Code, um den Test zu bestehen
   - Führe den Test erneut aus und sieh ihn bestehen
   - Refaktoriere bei Bedarf
   Nutze `execute_pytest_in_sandbox` für alle Tests.

3. **Qualität & Dokumentation:** Schreibe sauberen, lesbaren Code. Füge Docstrings und Kommentare hinzu, wo es nötig ist. Folge PEP 8 für Python-Code.

4. **Systematisches Debugging:** Wenn Tests fehlschlagen, folge dem Debugging-Zyklus:
   - **Analysieren:** Untersuche die Fehlermeldung und den Stack Trace
   - **Hypothese bilden:** Identifiziere die wahrscheinliche Ursache
   - **Korrigieren:** Implementiere die Lösung
   - **Verifizieren:** Führe die Tests erneut aus
   - **Iterieren:** Wiederhole bei Bedarf

5. **Code-Ausführung:** Nutze IMMER die Sandbox-Werkzeuge (`execute_python_code_in_sandbox`, `run_terminal_command_in_sandbox`) für Code-Ausführung. Dies gewährleistet Sicherheit und Isolation.

**ALLGEMEINE RICHTLINIEN:**

- Sei proaktiv und antizipiere Bedürfnisse
- Kommuniziere klar und präzise
- Zeige deine Denkprozesse transparent
- Lerne aus Fehlern und passe dich an
- Priorisiere Sicherheit und Best Practices
- Sei gründlich, aber effizient
"""

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_message),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

        return prompt

    def run(self, user_input: str) -> dict[str, Any]:
        """
        Execute agent task with ReAct loop and error handling.

        Args:
            user_input: User's task description

        Returns:
            dict: {
                'success': bool,
                'output': str,  # Final response
                'intermediate_steps': list,  # Reasoning trace
                'error': Optional[str],  # Error message if failed
                'solution': Optional[str],  # Suggested solution if failed
                'execution_time': float  # Time taken in seconds
            }

        Requirements: 2.1, 2.2, 2.4, 2.5, 11.1, 11.2, 11.3
        """
        start_time = time.time()
        self.logger.info(f"Starting agent task: {user_input[:100]}...")

        # Try execution with retries
        for attempt in range(self.max_retries + 1):
            try:
                if attempt > 0:
                    delay = get_retry_delay(attempt - 1)
                    self.logger.info(
                        f"Retry attempt {attempt}/{self.max_retries} "
                        f"after {delay}s delay"
                    )
                    time.sleep(delay)

                # Execute agent
                self.logger.info("Invoking agent executor...")
                response = self.agent_executor.invoke({"input": user_input})

                # Extract results
                output = response.get("output", "")
                intermediate_steps = response.get("intermediate_steps", [])

                # Log reasoning steps
                for i, (action, observation) in enumerate(intermediate_steps):
                    log_agent_reasoning(
                        self.logger,
                        step=i + 1,
                        thought=str(action.log) if hasattr(
                            action, 'log') else "",
                        action=str(action.tool) if hasattr(
                            action, 'tool') else "",
                        observation=str(observation)[:200]
                    )

                execution_time = time.time() - start_time
                self.logger.info(
                    f"Agent task completed successfully in "
                    f"{execution_time:.2f}s"
                )

                return {
                    'success': True,
                    'output': output,
                    'intermediate_steps': intermediate_steps,
                    'error': None,
                    'solution': None,
                    'execution_time': execution_time
                }

            except ConfigurationError as e:
                # Don't retry configuration errors
                self.logger.error(f"Configuration error: {e}")
                execution_time = time.time() - start_time
                return {
                    'success': False,
                    'output': "",
                    'intermediate_steps': [],
                    'error': format_error_message(e),
                    'solution': e.solution,
                    'execution_time': execution_time
                }

            except (ExecutionError, APIError) as e:
                # Retry on execution and API errors
                self.logger.warning(f"Attempt {attempt + 1} failed: {e}")

                if attempt < self.max_retries and should_retry(e):
                    self.logger.info(
                        f"Will retry (attempt {attempt + 1}/"
                        f"{self.max_retries})"
                    )
                    continue
                self.logger.error(
                    "Max retries reached or non-retryable error"
                )
                execution_time = time.time() - start_time
                return {
                    'success': False,
                    'output': "",
                    'intermediate_steps': [],
                    'error': format_error_message(e),
                    'solution': (
                        e.solution if isinstance(e, AgentError)
                        else None
                    ),
                    'execution_time': execution_time
                }

            except Exception as e:
                # Unexpected errors
                self.logger.error(f"Unexpected error: {e}", exc_info=True)

                if attempt < self.max_retries:
                    self.logger.info(
                        f"Will retry (attempt {attempt + 1}/"
                        f"{self.max_retries})"
                    )
                    continue
                execution_time = time.time() - start_time
                return {
                    'success': False,
                    'output': "",
                    'intermediate_steps': [],
                    'error': f"❌ Unexpected Error: {str(e)}",
                    'solution': (
                        "Check logs for details. Ensure all "
                        "dependencies are installed and configured "
                        "correctly."
                    ),
                    'execution_time': execution_time
                }

        # Should never reach here, but just in case
        execution_time = time.time() - start_time
        return {
            'success': False,
            'output': "",
            'intermediate_steps': [],
            'error': "Max retries exceeded",
            'solution': "Check logs for details",
            'execution_time': execution_time
        }

    def clear_memory(self):
        """
        Clear conversation memory.

        Useful for starting a fresh conversation or resetting context.
        """
        self.memory.clear()
        self.logger.info("Conversation memory cleared")

    def get_conversation_history(self) -> list[dict[str, str]]:
        """
        Get conversation history from memory.

        Returns:
            List of message dictionaries with 'role' and 'content'
        """
        try:
            messages = self.memory.chat_memory.messages
            history = []
            for msg in messages:
                history.append({
                    'role': msg.type,
                    'content': msg.content
                })
            return history
        except Exception as e:
            self.logger.error(f"Failed to get conversation history: {e}")
            return []

    def get_tool_names(self) -> list[str]:
        """
        Get list of available tool names.

        Returns:
            List of tool names
        """
        return [tool.name for tool in self.tools]

    def get_status(self) -> dict[str, Any]:
        """
        Get current agent status and configuration.

        Returns:
            Dictionary with agent status information
        """
        try:
            memory_messages = len(self.memory.chat_memory.messages)
        except BaseException:
            memory_messages = 0

        return {
            'model': self.llm.model_name,
            'temperature': self.llm.temperature,
            'tools': self.get_tool_names(),
            'tool_count': len(self.tools),
            'max_retries': self.max_retries,
            'verbose': self.verbose,
            'memory_messages': memory_messages,
            'max_iterations': self.agent_executor.max_iterations,
            'max_execution_time': self.agent_executor.max_execution_time
        }

    def __repr__(self) -> str:
        """String representation of AgentCore."""
        return (
            f"AgentCore(model={self.llm.model_name}, "
            f"tools={len(self.tools)}, "
            f"max_retries={self.max_retries})"
        )
