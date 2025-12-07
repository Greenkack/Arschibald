"""
Call Protocol Logic for KAI Agent
==================================

Provides structured protocols and strategies for conducting
professional sales and consulting calls.

Requirements: 4.2, 4.3, 4.4
"""

from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class CallProtocol:
    """Structured call protocol with phases and strategies."""

    phase: str
    objective: str
    strategies: List[str]
    key_points: List[str]
    common_objections: List[Dict[str, str]]


class CallProtocolManager:
    """
    Manages call protocols and provides guidance for each call phase.

    The protocol follows a proven sales methodology:
    1. Knowledge Preparation
    2. Opening & Rapport Building
    3. Needs Discovery
    4. Solution Presentation
    5. Objection Handling
    6. Closing & Next Steps
    """

    def __init__(self):
        """Initialize protocol manager with predefined protocols."""
        self.protocols = self._initialize_protocols()

    def _initialize_protocols(self) -> Dict[str, CallProtocol]:
        """Initialize all call phase protocols."""
        return {
            'preparation': CallProtocol(
                phase='Knowledge Preparation',
                objective='Gather relevant information before the call',
                strategies=[
                    'Search knowledge base for product information',
                    'Review customer background if available',
                    'Prepare key statistics and benefits',
                    'Identify potential objections and responses',
                ],
                key_points=[
                    'Know your top 3 benefits with data backing',
                    'Understand current market conditions',
                    'Have financing options ready',
                    'Prepare ROI calculations',
                ],
                common_objections=[]
            ),

            'opening': CallProtocol(
                phase='Opening & Rapport Building',
                objective='Establish credibility and set call agenda',
                strategies=[
                    'Professional introduction with name and company',
                    'State the purpose of the call clearly',
                    'Ask permission to continue ("Passt es gerade?")',
                    'Set expectations for call duration',
                ],
                key_points=[
                    'Be confident but not aggressive',
                    'Use a warm, professional tone',
                    'Respect their time',
                    'Create curiosity about the solution',
                ],
                common_objections=[
                    {
                        'objection': 'Ich habe keine Zeit',
                        'response': (
                            'Ich verstehe, dass Ihre Zeit wertvoll ist. '
                            'Dieses Gespräch dauert nur 5 Minuten und '
                            'könnte Ihnen helfen, jährlich Tausende Euro '
                            'zu sparen. Passt es kurz?'
                        )
                    },
                    {
                        'objection': 'Ich bin nicht interessiert',
                        'response': (
                            'Das verstehe ich. Darf ich fragen, ob Sie '
                            'bereits eine Photovoltaikanlage haben oder '
                            'ob Sie einfach mehr Informationen benötigen?'
                        )
                    },
                ]
            ),

            'discovery': CallProtocol(
                phase='Needs Discovery',
                objective='Understand customer situation and needs',
                strategies=[
                    'Ask open-ended questions',
                    'Listen actively and take notes',
                    'Identify pain points and motivations',
                    'Qualify the opportunity',
                ],
                key_points=[
                    'Current energy costs and consumption',
                    'Property ownership and roof condition',
                    'Environmental concerns vs. financial motivation',
                    'Decision-making timeline',
                    'Budget considerations',
                ],
                common_objections=[]
            ),

            'presentation': CallProtocol(
                phase='Solution Presentation',
                objective='Present tailored solution with clear benefits',
                strategies=[
                    'Present top 3 benefits relevant to their needs',
                    'Use specific data and statistics',
                    'Paint a picture of their future with the solution',
                    'Address their specific pain points',
                ],
                key_points=[
                    'Financial savings (ROI, payback period)',
                    'Energy independence and security',
                    'Environmental impact (CO2 reduction)',
                    'Property value increase',
                    'Government incentives and financing',
                ],
                common_objections=[
                    {
                        'objection': 'Das ist zu teuer',
                        'response': (
                            'Ich verstehe Ihre Bedenken bezüglich der '
                            'Investition. Lassen Sie uns über die '
                            'langfristigen Einsparungen sprechen. '
                            'Bei durchschnittlichen Stromkosten '
                            'amortisiert sich die Anlage in 8-10 Jahren, '
                            'und sie hält 25-30 Jahre. Das bedeutet '
                            '15-20 Jahre praktisch kostenlosen Strom. '
                            'Außerdem gibt es Finanzierungsoptionen '
                            'ab 0% Zinsen.'
                        )
                    },
                    {
                        'objection': 'Ich bin mir nicht sicher',
                        'response': (
                            'Das ist völlig verständlich - es ist eine '
                            'wichtige Entscheidung. Was genau macht Sie '
                            'unsicher? Ist es die Technik, die Kosten, '
                            'oder etwas anderes? Ich kann Ihnen gerne '
                            'mehr Details zu Ihren spezifischen Bedenken '
                            'geben.'
                        )
                    },
                ]
            ),

            'objection_handling': CallProtocol(
                phase='Objection Handling',
                objective='Address concerns with validation and data',
                strategies=[
                    'VALIDATE: Acknowledge the concern as legitimate',
                    'CLARIFY: Ask questions to understand the real issue',
                    'RESPOND: Provide data-driven counter-arguments',
                    'CONFIRM: Check if the concern is resolved',
                ],
                key_points=[
                    'Never dismiss or argue with objections',
                    'Use the "Feel, Felt, Found" technique',
                    'Provide social proof (testimonials, case studies)',
                    'Offer guarantees or risk reversal',
                ],
                common_objections=[
                    {
                        'objection': 'Mein Dach ist nicht geeignet',
                        'response': (
                            'Das ist eine berechtigte Sorge. Moderne '
                            'Photovoltaikanlagen funktionieren auch bei '
                            'Ost-West-Ausrichtung sehr gut. Wir bieten '
                            'eine kostenlose Dachanalyse an, bei der wir '
                            'mit Satellitenbildern und Verschattungsanalyse '
                            'genau berechnen, wie viel Ertrag Ihr Dach '
                            'bringen würde. Darf ich das für Sie '
                            'vorbereiten?'
                        )
                    },
                    {
                        'objection': 'Ich muss mit meiner Familie sprechen',
                        'response': (
                            'Absolut, das ist eine Familienentscheidung. '
                            'Damit Sie alle Informationen für das Gespräch '
                            'haben, kann ich Ihnen eine detaillierte '
                            'Berechnung mit Ihren spezifischen Daten '
                            'zusenden? So können Sie gemeinsam die Zahlen '
                            'durchgehen. Wann wäre ein guter Zeitpunkt '
                            'für ein Folgegespräch?'
                        )
                    },
                    {
                        'objection': 'Die Technik ist noch nicht ausgereift',
                        'response': (
                            'Ich verstehe diese Sorge, aber die Fakten '
                            'zeigen etwas anderes. Photovoltaik gibt es '
                            'seit über 40 Jahren, und moderne Module haben '
                            '25-30 Jahre Leistungsgarantie. Die Technik '
                            'ist ausgereift und bewährt - allein in '
                            'Deutschland sind über 2 Millionen Anlagen '
                            'installiert. Die Frage ist eher: Wie lange '
                            'möchten Sie noch hohe Stromrechnungen zahlen?'
                        )
                    },
                    {
                        'objection': 'Was ist bei Bewölkung oder Winter?',
                        'response': (
                            'Ausgezeichnete Frage! PV-Anlagen produzieren '
                            'auch bei diffusem Licht Strom, nur weniger. '
                            'Im Jahresdurchschnitt erreichen Sie trotzdem '
                            'den vollen Ertrag. Außerdem: Mit einem '
                            'Batteriespeicher können Sie Sommerüberschüsse '
                            'für den Winter nutzen. Und wenn die Sonne '
                            'nicht scheint, beziehen Sie einfach Strom '
                            'aus dem Netz - aber zu deutlich reduzierten '
                            'Gesamtkosten.'
                        )
                    },
                ]
            ),

            'closing': CallProtocol(
                phase='Closing & Next Steps',
                objective='Secure commitment and define clear next actions',
                strategies=[
                    'Summarize key benefits discussed',
                    'Propose specific next step (not vague "follow-up")',
                    'Create urgency with limited-time offers if applicable',
                    'Get calendar commitment for next interaction',
                ],
                key_points=[
                    'Be direct but not pushy',
                    'Offer multiple next-step options',
                    'Confirm contact information',
                    'Set clear expectations for follow-up',
                ],
                common_objections=[
                    {
                        'objection': 'Ich melde mich bei Ihnen',
                        'response': (
                            'Das verstehe ich. Erfahrungsgemäß geht das '
                            'im Alltag oft unter. Wie wäre es, wenn wir '
                            'jetzt direkt einen Termin für ein kurzes '
                            'Folgegespräch vereinbaren? Dann haben Sie '
                            'Zeit, sich alles zu überlegen, und wir können '
                            'Ihre Fragen beantworten. Passt Ihnen nächste '
                            'Woche Dienstag oder Donnerstag besser?'
                        )
                    },
                ]
            ),
        }

    def get_protocol(self, phase: str) -> Optional[CallProtocol]:
        """
        Get protocol for a specific call phase.

        Args:
            phase: Call phase name

        Returns:
            CallProtocol object or None if phase not found
        """
        return self.protocols.get(phase.lower())

    def get_all_phases(self) -> List[str]:
        """Get list of all protocol phases."""
        return list(self.protocols.keys())

    def format_protocol_guide(self, phase: str) -> str:
        """
        Format protocol guide for display.

        Args:
            phase: Call phase name

        Returns:
            Formatted protocol guide string
        """
        protocol = self.get_protocol(phase)
        if not protocol:
            return f"Unknown phase: {phase}"

        guide = f"""
╔══════════════════════════════════════════════════════════════╗
║  CALL PROTOCOL: {protocol.phase.upper():^44} ║
╚══════════════════════════════════════════════════════════════╝

OBJECTIVE:
   {protocol.objective}

📋 STRATEGIES:
"""
        for i, strategy in enumerate(protocol.strategies, 1):
            guide += f"   {i}. {strategy}\n"

        guide += "\nKEY POINTS:\n"
        for point in protocol.key_points:
            guide += f"   • {point}\n"

        if protocol.common_objections:
            guide += "\n🛡️  COMMON OBJECTIONS & RESPONSES:\n"
            for obj in protocol.common_objections:
                guide += f"\n   ❓ \"{obj['objection']}\"\n"
                guide += f"   {obj['response']}\n"

        guide += "\n╚══════════════════════════════════════════════════════════════╝"
        return guide

    def get_objection_response(
        self,
        objection: str,
        phase: str = 'objection_handling'
    ) -> Optional[str]:
        """
        Find a response for a specific objection.

        Args:
            objection: Customer objection text
            phase: Call phase to search in

        Returns:
            Suggested response or None
        """
        protocol = self.get_protocol(phase)
        if not protocol:
            return None

        # Simple keyword matching
        objection_lower = objection.lower()

        for obj_data in protocol.common_objections:
            if any(
                keyword in objection_lower
                for keyword in obj_data['objection'].lower().split()
            ):
                return obj_data['response']

        return None

    def build_argument_structure(
        self,
        customer_need: str,
        knowledge_facts: List[str]
    ) -> str:
        """
        Build a structured argument based on customer needs and facts.

        Args:
            customer_need: Identified customer need or pain point
            knowledge_facts: Relevant facts from knowledge base

        Returns:
            Structured argument string
        """
        argument = f"""
ADDRESSING CUSTOMER NEED: {customer_need}

DATA-DRIVEN ARGUMENT STRUCTURE:

1. VALIDATE THE NEED:
   "Ich verstehe, dass {customer_need} für Sie wichtig ist."

2. PRESENT SOLUTION WITH DATA:
"""
        for i, fact in enumerate(knowledge_facts[:3], 1):
            argument += f"   {i}. {fact}\n"

        argument += """
3. PAINT THE FUTURE:
   "Stellen Sie sich vor, wie es wäre, wenn..."

4. CALL TO ACTION:
   "Der nächste Schritt wäre..."
"""
        return argument

    def generate_closing_statement(
        self,
        call_summary: str,
        proposed_next_step: str
    ) -> str:
        """
        Generate a professional closing statement.

        Args:
            call_summary: Brief summary of call discussion
            proposed_next_step: Specific next action

        Returns:
            Closing statement
        """
        return f"""
Vielen Dank für das Gespräch! Lassen Sie mich kurz zusammenfassen:

{call_summary}

Der nächste Schritt wäre: {proposed_next_step}

Passt Ihnen das? Dann würde ich das direkt für Sie vorbereiten.
"""


