"""
Atmospheric Complexity Framework (ACF)

AWCI RAG (Retrieval-Augmented Generation) Layer - Evidence Retrieval Only

Real implementation of the ``ai/rag/`` package named in
``docs/architecture/awci_reference_architecture.md`` section 14
(``src/awci/ai/rag/``), previously identified as a genuinely absent
piece in ``docs/architecture/acf_awci_architecture_gap_analysis.md``
(section 3, point 3, and line 48: "RAG is not implemented anywhere in
this codebase today").

User-confirmed scope (explicit, verbatim requirements this package
follows):

1. **Lexical, deterministic retrieval now** - Okapi BM25 (Robertson &
   Zaragoza), a real, published, citable ranking algorithm, implemented
   in pure Python over ``collections``/``math`` - no new dependency.
   ``requirements.txt`` has no embedding library, vector store, or LLM
   client (verified before writing a line of this package) - adding
   one was explicitly declined for this phase.
2. **A clean ``Retriever`` interface** (``retriever.py``) so a future
   local-embedding or hybrid backend can be added later WITHOUT
   changing this package's own public API (``retrieve()`` ->
   ``list[ScoredDocument]``) - ``BM25Retriever`` is Phase 1's one real
   implementation of it.
3. **No external LLM API, no network dependency** - nothing in this
   package makes a network call; there is no API key anywhere in it.
4. **No fake knowledge, no synthetic documents** - every ``Document``
   this package can return is built by real Python introspection
   (``inspect``) of an already-real, already-committed, already-cited
   module under ``awci.knowledge`` (the ~39-module ICAO/WMO/aviation
   knowledge base built earlier this session) - never invented text.
5. **Exact provenance preserved** - every ``Document`` carries its real
   source file path, dotted module name, symbol name (class/enum, or
   empty string for a whole-module document), and the real git commit
   hash that last touched that file (``None``, never fabricated, if git
   is unavailable or the file is untracked) - see ``documents.py``'s
   own ``Provenance`` dataclass.
6. **Strictly an evidence/retrieval layer** - this package returns real
   TEXT EVIDENCE (documents + citations) about what the AWCI knowledge
   base already, documentedly says. It never computes, estimates, or
   infers a scientific value; it never calls into
   ``awci.complexity.calculator.AWCICalculator`` or any hazard module,
   and nothing in ``awci.complexity``/``awci.hazards`` calls into this
   package either - a one-way, read-only relationship.
7. **Corpus scope: only documented/validated AWCI knowledge** - the
   corpus this package indexes is exactly, and only,
   ``awci.knowledge.*`` (every module already cites a real source -
   ICAO Annex/Doc, WMO, or a specific lavionnaire.fr page - in its own
   docstring; see that package's own modules). This package never
   indexes ``acf.science.encyclopedia`` or any other ACF-general
   corpus, and it never fabricates a threshold or law of its own -
   every returned document is a real excerpt of already-real,
   already-cited content, nothing synthesized "from assumptions".

**Deliberately not built this phase** (the blueprint's own
``ai/rag/embeddings.py``/``vector_store.py`` file names): no semantic
embedding backend exists yet (see point 1 above) - creating those two
files today would mean either an empty/fake implementation (against
this project's own "never invent placeholders" rule) or committing to
a specific new dependency without that decision having been made. The
``Retriever`` protocol in ``retriever.py`` is the real, already-built
extension point for that future work.
"""

from __future__ import annotations

from awci.ai.rag.citations import format_citation
from awci.ai.rag.documents import Document, Provenance, build_document_corpus
from awci.ai.rag.retriever import BM25Retriever, Retriever, ScoredDocument

__all__ = [
    "BM25Retriever",
    "Document",
    "Provenance",
    "Retriever",
    "ScoredDocument",
    "build_document_corpus",
    "format_citation",
]
