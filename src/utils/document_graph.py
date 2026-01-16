"""
Document relationship graph visualization.
Shows how documents are linked by keywords and topics.
"""

from typing import List, Dict, Any, Set, Tuple
from collections import defaultdict
import networkx as nx
from loguru import logger


class DocumentGraphBuilder:
    """Build relationship graphs between documents."""

    def __init__(self):
        """Initialize graph builder."""
        self.graph = nx.Graph()

    def build_relationship_graph(
        self,
        documents: List[Dict[str, Any]],
        similarity_threshold: float = 0.3,
    ) -> Dict[str, Any]:
        """
        Build relationship graph from documents.

        Args:
            documents: List of document metadata with chunks
            similarity_threshold: Minimum similarity to create edge

        Returns:
            Graph data for visualization
        """
        try:
            self.graph.clear()

            # Extract keywords from documents
            doc_keywords = {}
            for doc in documents:
                doc_id = doc.get("document_id", "unknown")
                filename = doc.get("filename", "Unknown")
                
                # Extract keywords from chunks (simplified)
                keywords = self._extract_keywords(doc)
                doc_keywords[doc_id] = {
                    "filename": filename,
                    "keywords": keywords,
                }
                
                # Add node
                self.graph.add_node(doc_id, label=filename, keywords=keywords)

            # Create edges based on keyword overlap
            doc_ids = list(doc_keywords.keys())
            for i, doc1_id in enumerate(doc_ids):
                for doc2_id in doc_ids[i + 1:]:
                    similarity = self._calculate_similarity(
                        doc_keywords[doc1_id]["keywords"],
                        doc_keywords[doc2_id]["keywords"],
                    )
                    
                    if similarity >= similarity_threshold:
                        self.graph.add_edge(
                            doc1_id,
                            doc2_id,
                            weight=similarity,
                            label=f"{similarity:.2f}",
                        )

            # Prepare graph data
            nodes = []
            edges = []

            for node_id, data in self.graph.nodes(data=True):
                nodes.append({
                    "id": node_id,
                    "label": data.get("label", node_id),
                    "keywords": data.get("keywords", []),
                    "group": self._get_node_group(node_id),
                })

            for source, target, data in self.graph.edges(data=True):
                edges.append({
                    "from": source,
                    "to": target,
                    "value": data.get("weight", 0.5),
                    "label": data.get("label", ""),
                })

            return {
                "nodes": nodes,
                "edges": edges,
                "stats": {
                    "total_nodes": len(nodes),
                    "total_edges": len(edges),
                    "density": nx.density(self.graph),
                },
            }

        except Exception as e:
            logger.error("Error building document graph: {}", e)
            return {"nodes": [], "edges": [], "stats": {}}

    def _extract_keywords(self, document: Dict[str, Any]) -> Set[str]:
        """Extract keywords from document (simplified)."""
        keywords = set()
        
        # Extract from filename
        filename = document.get("filename", "").lower()
        keywords.update(filename.split(".")[0].split("_"))
        
        # Extract from metadata
        metadata = document.get("metadata", {})
        if "file_type" in metadata:
            keywords.add(metadata["file_type"])
        
        # Common document keywords (would be enhanced with actual text analysis)
        common_words = {"document", "report", "analysis", "data", "information"}
        keywords = keywords - common_words
        
        return keywords

    def _calculate_similarity(self, keywords1: Set[str], keywords2: Set[str]) -> float:
        """Calculate Jaccard similarity between keyword sets."""
        if not keywords1 or not keywords2:
            return 0.0
        
        intersection = len(keywords1 & keywords2)
        union = len(keywords1 | keywords2)
        
        return intersection / union if union > 0 else 0.0

    def _get_node_group(self, node_id: str) -> int:
        """Get node group for visualization."""
        # Simple grouping based on node ID hash
        return hash(node_id) % 5
