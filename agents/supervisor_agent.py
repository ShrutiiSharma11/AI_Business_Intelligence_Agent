"""
Supervisor Agent: Routes user questions to appropriate specialized agents.
Uses LangGraph for multi-agent orchestration.
"""

import logging
from typing import Dict, Any, List, Optional
import json

logger = logging.getLogger(__name__)


class QuestionRouter:
    """
    Routes questions to appropriate agents based on content analysis.
    """

    # Keywords for each agent type
    DATA_AGENT_KEYWORDS = {
        "data": ["revenue", "profit", "sales", "cost", "top", "highest", "monthly",
                 "region", "product", "loss", "margin", "average", "total", "breakdown",
                 "trend", "comparison", "performance"],
        "requirement": ["data loaded", "csv", "excel", "dataset", "file"]
    }

    RAG_AGENT_KEYWORDS = {
        "data": ["policy", "document", "guideline", "procedure", "rule", "requirement",
                 "process", "information", "knowledge", "pdf", "text", "manual", "handbook"],
        "requirement": ["document", "file", "uploaded"]
    }

    RESEARCH_AGENT_KEYWORDS = {
        "data": ["industry", "market", "trend", "research", "analysis", "current",
                 "external", "web", "general", "why", "how", "comparison with"],
        "requirement": ["external", "research", "web", "general knowledge"]
    }

    def __init__(self):
        self.logger = logger

    def route_question(self, question: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Route a question to one or more agents.

        Args:
            question: User's question
            context: Additional context (e.g., what data/documents are loaded)

        Returns:
            Routing decision with recommended agents
        """
        question_lower = question.lower()

        # Score each agent
        data_score = self._score_agent(question_lower, self.DATA_AGENT_KEYWORDS)
        rag_score = self._score_agent(question_lower, self.RAG_AGENT_KEYWORDS)
        research_score = self._score_agent(question_lower, self.RESEARCH_AGENT_KEYWORDS)

        # Normalize context
        context = context or {}
        has_data = context.get("has_data", False)
        has_documents = context.get("has_documents", False)

        # Determine routing
        routing = self._determine_routing(
            data_score, rag_score, research_score,
            has_data, has_documents
        )

        return {
            "question": question,
            "agents": routing["agents"],
            "primary_agent": routing["primary_agent"],
            "secondary_agents": routing["secondary_agents"],
            "reasoning": routing["reasoning"],
            "scores": {
                "data_agent": data_score,
                "rag_agent": rag_score,
                "research_agent": research_score
            }
        }

    def _score_agent(self, question: str, keywords_config: Dict[str, List[str]]) -> float:
        """
        Score how relevant an agent is for a question.

        Args:
            question: Question text
            keywords_config: Agent's keyword configuration

        Returns:
            Relevance score (0-1)
        """
        data_keywords = keywords_config.get("data", [])
        matches = sum(1 for keyword in data_keywords if keyword in question)

        score = min(matches / max(len(data_keywords), 1), 1.0)
        return score

    def _determine_routing(self,
                          data_score: float,
                          rag_score: float,
                          research_score: float,
                          has_data: bool,
                          has_documents: bool) -> Dict[str, Any]:
        """
        Determine which agents should handle the question.

        Args:
            data_score: Data agent relevance score
            rag_score: RAG agent relevance score
            research_score: Research agent relevance score
            has_data: Whether data is loaded
            has_documents: Whether documents are loaded

        Returns:
            Routing decision
        """
        selected_agents = []
        reasoning_parts = []

        # Data agent
        if data_score > 0.3 and has_data:
            selected_agents.append("DATA_AGENT")
            reasoning_parts.append("Question requires data analysis")
        elif data_score > 0.3 and not has_data:
            reasoning_parts.append("Question needs data, but none is loaded")

        # RAG agent
        if rag_score > 0.3 and has_documents:
            selected_agents.append("RAG_AGENT")
            reasoning_parts.append("Question requires searching documents")
        elif rag_score > 0.3 and not has_documents:
            reasoning_parts.append("Question needs documents, but none are loaded")

        # Research agent
        if research_score > 0.3:
            selected_agents.append("RESEARCH_AGENT")
            reasoning_parts.append("Question requires external research")

        # Fallback
        if not selected_agents:
            if data_score > rag_score and data_score > research_score:
                selected_agents.append("DATA_AGENT")
                if has_data:
                    reasoning_parts.append("Using data agent for analysis")
                else:
                    reasoning_parts.append("Best match is data agent, but no data loaded")
            else:
                selected_agents.append("RESEARCH_AGENT")
                reasoning_parts.append("Using general research agent")

        primary = selected_agents[0] if selected_agents else "RESEARCH_AGENT"
        secondary = selected_agents[1:] if len(selected_agents) > 1 else []

        return {
            "agents": selected_agents,
            "primary_agent": primary,
            "secondary_agents": secondary,
            "reasoning": "; ".join(reasoning_parts)
        }


class SupervisorAgent:
    """
    Supervisor orchestrates multi-agent workflow.
    """

    def __init__(self, data_agent=None, rag_agent=None, research_agent=None):
        self.data_agent = data_agent
        self.rag_agent = rag_agent
        self.research_agent = research_agent
        self.router = QuestionRouter()
        self.logger = logger
        self.conversation_history: List[Dict[str, Any]] = []

    def process_question(self, question: str) -> Dict[str, Any]:
        """
        Process a user question using appropriate agents.

        Args:
            question: User's question

        Returns:
            Processed result with answer and metadata
        """
        # Get context
        context = self._get_context()

        # Route question
        routing = self.router.route_question(question, context)

        # Store in history
        self.conversation_history.append({
            "question": question,
            "routing": routing
        })

        self.logger.info(f"Routing decision: {routing['primary_agent']}")

        # Process with selected agents
        result = self._execute_agents(question, routing)

        return result

    def _get_context(self) -> Dict[str, Any]:
        """Get current context about available resources."""
        return {
            "has_data": self.data_agent is not None and self.data_agent.state.df is not None,
            "has_documents": self.rag_agent is not None and self.rag_agent.document_store.get_document_count() > 0
        }

    def _execute_agents(self, question: str, routing: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute agents based on routing decision.

        Args:
            question: User's question
            routing: Routing decision

        Returns:
            Combined result from all executed agents
        """
        agents_to_execute = routing.get("agents", [])

        results = {
            "question": question,
            "routing": routing,
            "agent_results": {}
        }

        # Execute each agent
        for agent_name in agents_to_execute:
            agent_result = self._execute_single_agent(agent_name, question)
            results["agent_results"][agent_name] = agent_result

        # Combine results
        results["combined_answer"] = self._combine_results(results["agent_results"])

        return results

    def _execute_single_agent(self, agent_name: str, question: str) -> Dict[str, Any]:
        """Execute a single agent."""
        try:
            if agent_name == "DATA_AGENT" and self.data_agent:
                return self.data_agent.process_question(question)

            elif agent_name == "RAG_AGENT" and self.rag_agent:
                return self.rag_agent.answer_question(question)

            elif agent_name == "RESEARCH_AGENT" and self.research_agent:
                return self.research_agent.research(question)

            else:
                return {
                    "success": False,
                    "error": f"{agent_name} not available"
                }

        except Exception as e:
            self.logger.error(f"Error executing {agent_name}: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    def _combine_results(self, agent_results: Dict[str, Any]) -> str:
        """
        Combine results from multiple agents into a coherent answer.

        Args:
            agent_results: Results from executed agents

        Returns:
            Combined answer string
        """
        answers = []

        for agent_name, result in agent_results.items():
            if result.get("success"):
                if agent_name == "DATA_AGENT":
                    answers.append(result.get("result", "No result"))

                elif agent_name == "RAG_AGENT":
                    answers.append(result.get("answer", "No answer found"))

                elif agent_name == "RESEARCH_AGENT":
                    answers.append(result.get("findings", "No findings"))

            else:
                error_msg = result.get("error", "Unknown error")
                answers.append(f"({agent_name}: {error_msg})")

        return "\n\n".join(answers) if answers else "Unable to process question"

    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get conversation history."""
        return self.conversation_history

    def clear_history(self) -> None:
        """Clear conversation history."""
        self.conversation_history = []
