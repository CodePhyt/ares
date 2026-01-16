"""
Agentic Reasoning Layer with PLAN/SEARCH/AUDIT capabilities.
Uses LangGraph patterns for structured reasoning workflows.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from loguru import logger

from src.core.rag_engine import HybridRAGEngine, DocumentChunk
from src.security.pii_masker import GermanPIIMasker


class AgentState(BaseModel):
    """State for the reasoning agent."""
    query: str
    plan: Optional[str] = None
    search_results: List[DocumentChunk] = Field(default_factory=list)
    context: str = ""
    answer: str = ""
    citations: List[Dict[str, Any]] = Field(default_factory=list)
    confidence: float = 0.0
    requires_search: bool = True
    iteration: int = 0
    max_iterations: int = 5


class ReasoningAgent:
    """
    Enterprise-grade reasoning agent with PLAN/SEARCH/AUDIT workflow.
    Ensures accurate, fact-checked responses with source citations.
    """

    def __init__(
        self,
        rag_engine: HybridRAGEngine,
        pii_masker: GermanPIIMasker,
        ollama_base_url: str = "http://localhost:11434",
        model: str = "llama3:8b",
        temperature: float = 0.1,
        max_iterations: int = 5,
    ):
        """
        Initialize the reasoning agent.

        Args:
            rag_engine: Hybrid RAG engine instance
            pii_masker: PII masker instance
            ollama_base_url: Base URL for Ollama
            model: LLM model name
            temperature: Temperature for LLM generation
            max_iterations: Maximum reasoning iterations
        """
        self.rag_engine = rag_engine
        self.pii_masker = pii_masker
        self.ollama_base_url = ollama_base_url
        self.model = model
        self.temperature = temperature
        self.max_iterations = max_iterations

        logger.info("Reasoning Agent initialized with model: {}", model)

    def _build_agent_graph(self):
        """Build the workflow for PLAN -> SEARCH -> AUDIT."""
        # Simplified workflow - execute nodes sequentially
        # LangGraph can be added later if needed for complex workflows
        return None

    def _plan_node(self, state: AgentState) -> AgentState:
        """
        PLAN: Decide if query needs document search or can be answered directly.
        """
        logger.info("Planning for query: {}", state.query[:50])

        planning_prompt = f"""Du bist ein intelligenter Assistent. Analysiere die folgende Frage und entscheide:

1. Benötigt diese Frage eine Suche in Dokumenten? (Antworte mit 'JA' oder 'NEIN')
2. Wenn JA, welche Schlüsselwörter sind wichtig für die Suche?
3. Wenn NEIN, kannst du die Frage direkt beantworten?

Frage: {state.query}

Antworte im Format:
SUCHE: JA/NEIN
SCHLÜSSELWÖRTER: [wenn SUCHE=JA, liste wichtige Begriffe]
DIREKTE_ANTWORT: [wenn SUCHE=NEIN, gib eine kurze Antwort]"""

        try:
            import httpx
            with httpx.Client(timeout=120.0) as client:
                response = client.post(
                    f"{self.ollama_base_url}/api/chat",
                    json={
                        "model": self.model,
                        "messages": [
                            {
                                "role": "system",
                                "content": "Du bist ein präziser Planungsassistent für Dokumentensuche.",
                            },
                            {"role": "user", "content": planning_prompt},
                        ],
                        "options": {"temperature": self.temperature},
                    },
                )
                response.raise_for_status()
                result = response.json()

                plan_text = result["message"]["content"]
            state.plan = plan_text

            # Determine if search is needed
            state.requires_search = "SUCHE: JA" in plan_text.upper() or "JA" in plan_text.upper()[:20]

            logger.info("Plan completed. Requires search: {}", state.requires_search)

        except Exception as e:
            logger.error("Error in planning: {}", e)
            state.requires_search = True  # Default to search on error

        return state

    def _search_node(self, state: AgentState) -> AgentState:
        """
        SEARCH: Execute hybrid RAG search if needed.
        """
        if not state.requires_search:
            logger.info("Skipping search - direct answer possible")
            return state

        logger.info("Searching for: {}", state.query)

        try:
            # Perform hybrid search
            results = self.rag_engine.hybrid_search(
                query=state.query,
                top_k=5,
                top_k_parents=3,
                rerank_top_k=3,
            )

            state.search_results = results

            # Build context from results
            context_parts = []
            citations = []

            for i, chunk in enumerate(results):
                context_parts.append(f"[{i+1}] {chunk.content}")
                citations.append({
                    "chunk_id": chunk.id,
                    "filename": chunk.metadata.get("filename", "Unknown"),
                    "page": chunk.metadata.get("page", "N/A"),
                    "score": chunk.score,
                })

            state.context = "\n\n".join(context_parts)
            state.citations = citations

            logger.info("Found {} relevant chunks", len(results))

        except Exception as e:
            logger.error("Error in search: {}", e)
            state.search_results = []

        return state

    def _generate_node(self, state: AgentState) -> AgentState:
        """
        GENERATE: Create answer from context or direct knowledge.
        """
        logger.info("Generating answer")

        if state.requires_search and state.context:
            # RAG-based answer
            prompt = f"""Basierend auf den folgenden Dokumenten, beantworte die Frage präzise und genau.
