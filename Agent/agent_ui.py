"""
Agent UI Module
===============

Streamlit interface for the O.M.I Agent system.
Provides task input, real-time status display, and results visualization.

Performance Optimizations (Task 15.3):
- Async agent execution: Non-blocking task execution with threading
- Streaming output: Real-time display of agent reasoning
- Optimized rendering: Efficient UI updates with minimal reruns
- Progress indicators: Clear feedback during execution
- Lazy loading: Defer heavy operations until needed
- Caching: Reuse expensive computations
"""

import os
import queue
import sys
import threading
import time
from typing import Any

import streamlit as st

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Lazy imports with error handling
try:
    from agent.tools.knowledge_tools import lazy_load_knowledge_base
except ImportError as e:
    def lazy_load_knowledge_base():
        """Fallback wenn langchain fehlt"""
        return None
    st.warning(f"Knowledge Tools nicht verfügbar: {e}")

try:
    from config import check_api_keys, get_missing_keys, get_setup_instructions
except ImportError as e:
    def check_api_keys():
        return True
    def get_missing_keys():
        return []
    def get_setup_instructions(keys):
        return ""
    st.warning(f"Config nicht verfügbar: {e}")

try:
    from agent.security import InputValidationError, sanitize_user_input
except ImportError as e:
    class InputValidationError(Exception):
        pass
    def sanitize_user_input(text):
        return text
    st.warning(f"Security Module nicht verfügbar: {e}")


# Import error handling
# Import security utilities (Task 12.1)


# Async execution state with progress tracking
class AsyncExecutionState:
    """
    Manages async agent execution state with progress tracking.

    Performance optimizations:
    - Non-blocking execution with threading
    - Progress queue for real-time updates
    - Efficient state management
    """

    def __getstate__(self):
        """Ermöglicht Pickle-Serialisierung für Session State"""
        return self.__dict__.copy()
    
    def __setstate__(self, state):
        """Ermöglicht Pickle-Deserialisierung für Session State"""
        self.__dict__.update(state)

    def __init__(self):
        self.running = False
        self.result = None
        self.error = None
        self.progress_queue = queue.Queue()
        self.thread = None
        self.start_time = None
        self.progress = 0

    def start(self, agent_core, user_input):
        """Start async execution with progress tracking."""
        self.running = True
        self.result = None
        self.error = None
        self.start_time = time.time()
        self.progress = 0

        def execute():
            try:
                # Update progress periodically
                def progress_callback(step):
                    self.progress = min(90, self.progress + 10)
                    self.progress_queue.put({
                        'type': 'progress',
                        'value': self.progress
                    })

                result = agent_core.run(user_input)
                self.result = result
                self.progress = 100
            except Exception as e:
                self.error = str(e)
            finally:
                self.running = False

        self.thread = threading.Thread(target=execute, daemon=True)
        self.thread.start()

    def is_running(self):
        """Check if execution is still running."""
        return self.running

    def get_result(self):
        """Get execution result."""
        return self.result

    def get_error(self):
        """Get execution error."""
        return self.error

    def get_elapsed_time(self):
        """Get elapsed execution time."""
        if self.start_time:
            return time.time() - self.start_time
        return 0

    def get_progress(self):
        """Get current progress percentage."""
        return self.progress


