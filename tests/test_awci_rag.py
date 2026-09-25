"""Tests for the new AWCI RAG evidence-retrieval layer
(src/awci/ai/rag/), built at the user's explicit request ("Le RAG
layer") after it was identified as a genuinely absent piece in
docs/architecture/acf_awci_architecture_gap_analysis.md.

User-confirmed scope: lexical/deterministic BM25 retrieval (no new
dependency, no network, no LLM API), a clean Retriever interface for a
future embedding backend, exact provenance (source path/module/
symbol/git commit) on every document, corpus strictly limited to
awci.knowledge.* (never acf.science.encyclopedia or any fabricated
text), and a strict evidence-only role (never feeding back into or
replacing any deterministic AWCI calculation).
"""

from __future__ import annotations

import subprocess

import pytest

from awci.ai.rag import (
    BM25Retriever,
    Document,
    Provenance,
    ScoredDocument,
    build_document_corpus,
    format_citation,
)
from awci.ai.rag.documents import _git_commit_for, _iter_knowledge_module_names


# --------------------------------------------------------------------- corpus


def test_build_document_corpus_is_real_and_non_empty():
    documents = build_document_corpus()
    assert len(documents) > 50
    for document in documents:
        assert isinstance(document, Document)
        assert document.content.strip() != ""


def test_document_corpus_is_deterministic_across_two_builds():
    """The same real checkout must always yield the same real corpus -
    no randomness, no hidden mutable state between calls."""
    first = build_document_corpus()
    second = build_document_corpus()
    assert [(d.content, d.provenance) for d in first] == [(d.content, d.provenance) for d in second]


def test_every_document_module_is_under_the_real_awci_knowledge_package():
    """Corpus-scope discipline: never acf.science.encyclopedia or any
    other package - only the real, cited AWCI knowledge base."""
    for document in build_document_corpus():
        assert document.provenance.module.startswith("awci.knowledge.")


def test_iter_knowledge_module_names_matches_a_real_pkgutil_walk():
    import pkgutil

    import awci.knowledge

    expected = sorted(
        m.name for m in pkgutil.walk_packages(awci.knowledge.__path__, prefix="awci.knowledge.") if not m.ispkg
    )
    assert _iter_knowledge_module_names() == expected
    assert len(expected) >= 30  # this session's own knowledge-base build-out


def test_a_known_module_docstring_appears_verbatim_in_the_corpus():
    """No paraphrasing, no fabrication - the exact real docstring text
    of a known, already-cited module must appear unchanged."""
    import inspect

    import awci.knowledge.meteorology.orographic_turbulence as orographic_module

    real_docstring = inspect.getdoc(orographic_module)
    documents = build_document_corpus()
    matching = [d for d in documents if d.provenance.module == orographic_module.__name__ and d.provenance.symbol == ""]
    assert len(matching) == 1
    assert matching[0].content == real_docstring


def test_a_known_class_docstring_is_indexed_under_its_own_defining_module():
    """awci.knowledge.meteorology.clouds.CloudGenus is reused (imported)
    by weather_front.py, but must only be indexed once, under its real
    defining module - never duplicated under every importer."""
    documents = build_document_corpus()
    cloud_genus_docs = [
        d for d in documents if d.provenance.symbol == "CloudGenus"
    ]
    assert len(cloud_genus_docs) == 1
    assert cloud_genus_docs[0].provenance.module == "awci.knowledge.meteorology.clouds"


def test_provenance_source_path_is_real_and_exists_on_disk():
    from pathlib import Path

    from awci.ai.rag.documents import _REPO_ROOT

    documents = build_document_corpus()
    for document in documents[:10]:
        assert (Path(_REPO_ROOT) / document.provenance.source_path).is_file()


def test_git_commit_for_returns_a_real_hash_or_honestly_none():
    """Never a fabricated hash - either a real 40-hex-char commit id or
    None (e.g. an untracked file, or git unavailable)."""
    documents = build_document_corpus()
    sampled = documents[0].provenance
    commit = sampled.git_commit
    if commit is not None:
        assert len(commit) == 40
        assert all(c in "0123456789abcdef" for c in commit)


def test_git_commit_for_a_real_tracked_file_matches_a_direct_git_log_call():
    from pathlib import Path

    from awci.ai.rag.documents import _REPO_ROOT

    real_path = Path("src/awci/knowledge/meteorology/orographic_turbulence.py")
    expected = subprocess.run(
        ["git", "log", "-1", "--format=%H", "--", str(real_path)],
        cwd=_REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    ).stdout.strip()
    if not expected:
        pytest.skip("git history not available in this checkout")
    assert _git_commit_for(real_path) == expected


def test_git_commit_for_is_cached_per_path():
    from pathlib import Path

    from awci.ai.rag.documents import _GIT_COMMIT_CACHE

    real_path = Path("src/awci/knowledge/meteorology/fog.py")
    _git_commit_for(real_path)
    assert str(real_path) in _GIT_COMMIT_CACHE


# --------------------------------------------------------------------- retriever