Zitiere die relevanten Abschnitte mit [1], [2], etc.

Dokumente:
{state.context}

Frage: {state.query}

Antwort:"""

        else:
            # Direct answer
            prompt = f"""Beantworte die folgende Frage präzise:

Frage: {state.query}

Antwort:"""

        try:
            import httpx
            with httpx.Client(timeout=120.0) as client:
                response = client.post(
                    f"{self.ollama_base_url}/api/chat",
                    json={
                        "model": self.model,
                        "messages": [
                            {
                                "role": "system",
                                "content": "Du bist ein präziser, faktenbasierter Assistent. Antworte nur mit verifizierten Informationen.",
                            },
                            {"role": "user", "content": prompt},
                        ],
                        "options": {"temperature": self.temperature},
                        "stream": False,
                    },
                )
                response.raise_for_status()
                result = response.json()
                state.answer = result["message"]["content"]
            logger.info("Answer generated (length: {})", len(state.answer))

        except Exception as e:
            logger.error("Error generating answer: {}", e)
            state.answer = "Entschuldigung, ich konnte keine Antwort generieren."

        return state

    def _audit_node(self, state: AgentState) -> AgentState:
        """
        AUDIT: Fact-check the answer against retrieved context.
        """
        logger.info("Auditing answer")

        if not state.requires_search or not state.context:
            # No context to audit against
            state.confidence = 0.8  # Default confidence for direct answers
            return state

        audit_prompt = f"""Überprüfe, ob die folgende Antwort mit den bereitgestellten Dokumenten übereinstimmt.
Bewerte die Übereinstimmung auf einer Skala von 0.0 bis 1.0.

Dokumente:
{state.context}

Antwort:
{state.answer}

Bewertung (nur Zahl zwischen 0.0 und 1.0):"""

        try:
            import httpx
            with httpx.Client(timeout=120.0) as client:
                response = client.post(
                    f"{self.ollama_base_url}/api/chat",
                    json={
                        "model": self.model,
                        "messages": [
                            {
                                "role": "system",
                                "content": "Du bist ein präziser Faktenprüfer. Antworte nur mit einer Zahl zwischen 0.0 und 1.0.",
                            },
                            {"role": "user", "content": audit_prompt},
                        ],
                        "options": {"temperature": 0.0},  # Deterministic for auditing
                    },
                )
                response.raise_for_status()
                result = response.json()
                
                # Extract confidence score
                score_text = result["message"]["content"].strip()
            try:
                # Try to extract number from response
                import re
                numbers = re.findall(r"0?\.\d+|\d+\.\d+", score_text)
                if numbers:
                    state.confidence = float(numbers[0])
                else:
                    state.confidence = 0.5  # Default if parsing fails
            except Exception:
                state.confidence = 0.5

            logger.info("Audit completed. Confidence: {:.2f}", state.confidence)

        except Exception as e:
            logger.error("Error in audit: {}", e)
            state.confidence = 0.5  # Default on error

        return state


    async def query(
        self,
        query: str,
        mask_pii: bool = True,
    ) -> Dict[str, Any]:
        """
        Execute the full reasoning workflow.

        Args:
            query: User query
            mask_pii: Whether to mask PII before processing

        Returns:
            Complete response with answer, citations, and metadata
        """
        logger.info("Processing query: {}", query[:50])

        # Mask PII if enabled
        original_query = query
        mask_result = {}
        if mask_pii:
            mask_result = self.pii_masker.mask_text(query)
            query = mask_result["masked_text"]
            if mask_result["masked"]:
                logger.info("PII masked: {} entities", mask_result["pii_count"])

        # Initialize state
        state = AgentState(
            query=query,
            max_iterations=self.max_iterations,
        )

        # Run the workflow: PLAN -> SEARCH -> GENERATE -> AUDIT
        try:
            # PLAN
            state = self._plan_node(state)
            
            # SEARCH
            state = self._search_node(state)
            
            # GENERATE
            state = self._generate_node(state)
            
            # AUDIT
            state = self._audit_node(state)
            
            # Iterate if confidence is low
            while state.confidence < 0.7 and state.iteration < self.max_iterations:
                state.iteration += 1
                logger.info("Low confidence ({:.2f}), iterating...", state.confidence)
                state = self._search_node(state)
                state = self._generate_node(state)
                state = self._audit_node(state)

            # Build response
            response = {
                "answer": state.answer,
                "citations": state.citations,
                "confidence": state.confidence,
                "context_used": state.context[:500] if state.context else "",
                "iterations": state.iteration,
                "pii_masked": mask_pii and mask_result.get("masked", False),
                "pii_count": mask_result.get("pii_count", 0) if mask_pii else 0,
            }

            logger.info(
                "Query completed. Confidence: {:.2f}, Citations: {}",
                state.confidence,
                len(state.citations),
            )

            return response

        except Exception as e:
            logger.error("Error in agent query: {}", e)
            return {
                "answer": "Entschuldigung, ein Fehler ist aufgetreten.",
                "citations": [],
                "confidence": 0.0,
                "error": str(e),
            }
