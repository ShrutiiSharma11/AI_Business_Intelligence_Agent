"""
RAG Agent: Handles document-based questions using retrieval-augmented generation.
Searches through uploaded documents for information.
"""

import logging
from typing import Dict, Any, Optional, List, Tuple
import json
from pathlib import Path

logger = logging.getLogger(__name__)


class DocumentStore:
    """Simple document storage and retrieval."""

    def __init__(self):
        self.documents: List[Dict[str, str]] = []
        self.logger = logger

    def add_document(self, file_path: str, content: str, doc_type: str = "text") -> bool:
        """
        Add a document to the store.

        Args:
            file_path: Path to the document
            content: Document content
            doc_type: Type of document (pdf, text, etc.)

        Returns:
            True if added successfully
        """
        try:
            doc = {
                "path": file_path,
                "content": content,
                "type": doc_type,
                "size": len(content)
            }
            self.documents.append(doc)
            self.logger.info(f"Added document: {file_path}")
            return True
        except Exception as e:
            self.logger.error(f"Error adding document: {str(e)}")
            return False

    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Simple keyword-based search through documents.

        Args:
            query: Search query
            top_k: Number of results to return

        Returns:
            List of relevant documents
        """
        query_lower = query.lower()
        query_words = set(query_lower.split())

        scored_docs = []

        for doc in self.documents:
            content_lower = doc["content"].lower()
            content_words = set(content_lower.split())

            # Simple scoring: number of matching words
            matches = len(query_words & content_words)

            if matches > 0:
                scored_docs.append((doc, matches))

        # Sort by score
        scored_docs.sort(key=lambda x: x[1], reverse=True)

        return [doc for doc, score in scored_docs[:top_k]]

    def get_document_count(self) -> int:
        """Get number of stored documents."""
        return len(self.documents)

    def list_documents(self) -> List[str]:
        """List all stored documents."""
        return [doc["path"] for doc in self.documents]


class RAGAgent:
    """
    Retrieval-Augmented Generation Agent for document-based questions.
    """

    def __init__(self):
        self.document_store = DocumentStore()
        self.logger = logger

    def load_document(self, file_path: str, doc_type: str = "text") -> Dict[str, Any]:
        """
        Load a document for RAG.

        Args:
            file_path: Path to the document
            doc_type: Type of document

        Returns:
            Loading result
        """
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            if not content.strip():
                return {
                    "success": False,
                    "error": "Document is empty"
                }

            success = self.document_store.add_document(file_path, content, doc_type)

            if success:
                return {
                    "success": True,
                    "message": f"Document loaded: {Path(file_path).name}",
                    "size": len(content),
                    "doc_type": doc_type
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to add document to store"
                }

        except Exception as e:
            self.logger.error(f"Error loading document: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    def answer_question(self, question: str) -> Dict[str, Any]:
        """
        Answer a question using documents.

        Args:
            question: User's question

        Returns:
            Answer with sources
        """
        if self.document_store.get_document_count() == 0:
            return {
                "success": False,
                "error": "No documents loaded. Please upload documents first."
            }

        # Search for relevant documents
        relevant_docs = self.document_store.search(question, top_k=3)

        if not relevant_docs:
            return {
                "success": False,
                "error": "No relevant information found in documents",
                "suggestion": "Try rephrasing your question or check if documents are loaded."
            }

        # Prepare result
        answer_parts = []
        sources = []

        for doc in relevant_docs:
            doc_name = Path(doc["path"]).name
            sources.append({
                "document": doc_name,
                "type": doc["type"]
            })

            # Find relevant excerpts
            content = doc["content"]
            excerpts = self._extract_relevant_excerpts(content, question, max_length=500)

            if excerpts:
                answer_parts.append(f"From {doc_name}:\n{excerpts}")

        answer = "\n\n".join(answer_parts) if answer_parts else "Information found but content extraction failed."

        return {
            "success": True,
            "answer": answer,
            "sources": sources,
            "documents_searched": len(relevant_docs)
        }

    def _extract_relevant_excerpts(self, content: str, query: str, max_length: int = 500) -> str:
        """
        Extract relevant excerpts from content based on query.

        Args:
            content: Document content
            query: Search query
            max_length: Maximum length of excerpt

        Returns:
            Relevant excerpts
        """
        query_words = set(query.lower().split())
        lines = content.split('\n')

        relevant_lines = []

        for line in lines:
            line_words = set(line.lower().split())
            matches = len(query_words & line_words)

            if matches > 0:
                relevant_lines.append(line.strip())

        # Combine relevant lines
        excerpt = " ".join(relevant_lines[:5])  # Take first 5 matching lines

        # Limit length
        if len(excerpt) > max_length:
            excerpt = excerpt[:max_length] + "..."

        return excerpt

    def get_document_info(self) -> Dict[str, Any]:
        """Get information about loaded documents."""
        return {
            "total_documents": self.document_store.get_document_count(),
            "documents": self.document_store.list_documents()
        }

    def clear_documents(self) -> bool:
        """Clear all loaded documents."""
        self.document_store.documents = []
        self.logger.info("All documents cleared")
        return True


class SimpleRAGPipeline:
    """
    Simplified RAG pipeline for basic document retrieval.
    Can be extended with vector stores and embeddings later.
    """

    def __init__(self):
        self.agent = RAGAgent()
        self.logger = logger

    def load_documents_from_folder(self, folder_path: str) -> Dict[str, Any]:
        """
        Load all documents from a folder.

        Args:
            folder_path: Path to folder with documents

        Returns:
            Loading results
        """
        folder = Path(folder_path)
        if not folder.exists():
            return {
                "success": False,
                "error": f"Folder not found: {folder_path}"
            }

        # Supported file types
        supported_types = {
            '.txt': 'text',
            '.pdf': 'pdf',
            '.md': 'markdown'
        }

        loaded = []
        failed = []

        for file_path in folder.iterdir():
            if file_path.suffix.lower() in supported_types:
                doc_type = supported_types[file_path.suffix.lower()]
                result = self.agent.load_document(str(file_path), doc_type)

                if result["success"]:
                    loaded.append(file_path.name)
                else:
                    failed.append({
                        "file": file_path.name,
                        "error": result.get("error", "Unknown error")
                    })

        return {
            "success": len(loaded) > 0,
            "loaded": loaded,
            "failed": failed,
            "total": len(loaded) + len(failed)
        }

    def answer_question(self, question: str) -> str:
        """
        Answer a question about the loaded documents.

        Args:
            question: User's question

        Returns:
            Answer as formatted string
        """
        result = self.agent.answer_question(question)

        if not result["success"]:
            return f"Error: {result.get('error', 'Unknown error')}"

        answer = result.get("answer", "")
        sources = result.get("sources", [])

        # Format answer with sources
        formatted = f"{answer}\n\n"
        if sources:
            formatted += "**Sources:**\n"
            for source in sources:
                formatted += f"- {source['document']} ({source['type']})\n"

        return formatted
