"""
Unstructured Data Processing Tools for Healthcare Payor System

This module provides tools for processing customer service communications
and prior authorization documents using NLP and vector search capabilities.
"""

import json
import os
import re
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import pandas as pd
from databricks.sdk import WorkspaceClient
from databricks.vector_search import VectorSearchClient
import openai
from sentence_transformers import SentenceTransformer
import spacy
from transformers import pipeline

@dataclass
class DocumentMetadata:
    """Metadata for unstructured documents"""
    document_id: str
    document_type: str
    member_id: str
    date: str
    content: str
    sentiment: Optional[str] = None
    key_entities: List[str] = None
    summary: Optional[str] = None
    confidence_score: Optional[float] = None

@dataclass
class ProcessingResult:
    """Result of document processing"""
    document_id: str
    processed_content: str
    extracted_entities: Dict[str, List[str]]
    sentiment_analysis: Dict[str, Any]
    summary: str
    key_issues: List[str]
    confidence_scores: Dict[str, float]

class UnstructuredDataProcessor:
    """Main processor for unstructured healthcare documents"""
    
    def __init__(self, workspace_url: str = None, vector_search_endpoint: str = None):
        """Initialize the processor with Databricks and vector search clients"""
        self.client = WorkspaceClient()
        self.vector_search_client = VectorSearchClient()
        
        # Initialize NLP models
        self._setup_nlp_models()
        
        # Vector search configuration
        self.vector_search_endpoint = vector_search_endpoint
        self.index_name = "healthcare_documents_index"
        
    def _setup_nlp_models(self):
        """Initialize NLP models for text processing"""
        try:
            # Load spaCy model for medical NER
            self.nlp = spacy.load("en_core_web_sm")
            print("✅ spaCy model loaded successfully")
        except OSError:
            print("⚠️ spaCy model not found, using basic tokenization")
            self.nlp = None
            
        # Initialize sentiment analysis
        try:
            self.sentiment_analyzer = pipeline("sentiment-analysis", 
                                             model="cardiffnlp/twitter-roberta-base-sentiment-latest")
            print("✅ Sentiment analysis model loaded")
        except Exception as e:
            print(f"⚠️ Sentiment analysis model failed to load: {e}")
            self.sentiment_analyzer = None
            
        # Initialize sentence transformer for embeddings
        try:
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            print("✅ Embedding model loaded")
        except Exception as e:
            print(f"⚠️ Embedding model failed to load: {e}")
            self.embedding_model = None

    def process_customer_service_communications(self, data_file: str) -> List[ProcessingResult]:
        """Process customer service communication documents"""
        print("🔄 Processing customer service communications...")
        
        with open(data_file, 'r') as f:
            data = json.load(f)
            
        results = []
        communications = data.get('customer_service_communications', [])
        
        for comm in communications:
            result = self._process_communication(comm)
            results.append(result)
            
        print(f"✅ Processed {len(results)} customer service communications")
        return results

    def process_prior_authorization_documents(self, data_file: str) -> List[ProcessingResult]:
        """Process prior authorization documents"""
        print("🔄 Processing prior authorization documents...")
        
        with open(data_file, 'r') as f:
            data = json.load(f)
            
        results = []
        auth_docs = data.get('prior_authorization_documents', [])
        
        for doc in auth_docs:
            result = self._process_authorization_document(doc)
            results.append(result)
            
        print(f"✅ Processed {len(results)} prior authorization documents")
        return results

    def _process_communication(self, comm: Dict[str, Any]) -> ProcessingResult:
        """Process individual customer service communication"""
        content = comm.get('content', '')
        
        # Extract entities
        entities = self._extract_entities(content)
        
        # Analyze sentiment
        sentiment = self._analyze_sentiment(content)
        
        # Generate summary
        summary = self._generate_summary(content)
        
        # Extract key issues
        key_issues = self._extract_key_issues(content, comm.get('key_issues', []))
        
        # Calculate confidence scores
        confidence_scores = {
            'entity_extraction': self._calculate_entity_confidence(entities),
            'sentiment_analysis': self._calculate_sentiment_confidence(sentiment),
            'summary_quality': self._calculate_summary_confidence(summary, content)
        }
        
        return ProcessingResult(
            document_id=comm.get('id', ''),
            processed_content=content,
            extracted_entities=entities,
            sentiment_analysis=sentiment,
            summary=summary,
            key_issues=key_issues,
            confidence_scores=confidence_scores
        )

    def _process_authorization_document(self, doc: Dict[str, Any]) -> ProcessingResult:
        """Process individual prior authorization document"""
        # Combine all text content
        content_parts = [
            doc.get('medical_necessity', ''),
            doc.get('clinical_notes', ''),
            doc.get('supporting_documentation', '')
        ]
        content = ' '.join(filter(None, content_parts))
        
        # Extract entities
        entities = self._extract_entities(content)
        
        # Analyze sentiment (for urgency/concern level)
        sentiment = self._analyze_sentiment(content)
        
        # Generate summary
        summary = self._generate_summary(content)
        
        # Extract key issues
        key_issues = self._extract_authorization_issues(doc)
        
        # Calculate confidence scores
        confidence_scores = {
            'entity_extraction': self._calculate_entity_confidence(entities),
            'sentiment_analysis': self._calculate_sentiment_confidence(sentiment),
            'summary_quality': self._calculate_summary_confidence(summary, content)
        }
        
        return ProcessingResult(
            document_id=doc.get('id', ''),
            processed_content=content,
            extracted_entities=entities,
            sentiment_analysis=sentiment,
            summary=summary,
            key_issues=key_issues,
            confidence_scores=confidence_scores
        )

    def _extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract named entities from text"""
        entities = {
            'medical_terms': [],
            'procedures': [],
            'diagnoses': [],
            'medications': [],
            'dates': [],
            'amounts': [],
            'member_ids': [],
            'claim_numbers': []
        }
        
        if self.nlp:
            doc = self.nlp(text)
            
            for ent in doc.ents:
                if ent.label_ == "PERSON":
                    # Could be provider names
                    entities['medical_terms'].append(ent.text)
                elif ent.label_ == "MONEY":
                    entities['amounts'].append(ent.text)
                elif ent.label_ == "DATE":
                    entities['dates'].append(ent.text)
        
        # Extract specific patterns
        entities['member_ids'].extend(re.findall(r'M\d{9}', text))
        entities['claim_numbers'].extend(re.findall(r'CLM\d{8}', text))
        entities['procedures'].extend(re.findall(r'CPT[_\s]?\d{5}', text))
        entities['diagnoses'].extend(re.findall(r'ICD10[_\s]?\w+', text))
        
        # Extract medication names (basic pattern)
        medication_patterns = [
            r'\b(?:insulin|metformin|lisinopril|atorvastatin|amlodipine)\b',
            r'\b(?:Lantus|Humalog|Novolog|Glucophage|Lipitor)\b'
        ]
        for pattern in medication_patterns:
            entities['medications'].extend(re.findall(pattern, text, re.IGNORECASE))
        
        return {k: list(set(v)) for k, v in entities.items() if v}

    def _analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment of the text"""
        if not self.sentiment_analyzer:
            return {'label': 'neutral', 'score': 0.5}
        
        try:
            result = self.sentiment_analyzer(text[:512])  # Limit text length
            return {
                'label': result[0]['label'],
                'score': result[0]['score']
            }
        except Exception as e:
            print(f"⚠️ Sentiment analysis failed: {e}")
            return {'label': 'neutral', 'score': 0.5}

    def _generate_summary(self, text: str, max_length: int = 150) -> str:
        """Generate a summary of the text"""
        # Simple extractive summarization
        sentences = text.split('.')
        if len(sentences) <= 3:
            return text[:max_length] + "..." if len(text) > max_length else text
        
        # Take first and last sentences for basic summary
        summary_sentences = [sentences[0], sentences[-1]]
        summary = '. '.join(summary_sentences)
        
        return summary[:max_length] + "..." if len(summary) > max_length else summary

    def _extract_key_issues(self, content: str, existing_issues: List[str]) -> List[str]:
        """Extract key issues from content"""
        issues = existing_issues.copy() if existing_issues else []
        
        # Common issue patterns
        issue_patterns = {
            'billing_issues': ['billing', 'charge', 'cost', 'payment', 'denied'],
            'coverage_issues': ['coverage', 'covered', 'benefit', 'plan'],
            'authorization_issues': ['authorization', 'approval', 'prior auth'],
            'network_issues': ['network', 'in-network', 'out-of-network'],
            'urgent_issues': ['urgent', 'emergency', 'immediate', 'asap']
        }
        
        content_lower = content.lower()
        for category, keywords in issue_patterns.items():
            if any(keyword in content_lower for keyword in keywords):
                if category not in issues:
                    issues.append(category)
        
        return issues

    def _extract_authorization_issues(self, doc: Dict[str, Any]) -> List[str]:
        """Extract specific issues from authorization documents"""
        issues = []
        
        if doc.get('status') == 'denied':
            issues.append('authorization_denied')
        
        if doc.get('urgency_level') == 'emergent':
            issues.append('emergency_authorization')
        
        if 'failed' in doc.get('medical_necessity', '').lower():
            issues.append('conservative_treatment_failed')
        
        if 'out-of-network' in doc.get('provider_name', '').lower():
            issues.append('out_of_network_provider')
        
        return issues

    def _calculate_entity_confidence(self, entities: Dict[str, List[str]]) -> float:
        """Calculate confidence score for entity extraction"""
        total_entities = sum(len(v) for v in entities.values())
        if total_entities == 0:
            return 0.0
        
        # Higher confidence if we found more diverse entity types
        entity_types = len([k for k, v in entities.items() if v])
        return min(1.0, entity_types / 5.0)  # Normalize to 0-1

    def _calculate_sentiment_confidence(self, sentiment: Dict[str, Any]) -> float:
        """Calculate confidence score for sentiment analysis"""
        return sentiment.get('score', 0.5)

    def _calculate_summary_confidence(self, summary: str, original: str) -> float:
        """Calculate confidence score for summary quality"""
        if not summary or not original:
            return 0.0
        
        # Simple heuristic: summary should be shorter but contain key information
        compression_ratio = len(summary) / len(original)
        return min(1.0, 1.0 - compression_ratio + 0.3)  # Prefer 30-70% compression

    def create_vector_search_index(self, processed_results: List[ProcessingResult]) -> str:
        """Create vector search index for processed documents"""
        print("🔄 Creating vector search index...")
        
        if not self.embedding_model:
            print("⚠️ Embedding model not available, skipping vector search")
            return None
        
        # Prepare documents for indexing
        documents = []
        for result in processed_results:
            doc = {
                'id': result.document_id,
                'content': result.processed_content,
                'summary': result.summary,
                'entities': json.dumps(result.extracted_entities),
                'sentiment': json.dumps(result.sentiment_analysis),
                'key_issues': json.dumps(result.key_issues)
            }
            documents.append(doc)
        
        # Generate embeddings
        texts = [doc['content'] for doc in documents]
        embeddings = self.embedding_model.encode(texts)
        
        # Create DataFrame for vector search
        df = pd.DataFrame(documents)
        df['embedding'] = embeddings.tolist()
        
        # Save to Delta table
        table_name = "healthcare_documents_embeddings"
        df.write.mode("overwrite").saveAsTable(table_name)
        
        print(f"✅ Vector search index created with {len(documents)} documents")
        return table_name

    def search_similar_documents(self, query: str, table_name: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar documents using vector search"""
        if not self.embedding_model:
            print("⚠️ Embedding model not available")
            return []
        
        # Generate query embedding
        query_embedding = self.embedding_model.encode([query])
        
        # Use Databricks SQL for similarity search
        # This is a simplified version - in production you'd use Vector Search service
        search_query = f"""
        SELECT document_id, content, summary, entities, sentiment, key_issues,
               array_cosine_similarity(embedding, {query_embedding[0].tolist()}) as similarity
        FROM {table_name}
        ORDER BY similarity DESC
        LIMIT {top_k}
        """
        
        try:
            results = self.client.statement.execute(search_query)
            return results.result.data_array
        except Exception as e:
            print(f"⚠️ Vector search failed: {e}")
            return []

def main():
    """Main function to demonstrate document processing"""
    processor = UnstructuredDataProcessor()
    
    # Process customer service communications
    cs_results = processor.process_customer_service_communications(
        'data/customer_service_communications.json'
    )
    
    # Process prior authorization documents
    pa_results = processor.process_prior_authorization_documents(
        'data/prior_authorization_documents.json'
    )
    
    # Create vector search index
    all_results = cs_results + pa_results
    table_name = processor.create_vector_search_index(all_results)
    
    # Example search
    if table_name:
        similar_docs = processor.search_similar_documents(
            "patient needs urgent surgery authorization",
            table_name
        )
        print(f"Found {len(similar_docs)} similar documents")

if __name__ == "__main__":
    main()

