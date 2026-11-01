# Mental Health Information Retrieval Engine

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.9%2B-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Flask-Core_Framework-black?style=for-the-badge&logo=flask&logoColor=white" alt="Flask">
  <img src="https://img.shields.io/badge/NLTK-NLP_Pipeline-green?style=for-the-badge&logo=python&logoColor=white" alt="NLTK">
  <img src="https://img.shields.io/badge/Algorithm-TF--IDF%20%26%20Cosine-orange?style=for-the-badge" alt="Algorithm">
</p>

---

## Overview

A domain-specific search and retrieval system engineered to index, rank, and query mental health and psychological literature using a native Vector Space Model (VSM) and algebraic text representation.

The platform processes unstructured clinical and informational texts, converts document collections into term-frequency multidimensional vector spaces, and evaluates user queries using cosine similarity metrics. The implementation builds the core Information Retrieval (IR) pipeline from first principles, ensuring low memory consumption and deterministic scoring without external search library dependencies.

---

## Architecture and Execution Pipeline

Below are the engineering blueprints and execution workflows of the system:

<table align="center" width="100%">
  <tr>
    <td width="50%" align="center">
      <b>Core System Architectural Flow</b><br><br>
      <img src="image_d05b22.png" alt="Core System Architectural Flow" width="100%" style="border-radius: 8px; border: 1px solid #ddd;"/>
      <p><i>End-to-end data pipeline from raw corpus ingestion to inverted index generation and user interface routing.</i></p>
    </td>
    <td width="50%" align="center">
      <b>Data Processing & Query Matching Execution</b><br><br>
      <img src="image_d05b40.png" alt="Data Processing & Query Matching Execution" width="100%" style="border-radius: 8px; border: 1px solid #ddd;"/>
      <p><i>NLP preprocessing, algebraic vector transformation, cosine scoring, and result ranking.</i></p>
    </td>
  </tr>
</table>

---

## Core Technical Features

- **Linguistic Preprocessing:** Normalizes input text by removing common stop words using NLTK resources and applying the Porter Stemming Algorithm to map morphological variants to single lexical roots.
- **Serialized Inverted Index:** Generates and maintains a structured mapping file (`inverted_index.json`) correlating terms with document occurrences to enable fast lookups.
- **Vector Space Scoring:** Dynamically builds sparse TF-IDF weight representations for queries and documents, calculating geometric alignment via vector dot products.
- **Context Snippets and Highlighting:** Locates matching query terms within target documents, extracting context windows and applying inline styling tags for clear snippet rendering.
- **Direct Source Verification:** Automatically maps query results to corresponding reference endpoints for verification and extended reading.

---

## Mathematical Formulation

Vector weights and query alignments are computed through standard Information Retrieval formulations:

### 1. Term Frequency ($TF$)
Quantifies the occurrence frequency of term $t$ within document $d$:

$$\text{TF}(t, d) = f_{t, d}$$

### 2. Inverse Document Frequency ($IDF$)
Measures the discriminatory power of term $t$ across the entire corpus collection $D$:

$$\text{IDF}(t) = \log_{10}\left(\frac{\vert{}D\vert{}}{\vert{}\{d \in D : t \in d\}\vert{}}\right)$$

### 3. Geometric Vector Alignment (Cosine Similarity)
Measures the angular deviation between the dynamic query vector $\vec{q}$ and the document vector $\vec{d}$:

$$\text{Similarity}(\vec{q}, \vec{d}) = \frac{\vec{q} \cdot \vec{d}}{\Vert{}\vec{q}\Vert{} \Vert{}\vec{d}\Vert{}} = \frac{\sum_{i} q_i d_i}{\sqrt{\sum_{i} q_i^2} \sqrt{\sum_{i} d_i^2}}$$

---

## Directory Layout

```text
├── articles/               # Extracted plain text documents for indexing
├── templates/              # Jinja2 presentation templates
│   └── index.html          # Web interface layout
├── app.py                  # Flask routing and search endpoint handler
├── search_engine.py        # Core Information Retrieval logic and scoring modules
├── build_index.py          # Script for parsing text and serializing inverted index
├── setup_articles.py       # Corpus extractor parsing raw JSON into individual files
├── articles_data.json      # Structured dataset containing article metadata and URLs
├── inverted_index.json     # Serialized dictionary mapping terms to document postings
├── image_d05b22.png        # System architecture diagram
└── image_d05b40.png        # Query execution pipeline flowchart
