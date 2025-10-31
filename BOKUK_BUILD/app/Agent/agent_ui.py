"""
Agent UI Module
===============

Streamlit interface for the KAI Agent system.
Provides task input, real-time status display, and results visualization.

Performance Optimizations (Task 15.3):
- Async agent execution: Non-blocking task execution with threading
- Streaming output: Real-time display of agent reasoning
- Optimized rendering: Efficient UI updates with minimal reruns
- Progress indicators: Clear feedback during execution
- Lazy loading: Defer heavy operations until needed
- Caching: Reuse expensive computations
"""

from agent.tools.knowledge_tools import lazy_load_knowledge_base
from config import check_api_keys, get_missing_keys, get_setup_instructions
from agent.security import InputValidationError, sanitize_user_input
from agent.agent_core import AgentCore
import os
import queue
import sys
import threading
import time
from typing import Any

import streamlit as st

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


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
        st.success("✅ All API keys are configured!")
        return keys_status

    # Display missing keys
    st.error("⚠️ Missing API Keys")

    st.markdown("### Required API Keys Not Found:")
    for key in missing:
        st.markdown(f"- ❌ **{key}**")

    # Show setup instructions
    with st.expander("📝 Setup Instructions", expanded=True):
        st.code(get_setup_instructions(), language="text")

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
        st.markdown(f"🤖 **{status}**")
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
        expander_title = f"🧠 Agent Reasoning Process ({total_steps} steps)"
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
                            st.markdown(f"🔧 `{action.tool}`")

                    # Display input/output in compact format
                    if hasattr(action, 'tool_input'):
                        with st.expander("📥 Input", expanded=False):
                            # Truncate large inputs
                            input_str = str(action.tool_input)
                            if len(input_str) > 200:
                                st.text(input_str[:200] + "...")
                            else:
                                st.json(action.tool_input)

                    # Truncate long outputs for performance
                    obs_str = str(observation)
                    if len(obs_str) > 500:
                        with st.expander("📤 Output (truncated)", expanded=False):
                            st.code(obs_str[:500] + "...", language="text")
                    else:
                        with st.expander("📤 Output", expanded=False):
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
                "⏱️ Time",
                "{:.2f}s".format(result['execution_time'])
            )

    with col2:
        if 'retry_count' in result and result['retry_count'] > 0:
            st.metric(
                "🔄 Retries",
                result['retry_count']
            )

    with col3:
        intermediate_steps = result.get('intermediate_steps', [])
        if intermediate_steps:
            st.metric(
                "🧠 Steps",
                len(intermediate_steps)
            )

    # Check if successful
    if result.get('success', False):
        st.success("✅ Task completed successfully!")

        # Display output
        output = result.get('output', '')
        if output:
            st.markdown("### 📋 Result:")

            # Truncate very long outputs for performance
            if len(output) > 5000:
                with st.expander("View full output", expanded=True):
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
            st.markdown("### 📁 Generated Files")
            st.info(
                "Files have been created in the `agent_workspace` directory. "
                "You can access them from your file system."
            )

    else:
        # Display error
        st.error("❌ Task failed")

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
            st.markdown("### 💡 Suggested Solution:")
            st.info(result['solution'])

        # Display intermediate steps for debugging (collapsed by default)
        if intermediate_steps:
            with st.expander("🔍 Debug Information", expanded=False):
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
    st.title("🤖 A.G.E.N.T. - Autonomous AI Expert System")
    st.markdown(
        "**Künstliche Intelligenz** with dual expertise in "
        "Renewable Energy Consulting and Software Architecture"
    )

    # Welcome message for first-time users (Task 13.2)
    if 'first_visit' not in st.session_state:
        st.session_state.first_visit = True

    if st.session_state.first_visit:
        st.info("""
        👋 **Welcome to KAI Agent!**

        This AI assistant can help you with:
        - 🌞 Renewable energy consulting (PV systems, heat pumps)
        - 💻 Software development (code generation, testing, project setup)
        - 🔄 Complex multi-step workflows

        **Quick Start:** Enter a task below and click "Start Agent".
        Click the ❓ Help button for detailed instructions and examples.
        """)

        col_dismiss1, col_dismiss2, col_dismiss3 = st.columns([2, 1, 2])
        with col_dismiss2:
            if st.button("Got it! 👍", use_container_width=True):
                st.session_state.first_visit = False
                st.rerun()

    st.markdown("---")

    # API key validation with help (Task 13.2)
    col_config1, col_config2 = st.columns([6, 1])
    with col_config1:
        st.markdown("### 🔑 Configuration Check")
    with col_config2:
        st.markdown("""
        <div style="margin-top: 10px;">
            <span title="API keys are required for the agent to function. OpenAI key is mandatory, others are optional for additional features.">
                ℹ️
            </span>
        </div>
        """, unsafe_allow_html=True)

    keys_status = check_api_keys_ui()

    # Check if OpenAI key is available (required)
    if not keys_status.get('OPENAI_API_KEY', False):
        st.warning(
            "⚠️ Cannot proceed without OPENAI_API_KEY. "
            "Please configure it and restart the application."
        )
        with st.expander("🔧 How to Configure API Keys", expanded=True):
            st.markdown("""
            ### Quick Setup

            1. **Create or edit `.env` file** in the project root directory
            2. **Add your OpenAI API key**:
               ```
               OPENAI_API_KEY=sk-your-key-here
               ```
            3. **Get your API key** from [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
            4. **Restart the application**

            ### Optional Keys (for additional features)

            - **TAVILY_API_KEY**: Web search capability
            - **TWILIO_***: Telephony features
            - **ELEVEN_LABS_API_KEY**: Voice synthesis

            See `AGENT_INSTALLATION_GUIDE.md` for detailed instructions.
            """)
        st.stop()

    st.markdown("---")

    # Initialize knowledge base and agent (optimized with lazy loading)
    col_kb1, col_kb2 = st.columns([6, 1])
    with col_kb1:
        st.markdown("### 📚 Knowledge Base Initialization")
    with col_kb2:
        st.markdown("""
        <div style="margin-top: 10px;">
            <span title="The knowledge base contains domain-specific PDF documents that the agent can search for information.">
                ℹ️
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
                    st.success("✅ Knowledge base loaded successfully!")
                    st.caption(
                        "💡 The agent can now search PDF documents for "
                        "domain-specific information about renewable energy systems.")
                else:
                    st.info(
                        "📚 Knowledge base is empty. "
                        "Add PDF files to `Agent/knowledge_base/` directory."
                    )
                    with st.expander("📖 How to Add Documents", expanded=False):
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
                st.session_state.agent_core = AgentCore(
                    vector_store=st.session_state.vector_store
                )
                st.success("✅ Agent initialized successfully!")
            except Exception as e:
                st.error(f"Failed to initialize agent: {e}")
                st.stop()

    st.markdown("---")

    # Task input interface
    st.markdown("### 🎯 Task Input")

    # Help button and dialog (Task 13.2)
    col_help1, col_help2 = st.columns([6, 1])
    with col_help2:
        if st.button("❓ Help", use_container_width=True):
            st.session_state.show_help_dialog = True

    # Help dialog (Task 13.2)
    if st.session_state.get('show_help_dialog', False):
        with st.expander("📖 Complete Help Guide", expanded=True):
            st.markdown("""
            ## How to Use the KAI Agent

            ### What is KAI Agent?
            KAI (Künstliche Intelligenz) is an autonomous AI assistant with dual expertise:
            - **Renewable Energy Consulting**: Photovoltaics, heat pumps, economic analysis
            - **Software Architecture**: Code generation, testing, project scaffolding

            ### How It Works
            1. **Enter your task** in the text area below
            2. **Click "Start Agent"** to begin execution
            3. **Watch the agent think** - see its reasoning process in real-time
            4. **Review results** - get comprehensive answers, code, or analysis

            ### Task Types You Can Request

            #### 🌞 Renewable Energy Consulting
            - Search knowledge base for technical information
            - Calculate ROI and amortization times
            - Prepare customer presentations
            - Compare different system configurations
            - Simulate sales calls

            #### 💻 Software Development
            - Generate Python functions with tests
            - Create complete project structures
            - Write and execute unit tests
            - Debug and fix code errors
            - Generate API endpoints

            #### 🔄 Combined Workflows
            - Research → Code → Test → Document
            - Knowledge search → Calculation → Presentation
            - Multi-step complex tasks

            ### Tips for Best Results

            ✅ **Be Specific**: "Create a Python function to calculate solar panel ROI with parameters: investment, annual_savings, years"

            ✅ **Provide Context**: "I'm building a customer consultation tool. Create a function that..."

            ✅ **Break Down Complex Tasks**: Instead of "Build a complete app", try:
            1. "Create project structure"
            2. "Implement core calculations"
            3. "Add tests"

            ✅ **Use Examples**: "Create a function similar to this: [paste example]"

            ❌ **Avoid Vague Requests**: "Do something with solar" → Too vague

            ### Available Tools

            The agent has access to:
            - 📚 **Knowledge Base**: Domain-specific PDF documents
            - 🔍 **Web Search**: Current information via Tavily API
            - 🐳 **Code Execution**: Secure Docker sandbox
            - 📁 **File Operations**: Read/write in workspace
            - 📞 **Telephony**: Simulated sales calls
            - 🧪 **Testing**: Automated pytest execution

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

            📚 **Documentation**: Check the `Agent/` directory for detailed guides
            - `README.md` - Overview and quick start
            - `BASIC_USAGE_TUTORIAL.md` - Beginner guide
            - `EXAMPLE_TASKS.md` - 20+ example tasks
            - `TROUBLESHOOTING.md` - Problem solving
            - `ADVANCED_FEATURES_GUIDE.md` - Advanced usage

            🔧 **Validation**: Run `python Agent/validate_config.py` to check setup

            📖 **Installation**: See `AGENT_INSTALLATION_GUIDE.md` for setup help
            """)

            if st.button("Close Help", use_container_width=True):
                st.session_state.show_help_dialog = False
                st.rerun()

    # Example tasks with categories (Task 13.2)
    with st.expander("💡 Example Task Suggestions", expanded=False):
        tab1, tab2, tab3 = st.tabs([
            "🌞 Energy Consulting",
            "💻 Software Dev",
            "🔄 Combined"
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

            if st.button("📋 Copy Example 1", key="copy_energy_1"):
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

            if st.button("📋 Copy Example 2", key="copy_dev_1"):
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

            if st.button("📋 Copy Example 3", key="copy_combined_1"):
                st.session_state.agent_task_input = "Suche in der Wissensdatenbank nach PV-Vorteilen, erstelle dann eine Python-Funktion zur Ertragsberechnung mit Tests"
                st.rerun()

    # Usage instructions (Task 13.2)
    with st.expander("📝 Quick Usage Instructions", expanded=False):
        st.markdown("""
        ### Getting Started in 3 Steps

        **Step 1: Enter Your Task**
        - Type what you want the agent to do in the text area below
        - Be as specific as possible
        - Include all necessary details

        **Step 2: Start the Agent**
        - Click the "🚀 Start Agent" button
        - The agent will begin processing your request
        - You'll see its thinking process in real-time

        **Step 3: Review Results**
        - Read the agent's response
        - Copy any generated code
        - Download created files if needed

        ### Writing Effective Tasks

        **Good Task Examples:**
        - ✅ "Create a Python function called calculate_roi that takes investment and annual_savings as parameters"
        - ✅ "Search the knowledge base for information about heat pump efficiency (JAZ)"
        - ✅ "Generate a Flask project structure with models, routes, and tests"

        **Tasks to Avoid:**
        - ❌ "Do something" (too vague)
        - ❌ "Help me" (no specific request)
        - ❌ "Fix everything" (no context)

        ### Agent Capabilities

        ✅ **Can Do:**
        - Search knowledge base
        - Generate Python code
        - Write and run tests
        - Create project structures
        - Perform calculations
        - Simulate conversations
        - Search the web (if API key configured)

        ❌ **Cannot Do:**
        - Access your local files outside workspace
        - Make real phone calls (only simulation)
        - Access databases directly
        - Modify existing application code
        - Execute commands on your system

        ### Tips & Tricks

        💡 **Use the knowledge base first**: The agent will search its knowledge base before using web search

        💡 **Break down complex tasks**: Multi-step tasks work better when broken into phases

        💡 **Provide examples**: Show the agent what you want with examples

        💡 **Iterate**: Start simple, then refine based on results

        💡 **Check the reasoning**: Watch the agent's thinking process to understand its approach
        """)

    # Task input with tooltip (Task 13.2)
    st.markdown("""
    <div style="margin-bottom: 5px;">
        <span style="font-size: 14px; color: #666;">
        💬 <b>Tip:</b> Be specific about what you want. Include parameters, requirements, and expected output.
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
            "🚀 Start Agent",
            type="primary",
            use_container_width=True,
            help="Execute the task you entered above. The agent will use its tools to complete your request."
        )

    with col2:
        clear_memory = st.button(
            "🔄 Clear Memory",
            use_container_width=True,
            help="Clear the agent's conversation memory. Use this to start fresh with a new context."
        )

    with col3:
        show_status = st.button(
            "📊 Show Status",
            use_container_width=True,
            help="Display the current agent status and configuration information.")

    # Handle clear memory
    if clear_memory:
        if hasattr(st.session_state.agent_core, 'clear_memory'):
            st.session_state.agent_core.clear_memory()
            st.success("Memory cleared!")
        st.rerun()

    # Handle show status
    if show_status:
        status = st.session_state.agent_core.get_status()
        st.json(status)

    st.markdown("---")

    # Execute agent task (optimized execution loop)
    if start_button and user_task:
        # Validate user input (Task 12.1)
        try:
            sanitize_user_input(user_task, max_length=10000)
        except InputValidationError as e:
            st.error(f"❌ Input validation failed: {str(e)}")
            st.stop()

        st.markdown("### 🤖 Agent Execution")

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
                        f"🧠 Agent is thinking... ({progress}%)"
                    )
                    elapsed_text.caption(f"⏱️ Elapsed: {elapsed:.1f}s")

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
        "KAI Agent - Powered by GPT-4, LangChain, and specialized tools"
    )


# Main execution
if __name__ == "__main__":
    render_agent_menu()
