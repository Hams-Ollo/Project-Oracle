"""Visualization tools for document relationships and knowledge graphs"""
from typing import Dict, List, Any, Optional
from pathlib import Path
import json
import logging
from datetime import datetime

import networkx as nx
import plotly.graph_objects as go
import plotly.express as px
from pyvis.network import Network

from .search_engine import SearchResult
from .kb_config import KBConfig

class KnowledgeVisualizer:
    """Visualization tools for knowledge base insights"""
    
    def __init__(self, config: KBConfig):
        self.config = config
        self.graph = nx.Graph()
        
    def create_relationship_graph(
        self,
        relationships: Dict[str, List[str]],
        metadata: Dict[str, Dict[str, Any]],
        min_weight: float = 0.3
    ) -> Path:
        """Create an interactive visualization of document relationships
        
        Args:
            relationships: Dictionary mapping document IDs to related document IDs
            metadata: Document metadata for node information
            min_weight: Minimum relationship weight to include
            
        Returns:
            Path to the generated HTML visualization
        """
        # Create network
        net = Network(
            height="750px",
            width="100%",
            bgcolor="#ffffff",
            font_color="#000000"
        )
        
        # Add nodes
        for doc_id, related in relationships.items():
            doc_meta = metadata.get(doc_id, {})
            net.add_node(
                doc_id,
                label=doc_meta.get("title", doc_id),
                title=f"Type: {doc_meta.get('doc_type', 'unknown')}\n"
                      f"Created: {doc_meta.get('created_at', 'unknown')}"
            )
            
        # Add edges
        for source, targets in relationships.items():
            for target in targets:
                net.add_edge(source, target)
                
        # Generate the visualization
        output_path = self.config.visualization_dir / "document_relationships.html"
        net.save_graph(str(output_path))
        
        return output_path
        
    def create_topic_clusters(
        self,
        documents: List[SearchResult],
        n_clusters: int = 5
    ) -> Path:
        """Create a scatter plot visualization of document clusters
        
        Args:
            documents: List of search results with embeddings
            n_clusters: Number of topic clusters
            
        Returns:
            Path to the generated HTML visualization
        """
        # Create figure
        fig = go.Figure()
        
        # Add scatter plot
        fig.add_trace(
            go.Scatter(
                x=[doc.semantic_score for doc in documents],
                y=[doc.keyword_score for doc in documents],
                mode="markers+text",
                text=[doc.metadata.get("title", doc.document_id) for doc in documents],
                hovertemplate=(
                    "<b>%{text}</b><br>"
                    "Semantic Score: %{x:.2f}<br>"
                    "Keyword Score: %{y:.2f}<br>"
                    "<extra></extra>"
                )
            )
        )
        
        # Update layout
        fig.update_layout(
            title="Document Topic Clusters",
            xaxis_title="Semantic Similarity",
            yaxis_title="Keyword Relevance",
            showlegend=False
        )
        
        # Save visualization
        output_path = self.config.visualization_dir / "topic_clusters.html"
        fig.write_html(str(output_path))
        
        return output_path
        
    def create_temporal_view(
        self,
        documents: List[SearchResult]
    ) -> Path:
        """Create a timeline visualization of document creation/modification
        
        Args:
            documents: List of search results with temporal metadata
            
        Returns:
            Path to the generated HTML visualization
        """
        # Extract temporal data
        dates = []
        titles = []
        types = []
        
        for doc in documents:
            created_at = doc.metadata.get("created_at")
            if created_at:
                dates.append(created_at)
                titles.append(doc.metadata.get("title", doc.document_id))
                types.append(doc.metadata.get("doc_type", "unknown"))
                
        # Create figure
        fig = px.timeline(
            {
                "Date": dates,
                "Title": titles,
                "Type": types
            },
            x_start="Date",
            y="Title",
            color="Type",
            title="Document Timeline"
        )
        
        # Update layout
        fig.update_layout(
            showlegend=True,
            height=400 + (len(documents) * 20)
        )
        
        # Save visualization
        output_path = self.config.visualization_dir / "document_timeline.html"
        fig.write_html(str(output_path))
        
        return output_path
        
    def create_knowledge_map(
        self,
        search_results: List[SearchResult],
        central_doc_id: Optional[str] = None
    ) -> Path:
        """Create an interactive knowledge map visualization
        
        Args:
            search_results: List of search results to visualize
            central_doc_id: Optional ID of the central document
            
        Returns:
            Path to the generated HTML visualization
        """
        # Create network
        net = Network(
            height="750px",
            width="100%",
            bgcolor="#ffffff",
            font_color="#000000"
        )
        
        # Add nodes
        added_nodes = set()
        for result in search_results:
            if result.document_id not in added_nodes:
                net.add_node(
                    result.document_id,
                    label=result.metadata.get("title", result.document_id),
                    title=f"Type: {result.metadata.get('doc_type', 'unknown')}\n"
                          f"Relevance: {result.relevance_score:.2f}",
                    color="#ff0000" if result.document_id == central_doc_id else "#1f77b4"
                )
                added_nodes.add(result.document_id)
                
        # Add edges based on semantic similarity
        for i, doc1 in enumerate(search_results):
            for doc2 in search_results[i+1:]:
                if doc1.semantic_score > 0.5 or doc2.semantic_score > 0.5:
                    net.add_edge(
                        doc1.document_id,
                        doc2.document_id,
                        value=min(doc1.semantic_score, doc2.semantic_score)
                    )
                    
        # Generate the visualization
        output_path = self.config.visualization_dir / "knowledge_map.html"
        net.save_graph(str(output_path))
        
        return output_path
        
    def export_graph_data(self, path: Optional[Path] = None) -> Dict[str, Any]:
        """Export graph data for external visualization tools
        
        Args:
            path: Optional path to save the exported data
            
        Returns:
            Dictionary containing graph data
        """
        data = nx.node_link_data(self.graph)
        
        if path:
            with open(path, 'w') as f:
                json.dump(data, f, indent=2)
                
        return data