def test_bm25_retriever_returns_scored_documents_ranked_highest_first():
    documents = build_document_corpus()
    retriever = BM25Retriever(documents)
    results = retriever.retrieve("orographic rotor descent speed", top_k=5)
    assert len(results) > 0
    assert all(isinstance(r, ScoredDocument) for r in results)
    scores = [r.score for r in results]
    assert scores == sorted(scores, reverse=True)
    assert all(score > 0.0 for score in scores)


def test_bm25_retriever_finds_the_real_relevant_document_at_the_top():
    documents = build_document_corpus()
    retriever = BM25Retriever(documents)
    results = retriever.retrieve("wake turbulence separation minima", top_k=3)
    assert results[0].document.provenance.module == "awci.knowledge.performance.wake_turbulence"


def test_bm25_retriever_respects_top_k():
    documents = build_document_corpus()
    retriever = BM25Retriever(documents)
    results = retriever.retrieve("real", top_k=2)
    assert len(results) <= 2


def test_bm25_retriever_returns_empty_list_for_a_query_with_no_real_match():
    """Never a fabricated 'closest match' below a real relevance floor -
    a genuinely unrelated query must return nothing."""
    documents = build_document_corpus()
    retriever = BM25Retriever(documents)
    results = retriever.retrieve("xyzzy quantum flux capacitor unicorn", top_k=5)
    assert results == []


def test_bm25_retriever_handles_an_empty_query_honestly():
    documents = build_document_corpus()
    retriever = BM25Retriever(documents)
    assert retriever.retrieve("", top_k=5) == []


def test_bm25_retriever_on_an_empty_corpus_never_crashes():
    retriever = BM25Retriever([])
    assert retriever.retrieve("anything", top_k=5) == []


def test_bm25_uses_the_real_published_standard_parameters():
    from awci.ai.rag.retriever import _BM25_B, _BM25_K1

    assert _BM25_K1 == 1.5
    assert _BM25_B == 0.75


def test_bm25_retriever_is_deterministic_across_repeated_queries():
    documents = build_document_corpus()
    retriever = BM25Retriever(documents)
    first = retriever.retrieve("icing severity threshold", top_k=5)
    second = retriever.retrieve("icing severity threshold", top_k=5)
    assert [(r.document.provenance, r.score) for r in first] == [(r.document.provenance, r.score) for r in second]


# --------------------------------------------------------------------- citations


def test_format_citation_includes_module_and_source_path():
    provenance = Provenance(
        source_path="src/awci/knowledge/meteorology/orographic_turbulence.py",
        module="awci.knowledge.meteorology.orographic_turbulence",
        symbol="",
        git_commit=None,
    )
    document = Document(content="real content", provenance=provenance)
    citation = format_citation(document)
    assert "awci.knowledge.meteorology.orographic_turbulence" in citation
    assert "src/awci/knowledge/meteorology/orographic_turbulence.py" in citation
    assert "commit" not in citation  # no fabricated hash when None


def test_format_citation_includes_symbol_when_present():
    provenance = Provenance(
        source_path="src/awci/knowledge/meteorology/clouds.py",
        module="awci.knowledge.meteorology.clouds",
        symbol="CloudGenus",
        git_commit="a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0",
    )
    document = Document(content="real content", provenance=provenance)
    citation = format_citation(document)
    assert "awci.knowledge.meteorology.clouds.CloudGenus" in citation
    assert "commit a1b2c3d4" in citation  # short hash, real prefix of the real hash


def test_format_citation_never_fabricates_a_commit_when_none():
    provenance = Provenance(source_path="x.py", module="awci.knowledge.x", symbol="", git_commit=None)
    document = Document(content="c", provenance=provenance)
    assert "commit" not in format_citation(document)


def test_real_corpus_citations_are_all_well_formed():
    documents = build_document_corpus()
    for document in documents[:20]:
        citation = format_citation(document)
        assert document.provenance.module in citation
        assert document.provenance.source_path in citation


# --------------------------------------------------------------------- evidence-only discipline


def test_rag_package_never_imports_awci_complexity_or_hazards():
    """Strict one-way, read-only relationship: the RAG layer must never
    import from awci.complexity (the deterministic AWCI scoring engine)
    or awci.hazards (per-point computed diagnostics) - it only reads
    real, already-committed documentation text."""
    import awci.ai.rag.citations as citations_module
    import awci.ai.rag.documents as documents_module
    import awci.ai.rag.retriever as retriever_module

    for module in (documents_module, retriever_module, citations_module):
        source = module.__file__
        assert source is not None
        with open(source, encoding="utf-8") as handle:
            text = handle.read()
        assert "awci.complexity" not in text
        assert "awci.hazards" not in text


def test_rag_package_has_no_heavy_ml_dependency_imports():
    """No embedding library, vector store, or LLM client - the
    user-confirmed "no new dependency, no network" constraint, verified
    by source inspection rather than trusting the docstring alone."""
    import awci.ai.rag.citations as citations_module
    import awci.ai.rag.documents as documents_module
    import awci.ai.rag.retriever as retriever_module

    forbidden = ("openai", "anthropic", "sentence_transformers", "faiss", "chromadb", "torch", "requests", "httpx")
    for module in (documents_module, retriever_module, citations_module):
        source = module.__file__
        assert source is not None
        with open(source, encoding="utf-8") as handle:
            text = handle.read().lower()
        for name in forbidden:
            assert name not in text