@st.cache_data(ttl=300)  # Cache for 5 minutes
def check_api_keys_ui() -> dict[str, bool]:
    """
    Check and validate all required API keys.

    Performance optimization: Cached to avoid repeated checks.

    Returns:
        Dictionary with key names and their availability status

    Displays:
        - Success message if all keys are configured
        - Error message with missing keys and setup instructions
    """
    keys_status = check_api_keys()
    missing = get_missing_keys()

    if not missing:
        st.success("All API keys are configured!")
        return keys_status

    # Display missing keys
    st.error("Missing API Keys")

    st.markdown("### Required API Keys Not Found:")
    for key in missing:
        st.markdown(f"- **{key}**")

    # Show setup instructions - styled mit weißem Hintergrund und orangenen Akzenten
    with st.expander("Setup Instructions", expanded=False):
        instructions_text = get_setup_instructions()
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #ffffff 0%, #f7f9fc 100%);
                    border-left: 4px solid #ff8c00;
                    border-radius: 8px;
                    padding: 20px;
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15), 0 2px 6px rgba(0, 0, 0, 0.1);
                    font-family: 'Courier New', monospace;
                    color: #2d3748;
                    white-space: pre-wrap;
                    line-height: 1.6;">
{instructions_text}
        </div>
        """, unsafe_allow_html=True)

    return keys_status


def display_agent_status(
    status: str,
    intermediate_steps: list | None = None,
    streaming: bool = False,
    progress: int = 0
):
    """
    Display real-time agent status and thinking process.

    Performance optimizations (Task 15.3):
    - Streaming mode for real-time updates
    - Efficient rendering with minimal DOM updates
    - Progressive disclosure of information
    - Lazy rendering of detailed information

    Args:
        status: Current status message
        intermediate_steps: List of intermediate reasoning steps
        streaming: Whether to use streaming mode
        progress: Progress percentage (0-100)

    Displays:
        - Progress indicator
        - Agent thinking process
        - Intermediate steps with tool usage
    """
    # Show status with optimized progress indicator
    if streaming:
        # Use progress bar for streaming (efficient updates)
        if progress > 0:
            st.progress(progress / 100.0)
        st.markdown(f" **{status}**")
    else:
        # Use spinner for non-streaming
        with st.spinner(status):
            st.markdown(f"**Status:** {status}")

    # Display intermediate steps if available (optimized rendering)
    if intermediate_steps:
        # Limit displayed steps for performance
        max_display_steps = 10
        total_steps = len(intermediate_steps)
        display_steps = intermediate_steps[-max_display_steps:]

        # Use expander for better performance with many steps
        expander_title = f" Agent Reasoning Process ({total_steps} steps)"
        if total_steps > max_display_steps:
            expander_title += f" - Showing last {max_display_steps}"

        with st.expander(
            expander_title,
            expanded=total_steps <= 3
        ):
            # Render steps efficiently (batch rendering)
            for i, step in enumerate(display_steps, 1):
                if isinstance(step, tuple) and len(step) >= 2:
                    action, observation = step[0], step[1]

                    # Display action (compact format)
                    col1, col2 = st.columns([1, 4])
                    with col1:
                        step_num = total_steps - max_display_steps + i
                        st.markdown(f"**Step {step_num}**")
                    with col2:
                        if hasattr(action, 'tool'):
                            st.markdown(f"`{action.tool}`")

                    # Display input/output in compact format
                    if hasattr(action, 'tool_input'):
                        with st.expander(" Input", expanded=False):
                            # Truncate large inputs
                            input_str = str(action.tool_input)
                            if len(input_str) > 200:
                                st.text(input_str[:200] + "...")
                            else:
                                st.json(action.tool_input)

                    # Truncate long outputs for performance
                    obs_str = str(observation)
                    if len(obs_str) > 500:
                        with st.expander(" Output (truncated)", expanded=False):
                            st.code(obs_str[:500] + "...", language="text")
                    else:
                        with st.expander(" Output", expanded=False):
                            st.code(obs_str, language="text")

                    if i < len(display_steps):
                        st.markdown("---")


def format_agent_output(
        result: dict[str, Any], streaming: bool = False) -> None:
    """
    Format and display agent execution results.

    Optimized for performance:
    - Efficient rendering of large outputs
    - Progressive disclosure of information
    - Lazy loading of detailed information

    Args:
        result: Dictionary containing agent execution results
            - output: Final response string
            - success: Boolean indicating success/failure
            - error: Error message if failed
            - execution_time: Time taken in seconds
            - intermediate_steps: List of reasoning steps
            - retry_count: Number of retries attempted
        streaming: Whether to use streaming mode

    Displays:
        - Formatted text results
        - Code with syntax highlighting
        - Error messages with solutions
        - Execution metrics
        - File download options
    """
    # Display execution metrics in columns
    col1, col2, col3 = st.columns(3)

    with col1:
        if 'execution_time' in result:
            st.metric(
                "⏱ Time",
                "{:.2f}s".format(result['execution_time'])
            )

    with col2:
        if 'retry_count' in result and result['retry_count'] > 0:
            st.metric(
                " Retries",
                result['retry_count']
            )

    with col3:
        intermediate_steps = result.get('intermediate_steps', [])
        if intermediate_steps:
            st.metric(
                " Steps",
                len(intermediate_steps)
            )

    # Check if successful
    if result.get('success', False):
        st.success("Task completed successfully!")

        # Display output
        output = result.get('output', '')
        if output:
            st.markdown("###  Result:")

            # Truncate very long outputs for performance
            if len(output) > 5000:
                with st.expander("View full output", expanded=false):
                    st.markdown(output[:5000] + "\n\n... (truncated)")
                    st.download_button(
                        "Download full output",
                        output,
                        file_name="agent_output.txt",
                        mime="text/plain"
                    )
            else:
                # Check if output contains code
                if '```' in output or 'def ' in output or 'class ' in output:
                    st.markdown(output)
                else:
                    st.markdown(output)

        # Display intermediate steps (optimized)
        if intermediate_steps:
            display_agent_status(
                "Processing complete",
                intermediate_steps,
                streaming=streaming
            )

        # Offer file downloads if files were created
        if 'agent_workspace' in output.lower() or 'file' in output.lower():
            st.markdown("### Generated Files")
            st.info(
                "Files have been created in the `agent_workspace` directory. "
                "You can access them from your file system."
            )

    else:
        # Display error
        st.error("Task failed")

        error_msg = result.get('error', 'Unknown error')

        # Truncate very long error messages
        if len(error_msg) > 1000:
            st.markdown(f"**Error:** {error_msg[:1000]}...")
            with st.expander("View full error", expanded=False):
                st.code(error_msg, language="text")
        else:
            st.markdown(f"**Error:** {error_msg}")

        # Display error type
        if 'error_type' in result:
            st.caption(f"Error Type: {result['error_type']}")

        # Display solution if available
        if 'solution' in result:
            st.markdown("### Suggested Solution:")
            st.info(result['solution'])

        # Display intermediate steps for debugging (collapsed by default)
        if intermediate_steps:
            with st.expander("Debug Information", expanded=False):
                display_agent_status(
                    "Failed during execution",
                    intermediate_steps,
                    streaming=streaming
                )


def render_agent_menu():
    """
    Main entry point for the A.G.E.N.T. menu interface.

    Renders:
        - Page configuration
        - API key validation
        - Task input interface
        - Start button and controls
        - Real-time status display
        - Results visualization

    Raises:
        ConfigurationError: If required API keys are missing
    """
    # Page configuration
    st.title(" A.G.E.N.T. - Autonomous AI Expert System")
    st.markdown(
        "**Künstliche Intelligenz** with dual expertise in "
        "Renewable Energy Consulting and Software Architecture"
    )

    # Welcome message for first-time users (Task 13.2)
    if 'first_visit' not in st.session_state:
        st.session_state.first_visit = True

    if st.session_state.first_visit:
        st.info("""
         **Welcome to O.M.I Agent!**

        This AI assistant can help you with:
        -  Renewable energy consulting (PV systems, heat pumps)
        -  Software development (code generation, testing, project setup)
        -  Complex multi-step workflows

        **Quick Start:** Enter a task below and click "Start Agent".
        Click the  Help button for detailed instructions and examples.
        """)

        col_dismiss1, col_dismiss2, col_dismiss3 = st.columns([2, 1, 2])
        with col_dismiss2:
            if st.button("Got it! ", use_container_width=True):
                st.session_state.first_visit = False
                st.rerun()

    st.markdown("---")

    # API key validation with help (Task 13.2)
    col_config1, col_config2 = st.columns([6, 1])
    with col_config1:
        st.markdown("###  Configuration Check")
    with col_config2:
        st.markdown("""
        <div style="margin-top: 10px;">
            <span title="API keys are required for the agent to function. OpenAI key is mandatory, others are optional for additional features.">
                </span>
        </div>
        """, unsafe_allow_html=True)

    keys_status = check_api_keys_ui()

    # Check if OpenAI key is available (optional warning, but don't block)
    if not keys_status.get('OPENAI_API_KEY', False):
        st.warning(
            "OPENAI_API_KEY nicht konfiguriert. "
            "Agent-Funktionalität ist eingeschränkt, aber Du kannst alle Bereiche erkunden."
        )
        with st.expander("Wie API Keys konfigurieren (optional)", expanded=False):
            st.markdown("""
            ### Quick Setup

            1. **Erstelle/Bearbeite `.env` Datei** im Projektverzeichnis
            2. **Füge deinen OpenAI API Key hinzu**:
            """)
            
            # Gestyltes Code-Feld mit weißem Hintergrund und orangen Akzenten
            st.markdown("""
            <div style="background: linear-gradient(135deg, #ffffff 0%, #f7f9fc 100%);
                        border: 2px solid rgba(200, 210, 220, 0.5); border-left: 4px solid #ff8c00;
                        border-radius: 8px; padding: 12px; margin: 10px 0;
                        box-shadow: 0 10px 12px rgba(0, 0, 0, 0.15), 0 10px 10px rgba(0, 0, 0, 0.1);
                        font-family: 'Courier New', monospace;">
                <code style="color: #ffffff; font-size: 14px; font-weight: 600;">
                    OPENAI_API_KEY=sk-your-key-here
                </code>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            3. **Hole deinen API Key** von [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
            4. **Starte die Anwendung neu**

            ### Optionale Keys (für zusätzliche Features)

            - **TAVILY_API_KEY**: Web-Suche
            - **TWILIO_***: Telefonie-Features
            - **ELEVEN_LABS_API_KEY**: Voice Synthesis

            Siehe `AGENT_INSTALLATION_GUIDE.md` für Details.
            """)
        # Don't stop - let the owner explore all areas!

    st.markdown("---")

    # Initialize knowledge base and agent (optimized with lazy loading)
    col_kb1, col_kb2 = st.columns([6, 1])
    with col_kb1:
        st.markdown("###  Knowledge Base Initialization")
    with col_kb2:
        st.markdown("""
        <div style="margin-top: 10px;">
            <span title="The knowledge base contains domain-specific PDF documents that the agent can search for information.">
                </span>
        </div>
        """, unsafe_allow_html=True)

    if 'vector_store' not in st.session_state:
        # Use lazy loading for faster startup
        with st.spinner("Loading knowledge base..."):
            try:
                # Lazy load: defer actual loading until first search
                st.session_state.vector_store = lazy_load_knowledge_base()
                if st.session_state.vector_store is not None:
                    st.success("Knowledge base loaded successfully!")
                    st.caption(
                        "The agent can now search PDF documents for "
                        "domain-specific information about renewable energy systems.")
                else:
                    st.info(
                        " Knowledge base is empty. "
                        "Add PDF files to `Agent/knowledge_base/` directory."
                    )
                    with st.expander(" How to Add Documents", expanded=False):
                        st.markdown("""
                        ### Adding Documents to Knowledge Base

                        1. **Place PDF files** in the `Agent/knowledge_base/` directory
                        2. **Restart the application** to index the documents
                        3. **The agent will automatically** create a searchable index

                        **Recommended Documents:**
                        - Technical specifications for PV systems
                        - Heat pump documentation
                        - Economic analysis guides
                        - Installation manuals
                        - Product datasheets

                        **Note:** The agent will work without a knowledge base but will have limited domain-specific information.
                        """)
            except Exception as e:
                st.error(f"Failed to load knowledge base: {e}")
                st.info(
                    "The agent will continue without knowledge base. "
                    "Add PDF files to the `Agent/knowledge_base/` directory "
                    "and restart."
                )
                st.session_state.vector_store = None

    # Initialize agent (cached in session state)
    if 'agent_core' not in st.session_state:
        with st.spinner("Initializing agent..."):
            try:
                # Lazy import to avoid heavy dependencies at app startup
                from agent.agent_core import AgentCore
                st.session_state.agent_core = AgentCore(
                    vector_store=st.session_state.vector_store
                )
                st.success("Agent initialized successfully!")
            except Exception as e:
                st.error(f"Failed to initialize agent: {e}")
                # Helpful hint if a known optional dependency is missing
                if isinstance(e, ModuleNotFoundError) and 'langchain_classic' in str(e):
                    st.info(
                        "Optionales Paket 'langchain_classic' fehlt. "
                        "Bitte das passende Wheel in den Ordner 'BOKUK_BUILD/wheelhouse' legen "
                        "und offline installieren, damit die Agent-Funktionalität aktiv wird."
                    )
                # Don't stop - let the owner explore all areas!
                st.session_state.agent_core = None  # Mark as not initialized

    st.markdown("---")

    # Task input interface
    st.markdown("### Task Input")
    
    # Voice input option
    if st.session_state.get('voice_mode'):
        st.info(" **Sprachsteuerung aktiviert!**")
        try:
            from voice_command import render_voice_input_ui, integrate_voice_with_agent
            
            voice_result = render_voice_input_ui()
            voice_text = integrate_voice_with_agent(voice_result)
            
            if voice_text:
                st.success(f"Erkannt: {voice_text}")
                st.session_state['task_input'] = voice_text
                st.session_state['voice_mode'] = False
                st.rerun()
        except ImportError:
            st.warning("Sprachmodul nicht verfügbar.")
            st.session_state['voice_mode'] = False

    # Help button and dialog (Task 13.2)
    col_help1, col_help2 = st.columns([6, 1])
    with col_help2:
        if st.button(" Help", use_container_width=True):
            st.session_state.show_help_dialog = True

    # Help dialog (Task 13.2)
    if st.session_state.get('show_help_dialog', False):
        with st.expander(" Complete Help Guide", expanded=false):
            st.markdown("""
            ## How to Use the O.M.I Agent

            ### What is O.M.I Agent?
            O.M.I (Künstliche Intelligenz) is an autonomous AI assistant with dual expertise:
            - **Renewable Energy Consulting**: Photovoltaics, heat pumps, economic analysis
            - **Software Architecture**: Code generation, testing, project scaffolding

            ### How It Works
            1. **Enter your task** in the text area below
            2. **Click "Start Agent"** to begin execution
            3. **Watch the agent think** - see its reasoning process in real-time
            4. **Review results** - get comprehensive answers, code, or analysis

            ### Task Types You Can Request

            ####  Renewable Energy Consulting
            - Search knowledge base for technical information
            - Calculate ROI and amortization times
            - Prepare customer presentations
            - Compare different system configurations
            - Simulate sales calls

            ####  Software Development
            - Generate Python functions with tests
            - Create complete project structures
            - Write and execute unit tests
            - Debug and fix code errors
            - Generate API endpoints

            ####  Combined Workflows
            - Research → Code → Test → Document
            - Knowledge search → Calculation → Presentation
            - Multi-step complex tasks

            ### Tips for Best Results

            **Be Specific**: "Create a Python function to calculate solar panel ROI with parameters: investment, annual_savings, years"

            **Provide Context**: "I'm building a customer consultation tool. Create a function that..."

            **Break Down Complex Tasks**: Instead of "Build a complete app", try:
            1. "Create project structure"
            2. "Implement core calculations"
            3. "Add tests"

            **Use Examples**: "Create a function similar to this: [paste example]"

            **Avoid Vague Requests**: "Do something with solar" → Too vague

            ### Available Tools

            The agent has access to:
            -  **Knowledge Base**: Domain-specific PDF documents
            - **Web Search**: Current information via Tavily API
            -  **Code Execution**: Secure Docker sandbox
            - **File Operations**: Read/write in workspace
            -  **Telephony**: Simulated sales calls
            -  **Testing**: Automated pytest execution

            ### Common Use Cases

            **Quick Information**: "What are the benefits of heat pumps?"

            **Calculations**: "Calculate ROI for a 10 kWp PV system with 15,000€ investment"

            **Code Generation**: "Write a function to calculate annual solar yield"

            **Project Setup**: "Generate a Flask API structure for solar calculations"

            **Testing**: "Write unit tests for the calculate_roi function"

            ### Troubleshooting

            **Agent not responding?**
            - Check internet connection
            - Verify API keys are configured
            - Try a simpler task first

            **Unexpected results?**
            - Rephrase your request more clearly
            - Provide more context or examples
            - Break into smaller steps

            **Docker errors?**
            - Ensure Docker is running
            - Check if sandbox image is built
            - See troubleshooting guide

            ### Need More Help?

             **Documentation**: Check the `Agent/` directory for detailed guides
            - `README.md` - Overview and quick start
            - `BASIC_USAGE_TUTORIAL.md` - Beginner guide
            - `EXAMPLE_TASKS.md` - 20+ example tasks
            - `TROUBLESHOOTING.md` - Problem solving
            - `ADVANCED_FEATURES_GUIDE.md` - Advanced usage

            **Validation**: Run `python Agent/validate_config.py` to check setup

             **Installation**: See `AGENT_INSTALLATION_GUIDE.md` for setup help
            """)

            if st.button("Close Help", use_container_width=True):
                st.session_state.show_help_dialog = False
                st.rerun()

    # Example tasks with categories (Task 13.2)
    with st.expander("Example Task Suggestions", expanded=False):
        # CSS für Tabs mit weißem Hintergrund und orangenen Akzenten - VOLLSTÄNDIG
        st.markdown("""
        <style>
        /* Example Tasks Tabs - Alle schwarzen Hintergründe entfernen */
        div[data-baseweb="tab-list"] {
            background: transparent !important;
        }
        div[data-baseweb="tab-list"] button {
            background: linear-gradient(135deg, #ffffff 0%, #f7f9fc 100%) !important;
            color: #4a5568 !important;
            border-radius: 8px 8px 0 0 !important;
            border: 1px solid rgba(200, 210, 220, 0.5) !important;
            border-bottom: none !important;
            padding: 10px 20px !important;
            margin: 0 2px !important;
            box-shadow: 0 10px 10px rgba(0, 0, 0, 0.1) !important;
            transition: all 0.3s ease !important;
        }
        div[data-baseweb="tab-list"] button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 10px 12px rgba(255, 140, 0, 0.3) !important;
            color: #2d3748 !important;
        }
        div[data-baseweb="tab-list"] button[aria-selected="true"] {
            background: linear-gradient(135deg, #ffffff 0%, #fff8f0 100%) !important;
            color: #1a202c !important;
            border-bottom: 4px solid #ff8c00 !important;
            font-weight: 600 !important;
            box-shadow: 0 10px 12px rgba(255, 140, 0, 0.2) !important;
        }
        div[data-baseweb="tab-panel"] {
            background: linear-gradient(135deg, #ffffff 0%, #f7f9fc 100%) !important;
            border-radius: 0 0 8px 8px !important;
            border: 1px solid rgba(200, 210, 220, 0.5) !important;
            border-top: none !important;
            padding: 20px !important;
            box-shadow: 0 10px 12px rgba(0, 0, 0, 0.1) !important;
        }
        /* Alle verschachtelten Container weiß/transparent */
        div[data-baseweb="tab-panel"] * {
            background-color: transparent !important;
        }
        div[data-baseweb="tab-panel"] div[data-testid="stVerticalBlock"],
        div[data-baseweb="tab-panel"] div[data-testid="column"],
        div[data-baseweb="tab-panel"] div[data-testid="stHorizontalBlock"] {
            background: transparent !important;
        }
        /* Code-Blöcke in Tabs weiß stylen */
        div[data-baseweb="tab-panel"] pre {
            background: linear-gradient(135deg, #ffffff 0%, #f7f9fc 100%) !important;
            border-left: 4px solid #ff8c00 !important;
            border-radius: 8px !important;
            padding: 15px !important;
            box-shadow: 0 10px 10px rgba(0, 0, 0, 0.1) !important;
        }
        div[data-baseweb="tab-panel"] code {
            background: linear-gradient(135deg, #ffffff 0%, #f7f9fc 100%) !important;
            color: #2d3748 !important;
            font-family: 'Courier New', monospace !important;
        }
        /* Markdown Container */
        div[data-baseweb="tab-panel"] .stMarkdown {
            background: transparent !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
        tab1, tab2, tab3 = st.tabs([
            " Energy Consulting",
            " Software Dev",
            " Combined"
        ])

        with tab1:
            st.markdown("""
            **Quick Information Queries:**
            ```
            Was sind die wichtigsten Vorteile von Photovoltaik-Anlagen?
            ```
            ```
            Wie funktioniert eine Luft-Wasser-Wärmepumpe?
            ```

            **Economic Calculations:**
            ```
            Berechne den ROI für eine 10 kWp PV-Anlage:
            - Investition: 15.000 €
            - Jahresverbrauch: 4.500 kWh
            - Strompreis: 0,35 €/kWh
            - Eigenverbrauch: 30%
            ```

            **Customer Consultation:**
            ```
            Erstelle eine Beratung für einen Kunden mit:
            - Einfamilienhaus, 150 m²
            - Jahresverbrauch: 5.000 kWh
            - Budget: 20.000 €
            - Interesse: PV + Speicher
            ```

            **Sales Call Simulation:**
            ```
            Simuliere einen Beratungsanruf für Photovoltaik.
            Präsentiere die Top 3 Vorteile mit Daten.
            ```
            """)

            if st.button(" Copy Example 1", key="copy_energy_1"):
                st.session_state.agent_task_input = "Was sind die wichtigsten Vorteile von Photovoltaik-Anlagen?"
                st.rerun()

        with tab2:
            st.markdown("""
            **Simple Function:**
            ```
            Schreibe eine Python-Funktion zur Berechnung des ROI:
            - Parameter: investment, annual_savings, years
            - Mit Type Hints und Docstring
            - Inkl. Fehlerbehandlung
            - Mit Unit Tests
            ```

            **Class with TDD:**
            ```
            Entwickle eine Klasse SolarPanel mit TDD:
            - Attribute: manufacturer, model, power_wp, efficiency
            - Methode: calculate_annual_yield(location)
            - Folge dem TDD-Zyklus
            ```

            **API Endpoint:**
            ```
            Erstelle einen Flask REST API Endpoint:
            POST /api/calculate-yield
            Request: {kwp, location, orientation}
            Response: {annual_yield_kwh, monthly_breakdown}
            Mit Validierung und Tests
            ```

            **Project Scaffolding:**
            ```
            Generiere ein Flask API Projekt für PV-Berechnungen:
            - REST API mit Flask
            - SQLite Datenbank
            - Unit Tests
            - README mit Setup
            ```
            """)

            if st.button(" Copy Example 2", key="copy_dev_1"):
                st.session_state.agent_task_input = "Schreibe eine Python-Funktion zur Berechnung des ROI mit Type Hints, Docstring und Unit Tests"
                st.rerun()

        with tab3:
            st.markdown("""
            **Research → Code → Test:**
            ```
            1. Suche in der Wissensdatenbank nach PV-Ertragsdaten
            2. Erstelle eine Funktion zur Ertragsberechnung
            3. Schreibe Tests für die Funktion
            4. Führe die Tests im Sandbox aus
            ```

            **Consultation Tool:**
            ```
            Erstelle ein Beratungstool:
            1. Recherchiere durchschnittliche PV-Erträge
            2. Erstelle Ertragsfunktion
            3. Erstelle ROI-Funktion
            4. Schreibe Tests
            5. Erstelle CLI-Tool
            6. Generiere Beispiel-Beratung
            ```

            **Complete Workflow:**
            ```
            Entwickle eine Lösung für Amortisationsberechnung:
            - Suche relevante Formeln in der Wissensdatenbank
            - Implementiere die Berechnung in Python
            - Erstelle Unit Tests
            - Generiere Beispielberechnungen
            - Erstelle eine Dokumentation
            ```
            """)

            if st.button(" Copy Example 3", key="copy_combined_1"):
                st.session_state.agent_task_input = "Suche in der Wissensdatenbank nach PV-Vorteilen, erstelle dann eine Python-Funktion zur Ertragsberechnung mit Tests"
                st.rerun()

    # Usage instructions (Task 13.2)
    with st.expander("Quick Usage Instructions", expanded=False):
        st.markdown("""
        ### Getting Started in 3 Steps

        **Step 1: Enter Your Task**
        - Type what you want the agent to do in the text area below
        - Be as specific as possible
        - Include all necessary details

        **Step 2: Start the Agent**
        - Click the "Start Agent" button
        - The agent will begin processing your request
        - You'll see its thinking process in real-time

        **Step 3: Review Results**
        - Read the agent's response
        - Copy any generated code
        - Download created files if needed

        ### Writing Effective Tasks

        **Good Task Examples:**
        - "Create a Python function called calculate_roi that takes investment and annual_savings as parameters"
        - "Search the knowledge base for information about heat pump efficiency (JAZ)"
        - "Generate a Flask project structure with models, routes, and tests"

        **Tasks to Avoid:**
        - "Do something" (too vague)
        - "Help me" (no specific request)
        - "Fix everything" (no context)

        ### Agent Capabilities

        **Can Do:**
        - Search knowledge base
        - Generate Python code
        - Write and run tests
        - Create project structures
        - Perform calculations
        - Simulate conversations
        - Search the web (if API key configured)

        **Cannot Do:**
        - Access your local files outside workspace
        - Make real phone calls (only simulation)
        - Access databases directly
        - Modify existing application code
        - Execute commands on your system

        ### Tips & Tricks

        **Use the knowledge base first**: The agent will search its knowledge base before using web search

        **Break down complex tasks**: Multi-step tasks work better when broken into phases

        **Provide examples**: Show the agent what you want with examples

        **Iterate**: Start simple, then refine based on results

        **Check the reasoning**: Watch the agent's thinking process to understand its approach
        """)

    # ====================================================================
    # TELEPHONY MEGA EXTENSION - ALL NEW FEATURES
    # ====================================================================
    
    with st.expander(" Telephony System - Bria Softphone & Advanced Features", expanded=False):
        st.markdown("### Telephony Management Console")
        st.markdown("Vollständiges Telefonsystem mit 36 Tools für professionelle Anrufverwaltung")
        
        # CSS für Telephony-Tabs - ALLE SCHWARZEN HINTERGRÜNDE ENTFERNEN
        st.markdown("""
        <style>
        /* Telephony Tabs - Komplett weiß ohne schwarze Hintergründe */
        div[data-baseweb="tab-list"] {
            background: transparent !important;
        }
        div[data-baseweb="tab-list"] button {
            background: linear-gradient(135deg, #ffffff 0%, #f7f9fc 100%) !important;
            color: #4a5568 !important;
            border-radius: 8px 8px 0 0 !important;
            border: 1px solid rgba(200, 210, 220, 0.5) !important;
            border-bottom: none !important;
            padding: 10px 20px !important;
            margin: 0 2px !important;
            box-shadow: 0 10px 10px rgba(0, 0, 0, 0.1) !important;
            transition: all 0.3s ease !important;
        }
        div[data-baseweb="tab-list"] button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 10px 12px rgba(255, 140, 0, 0.3) !important;
            color: #2d3748 !important;
        }
        div[data-baseweb="tab-list"] button[aria-selected="true"] {
            background: linear-gradient(135deg, #ffffff 0%, #fff8f0 100%) !important;
            color: #1a202c !important;
            border-bottom: 4px solid #ff8c00 !important;
            font-weight: 600 !important;
            box-shadow: 0 10px 12px rgba(255, 140, 0, 0.2) !important;
        }
        div[data-baseweb="tab-panel"] {
            background: linear-gradient(135deg, #ffffff 0%, #f7f9fc 100%) !important;
            border-radius: 0 0 8px 8px !important;
            border: 1px solid rgba(200, 210, 220, 0.5) !important;
            border-top: none !important;
            padding: 20px !important;
            box-shadow: 0 10px 12px rgba(0, 0, 0, 0.1) !important;
        }
        /* KRITISCH: Alle verschachtelten Elemente transparent/weiß */
        div[data-baseweb="tab-panel"] * {
            background-color: transparent !important;
        }
        div[data-baseweb="tab-panel"] div[data-testid="stVerticalBlock"],
        div[data-baseweb="tab-panel"] div[data-testid="column"],
        div[data-baseweb="tab-panel"] div[data-testid="stHorizontalBlock"],
        div[data-baseweb="tab-panel"] .stMarkdown,
        div[data-baseweb="tab-panel"] .element-container {
            background: transparent !important;
        }
        /* Expander innerhalb der Tabs weiß */
        div[data-baseweb="tab-panel"] details {
            background: linear-gradient(135deg, #ffffff 0%, #f7f9fc 100%) !important;
        }
        div[data-baseweb="tab-panel"] details summary {
            background: linear-gradient(135deg, #ffffff 0%, #f7f9fc 100%) !important;
            color: #2d3748 !important;
        }
        div[data-baseweb="tab-panel"] details[open] {
            background: linear-gradient(135deg, #ffffff 0%, #fff8f0 100%) !important;
            border-left: 4px solid #ff8c00 !important;
        }
        /* Code-Blöcke weiß stylen */
        div[data-baseweb="tab-panel"] pre {
            background: linear-gradient(135deg, #ffffff 0%, #f7f9fc 100%) !important;
            border-left: 4px solid #ff8c00 !important;
            border-radius: 8px !important;
            padding: 15px !important;
            box-shadow: 0 10px 10px rgba(0, 0, 0, 0.1) !important;
        }
        div[data-baseweb="tab-panel"] code {
            background: linear-gradient(135deg, #ffffff 0%, #f7f9fc 100%) !important;
            color: #2d3748 !important;
            font-family: 'Courier New', monospace !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Tabs für verschiedene Bereiche
        phone_tab1, phone_tab2, phone_tab3, phone_tab4, phone_tab5 = st.tabs([
            " Bria Softphone",
            " Kontakte",
            "Analytics",
            " Knowledge Base",
            "Erweiterte Features"
        ])
        
        # TAB 1: Bria Softphone
        with phone_tab1:
            with st.expander(" SIP Verbindung", expanded=False):
                st.markdown("**Bria Softphone Verbindung konfigurieren**")
                
                col1, col2 = st.columns(2)
                with col1:
                    sip_server = st.text_input("SIP Server", placeholder="sip.example.com", key="sip_server")
                    sip_user = st.text_input("Benutzername", placeholder="user123", key="sip_user")
                with col2:
                    sip_pass = st.text_input("Passwort", type="password", key="sip_pass")
                    
                if st.button("Verbinden", key="bria_connect"):
                    if sip_server and sip_user and sip_pass:
                        st.code(f"bria_connect('{sip_server}', '{sip_user}', '***')")
                        st.info("Führe diesen Befehl im Agent-Chat aus")
                    else:
                        st.warning("Bitte alle Felder ausfüllen")
                
                if st.button("Trennen", key="bria_disconnect"):
                    st.code("bria_disconnect()")
            
            with st.expander(" Ausgehende Anrufe", expanded=False):
                st.markdown("**Anruf starten**")
                
                col1, col2 = st.columns([2, 1])
                with col1:
                    out_phone = st.text_input("Telefonnummer", placeholder="+49301234567", key="out_phone")
                    out_goal = st.text_input("Anrufziel", placeholder="Beratungstermin vereinbaren", key="out_goal")
                with col2:
                    st.markdown("**Schnellwahl**")
                    fav_contact = st.selectbox("Favorit", ["", "Max Mustermann", "Firma ABC", "VIP Kunde"], key="fav")
                    if st.button("Anrufen", key="quick_dial"):
                        if fav_contact:
                            st.code(f"quick_dial_favorite('{fav_contact}')")
                
                if st.button("Anruf starten", key="make_call"):
                    if out_phone:
                        st.code(f"bria_make_call('{out_phone}', '{out_goal}')")
                    else:
                        st.warning("Bitte Telefonnummer eingeben")
            
            with st.expander(" Anrufsteuerung", expanded=False):
                st.markdown("**Aktiven Anruf verwalten**")
                
                call_id_control = st.text_input("Call ID", placeholder="CALL-12345678", key="call_id_control")
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    if st.button("⏸ Halten", key="hold_call"):
                        st.code(f"bria_hold_call('{call_id_control}')")
                with col2:
                    if st.button(" Fortsetzen", key="resume_call"):
                        st.code(f"bria_resume_call('{call_id_control}')")
                with col3:
                    if st.button(" Weiterleiten", key="transfer_btn"):
                        target = st.text_input("Ziel", key="transfer_target")
                        if target:
                            st.code(f"bria_transfer_call('{call_id_control}', '{target}')")
                with col4:
                    if st.button("Auflegen", key="hangup_call"):
                        st.code(f"bria_hangup('{call_id_control}')")
        
        # TAB 2: Kontakte
        with phone_tab2:
            with st.expander(" Kontakt hinzufügen", expanded=False):
                st.markdown("**Neuen Kontakt anlegen**")
                
                col1, col2 = st.columns(2)
                with col1:
                    contact_name = st.text_input("Name", placeholder="Max Mustermann", key="contact_name")
                    contact_phone = st.text_input("Telefon", placeholder="+49301234567", key="contact_phone")
                    contact_email = st.text_input("E-Mail", placeholder="max@example.com", key="contact_email")
                with col2:
                    contact_company = st.text_input("Firma", placeholder="Musterfirma GmbH", key="contact_company")
                    contact_tags = st.text_input("Tags", placeholder="lead,vip,interessiert", key="contact_tags")
                    contact_notes = st.text_area("Notizen", placeholder="Weitere Informationen...", key="contact_notes", height=100)
                
                if st.button("Kontakt speichern", key="save_contact"):
                    if contact_name and contact_phone:
                        st.code(f"""add_phone_contact(
    name='{contact_name}',
    phone_number='{contact_phone}',
    email='{contact_email}',
    company='{contact_company}',
    tags='{contact_tags}',
    notes='{contact_notes}'
)""")
                    else:
                        st.warning("Name und Telefonnummer sind Pflichtfelder")
            
            with st.expander("Kontakte suchen", expanded=False):
                st.markdown("**Kontaktdatenbank durchsuchen**")
                
                search_query = st.text_input("Suche nach Name, Nummer oder Firma", key="contact_search")
                if st.button("Suchen", key="search_contacts"):
                    if search_query:
                        st.code(f"search_phone_contacts('{search_query}')")
                    else:
                        st.warning("Bitte Suchbegriff eingeben")
            
            with st.expander("Bulk Import (CSV/XLSX)", expanded=False):
                st.markdown("**Mehrere Kontakte auf einmal importieren**")
                st.markdown("""
                **Erforderliche Spalten:**
                - `name` - Kontaktname (Pflicht)
                - `phone_number` - Telefonnummer (Pflicht)
                - `email` - E-Mail Adresse (optional)
                - `company` - Firmenname (optional)
                - `tags` - Tags kommagetrennt (optional)
                - `notes` - Notizen (optional)
                """)
                
                import_file = st.text_input("Dateipfad", placeholder="C:/contacts.xlsx", key="import_file")
                if st.button("Import starten", key="bulk_import"):
                    if import_file:
                        st.code(f"bulk_import_phone_numbers('{import_file}')")
                    else:
                        st.warning("Bitte Dateipfad angeben")
        
        # TAB 3: Analytics
        with phone_tab3:
            with st.expander("Anruf-Statistiken", expanded=False):
                st.markdown("**Auswertung der Anrufaktivitäten**")
                
                analytics_days = st.slider("Zeitraum (Tage)", min_value=1, max_value=90, value=30, key="analytics_days")
                
                if st.button("Statistiken abrufen", key="get_analytics"):
                    st.code(f"get_call_analytics(days={analytics_days})")
                
                st.markdown("""
                **Metriken:**
                - Gesamtanzahl Anrufe
                - Erfolgreiche vs. fehlgeschlagene Anrufe
                - Conversion Rate
                - Durchschnittliche Anrufdauer
                - Gesamte Gesprächszeit
                - Durchschnittliche Stimmung
                """)
            
            with st.expander("Anruf-Historie durchsuchen", expanded=False):
                st.markdown("**Vergangene Anrufe finden**")
                
                col1, col2 = st.columns(2)
                with col1:
                    history_phone = st.text_input("Nach Nummer filtern", placeholder="+49301234567", key="history_phone")
                    history_days = st.number_input("Tage zurück", min_value=1, max_value=365, value=30, key="history_days")
                with col2:
                    history_outcome = st.text_input("Nach Ergebnis filtern", placeholder="success, scheduled, ...", key="history_outcome")
                
                if st.button("Historie durchsuchen", key="search_history"):
                    filters = []
                    if history_phone:
                        filters.append(f"phone_number='{history_phone}'")
                    filters.append(f"days={history_days}")
                    if history_outcome:
                        filters.append(f"outcome_filter='{history_outcome}'")
                    
                    st.code(f"search_call_history({', '.join(filters)})")
            
            with st.expander(" Sentiment-Analyse", expanded=False):
                st.markdown("**Stimmungsanalyse eines Anrufs**")
                
                sentiment_call_id = st.text_input("Call ID", placeholder="CALL-12345678", key="sentiment_call_id")
                
                if st.button("Stimmung analysieren", key="analyze_sentiment"):
                    if sentiment_call_id:
                        st.code(f"analyze_call_sentiment('{sentiment_call_id}')")
                    else:
                        st.warning("Bitte Call ID eingeben")
                
                st.markdown("""
                **Analysiert:**
                - Positive/Negative Keywords
                - Sentiment Score (-1 bis +1)
                - Stimmungskategorie (Positiv/Neutral/Negativ)
                """)
        
        # TAB 4: Knowledge Base
        with phone_tab4:
            with st.expander(" Call-Skript speichern", expanded=False):
                st.markdown("**Neues Anruf-Skript in Knowledge Base ablegen**")
                
                col1, col2 = st.columns(2)
                with col1:
                    script_name = st.text_input("Skriptname", placeholder="PV-Beratung Standard", key="script_name")
                    script_category = st.selectbox("Kategorie", ["Verkauf", "Support", "Beratung", "Follow-up"], key="script_category")
                    script_opening = st.text_area("Eröffnungssatz", placeholder="Guten Tag, hier ist O.M.I von...", key="script_opening", height=100)
                with col2:
                    script_keypoints = st.text_input("Key Points (kommagetrennt)", placeholder="Kostenersparnis,Umweltschutz,Unabhängigkeit", key="script_keypoints")
                    script_objections = st.text_area("Einwandbehandlung", placeholder="JSON format", key="script_objections", height=80)
                    script_closing = st.text_area("Abschlusssatz", placeholder="Vielen Dank für das Gespräch...", key="script_closing", height=80)
                
                if st.button("Skript speichern", key="save_script"):
                    if script_name and script_category and script_opening:
                        st.code(f"""save_call_script(
    name='{script_name}',
    category='{script_category}',
    opening_statement='{script_opening}',
    key_points='{script_keypoints}',
    objection_responses='{script_objections}',
    closing_statement='{script_closing}'
)""")
                    else:
                        st.warning("Name, Kategorie und Eröffnung sind Pflichtfelder")
            
            with st.expander(" Call-Skripte abrufen", expanded=False):
                st.markdown("**Gespeicherte Skripte anzeigen**")
                
                script_filter = st.selectbox("Kategorie filtern", ["", "Verkauf", "Support", "Beratung", "Follow-up"], key="script_filter")
                
                if st.button("Skripte laden", key="load_scripts"):
                    if script_filter:
                        st.code(f"get_call_script(category='{script_filter}')")
                    else:
                        st.code("get_call_script()")
        
        # TAB 5: Erweiterte Features
        with phone_tab5:
            with st.expander(" Call Recording", expanded=False):
                st.markdown("**Anrufaufnahme starten & transkribieren**")
                
                col1, col2 = st.columns(2)
                with col1:
                    rec_call_id = st.text_input("Call ID", placeholder="CALL-12345678", key="rec_call_id")
                    rec_path = st.text_input("Aufnahmepfad (optional)", placeholder="C:/recordings/call.wav", key="rec_path")
                    
                    if st.button("Aufnahme starten", key="start_recording"):
                        if rec_call_id:
                            if rec_path:
                                st.code(f"start_call_recording('{rec_call_id}', '{rec_path}')")
                            else:
                                st.code(f"start_call_recording('{rec_call_id}')")
                        else:
                            st.warning("Bitte Call ID eingeben")
                
                with col2:
                    trans_path = st.text_input("Audiodatei transkribieren", placeholder="C:/recordings/call.wav", key="trans_path")
                    
                    if st.button("Transkribieren (Whisper)", key="transcribe"):
                        if trans_path:
                            st.code(f"transcribe_call_recording('{trans_path}')")
                        else:
                            st.warning("Bitte Dateipfad angeben")
            
            with st.expander(" CRM Integration", expanded=False):
                st.markdown("**Anruf ins CRM-System protokollieren**")
                
                col1, col2 = st.columns(2)
                with col1:
                    crm_call_id = st.text_input("Call ID", placeholder="CALL-12345678", key="crm_call_id")
                with col2:
                    crm_customer_id = st.text_input("CRM Kunden-ID (optional)", placeholder="CRM-001", key="crm_customer_id")
                
                if st.button("Ins CRM protokollieren", key="log_crm"):
                    if crm_call_id:
                        if crm_customer_id:
                            st.code(f"log_call_to_crm('{crm_call_id}', '{crm_customer_id}')")
                        else:
                            st.code(f"log_call_to_crm('{crm_call_id}')")
                    else:
                        st.warning("Bitte Call ID eingeben")
            
            with st.expander(" Follow-up planen", expanded=False):
                st.markdown("**Wiedervorlage nach Anruf setzen**")
                
                col1, col2 = st.columns(2)
                with col1:
                    followup_call_id = st.text_input("Call ID", placeholder="CALL-12345678", key="followup_call_id")
                    followup_date = st.date_input("Follow-up Datum", key="followup_date")
                with col2:
                    followup_action = st.text_area("Geplante Aktion", placeholder="Angebot nachfassen", key="followup_action", height=100)
                
                if st.button("Wiedervorlage setzen", key="schedule_followup"):
                    if followup_call_id and followup_action:
                        st.code(f"""schedule_follow_up(
    call_id='{followup_call_id}',
    follow_up_date='{followup_date}',
    follow_up_action='{followup_action}'
)""")
                    else:
                        st.warning("Call ID und Aktion sind Pflichtfelder")
            
            with st.expander("Auto-Dialer Kampagne", expanded=False):
                st.markdown("**Automatische Anrufkampagne für Kontakte mit Tag**")
                
                col1, col2 = st.columns(2)
                with col1:
                    dialer_tag = st.text_input("Kontakt-Tag", placeholder="lead", key="dialer_tag")
                    dialer_goal = st.text_input("Kampagnenziel", placeholder="Beratungstermin vereinbaren", key="dialer_goal")
                with col2:
                    dialer_max = st.number_input("Max. Anrufe", min_value=1, max_value=100, value=10, key="dialer_max")
                
                if st.button("Kampagne starten", key="start_campaign"):
                    if dialer_tag and dialer_goal:
                        st.code(f"""auto_dialer_campaign(
    contact_tag='{dialer_tag}',
    call_goal='{dialer_goal}',
    max_calls={dialer_max}
)""")
                    else:
                        st.warning("Tag und Ziel sind Pflichtfelder")
            
            with st.expander(" Weitere Features", expanded=False):
                st.markdown("**Zusätzliche Telephony-Tools**")
                
                # Call Tags
                st.markdown("**Call Tags hinzufügen:**")
                col1, col2 = st.columns(2)
                with col1:
                    tag_call_id = st.text_input("Call ID", placeholder="CALL-12345678", key="tag_call_id")
                with col2:
                    call_tags = st.text_input("Tags", placeholder="wichtig,hot-lead", key="call_tags")
                if st.button("Tags hinzufügen", key="add_tags"):
                    if tag_call_id and call_tags:
                        st.code(f"add_call_tags('{tag_call_id}', '{call_tags}')")
                
                st.markdown("---")
                
                # Conference Call
                st.markdown("**Konferenzschaltung:**")
                col1, col2 = st.columns(2)
                with col1:
                    conf_call_id = st.text_input("Konferenz Call ID", placeholder="CALL-12345678", key="conf_call_id")
                with col2:
                    conf_participant = st.text_input("Teilnehmer hinzufügen", placeholder="+49301234567", key="conf_participant")
                if st.button("Teilnehmer hinzufügen", key="add_participant"):
                    if conf_call_id and conf_participant:
                        st.code(f"conference_call_add_participant('{conf_call_id}', '{conf_participant}')")
                
                st.markdown("---")
                
                # DND Mode
                st.markdown("**Bitte nicht stören:**")
                col1, col2 = st.columns(2)
                with col1:
                    dnd_enabled = st.checkbox("Aktivieren", key="dnd_enabled")
                with col2:
                    dnd_until = st.text_input("Bis (YYYY-MM-DD HH:MM)", placeholder="2024-01-15 17:00", key="dnd_until")
                if st.button("DND setzen", key="set_dnd"):
                    if dnd_until:
                        st.code(f"set_do_not_disturb({str(dnd_enabled)}, '{dnd_until}')")
                    else:
                        st.code(f"set_do_not_disturb({str(dnd_enabled)})")
                
                st.markdown("---")
                
                # Call Routing
                st.markdown("**Call Routing konfigurieren:**")
                routing_rules = st.text_area("Routing-Regeln (JSON)", 
                    placeholder='{"vip": "agent1", "support": "agent2", "sales": "agent3"}',
                    key="routing_rules", height=100)
                if st.button("Routing aktivieren", key="enable_routing"):
                    if routing_rules:
                        st.code(f"enable_call_routing('{routing_rules}')")
                
                st.markdown("---")
                
                # Voicemail
                st.markdown("**Voicemail prüfen:**")
                voicemail_box = st.text_input("Mailbox", placeholder="default", key="voicemail_box")
                if st.button("Voicemail abrufen", key="check_voicemail"):
                    if voicemail_box:
                        st.code(f"check_voicemail('{voicemail_box}')")
                    else:
                        st.code("check_voicemail()")

    # Task input with tooltip (Task 13.2)
    st.markdown("""
    <div style="margin-bottom: 5px;">
        <span style="font-size: 14px; color: #666;">
         <b>Tip:</b> Be specific about what you want. Include parameters, requirements, and expected output.
        </span>
    </div>
    """, unsafe_allow_html=True)

    # Task input
    user_task = st.text_area(
        "Enter your task:",
        height=100,
        placeholder="Describe what you want the agent to do...",
        key="agent_task_input"
    )

    # Control buttons with tooltips (Task 13.2)
    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        start_button = st.button(
            "Start Agent",
            type="primary",
            use_container_width=True,
            help="Execute the task you entered above. The agent will use its tools to complete your request."
        )

    with col2:
        clear_memory = st.button(
            " Clear Memory",
            use_container_width=True,
            help="Clear the agent's conversation memory. Use this to start fresh with a new context."
        )

    with col3:
        show_status = st.button(
            "Show Status",
            use_container_width=True,
            help="Display the current agent status and configuration information.")

    # Handle clear memory
    if clear_memory:
        if st.session_state.agent_core is not None and hasattr(st.session_state.agent_core, 'clear_memory'):
            st.session_state.agent_core.clear_memory()
            st.success("Memory cleared!")
        else:
            st.warning("Agent nicht initialisiert - kann Memory nicht löschen.")
        st.rerun()

    # Handle show status
    if show_status:
        if st.session_state.agent_core is not None:
            status = st.session_state.agent_core.get_status()
            st.json(status)
        else:
            st.warning("Agent nicht initialisiert - kein Status verfügbar.")

    st.markdown("---")

    # Execute agent task (optimized execution loop)
    if start_button and user_task:
        # Check if agent is initialized
        if st.session_state.agent_core is None:
            st.error("Agent nicht initialisiert. Bitte OpenAI API Key konfigurieren.")
            st.stop()
        
        # Validate user input (Task 12.1)
        try:
            sanitize_user_input(user_task, max_length=10000)
        except InputValidationError as e:
            st.error(f"Input validation failed: {str(e)}")
            st.stop()

        st.markdown("###  Agent Execution")

        # Initialize async execution state if not exists
        if 'async_state' not in st.session_state:
            st.session_state.async_state = AsyncExecutionState()

        # Start async execution
        if not st.session_state.async_state.is_running():
            st.session_state.async_state.start(
                st.session_state.agent_core,
                user_task
            )

        # Create containers for real-time updates (efficient rendering)
        status_container = st.container()
        result_container = st.container()

        # Show progress while running (optimized with fewer reruns)
        with status_container:
            if st.session_state.async_state.is_running():
                # Efficient progress display
                progress_bar = st.progress(0)
                status_text = st.empty()
                elapsed_text = st.empty()

                # Update progress with adaptive rerun frequency
                max_iterations = 50  # Reduced from 100 for fewer reruns
                for i in range(max_iterations):
                    if not st.session_state.async_state.is_running():
                        break

                    # Get current progress
                    progress = st.session_state.async_state.get_progress()
                    elapsed = st.session_state.async_state.get_elapsed_time()

                    # Update UI
                    progress_bar.progress(progress / 100.0)
                    status_text.markdown(
                        f" Agent is thinking... ({progress}%)"
                    )
                    elapsed_text.caption(f"⏱ Elapsed: {elapsed:.1f}s")

                    # Adaptive sleep (longer sleep = fewer reruns)
                    time.sleep(0.2)

                    # Rerun only every 5 iterations (reduce rerun frequency)
                    if i % 5 == 0:
                        st.rerun()

                # Clear progress when done
                if not st.session_state.async_state.is_running():
                    progress_bar.empty()
                    status_text.empty()
                    elapsed_text.empty()

        # Check if execution completed
        if not st.session_state.async_state.is_running():
            result = st.session_state.async_state.get_result()
            error = st.session_state.async_state.get_error()

            if error:
                st.error(f"Unexpected error: {error}")
            elif result:
                # Display results with streaming mode
                with result_container:
                    format_agent_output(result, streaming=True)

            # Reset state for next execution
            st.session_state.async_state = AsyncExecutionState()
        else:
            # Still running, trigger rerun with longer delay
            time.sleep(1.0)  # Increased from 0.5s
            st.rerun()

    # Footer
    st.markdown("---")
    st.caption(
        "Telefonagent O.M.I powered von Ömer"
    )


# Main execution
if __name__ == "__main__":
    render_agent_menu()