# Global protocol manager instance
_protocol_manager = CallProtocolManager()


def get_call_protocol(phase: str) -> Optional[CallProtocol]:
    """
    Get call protocol for a specific phase.

    Args:
        phase: Call phase name (preparation, opening, discovery,
               presentation, objection_handling, closing)

    Returns:
        CallProtocol object

    Requirements: 4.2, 4.3
    """
    return _protocol_manager.get_protocol(phase)


def format_protocol_guide(phase: str) -> str:
    """
    Get formatted protocol guide for display.

    Args:
        phase: Call phase name

    Returns:
        Formatted guide string

    Requirements: 4.2, 4.3
    """
    return _protocol_manager.format_protocol_guide(phase)


def handle_objection(objection: str) -> str:
    """
    Get suggested response for a customer objection.

    Args:
        objection: Customer objection text

    Returns:
        Suggested response or guidance

    Requirements: 4.3, 4.4
    """
    # Try to find a matching response
    response = _protocol_manager.get_objection_response(objection)

    if response:
        return f"""
🛡️  OBJECTION DETECTED: "{objection}"

SUGGESTED RESPONSE:
{response}

REMEMBER THE 4-STEP PROCESS:
1. VALIDATE: Acknowledge the concern
2. CLARIFY: Ask questions to understand
3. RESPOND: Provide data-driven counter-argument
4. CONFIRM: Check if concern is resolved
"""

    # Generic objection handling guidance
    return f"""
🛡️  OBJECTION DETECTED: "{objection}"

No pre-defined response found. Follow the 4-STEP PROCESS:

1. VALIDATE:
   "Ich verstehe Ihre Bedenken bezüglich..."

2. CLARIFY:
   "Darf ich fragen, was genau Sie dabei am meisten beschäftigt?"

3. RESPOND:
   - Search knowledge base for relevant facts
   - Provide data-driven counter-argument
   - Use social proof if available

4. CONFIRM:
   "Konnte ich Ihre Bedenken damit ausräumen?"

TIP: Use the knowledge_base_search tool to find relevant facts!
"""


def build_argument_structure(
    customer_need: str,
    knowledge_facts: List[str]
) -> str:
    """
    Build a structured sales argument.

    Args:
        customer_need: Customer need or pain point
        knowledge_facts: Facts from knowledge base

    Returns:
        Structured argument

    Requirements: 4.2, 4.3
    """
    return _protocol_manager.build_argument_structure(
        customer_need,
        knowledge_facts
    )


def generate_closing_statement(
    call_summary: str,
    proposed_next_step: str
) -> str:
    """
    Generate professional closing statement.

    Args:
        call_summary: Summary of discussion
        proposed_next_step: Specific next action

    Returns:
        Closing statement

    Requirements: 4.4
    """
    return _protocol_manager.generate_closing_statement(
        call_summary,
        proposed_next_step
    )
