"""Advanced search features including faceted search, topic modeling, and auto-tagging"""
from typing import List, Dict, Any, Optional, Set, Tuple
from pathlib import Path
import logging
from dataclasses import dataclass
from collections import Counter
from datetime import datetime

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation, NMF
from sklearn.cluster import KMeans
from gensim.models import KeyBERT
from gensim.summarization import keywords
import spacy
from langchain_openai import ChatOpenAI

from .document_processor import ProcessedDocument
from .search_engine import SearchResult
from .kb_config import KBConfig

@dataclass
class SearchFacets:
    """Container for search facets"""
    doc_types: Dict[str, int]
    topics: Dict[str, int]
    authors: Dict[str, int]
    date_ranges: Dict[str, int]
    tags: Dict[str, int]

@dataclass
class TopicModel:
    """Container for topic modeling results"""
    topics: List[List[str]]
    doc_topic_dist: np.ndarray
    topic_term_dist: np.ndarray
    feature_names: List[str]

class AdvancedSearch:
    """Advanced search features with topic modeling and auto-tagging"""
    
    def __init__(self, config: KBConfig):
        self.config = config
        self.llm = ChatOpenAI(temperature=0)
        self.nlp = spacy.load("en_core_web_sm")
        self.keyword_model = KeyBERT()
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        
    def extract_facets(self, documents: List[ProcessedDocument]) -> SearchFacets:
        """Extract search facets from documents
        
        Args:
            documents: List of processed documents
            
        Returns:
            SearchFacets object containing facet information
        """
        doc_types = Counter()
        topics = Counter()
        authors = Counter()
        tags = Counter()
        date_ranges = Counter()
        
        for doc in documents:
            # Document types
            doc_types[doc.doc_type] += 1
            
            # Extract topics from metadata
            if "topics" in doc.metadata:
                for topic in doc.metadata["topics"]:
                    topics[topic] += 1
                    
            # Authors
            if "author" in doc.metadata:
                authors[doc.metadata["author"]] += 1
                
            # Tags
            if "tags" in doc.metadata:
                for tag in doc.metadata["tags"]:
                    tags[tag] += 1
                    
            # Date ranges
            if "created_at" in doc.metadata:
                date = datetime.fromisoformat(doc.metadata["created_at"])
                date_range = f"{date.year}-{date.month:02d}"
                date_ranges[date_range] += 1
                
        return SearchFacets(
            doc_types=dict(doc_types),
            topics=dict(topics),
            authors=dict(authors),
            date_ranges=dict(date_ranges),
            tags=dict(tags)
        )
        
    def apply_faceted_filters(
        self,
        documents: List[SearchResult],
        filters: Dict[str, Set[str]]
    ) -> List[SearchResult]:
        """Apply faceted filters to search results
        
        Args:
            documents: List of search results
            filters: Dictionary of facet filters
            
        Returns:
            Filtered list of search results
        """
        filtered_docs = []
        
        for doc in documents:
            matches_all = True
            
            for facet, values in filters.items():
                if facet == "doc_type" and doc.metadata.get("doc_type") not in values:
                    matches_all = False
                    break
                elif facet == "topics" and not any(t in values for t in doc.metadata.get("topics", [])):
                    matches_all = False
                    break
                elif facet == "author" and doc.metadata.get("author") not in values:
                    matches_all = False
                    break
                elif facet == "tags" and not any(t in values for t in doc.metadata.get("tags", [])):
                    matches_all = False
                    break
                elif facet == "date_range":
                    doc_date = datetime.fromisoformat(doc.metadata.get("created_at", ""))
                    doc_range = f"{doc_date.year}-{doc_date.month:02d}"
                    if doc_range not in values:
                        matches_all = False
                        break
                        
            if matches_all:
                filtered_docs.append(doc)
                
        return filtered_docs
        
    def extract_topics(self, documents: List[ProcessedDocument], num_topics: int = 5, method: str = 'lda') -> TopicModel:
        """Extract topics from a collection of documents using either LDA or NMF.
        
        Args:
            documents: List of processed documents
            num_topics: Number of topics to extract
            method: Topic modeling method ('lda' or 'nmf')
            
        Returns:
            TopicModel containing topics and distributions
        """
        # Prepare document texts
        texts = [doc.content for doc in documents]
        
        # Create document-term matrix
        dtm = self.vectorizer.fit_transform(texts)
        feature_names = self.vectorizer.get_feature_names_out()
        
        # Choose topic modeling method
        if method == 'lda':
            model = LatentDirichletAllocation(
                n_components=num_topics,
                max_iter=10,
                learning_method='online',
                random_state=42
            )
        else:
            model = NMF(
                n_components=num_topics,
                random_state=42,
                max_iter=1000
            )
            
        # Fit model and transform documents
        doc_topic_dist = model.fit_transform(dtm)
        topic_term_dist = model.components_
        
        # Extract top terms for each topic
        n_top_words = 10
        topics = []
        for topic_idx, topic in enumerate(topic_term_dist):
            top_terms_idx = topic.argsort()[:-n_top_words-1:-1]
            top_terms = [feature_names[i] for i in top_terms_idx]
            topics.append(top_terms)
            
        return TopicModel(
            topics=topics,
            doc_topic_dist=doc_topic_dist,
            topic_term_dist=topic_term_dist,
            feature_names=feature_names.tolist()
        )
        
    def cluster_documents(self, documents: List[ProcessedDocument], n_clusters: int = 5) -> Dict[int, List[ProcessedDocument]]:
        """Cluster documents using K-means clustering.
        
        Args:
            documents: List of processed documents
            n_clusters: Number of clusters
            
        Returns:
            Dictionary mapping cluster IDs to lists of documents
        """
        # Prepare document texts
        texts = [doc.content for doc in documents]
        
        # Create document vectors
        vectors = self.vectorizer.fit_transform(texts)
        
        # Perform clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        cluster_labels = kmeans.fit_predict(vectors)
        
        # Group documents by cluster
        clusters: Dict[int, List[ProcessedDocument]] = {}
        for doc, label in zip(documents, cluster_labels):
            if label not in clusters:
                clusters[label] = []
            clusters[label].append(doc)
            
        return clusters
        
    def auto_tag_document(self, document: ProcessedDocument) -> Set[str]:
        """Automatically generate tags for a document using multiple methods.
        
        Args:
            document: ProcessedDocument to tag
            
        Returns:
            Set of generated tags
        """
        tags = set()
        
        # Method 1: KeyBERT for keyword extraction
        keywords = self.keyword_model.extract_keywords(
            document.content,
            keyphrase_ngram_range=(1, 2),
            stop_words='english',
            use_maxsum=True,
            nr_candidates=20,
            top_n=5
        )
        tags.update(kw[0] for kw in keywords)
        
        # Method 2: spaCy for named entity recognition
        doc = self.nlp(document.content)
        for ent in doc.ents:
            if ent.label_ in {'ORG', 'PERSON', 'GPE', 'PRODUCT', 'EVENT'}:
                tags.add(f"{ent.label_.lower()}:{ent.text}")
                
        # Method 3: Use LLM for high-level topic identification
        prompt = f"""
        Given the following document content, identify 3-5 relevant topic tags.
        Keep tags concise (1-3 words) and relevant to the main themes.
        
        Document:
        {document.content[:500]}...
        
        Tags:
        """
        
        response = self.llm.invoke(prompt)
        ai_tags = [tag.strip() for tag in response.content.split('\n') if tag.strip()]
        tags.update(ai_tags)
        
        return tags
        
    def get_search_facets(self, documents: List[ProcessedDocument]) -> SearchFacets:
        """Generate search facets from a collection of documents.
        
        Args:
            documents: List of processed documents
            
        Returns:
            SearchFacets containing various facet categories and counts
        """
        doc_types = Counter()
        authors = Counter()
        tags = Counter()
        date_ranges = Counter()
        
        for doc in documents:
            # Document type facets
            doc_types[doc.doc_type] += 1
            
            # Author facets
            if doc.metadata.get('author'):
                authors[doc.metadata['author']] += 1
                
            # Tag facets
            if doc.metadata.get('tags'):
                for tag in doc.metadata['tags']:
                    tags[tag] += 1
                    
            # Date range facets
            if doc.metadata.get('created_date'):
                date = datetime.fromisoformat(doc.metadata['created_date'])
                month_year = date.strftime('%Y-%m')
                date_ranges[month_year] += 1
                
        # Extract topics
        topic_model = self.extract_topics(documents, num_topics=5)
        topics = {f"Topic {i+1}: {', '.join(terms[:3])}": 0 
                 for i, terms in enumerate(topic_model.topics)}
                 
        # Count documents per topic
        doc_topics = topic_model.doc_topic_dist.argmax(axis=1)
        for topic_idx in doc_topics:
            topic_name = f"Topic {topic_idx+1}: {', '.join(topic_model.topics[topic_idx][:3])}"
            topics[topic_name] += 1
        
        return SearchFacets(
            doc_types=dict(doc_types),
            topics=dict(topics),
            authors=dict(authors),
            date_ranges=dict(date_ranges),
            tags=dict(tags)
        )
        
    def create_topic_model(
        self,
        documents: List[ProcessedDocument],
        n_topics: int = 10,
        n_words: int = 10,
        method: str = "lda"
    ) -> TopicModel:
        """Create topic model from documents
        
        Args:
            documents: List of processed documents
            n_topics: Number of topics to extract
            n_words: Number of words per topic
            method: Topic modeling method ('lda' or 'nmf')
            
        Returns:
            TopicModel object containing topics and distributions
        """
        # Prepare document texts
        texts = []
        for doc in documents:
            text = " ".join(doc.chunks)
            texts.append(text)
            
        # Create document-term matrix
        dtm = self.vectorizer.fit_transform(texts)
        feature_names = self.vectorizer.get_feature_names_out()
        
        # Create topic model
        if method == "lda":
            model = LatentDirichletAllocation(
                n_components=n_topics,
                random_state=42
            )
        else:
            model = NMF(
                n_components=n_topics,
                random_state=42
            )
            
        # Fit model and get topic-term distribution
        doc_topic_dist = model.fit_transform(dtm)
        topic_term_dist = model.components_
        
        # Extract top words for each topic
        topics = []
        for topic_idx in range(n_topics):
            top_words_idx = topic_term_dist[topic_idx].argsort()[:-n_words-1:-1]
            top_words = [feature_names[i] for i in top_words_idx]
            topics.append(top_words)
            
        return TopicModel(
            topics=topics,
            doc_topic_dist=doc_topic_dist,
            topic_term_dist=topic_term_dist,
            feature_names=feature_names.tolist()
        )
        
    def auto_tag_document(
        self,
        document: ProcessedDocument,
        n_tags: int = 5
    ) -> List[str]:
        """Automatically generate tags for a document
        
        Args:
            document: Document to tag
            n_tags: Number of tags to generate
            
        Returns:
            List of generated tags
        """
        # Combine document chunks
        text = " ".join(document.chunks)
        
        # Extract keywords using multiple methods
        tags = set()
        
        # Method 1: KeyBERT
        keybert_keywords = self.keyword_model.extract_keywords(
            text,
            keyphrase_ngram_range=(1, 2),
            stop_words='english',
            top_n=n_tags
        )
        tags.update(kw[0] for kw in keybert_keywords)
        
        # Method 2: TextRank
        textrank_keywords = keywords.keywords(text, ratio=0.1).split('\n')
        tags.update(textrank_keywords[:n_tags])
        
        # Method 3: Named Entity Recognition
        doc = self.nlp(text[:10000])  # Limit text length for processing
        entities = set()
        for ent in doc.ents:
            if ent.label_ in ["ORG", "PRODUCT", "GPE", "PERSON", "WORK_OF_ART"]:
                entities.add(ent.text)
        tags.update(list(entities)[:n_tags])
        
        # Method 4: LLM-based tagging
        try:
            prompt = f"""Generate {n_tags} relevant tags for the following text. 
            Return only the tags, separated by commas:
            
            {text[:2000]}"""
            
            response = self.llm.invoke(prompt)
            llm_tags = [
                tag.strip()
                for tag in response.content.split(',')
                if tag.strip()
            ]
            tags.update(llm_tags)
        except Exception as e:
            logging.warning(f"Error generating LLM tags: {str(e)}")
            
        return list(tags)[:n_tags]
        
    def cluster_documents(
        self,
        documents: List[ProcessedDocument],
        n_clusters: int = 5
    ) -> Dict[str, List[str]]:
        """Cluster documents based on content similarity
        
        Args:
            documents: List of documents to cluster
            n_clusters: Number of clusters
            
        Returns:
            Dictionary mapping cluster IDs to document IDs
        """
        # Prepare document texts
        texts = []
        doc_ids = []
        for doc in documents:
            text = " ".join(doc.chunks)
            texts.append(text)
            doc_ids.append(doc.source_id)
            
        # Create document vectors
        vectors = self.vectorizer.fit_transform(texts)
        
        # Perform clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        clusters = kmeans.fit_predict(vectors)
        
        # Group documents by cluster
        cluster_docs = {}
        for i, cluster_id in enumerate(clusters):
            cluster_key = f"cluster_{cluster_id}"
            if cluster_key not in cluster_docs:
                cluster_docs[cluster_key] = []
            cluster_docs[cluster_key].append(doc_ids[i])
            
        return cluster_docs
        
    def optimize_search_ranking(
        self,
        query: str,
        results: List[SearchResult],
        user_context: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """Optimize search result ranking based on multiple factors
        
        Args:
            query: Search query
            results: Initial search results
            user_context: Optional user context for personalization
            
        Returns:
            Re-ranked search results
        """
        for result in results:
            score = result.relevance_score
            
            # Boost based on metadata quality
            metadata_score = len(result.metadata) / 10  # Normalize by expected fields
            score += metadata_score * 0.1
            
            # Boost based on recency
            if "created_at" in result.metadata:
                created_at = datetime.fromisoformat(result.metadata["created_at"])
                days_old = (datetime.now() - created_at).days
                recency_score = 1.0 / (1.0 + np.log1p(days_old))
                score += recency_score * 0.1
                
            # Boost based on document type preferences
            if user_context and "preferred_types" in user_context:
                if result.metadata.get("doc_type") in user_context["preferred_types"]:
                    score += 0.1
                    
            # Update relevance score
            result.relevance_score = score
            
        # Re-sort results
        results.sort(key=lambda x: x.relevance_score, reverse=True)
        
        return results
