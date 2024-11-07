import json
from typing import Dict, List, Optional
from pathlib import Path

class KnowledgeBase:
    def __init__(self, json_path: str = "knowledge_base.json"):
        self.json_path = json_path
        self.data = self._load_knowledge_base()
        
    def _load_knowledge_base(self) -> Dict:
        """Load the knowledge base from JSON file"""
        try:
            with open(self.json_path, 'r', encoding='utf-8') as file:
                return json.load(file)
        except Exception as e:
            print(f"[ERROR] Failed to load knowledge base: {str(e)}")
            return {}
            
    def search(self, query: str, category: Optional[str] = None) -> List[Dict]:
        """
        Search the knowledge base for relevant information
        
        Args:
            query (str): Search query
            category (str, optional): Specific category to search in ('documentation', 'faqs', 'project_info')
            
        Returns:
            List[Dict]: List of relevant information chunks
        """
        results = []
        query_terms = set(query.lower().split())
        
        def _check_relevance(text: str) -> bool:
            """Check if text is relevant to query"""
            return any(term in text.lower() for term in query_terms)
        
        # Search project info
        if not category or category == 'project_info':
            project_info = self.data.get('project_info', {})
            if any(_check_relevance(str(v)) for v in project_info.values()):
                results.append({
                    'type': 'project_info',
                    'content': project_info
                })
        
        # Search documentation
        if not category or category == 'documentation':
            for doc_id, doc in self.data.get('documentation', {}).items():
                if _check_relevance(doc['content']) or _check_relevance(doc['title']):
                    results.append({
                        'type': 'documentation',
                        'id': doc_id,
                        'content': doc
                    })
        
        # Search FAQs
        if not category or category == 'faqs':
            for faq_category, faqs in self.data.get('faqs', {}).items():
                for faq in faqs:
                    if _check_relevance(faq['question']) or _check_relevance(faq['answer']):
                        results.append({
                            'type': 'faq',
                            'category': faq_category,
                            'content': faq
                        })
        
        return results
    
    def get_category_content(self, category: str) -> Dict:
        """Get all content for a specific category"""
        return self.data.get(category, {})
    
    def format_response(self, results: List[Dict]) -> str:
        """Format search results into a readable response"""
        if not results:
            return "I couldn't find any relevant information in my knowledge base."
        
        response = []
        
        for result in results:
            if result['type'] == 'project_info':
                response.append("Project Information:")
                for key, value in result['content'].items():
                    response.append(f"- {key}: {value}")
                    
            elif result['type'] == 'documentation':
                doc = result['content']
                response.append(f"\nFrom {doc['title']}:")
                response.append(doc['content'])
                
            elif result['type'] == 'faq':
                faq = result['content']
                response.append(f"\nFAQ ({result['category']}):")
                response.append(f"Q: {faq['question']}")
                response.append(f"A: {faq['answer']}")
                
        return "\n".join(response) 