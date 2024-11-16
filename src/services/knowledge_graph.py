"""Knowledge graph implementation for managing relationships between articles"""
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
import json
import networkx as nx
from datetime import datetime

class KnowledgeGraph:
    """Manages relationships between knowledge base articles using a graph structure"""
    
    def __init__(self, config):
        """Initialize knowledge graph
        
        Args:
            config: KBConfig instance
        """
        self.config = config
        self.graph_file = config.graph_dir / "knowledge_graph.json"
        self.graph = nx.DiGraph()  # Directed graph for relationships
        self.config.graph_dir.mkdir(parents=True, exist_ok=True)
        self._load_graph()
        
    def add_relationship(self, source_id: str, target_id: str, relationship_type: str, metadata: Optional[Dict] = None):
        """Add a relationship between two articles
        
        Args:
            source_id: Source article ID
            target_id: Target article ID
            relationship_type: Type of relationship (must be in config.relationship_types)
            metadata: Optional relationship metadata
        """
        if relationship_type not in self.config.relationship_types:
            raise ValueError(f"Invalid relationship type: {relationship_type}")
            
        # Add nodes if they don't exist
        for node_id in [source_id, target_id]:
            if not self.graph.has_node(node_id):
                self.graph.add_node(node_id)
                
        # Add or update edge
        self.graph.add_edge(
            source_id,
            target_id,
            type=relationship_type,
            metadata=metadata or {},
            created_at=datetime.now().isoformat()
        )
        
        self._save_graph()
        
    def remove_relationship(self, source_id: str, target_id: str, relationship_type: Optional[str] = None) -> bool:
        """Remove a relationship between articles
        
        Args:
            source_id: Source article ID
            target_id: Target article ID
            relationship_type: Optional relationship type filter
            
        Returns:
            bool: True if relationship was removed
        """
        if not self.graph.has_edge(source_id, target_id):
            return False
            
        if relationship_type:
            edge_data = self.graph.get_edge_data(source_id, target_id)
            if edge_data["type"] != relationship_type:
                return False
                
        self.graph.remove_edge(source_id, target_id)
        self._save_graph()
        return True
        
    def get_relationships(self, article_id: str, relationship_type: Optional[str] = None) -> Dict[str, List[Dict]]:
        """Get all relationships for an article
        
        Args:
            article_id: Article ID
            relationship_type: Optional relationship type filter
            
        Returns:
            Dict with incoming and outgoing relationships
        """
        if not self.graph.has_node(article_id):
            return {"incoming": [], "outgoing": []}
            
        incoming = []
        outgoing = []
        
        # Get incoming relationships
        for source in self.graph.predecessors(article_id):
            edge_data = self.graph.get_edge_data(source, article_id)
            if not relationship_type or edge_data["type"] == relationship_type:
                incoming.append({
                    "article_id": source,
                    "type": edge_data["type"],
                    "metadata": edge_data["metadata"],
                    "created_at": edge_data["created_at"]
                })
                
        # Get outgoing relationships
        for target in self.graph.successors(article_id):
            edge_data = self.graph.get_edge_data(article_id, target)
            if not relationship_type or edge_data["type"] == relationship_type:
                outgoing.append({
                    "article_id": target,
                    "type": edge_data["type"],
                    "metadata": edge_data["metadata"],
                    "created_at": edge_data["created_at"]
                })
                
        return {
            "incoming": sorted(incoming, key=lambda x: x["created_at"], reverse=True),
            "outgoing": sorted(outgoing, key=lambda x: x["created_at"], reverse=True)
        }
        
    def find_path(self, source_id: str, target_id: str) -> Optional[List[Tuple[str, str]]]:
        """Find the shortest path between two articles
        
        Args:
            source_id: Source article ID
            target_id: Target article ID
            
        Returns:
            Optional[List[Tuple[str, str]]]: List of (node_id, relationship_type) pairs if path exists
        """
        try:
            path = nx.shortest_path(self.graph, source_id, target_id)
            result = []
            for i in range(len(path) - 1):
                edge_data = self.graph.get_edge_data(path[i], path[i + 1])
                result.append((path[i + 1], edge_data["type"]))
            return result
        except nx.NetworkXNoPath:
            return None
            
    def get_related_articles(self, article_id: str, max_depth: int = 2) -> List[Dict]:
        """Get related articles within specified graph distance
        
        Args:
            article_id: Article ID
            max_depth: Maximum path length to consider
            
        Returns:
            List[Dict]: Related articles with relationship information
        """
        if not self.graph.has_node(article_id):
            return []
            
        related = []
        for node in nx.single_source_shortest_path_length(self.graph, article_id, cutoff=max_depth):
            if node != article_id:
                path = self.find_path(article_id, node)
                if path:
                    related.append({
                        "article_id": node,
                        "distance": len(path),
                        "path": path
                    })
                    
        return sorted(related, key=lambda x: x["distance"])
        
    def get_central_articles(self, limit: int = 10) -> List[Dict]:
        """Get most central articles based on graph metrics
        
        Args:
            limit: Maximum number of articles to return
            
        Returns:
            List[Dict]: Central articles with metrics
        """
        if not self.graph.nodes():
            return []
            
        # Calculate centrality metrics
        degree_centrality = nx.degree_centrality(self.graph)
        betweenness_centrality = nx.betweenness_centrality(self.graph)
        
        # Combine metrics
        centrality_scores = {}
        for node in self.graph.nodes():
            centrality_scores[node] = {
                "article_id": node,
                "degree_centrality": degree_centrality[node],
                "betweenness_centrality": betweenness_centrality[node],
                "combined_score": degree_centrality[node] + betweenness_centrality[node]
            }
            
        # Sort by combined score
        sorted_articles = sorted(
            centrality_scores.values(),
            key=lambda x: x["combined_score"],
            reverse=True
        )
        
        return sorted_articles[:limit]
        
    def _load_graph(self):
        """Load graph from disk"""
        if self.graph_file.exists():
            try:
                with open(self.graph_file, 'r', encoding='utf-8') as f:
                    graph_data = json.load(f)
                    
                # Reconstruct graph
                self.graph = nx.node_link_graph(graph_data)
            except Exception as e:
                print(f"Error loading graph: {str(e)}")
                self.graph = nx.DiGraph()
                
    def _save_graph(self):
        """Save graph to disk"""
        try:
            # Convert graph to serializable format
            graph_data = nx.node_link_data(self.graph)
            
            with open(self.graph_file, 'w', encoding='utf-8') as f:
                json.dump(graph_data, f, indent=2)
        except Exception as e:
            print(f"Error saving graph: {str(e)}")
            
    def analyze_graph(self) -> Dict:
        """Analyze graph structure and return metrics
        
        Returns:
            Dict: Graph metrics and statistics
        """
        if not self.graph.nodes():
            return {
                "nodes": 0,
                "edges": 0,
                "density": 0,
                "average_degree": 0
            }
            
        return {
            "nodes": self.graph.number_of_nodes(),
            "edges": self.graph.number_of_edges(),
            "density": nx.density(self.graph),
            "average_degree": sum(dict(self.graph.degree()).values()) / self.graph.number_of_nodes(),
            "relationship_types": self._count_relationship_types()
        }
        
    def _count_relationship_types(self) -> Dict[str, int]:
        """Count occurrences of each relationship type"""
        counts = {}
        for _, _, edge_data in self.graph.edges(data=True):
            rel_type = edge_data["type"]
            counts[rel_type] = counts.get(rel_type, 0) + 1
        return counts
