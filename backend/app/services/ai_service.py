from typing import List, Dict, Any
import torch
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    AutoModelForTokenClassification,
    pipeline
)
from sentence_transformers import SentenceTransformer
import numpy as np
from ..core.config import settings

class AIService:
    def __init__(self):
        # Initialize models
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Text classification model for clause analysis
        self.classifier_tokenizer = AutoTokenizer.from_pretrained("nlpaueb/legal-bert-base-uncased")
        self.classifier_model = AutoModelForSequenceClassification.from_pretrained(
            "nlpaueb/legal-bert-base-uncased",
            num_labels=3  # [keep, modify, remove]
        ).to(self.device)
        
        # Named Entity Recognition for clause extraction
        self.ner_tokenizer = AutoTokenizer.from_pretrained("nlpaueb/legal-bert-base-uncased")
        self.ner_model = AutoModelForTokenClassification.from_pretrained(
            "nlpaueb/legal-bert-base-uncased",
            num_labels=5  # [O, B-CLAUSE, I-CLAUSE, B-SECTION, I-SECTION]
        ).to(self.device)
        
        # Sentence transformer for semantic similarity
        self.sentence_transformer = SentenceTransformer('all-MiniLM-L6-v2').to(self.device)
        
        # Text generation pipeline for suggestions
        self.text_generator = pipeline(
            "text-generation",
            model="gpt2",  # Using GPT-2 as base model
            device=0 if self.device == "cuda" else -1
        )

    async def analyze_document(self, content: str) -> List[Dict[str, Any]]:
        """Analyze document content and generate suggestions"""
        # Extract clauses using NER
        clauses = self._extract_clauses(content)
        
        analysis_results = []
        for clause in clauses:
            # Analyze clause
            classification = self._classify_clause(clause)
            
            if classification["label"] == "modify":
                # Generate suggestion
                suggested_text = self._generate_suggestion(clause)
                confidence_score = classification["score"]
            else:
                suggested_text = clause
                confidence_score = 100 if classification["label"] == "keep" else 0
            
            analysis_results.append({
                "clause_text": clause,
                "original_text": clause,
                "suggested_text": suggested_text,
                "confidence_score": int(confidence_score * 100)
            })
        
        return analysis_results

    async def validate_clause(
        self,
        clause_text: str,
        suggested_text: str,
        similar_clauses: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Validate a clause and its suggestion"""
        # Compare with similar clauses
        similar_texts = [c["metadata"]["text"] for c in similar_clauses]
        similarity_scores = self._calculate_similarity(suggested_text, similar_texts)
        
        # Calculate validation score based on similarity and confidence
        avg_similarity = np.mean(similarity_scores)
        validation_score = int(avg_similarity * 100)
        
        return {
            "validation_score": validation_score,
            "validation_notes": "Validated against similar clauses in the database"
        }

    async def create_redline_document(
        self,
        content: str,
        analysis_results: List[Dict[str, Any]]
    ) -> str:
        """Create a redline version of the document with suggested changes"""
        # Implementation for creating redline document
        # This would use python-docx to create a document with tracked changes
        return content  # Placeholder

    def _extract_clauses(self, text: str) -> List[str]:
        """Extract clauses from text using NER"""
        inputs = self.ner_tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=512
        ).to(self.device)
        
        outputs = self.ner_model(**inputs)
        predictions = torch.argmax(outputs.logits, dim=2)
        
        # Process predictions to extract clauses
        clauses = []
        current_clause = []
        
        for token, pred in zip(self.ner_tokenizer.tokenize(text), predictions[0]):
            if pred.item() in [1, 2]:  # B-CLAUSE or I-CLAUSE
                current_clause.append(token)
            elif current_clause:
                clauses.append(" ".join(current_clause))
                current_clause = []
        
        if current_clause:
            clauses.append(" ".join(current_clause))
        
        return clauses

    def _classify_clause(self, clause: str) -> Dict[str, Any]:
        """Classify a clause as keep, modify, or remove"""
        inputs = self.classifier_tokenizer(
            clause,
            return_tensors="pt",
            truncation=True,
            max_length=512
        ).to(self.device)
        
        outputs = self.classifier_model(**inputs)
        probabilities = torch.softmax(outputs.logits, dim=1)[0]
        
        label_map = {0: "keep", 1: "modify", 2: "remove"}
        label_id = torch.argmax(probabilities).item()
        
        return {
            "label": label_map[label_id],
            "score": probabilities[label_id].item()
        }

    def _generate_suggestion(self, clause: str) -> str:
        """Generate a suggested modification for a clause"""
        # Use the text generation pipeline to generate suggestions
        prompt = f"Improve this legal clause: {clause}\nImproved version:"
        generated = self.text_generator(
            prompt,
            max_length=len(clause.split()) + 20,
            num_return_sequences=1,
            temperature=0.7
        )
        
        return generated[0]["generated_text"].split("Improved version:")[1].strip()

    def _calculate_similarity(self, text: str, texts: List[str]) -> List[float]:
        """Calculate semantic similarity between texts"""
        embeddings = self.sentence_transformer.encode([text] + texts)
        query_embedding = embeddings[0]
        text_embeddings = embeddings[1:]
        
        similarities = []
        for text_embedding in text_embeddings:
            similarity = np.dot(query_embedding, text_embedding) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(text_embedding)
            )
            similarities.append(float(similarity))
        
        return similarities 