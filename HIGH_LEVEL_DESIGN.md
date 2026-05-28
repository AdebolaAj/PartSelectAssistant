# High-Level Design

```mermaid
flowchart LR
    subgraph LEFT[" "]
        direction LR
        DF[Data Files]
        WS[Web Scraper]
        WS --> DF
    end

    subgraph USERFLOW[" "]
        direction TB
        U((User))
        UQ[User Query]
        IS{In scope?<br/>DeepSeek LLM}
        U --> UQ --> IS
        IS -- No --> U
    end

    subgraph RAG["Retrieval-Augmented Generation"]
        direction LR
        ST[Sentence<br/>Transformer]
        C[(Chroma Vector<br/>DB)]
        API[FastAPI<br/>Microservice]
        LLM[DeepSeek Language<br/>Model]

        ST -->|Embeddings| C
        C <--> API
        API -->|Retrieved Context| LLM
    end

    DF --> ST
    UQ -->|User Query| API
    UQ -.->|User Query +<br/>Previous Messages| LLM
    IS -- Yes --> LLM

    classDef data fill:#ffe14a,stroke:#d1b200,color:#222,stroke-width:1px;
    classDef scraper fill:#f6d2ac,stroke:#d3a97a,color:#222,stroke-width:1px;
    classDef transformer fill:#f5a25b,stroke:#cc7d37,color:#222,stroke-width:1px;
    classDef service fill:#d9d3ff,stroke:#a8a0e8,color:#222,stroke-width:1px;
    classDef llm fill:#80aef7,stroke:#5b8fe3,color:#222,stroke-width:1px;
    classDef db fill:#b9efc7,stroke:#62b37d,color:#222,stroke-width:1px;
    classDef decision fill:#262933,stroke:#262933,color:#fff,stroke-width:1px;
    classDef user fill:#ffffff,stroke:#6a6f7d,color:#222,stroke-width:1px;

    class DF data;
    class WS scraper;
    class ST transformer;
    class API service;
    class LLM,UQ llm;
    class C db;
    class IS decision;
    class U user;

    style RAG fill:transparent,stroke:#8a8a8a,stroke-dasharray: 5 5
    style LEFT fill:transparent,stroke:transparent
    style USERFLOW fill:transparent,stroke:transparent
```

## Summary

- The frontend handles the chat experience and calls DeepSeek directly for scope check and answer generation.
- The Python backend handles retrieval by embedding the user query and searching ChromaDB for relevant product context.
- The scraper and `load_docs.py` prepare the knowledge base ahead of time from PartSelect product and repair pages.
- ChromaDB sits in the middle as the vector store used during live chat responses.
