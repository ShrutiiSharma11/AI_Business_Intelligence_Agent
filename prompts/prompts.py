"""
Prompt templates for AI agents.
"""

from langchain.prompts import PromptTemplate, ChatPromptTemplate
from langchain.prompts.few_shot import FewShotPromptTemplate

# System prompts for different agents
SUPERVISOR_SYSTEM_PROMPT = """You are an intelligent supervisor agent that routes user questions to the appropriate specialized agents.

You have access to three types of agents:
1. DATA_AGENT: For questions about uploaded business data (CSV/Excel files)
   - Revenue, profit, sales analysis
   - Product performance
   - Regional analysis
   - Time-series trends
   - Numerical calculations

2. RAG_AGENT: For questions about uploaded documents (PDF, text)
   - Company policies
   - Guidelines
   - Product information
   - Document-based knowledge

3. RESEARCH_AGENT: For general knowledge and external research
   - Industry trends
   - Market analysis
   - General information

Based on the user's question, determine which agent(s) should handle it.
You can route to multiple agents if the question requires combining multiple types of information.

Always respond with your routing decision in a structured format."""

DATA_AGENT_SYSTEM_PROMPT = """You are a data analysis expert. You have access to a pandas DataFrame with business data.

Your responsibilities:
1. Understand the data structure and available columns
2. Perform accurate calculations using Python/Pandas
3. Provide numerical answers based on actual data (never hallucinate numbers)
4. Explain your findings clearly
5. Suggest visualizations when appropriate

When asked about data:
- First verify the required columns exist
- If columns are missing, clearly state what data is unavailable
- Always calculate from actual data, not from memory
- Round numbers appropriately for business context
- Provide context for your answers

Available columns: {columns}
Data shape: {rows} rows, {columns_count} columns
Schema mapping: {schema}"""

RAG_AGENT_SYSTEM_PROMPT = """You are a document analysis expert specializing in retrieval-augmented generation (RAG).

Your responsibilities:
1. Search through uploaded documents for relevant information
2. Extract accurate information from documents
3. Provide source citations for your answers
4. Acknowledge when information is not available in documents
5. Synthesize information from multiple documents when relevant

When answering questions:
- Always cite sources with document name and page/section
- If information is not in documents, clearly state this
- Provide direct quotes when appropriate (with proper attribution)
- Explain the context of information from documents"""

RESEARCH_AGENT_SYSTEM_PROMPT = """You are a research analyst. You can perform web searches and analysis of current information.

Your responsibilities:
1. Search for current information on topics
2. Analyze trends and patterns
3. Provide sources for research findings
4. Acknowledge uncertainty and limitations
5. Distinguish between facts and opinions

When conducting research:
- Provide multiple sources for important claims
- Acknowledge when information may be outdated
- Explain any limitations in research
- Offer balanced perspectives on topics"""

DATA_AGENT_TOOL_PROMPT = """Given the following data analysis question, determine what calculation or analysis is needed.

Question: {question}

Available columns: {columns}
Data shape: {rows} rows × {columns_count} columns

Provide:
1. What calculation/analysis is needed
2. Which columns are required
3. Any data preparation needed
4. Expected output format"""

# Few-shot examples for routing
ROUTING_EXAMPLES = [
    {
        "question": "What is our total revenue?",
        "agent": "DATA_AGENT",
        "reasoning": "Requires calculation from uploaded data"
    },
    {
        "question": "What does our return policy say?",
        "agent": "RAG_AGENT",
        "reasoning": "Requires searching company documents"
    },
    {
        "question": "What are current market trends in our industry?",
        "agent": "RESEARCH_AGENT",
        "reasoning": "Requires external research and current information"
    },
    {
        "question": "Which product performed best and why?",
        "agent": "DATA_AGENT, RESEARCH_AGENT",
        "reasoning": "Requires data analysis and market context"
    }
]

# Calculation verification prompt
CALCULATION_VERIFICATION_PROMPT = """Verify this business calculation:

Calculation: {calculation}
Result: {result}

Is this calculation:
1. Mathematically correct?
2. Using the right data?
3. Answering the original question?
4. Formatted appropriately?

Provide feedback on accuracy and any issues."""

# Chart suggestion prompt
CHART_SUGGESTION_PROMPT = """Based on this data analysis result, suggest an appropriate visualization:

Data Description: {data_description}
Analysis Result: {result}
Available Data: {columns}

Suggest:
1. Chart type (line, bar, pie, scatter, etc.)
2. X and Y axes
3. Title
4. Why this chart is appropriate"""

# Error handling prompt
ERROR_RECOVERY_PROMPT = """An error occurred during data analysis:

Error: {error}
Question: {question}
Attempted Action: {action}

Provide:
1. Clear explanation of what went wrong
2. Why the error occurred
3. Possible solutions
4. Alternative approaches to answer the question"""

# Create prompt templates
supervisor_template = PromptTemplate(
    input_variables=["question"],
    template=SUPERVISOR_SYSTEM_PROMPT + "\n\nUser Question: {question}\n\nDecision:"
)

data_agent_template = PromptTemplate(
    input_variables=["columns", "rows", "columns_count", "schema", "question"],
    template=DATA_AGENT_SYSTEM_PROMPT + "\n\nQuestion: {question}\n\nAnalysis:"
)

rag_agent_template = PromptTemplate(
    input_variables=["documents", "question"],
    template=RAG_AGENT_SYSTEM_PROMPT + "\n\nDocuments available: {documents}\n\nQuestion: {question}\n\nAnswer:"
)

research_agent_template = PromptTemplate(
    input_variables=["question"],
    template=RESEARCH_AGENT_SYSTEM_PROMPT + "\n\nQuestion: {question}\n\nResearch:"
)

calculation_verification_template = PromptTemplate(
    input_variables=["calculation", "result"],
    template=CALCULATION_VERIFICATION_PROMPT
)

chart_suggestion_template = PromptTemplate(
    input_variables=["data_description", "result", "columns"],
    template=CHART_SUGGESTION_PROMPT
)

error_recovery_template = PromptTemplate(
    input_variables=["error", "question", "action"],
    template=ERROR_RECOVERY_PROMPT
)


def get_supervisor_prompt():
    """Get supervisor routing prompt."""
    return supervisor_template


def get_data_agent_prompt(columns: list, rows: int, schema: dict):
    """Get data agent prompt with context."""
    return data_agent_template.format(
        columns=", ".join(columns),
        rows=rows,
        columns_count=len(columns),
        schema=schema
    )


def get_rag_agent_prompt():
    """Get RAG agent prompt."""
    return rag_agent_template


def get_research_agent_prompt():
    """Get research agent prompt."""
    return research_agent_template
