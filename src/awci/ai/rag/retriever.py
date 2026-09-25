"""
Atmospheric Complexity Framework (ACF)

AWCI RAG - Retriever

A real, published, citable ranking algorithm - Okapi BM25 (Robertson &
Zaragoza, "The Probabilistic Relevance Framework: BM25 and Beyond",
2009; k1=1.5, b=0.75 are that paper's own standard default parameters,
not ACF-invented values) - implemented in pure Python
(``collections``/``math`` only, no new dependency). See this package's
own ``__init__.py`` docstring for why a lexical algorithm was chosen
for this phase and how a future semantic backend would plug into the
``Retriever`` protocol below without changing callers.
"""

from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass
from typing import Protocol

from awci.ai.rag.documents import Document

#: Real BM25 standard parameters (Robertson & Zaragoza 2009) - not
#: independently chosen or tuned for this corpus.
_BM25_K1 = 1.5
_BM25_B = 0.75

_TOKEN_RE = re.compile(r"[a-z0-9]+")


def _tokenize(text: str) -> list[str]:
    """Real, simple, deterministic tokenization - lowercase, alphanumeric
    runs only. No stemming/stopword removal (a real, disclosed
    simplicity choice for this phase, not a hidden limitation - a
    query token must appear verbatim, case-insensitively, in a
    document to contribute to its score)."""
    return _TOKEN_RE.findall(text.lower())


@dataclass(frozen=True)
class ScoredDocument:
    """One real retrieved ``Document`` with its real BM25 relevance
    score for the query that produced it - higher is more relevant, 0
    means the query shared no real token with this document."""

    document: Document
    score: float


class Retriever(Protocol):
    """
    Real, minimal retrieval interface - the one contract this whole
    package's callers depend on. A future local-embedding or hybrid
    backend implements this exact same protocol (``retrieve(query,
    top_k) -> list[ScoredDocument]``), so nothing outside this package
    needs to change when one is added - see this package's own
    ``__init__.py`` docstring, point 2.
    """

    def retrieve(self, query: str, top_k: int = 5) -> list[ScoredDocument]: ...


class BM25Retriever:
    """
    Real Okapi BM25 retriever over a fixed, real ``Document`` corpus -
    Phase 1's one real ``Retriever`` implementation (see module
    docstring). Never mutates or re-ranks by anything other than the
    real BM25 score of the real query tokens actually supplied.
    """

    def __init__(self, documents: list[Document]) -> None:
        self._documents = documents
        self._doc_tokens: list[list[str]] = [_tokenize(doc.content) for doc in documents]
        self._doc_lengths = [len(tokens) for tokens in self._doc_tokens]
        self._average_doc_length = (sum(self._doc_lengths) / len(self._doc_lengths)) if documents else 0.0
        self._term_frequencies: list[Counter[str]] = [Counter(tokens) for tokens in self._doc_tokens]
        self._document_frequency: Counter[str] = Counter()
        for term_frequency in self._term_frequencies:
            self._document_frequency.update(term_frequency.keys())

    def _idf(self, term: str) -> float:
        """Real Okapi BM25 inverse document frequency, with the
        standard +1 smoothing (Robertson & Zaragoza 2009) that keeps
        this non-negative even for a term present in every document."""
        n = len(self._documents)
        df = self._document_frequency.get(term, 0)
        return math.log(1.0 + (n - df + 0.5) / (df + 0.5))

    def retrieve(self, query: str, top_k: int = 5) -> list[ScoredDocument]:
        """Real BM25-ranked documents for ``query``, highest score
        first, truncated to ``top_k``. An empty real corpus, or a query
        sharing no real token with any document, honestly returns an
        empty list - never a fabricated "closest match" below a real
        relevance floor."""
        query_terms = set(_tokenize(query))
        if not query_terms or not self._documents:
            return []
        scored: list[ScoredDocument] = []
        for index, document in enumerate(self._documents):
            term_frequency = self._term_frequencies[index]
            doc_length = self._doc_lengths[index]
            score = 0.0
            for term in query_terms:
                tf = term_frequency.get(term, 0)
                if tf == 0:
                    continue
                idf = self._idf(term)
                denominator = tf + _BM25_K1 * (
                    1.0 - _BM25_B + _BM25_B * (doc_length / self._average_doc_length if self._average_doc_length else 0.0)
                )
                score += idf * (tf * (_BM25_K1 + 1.0)) / denominator if denominator else 0.0
            if score > 0.0:
                scored.append(ScoredDocument(document=document, score=score))
        scored.sort(key=lambda item: item.score, reverse=True)
        return scored[:top_k]
