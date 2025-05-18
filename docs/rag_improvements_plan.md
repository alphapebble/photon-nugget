# Advanced RAG Improvements for Solar Sage

This document outlines planned improvements to the Retrieval Augmented Generation (RAG) system in Solar Sage, based on techniques from the [langchain-ai/rag-from-scratch](https://github.com/langchain-ai/rag-from-scratch) repository and other advanced RAG research.

## Table of Contents

- [Overview](#overview)
- [Implementation Phases](#implementation-phases)
- [Detailed Techniques](#detailed-techniques)
- [Energy Sector Applications](#energy-sector-applications)
- [Implementation Roadmap](#implementation-roadmap)
- [Evaluation Strategy](#evaluation-strategy)

## Overview

The current Solar Sage RAG system provides basic retrieval and generation capabilities. By implementing advanced RAG techniques, we can significantly improve the quality, relevance, and accuracy of responses, particularly for complex energy sector queries.

## Implementation Phases

### Phase 1: Immediate Improvements

These improvements can be implemented quickly and will provide significant benefits:

1. **Query Expansion**
2. **Reranking**
3. **Enhanced Evaluation Framework**

### Phase 2: Medium-term Improvements

These improvements require more development effort but provide substantial enhancements:

1. **Hybrid Search**
2. **Contextual Compression**
3. **Metadata Filtering**

### Phase 3: Advanced Features

These advanced features represent the cutting edge of RAG technology:

1. **FLARE Implementation**
2. **Knowledge Graph Integration**
3. **Self-Querying Retrieval**

## Detailed Techniques

### 1. Query Expansion

**Description**: Generate multiple variations of the user's query to improve recall.

**Implementation**:
```python
def expand_query(query: str, llm) -> List[str]:
    """Generate multiple query variations to improve retrieval."""
    prompt = f"""
    Generate 3 different versions of the following query to help with document retrieval.
    Make each version focus on different aspects or use different terminology.
    Original query: {query}
    
    Return only the 3 queries, one per line.
    """
    response = llm.generate(prompt)
    return [q.strip() for q in response.split('\n') if q.strip()]
```

**Energy Sector Example**:
- Original query: "How do solar panels perform in cloudy weather?"
- Expanded queries:
  1. "What is the efficiency of photovoltaic systems during overcast conditions?"
  2. "Do solar arrays generate electricity on cloudy days?"
  3. "Impact of cloud cover on solar energy production"

### 2. Reranking

**Description**: Apply a second-stage ranking to initial retrieval results to improve precision.

**Implementation**:
```python
def rerank_documents(query: str, documents: List[str], reranker) -> List[str]:
    """Rerank retrieved documents using a cross-encoder model."""
    pairs = [[query, doc] for doc in documents]
    scores = reranker.predict(pairs)
    
    # Sort documents by score
    ranked_results = sorted(zip(documents, scores), key=lambda x: x[1], reverse=True)
    return [doc for doc, _ in ranked_results]
```

**Energy Sector Example**:
- Query: "What maintenance is required for residential solar installations?"
- Initial retrieval might return general maintenance documents
- Reranking would prioritize documents specifically about residential systems

### 3. Hybrid Search

**Description**: Combine semantic search with keyword-based search for better retrieval performance.

**Implementation**:
```python
def hybrid_search(query: str, vector_db, keyword_index, alpha: float = 0.5) -> List[str]:
    """Combine vector search with keyword search."""
    # Get vector search results
    vector_results = vector_db.search(query, k=10)
    
    # Get keyword search results
    keyword_results = keyword_index.search(query, k=10)
    
    # Combine results with weighted scoring
    combined_results = {}
    for doc, score in vector_results:
        combined_results[doc] = alpha * score
        
    for doc, score in keyword_results:
        if doc in combined_results:
            combined_results[doc] += (1 - alpha) * score
        else:
            combined_results[doc] = (1 - alpha) * score
    
    # Sort by combined score
    sorted_results = sorted(combined_results.items(), key=lambda x: x[1], reverse=True)
    return [doc for doc, _ in sorted_results[:10]]
```

**Energy Sector Example**:
- Query: "solar panel efficiency degradation over time"
- Vector search captures semantic meaning of degradation and efficiency
- Keyword search ensures documents with exact terms "solar panel" are included

### 4. Contextual Compression

**Description**: Extract only the most relevant parts of retrieved documents to include more context within the LLM's context window.

**Implementation**:
```python
def compress_documents(query: str, documents: List[str], llm) -> List[str]:
    """Extract only the relevant portions of each document."""
    compressed_docs = []
    for doc in documents:
        prompt = f"""
        Extract only the portions of the following document that are relevant to the query.
        Query: {query}
        Document: {doc}
        
        Relevant portions:
        """
        compressed = llm.generate(prompt)
        compressed_docs.append(compressed)
    return compressed_docs
```

**Energy Sector Example**:
- Query: "How do solar inverters handle power outages?"
- Original document: A 10-page technical specification of inverters
- Compressed document: Only the sections about grid disconnection and backup power

### 5. FLARE (Forward-Looking Active REtrieval)

**Description**: Implement iterative retrieval where the LLM can request additional information during generation.

**Implementation**:
```python
def flare_generation(query: str, initial_docs: List[str], retriever, llm, max_iterations: int = 3) -> str:
    """Generate response with Forward-Looking Active REtrieval."""
    context = "\n".join(initial_docs)
    response_so_far = ""
    
    for i in range(max_iterations):
        prompt = f"""
        Query: {query}
        Context: {context}
        Response so far: {response_so_far}
        
        Continue the response. If you need more information, respond with NEED_INFO: [specific question].
        Otherwise, continue with CONTINUE: [next part of response]
        """
        
        next_step = llm.generate(prompt)
        
        if next_step.startswith("NEED_INFO:"):
            # Extract the question
            follow_up_question = next_step.replace("NEED_INFO:", "").strip()
            
            # Retrieve additional information
            additional_docs = retriever.retrieve(follow_up_question)
            context += "\n" + "\n".join(additional_docs)
        
        elif next_step.startswith("CONTINUE:"):
            # Add to the response
            next_part = next_step.replace("CONTINUE:", "").strip()
            response_so_far += " " + next_part
        
        else:
            # Just add the response as is
            response_so_far += " " + next_step
    
    return response_so_far
```

**Energy Sector Example**:
- Query: "What's the ROI for installing solar in Arizona with the new tax credits?"
- Initial retrieval: General information about solar ROI and tax credits
- FLARE follow-up: "What are the specific solar irradiance levels in Arizona?"
- Second retrieval: Arizona-specific solar production data
- Final response: Accurate ROI calculation incorporating all factors

### 6. Metadata Filtering

**Description**: Enhance retrieval with metadata filters to narrow down results.

**Implementation**:
```python
def metadata_filtered_retrieval(query: str, metadata_filters: Dict[str, Any], retriever) -> List[str]:
    """Retrieve documents with metadata filtering."""
    return retriever.retrieve(
        query=query,
        filters=metadata_filters,
        top_k=5
    )
```

**Energy Sector Example**:
- Query: "Recent advancements in solar panel efficiency"
- Metadata filter: {"document_type": "research_paper", "publication_date": {"$gt": "2022-01-01"}}
- Result: Only recent research papers on solar efficiency

### 7. Knowledge Graph Integration

**Description**: Enhance retrieval with structured relationships from a knowledge graph.

**Implementation**:
```python
def knowledge_graph_enhanced_retrieval(query: str, kg, retriever) -> List[str]:
    """Enhance retrieval with knowledge graph relationships."""
    # Extract entities from query
    entities = extract_entities(query)
    
    # Get related entities from knowledge graph
    related_entities = []
    for entity in entities:
        related = kg.get_related_entities(entity)
        related_entities.extend(related)
    
    # Expand query with related entities
    expanded_query = f"{query} {' '.join(related_entities)}"
    
    # Retrieve with expanded query
    return retriever.retrieve(expanded_query)
```

**Energy Sector Example**:
- Query: "How do microinverters compare to string inverters?"
- KG identifies: microinverters related to "Enphase", "module-level", "rapid shutdown"
- KG identifies: string inverters related to "SMA", "central conversion", "single point failure"
- Enhanced retrieval includes these related concepts

## Energy Sector Applications

### 1. Complex Technical Queries

**Example Query**: "What's the impact of partial shading on different solar panel technologies?"

**Current System**: Might retrieve general information about shading impacts.

**Improved System**: 
- Query expansion generates variations about "partial shading effects on monocrystalline vs. polycrystalline panels"
- Reranking prioritizes documents with specific technical comparisons
- FLARE retrieves additional information about bypass diodes and hotspot formation

### 2. Location-Specific Solar Performance

**Example Query**: "How would a 10kW solar system perform in Seattle compared to Phoenix?"

**Current System**: Might provide general information about geographic differences.

**Improved System**:
- Metadata filtering retrieves location-specific solar irradiance data
- Knowledge graph integration adds information about typical weather patterns
- Contextual compression extracts only the relevant performance metrics

### 3. Financial and Regulatory Analysis

**Example Query**: "What's the payback period for commercial solar with the new IRA tax credits?"

**Current System**: Might provide generic information about tax credits.

**Improved System**:
- Hybrid search combines semantic understanding with specific IRA terminology
- Metadata filtering focuses on commercial installations
- FLARE retrieves additional information about depreciation schedules and specific state incentives

### 4. Troubleshooting and Diagnostics

**Example Query**: "Why is my solar production lower than expected in the afternoon?"

**Current System**: Might provide general reasons for production issues.

**Improved System**:
- Query expansion generates variations about "afternoon solar production drop"
- Knowledge graph integration adds related concepts like "western orientation" and "temperature coefficient"
- Reranking prioritizes documents about time-of-day performance factors

### 5. Grid Integration Queries

**Example Query**: "How do smart inverters help with grid stability during peak demand?"

**Current System**: Might provide basic information about smart inverters.

**Improved System**:
- Hybrid search captures both technical and policy documents
- Contextual compression extracts specific grid support functions
- FLARE retrieves additional information about frequency regulation and voltage support

## Implementation Roadmap

### Phase 1 (1-2 months)

1. **Query Expansion** (2 weeks)
   - Implement basic LLM-based query expansion
   - Integrate with existing retrieval pipeline
   - Test with energy sector queries

2. **Reranking** (2 weeks)
   - Implement cross-encoder reranking
   - Optimize for solar energy domain
   - Benchmark against baseline retrieval

3. **Enhanced Evaluation** (2 weeks)
   - Implement RAGAS metrics
   - Create energy-specific evaluation dataset
   - Set up automated evaluation pipeline

### Phase 2 (2-3 months)

4. **Hybrid Search** (3 weeks)
   - Implement BM25 keyword search
   - Develop combination algorithm
   - Optimize weighting for energy domain

5. **Contextual Compression** (3 weeks)
   - Implement LLM-based document compression
   - Optimize prompt for energy technical content
   - Benchmark context window utilization

6. **Metadata Filtering** (2 weeks)
   - Enhance document schema with energy-specific metadata
   - Implement filtering in retrieval pipeline
   - Create user interface for filter selection

### Phase 3 (3-4 months)

7. **FLARE Implementation** (4 weeks)
   - Develop iterative retrieval mechanism
   - Implement specialized prompting
   - Test with complex energy queries

8. **Knowledge Graph Integration** (6 weeks)
   - Build energy domain knowledge graph
   - Implement graph-enhanced retrieval
   - Connect entities to document retrieval

9. **Self-Querying Retrieval** (4 weeks)
   - Implement LLM-based query generation
   - Create structured query templates
   - Test with diverse energy questions

## Evaluation Strategy

We will evaluate improvements using:

1. **Retrieval Metrics**:
   - Precision@k
   - Recall@k
   - Mean Reciprocal Rank (MRR)

2. **RAG-specific Metrics** (using RAGAS):
   - Context Relevancy
   - Answer Relevancy
   - Faithfulness
   - Context Recall

3. **Energy Domain Specific Tests**:
   - Technical accuracy on solar terminology
   - Accuracy of performance calculations
   - Regulatory compliance information

4. **User Experience Metrics**:
   - Response time
   - User satisfaction ratings
   - Follow-up question rate
