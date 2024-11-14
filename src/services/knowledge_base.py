"""
Knowledge base service for information storage and retrieval.
"""

import json
from typing import List, Optional
from pathlib import Path
from langchain_core.tools import Tool

from src.config.settings import log_step
from src.services.vector_store import VectorStore

class KnowledgeBase:
    """
    Knowledge base management and querying system
    
    Handles loading, searching, and retrieving information using both direct and vector search
    """
    def __init__(self, json_path: str = "knowledge_base.json", vector_store_dir: str = "./vector_store"):
        """
        Initialize knowledge base and vector store
        
        Args:
            json_path (str): Path to knowledge base JSON file
            vector_store_dir (str): Directory for vector store
        """
        try:
            # Load JSON data
            with open(json_path, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
            
            # Initialize vector store
            self.vector_store = VectorStore(vector_store_dir)
            
            # Process documents for vector store
            self._initialize_vector_store()
            
            # Create traditional search mappings
            self._create_topic_mappings()
            
            log_step('success', f"Knowledge base loaded successfully with {len(self.data['topics'])} topics")
            log_step('info', f"Available topics: {list(self.data['topics'].keys())}")
            
        except Exception as e:
            log_step('error', f"Failed to load knowledge base: {e}")
            self.data = {"topics": {}, "articles": {}}
            self.topic_aliases = {}
            self.article_aliases = {}
            raise

    def _initialize_vector_store(self):
        """Initialize vector store with documents from JSON data"""
        try:
            # Convert JSON data to documents
            documents = self.vector_store.process_json_data(self.data)
            
            # Add documents to vector store
            self.vector_store.add_documents(documents)
            log_step('success', "Vector store initialized successfully")
        except Exception as e:
            log_step('error', f"Failed to initialize vector store: {e}")
            raise

    def _create_topic_mappings(self):
        """Create mappings for traditional search"""
        self.topic_aliases = {}
        for category in self.data["topics"]:
            for topic in self.data["topics"][category]:
                self.topic_aliases[topic.lower()] = (category, topic)

    def search(self, query: str, search_type: str = "hybrid", k: int = 3) -> str:
        """
        Search the knowledge base using specified search type
        
        Args:
            query: Search query
            search_type: Type of search ("vector", "traditional", or "hybrid")
            k: Number of results for vector search
            
        Returns:
            str: Formatted search results
        """
        try:
            if search_type == "vector":
                return self._vector_search(query, k)
            elif search_type == "traditional":
                return self._traditional_search(query)
            else:  # hybrid search
                vector_results = self._vector_search(query, k)
                traditional_results = self._traditional_search(query)
                return self._combine_search_results(vector_results, traditional_results)
        except Exception as e:
            log_step('error', f"Search failed: {e}")
            return f"Search failed: {str(e)}"

    def _vector_search(self, query: str, k: int = 3) -> str:
        """Perform vector similarity search"""
        try:
            docs = self.vector_store.similarity_search(query, k=k)
            if not docs:
                return "No relevant information found."
            
            results = []
            for doc in docs:
                results.append(doc.page_content)
            
            return "\n\n".join(results)
        except Exception as e:
            log_step('error', f"Vector search failed: {e}")
            return f"Vector search failed: {str(e)}"

    def _traditional_search(self, query: str) -> str:
        """Perform traditional keyword search"""
        query_lower = query.lower()
        
        # Direct topic match
        for alias, (category, topic) in self.topic_aliases.items():
            if alias in query_lower:
                topic_data = self.data["topics"][category][topic]
                return self._format_topic_data(topic, topic_data)
        
        return "No direct matches found in topics."

    def _combine_search_results(self, vector_results: str, traditional_results: str) -> str:
        """Combine results from both search methods"""
        if "No" in traditional_results and "No" in vector_results:
            return "No relevant information found in the knowledge base."
        
        results = []
        if "No" not in traditional_results:
            results.append("Direct Matches:\n" + traditional_results)
        if "No" not in vector_results:
            results.append("Related Information:\n" + vector_results)
        
        return "\n\n".join(results)

    def _format_topic_data(self, topic: str, data: dict) -> str:
        """Format topic data for output"""
        lines = [f"Information about {topic}:"]
        
        if "definition" in data:
            lines.append(f"\nDefinition: {data['definition']}")
        
        if "history" in data:
            lines.append(f"\nHistory: {data['history']}")
        
        if "key_concepts" in data:
            lines.append("\nKey Concepts:")
            lines.extend([f"- {concept}" for concept in data["key_concepts"]])
        
        if "important_figures" in data:
            lines.append("\nImportant Figures:")
            lines.extend([f"- {figure}" for figure in data["important_figures"]])
        
        if "cultural_significance" in data:
            lines.append(f"\nCultural Significance: {data['cultural_significance']}")
        
        return "\n".join(lines)

def create_knowledge_tools(kb) -> list[Tool]:
    """Creates the enhanced knowledge base tools"""
    return [
        Tool(
            name="search_topic",
            description="""Search for information using vector, traditional, or hybrid search.
            Format: 'query|search_type' (e.g., 'Jedi training|vector' or just 'Jedi training' for hybrid)""",
            func=lambda x: kb.search(*x.split('|')) if '|' in x else kb.search(x)
        ),
        Tool(
            name="list_topics",
            description="List all available topics in the knowledge base",
            func=lambda: f"Available topics: {list(kb.topic_aliases.keys())}"
        ),
        Tool(
            name="get_article",
            description="Get a specific article by its title",
            func=lambda x: kb.search(x, search_type="traditional")
        )
    ]

def update_knowledge_base_step1():
    """Update knowledge base with organizational structure data"""
    
    # Read existing knowledge base
    with open('knowledge_base.json', 'r') as f:
        kb_data = json.load(f)
    
    # Update organization topics
    kb_data['topics']['organization'].update({
        "company_overview": {
            "definition": "K Korp Inc. - A pioneer in enterprise AI solutions",
            "history": "Founded in 2018 by a team of AI researchers and enterprise software veterans...",
            # ... rest of company_overview data
        },
        "specialized_teams": {
            # ... specialized_teams data
        },
        "organizational_hierarchy": {
            # ... organizational_hierarchy data
        }
    })
    
    # Write updated knowledge base back to file
    with open('knowledge_base.json', 'w') as f:
        json.dump(kb_data, f, indent=4)

def update_knowledge_base_step2():
    """Update knowledge base with team profiles and role documentation"""
    
    # Read existing knowledge base
    with open('knowledge_base.json', 'r') as f:
        kb_data = json.load(f)
    
    # Add team profiles
    kb_data['articles']['team_profiles'] = {
        "ai_research_team": {
            "title": "AI Research & Development Team Profiles",
            "summary": "Current team members and their roles in AI R&D",
            "team_members": [
                {
                    "name": "Dr. Sarah Chen",
                    "role": "Team Lead & Principal Researcher",
                    "title": "Director of AI Research",
                    "experience": "15 years in AI/ML",
                    "expertise": [
                        "Deep Learning Architecture",
                        "Natural Language Processing",
                        "Neural Network Optimization"
                    ],
                    "education": {
                        "phd": "Machine Learning - Stanford University",
                        "masters": "Computer Science - MIT"
                    },
                    "publications": 25,
                    "patents": 8,
                    "projects_led": [
                        "Neural Framework Initiative",
                        "Adaptive Learning Systems",
                        "Project Oracle Architecture"
                    ]
                },
                {
                    "name": "Dr. Michael Park",
                    "role": "Senior AI Researcher",
                    "expertise": [
                        "Reinforcement Learning",
                        "Computer Vision",
                        "Model Optimization"
                    ],
                    "current_projects": [
                        "Self-optimizing Neural Networks",
                        "Computer Vision Enhancement Module"
                    ]
                },
                {
                    "name": "Lisa Rodriguez",
                    "role": "ML Operations Lead",
                    "expertise": [
                        "MLOps",
                        "Pipeline Automation",
                        "Cloud Infrastructure"
                    ],
                    "current_projects": [
                        "ML Pipeline Optimization",
                        "Automated Model Deployment"
                    ]
                }
            ]
        },
        "enterprise_solutions_team": {
            "title": "Enterprise Solutions Team Profiles",
            "summary": "Key members of the solutions implementation team",
            "team_members": [
                {
                    "name": "Marcus Wong",
                    "role": "Team Lead & Solutions Architect",
                    "title": "Director of Enterprise Solutions",
                    "experience": "18 years in enterprise software",
                    "expertise": [
                        "Enterprise Architecture",
                        "System Integration",
                        "Cloud Solutions"
                    ],
                    "certifications": [
                        "AWS Solutions Architect Professional",
                        "Google Cloud Professional Architect",
                        "Azure Solutions Expert"
                    ],
                    "projects_led": [
                        "Global Financial Institution Integration",
                        "Healthcare System Modernization",
                        "Retail Analytics Platform"
                    ]
                }
            ]
        },
        "ai_ethics_team": {
            "title": "AI Ethics & Governance Team Profiles",
            "summary": "Members focused on ethical AI development",
            "team_members": [
                {
                    "name": "Dr. Maya Patel",
                    "role": "Team Lead & Chief Ethics Officer",
                    "title": "Director of AI Ethics",
                    "experience": "12 years in AI ethics",
                    "expertise": [
                        "AI Safety",
                        "Ethical Framework Development",
                        "Regulatory Compliance"
                    ],
                    "education": {
                        "phd": "AI Ethics - Oxford University",
                        "masters": "Philosophy - Cambridge University"
                    },
                    "publications": 15,
                    "projects_led": [
                        "Global AI Ethics Framework",
                        "Bias Detection System",
                        "Ethical AI Guidelines"
                    ]
                }
            ]
        }
    }
    
    # Add role documentation
    kb_data['articles']['role_documentation'] = {
        "ai_research_roles": {
            "title": "AI Research & Development Roles",
            "summary": "Detailed role descriptions and requirements",
            "roles": {
                "senior_ai_researcher": {
                    "title": "Senior AI Researcher",
                    "level": "L5",
                    "responsibilities": [
                        "Lead research initiatives in AI/ML",
                        "Develop novel AI architectures",
                        "Publish research findings",
                        "Mentor junior researchers",
                        "Collaborate with ethics team"
                    ],
                    "required_skills": [
                        "Advanced ML algorithms",
                        "Neural network architecture",
                        "Research methodology",
                        "Python/PyTorch/TensorFlow",
                        "Technical writing"
                    ],
                    "preferred_qualifications": {
                        "education": "Ph.D. in Computer Science, ML, or related field",
                        "experience": "5+ years in AI research",
                        "publications": "Track record in top AI conferences"
                    },
                    "growth_path": {
                        "next_role": "Principal AI Researcher",
                        "key_milestones": [
                            "Lead major research initiative",
                            "Publish significant findings",
                            "Develop patent-worthy innovations"
                        ]
                    }
                }
            }
        }
    }
    
    # Write updated knowledge base back to file
    with open('knowledge_base.json', 'w') as f:
        json.dump(kb_data, f, indent=4)

def update_knowledge_base_step3():
    """Update knowledge base with candidate profiles and learning paths"""
    
    # Read existing knowledge base
    with open('knowledge_base.json', 'r') as f:
        kb_data = json.load(f)
    
    # Add candidate profiles
    kb_data['articles']['candidate_profiles'] = {
        "ai_research_candidates": {
            "title": "AI Research Team Candidates",
            "candidates": [
                {
                    "id": "CAND001",
                    "name": "Dr. Alex Zhang",
                    "applying_for": "Senior AI Researcher",
                    "resume": {
                        "summary": "ML researcher with focus on LLMs and neural architectures",
                        "education": {
                            "phd": {
                                "degree": "Ph.D. in Computer Science",
                                "institution": "UC Berkeley",
                                "year": 2020,
                                "focus": "Deep Learning"
                            },
                            "masters": {
                                "degree": "M.S. in Computer Science",
                                "institution": "UC Berkeley",
                                "year": 2017
                            }
                        },
                        "experience": [
                            {
                                "title": "Research Scientist",
                                "company": "TechCorp AI",
                                "duration": "2020-Present",
                                "achievements": [
                                    "Led team of 5 researchers on LLM optimization",
                                    "Published 4 papers in top AI conferences",
                                    "Developed novel attention mechanism",
                                    "Reduced model training time by 40%"
                                ]
                            }
                        ],
                        "publications": [
                            {
                                "title": "Efficient LLM Training Methods",
                                "conference": "NeurIPS 2022"
                            },
                            {
                                "title": "Novel Attention Mechanisms",
                                "conference": "ICML 2021"
                            }
                        ]
                    }
                }
            ]
        }
    }
    
    # Add learning paths
    kb_data['articles']['learning_paths'] = {
        "ai_research_paths": {
            "title": "AI Research Team Learning Paths",
            "paths": {
                "senior_researcher": {
                    "role": "Senior AI Researcher",
                    "onboarding_phases": [
                        {
                            "phase": 1,
                            "duration": "Week 1",
                            "focus": "Organization Introduction",
                            "activities": [
                                {
                                    "name": "Company Overview",
                                    "type": "Training",
                                    "duration": "1 day",
                                    "resources": [
                                        "Company handbook",
                                        "Mission statement",
                                        "Team structure documentation"
                                    ]
                                },
                                {
                                    "name": "Team Introductions",
                                    "type": "Meetings",
                                    "duration": "2 days",
                                    "activities": [
                                        "Meet with team leaders",
                                        "Research group presentations",
                                        "Project overview sessions"
                                    ]
                                }
                            ]
                        },
                        {
                            "phase": 2,
                            "duration": "Weeks 2-3",
                            "focus": "Technical Environment",
                            "activities": [
                                {
                                    "name": "Codebase Introduction",
                                    "type": "Technical",
                                    "duration": "1 week",
                                    "components": [
                                        "Architecture overview",
                                        "Code standards review",
                                        "Testing frameworks",
                                        "Development workflows"
                                    ]
                                }
                            ]
                        }
                    ],
                    "success_metrics": [
                        {
                            "category": "Research Impact",
                            "metrics": [
                                "Research project initiation",
                                "Publication submissions",
                                "Innovation metrics"
                            ]
                        }
                    ]
                }
            }
        }
    }
    
    # Write updated knowledge base back to file
    with open('knowledge_base.json', 'w') as f:
        json.dump(kb_data, f, indent=4)

def update_knowledge_base_step4():
    """Update knowledge base with corporate policies and documentation"""
    
    # Read existing knowledge base
    with open('knowledge_base.json', 'r') as f:
        kb_data = json.load(f)
    
    # Add organizational documentation
    kb_data['articles']['organizational_docs'] = {
        "corporate_policies": {
            "title": "K Korp Inc. Corporate Policies and Guidelines",
            "summary": "Comprehensive overview of company policies, procedures, and standards",
            "key_points": [
                "Company-wide policies and procedures",
                "Compliance requirements",
                "Employee guidelines",
                "Security protocols",
                "Communication standards"
            ],
            "content": {
                "code_of_conduct": {
                    "title": "Professional Code of Conduct",
                    "description": "Guidelines for professional behavior and ethical conduct",
                    "sections": [
                        {
                            "title": "Professional Ethics",
                            "content": "K Korp employees are expected to maintain the highest standards of professional conduct. This includes honesty in communication, respect for intellectual property, and commitment to data privacy. All employees must complete annual ethics training and certify compliance with our ethical guidelines."
                        },
                        {
                            "title": "Workplace Behavior",
                            "content": "Our workplace promotes inclusivity, respect, and professional growth. Employees are expected to contribute to a positive work environment, participate in team activities, and maintain professional relationships with colleagues, clients, and partners."
                        }
                    ]
                },
                "security_protocols": {
                    "title": "Security and Data Protection Protocols",
                    "description": "Essential security practices and data protection guidelines",
                    "sections": [
                        {
                            "title": "Data Security",
                            "content": "All employees must follow our comprehensive data security protocols, including use of approved encryption methods, secure communication channels, and proper data handling procedures. Regular security audits are conducted to ensure compliance."
                        }
                    ]
                }
            }
        },
        "standard_operating_procedures": {
            "title": "Standard Operating Procedures (SOPs)",
            "summary": "Detailed procedures for key organizational processes",
            "key_points": [
                "Development workflows",
                "Quality assurance processes",
                "Deployment procedures",
                "Incident response protocols",
                "Change management procedures"
            ],
            "content": {
                "development_workflow": {
                    "title": "Development Workflow and Processes",
                    "description": "Standardized development procedures and best practices",
                    "procedures": [
                        {
                            "name": "Code Development Process",
                            "steps": [
                                "Create feature branch from development",
                                "Implement changes following coding standards",
                                "Write unit tests achieving 80%+ coverage",
                                "Conduct code self-review",
                                "Submit pull request with detailed description",
                                "Address reviewer comments",
                                "Obtain approval from two senior developers",
                                "Merge to development branch"
                            ]
                        }
                    ]
                }
            }
        },
        "best_practices": {
            "title": "K Korp Best Practices Guidelines",
            "summary": "Compilation of best practices across different areas of operation",
            "key_points": [
                "Development standards",
                "Security practices",
                "Documentation guidelines",
                "Collaboration protocols",
                "Quality assurance methods"
            ],
            "content": {
                "development_standards": {
                    "title": "Development Best Practices",
                    "guidelines": [
                        {
                            "category": "Code Quality",
                            "practices": [
                                "Follow PEP 8 style guide for Python code",
                                "Maintain test coverage above 80%",
                                "Document all public APIs",
                                "Use type hints and docstrings",
                                "Implement error handling for all edge cases"
                            ]
                        }
                    ]
                }
            }
        }
    }
    
    # Write updated knowledge base back to file
    with open('knowledge_base.json', 'w') as f:
        json.dump(kb_data, f, indent=4)