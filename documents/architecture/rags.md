# Retrieval-Agumentend Generative (RAG) Systems
A collection of RAG systems to be used by the agents in AFIE. 

## Components
All RAG systems contain the following components:

| Component Name | Description | Examples |
| -------------- | ----------- | -------- |
| `SourceData` | The collection of raw data that is the source of knowledge. | PDF files, codebase, websites, etc. |
| `SplittingStrategy` | A description, protocol, and potentialy functions for splitting the source data into chunks. Large documents will require splitting, while collections of smaller files can be used as chunks themselves. | Character splitting, semantic splitting, files-as-chunks |
| `EmbeddingModel` | The embedding model to use for vector encoding. | `embedding-model-001`, OpenAI or GoogleAI |
| `VectorStore` | The vector store with embeddings and chunks. This is a disk-cached store that persists. | Chroma DB |
| `Manager` | Strategy and functionality for keeping the vector store up to date as changes are made. | Dedicated code to re-run vectorization, or add documents to vector store |
| `Retriever` | The object that will retrieve documents from the vector store based on some kind of similarity and quantity criteria. | `MultiQueryRetriever` |
| `Exporter` | Takes the retrieved documents and packages them as a single block of text, with some brief preamble to assist interpretation. | Dedicated code to concatenate and augment documents. |

## Systems
The following is a collection of the RAG systems that will be implemented in the AFIE system:

### **`ProjectContextManager`**
Provides AFIE agents with relevant segments of code from the codebase of the game.
 * `SourceData`: The codebase of the game project, stored and maintained in a local GitHub repo.
 * `SplittingStrategy`: Semantic or file-based. Files under 150 lines should be vectorized as they are, while larger files will need to be split at contextually convenient points, e.g. classes, functions, methods. Splitting of classes will have to ensure context to the rest of the class is maintained.
 * `EmbeddingModel`: TBD, likely a standard model.
 * `VectorStore`: Chroma DB.
 * `Manager`: Custom code for updating. Given that the project codebase is continually evolving during development, it is likely most efficient to re-process the entire codebase following each successful feature implementation and validation. This will be the actual `ProjectContextManager`.
 * `Retriever`: TBD, likely `MultiQueryRetriever`.
 * `Exporter`: TBD, custom code.

 ### **`FeatureRequestHistory`**
The collection of feature requests that are input to the AFIE process. These are the features described by the human operator (and potentially a chat agent e.g. "production manager") and used as input to the technical architect to being the process of creating a FIP.
 * `SourceData`: Collection of markdown files, each file representing an approved feature request.
 * `SplittingStrategy`: File-based.
 * `EmbeddingModel`: TBD, likely a standard model.
 * `VectorStore`: Chroma DB.
 * `Manager`: Custom code for updating. Needs to add files to folder and vector store.
 * `Retriever`: TBD, likely `MultiQueryRetriever`.
 * `Exporter`: TBD, custom code.

 ### **`FeatureImplementationPackageCollection`**
The collection of FIPs that have been produced by AFIE.
 * `SourceData`: Collection of markdown files of FIPs as produced, reviewed, and approved in AFIE.
 * `SplittingStrategy`: File-based.
 * `EmbeddingModel`: TBD, likely a standard model.
 * `VectorStore`: Chroma DB.
 * `Manager`: Custom code for updating. Needs to add files to folder and vector store.
 * `Retriever`: TBD, likely `MultiQueryRetriever`.
 * `Exporter`: TBD, custom code.

 ### **`ArchitecturalDecisionRecord`**
The collection of summaries of architectural decisions that have been implemented. This does not contain all the details of the FIP, but rather is intended to be a summary of each feature after it is implemented and validated so AFIE can more easily understand the state of the game. Consider if this can be merged with the Feature Request History in a sensible way, or if one or the other is redundant.
 * `SourceData`: Collection of markdown files of architectural decisions.
 * `SplittingStrategy`: File-based.
 * `EmbeddingModel`: TBD, likely a standard model.
 * `VectorStore`: Chroma DB.
 * `Manager`: Custom code for updating. Needs to add files to folder and vector store. Needs an `ADRManager`.
 * `Retriever`: TBD, likely `MultiQueryRetriever`.
 * `Exporter`: TBD, custom code. 

 ### **`EngineDoc`**
A RAG providing context for the documentation of the chosen game engine.
 * `SourceData`: Game engine documentation website.
 * `SplittingStrategy`: Semantic.
 * `EmbeddingModel`: TBD, likely a standard model.
 * `VectorStore`: Chroma DB.
 * `Manager`: Basic. Will only need to be initialized once since the game engine will not change during the project.
 * `Retriever`: TBD, likely `MultiQueryRetriever`.
 * `Exporter`: TBD, custom code.

 ### **`EngineAPI`**
A RAG providing context for the API reference of the chosen game engine.
 * `SourceData`: Game engine API reference website.
 * `SplittingStrategy`: Semantic.
 * `EmbeddingModel`: TBD, likely a standard model.
 * `VectorStore`: Chroma DB.
 * `Manager`: Basic. Will only need to be initialized once since the game engine will not change during the project.
 * `Retriever`: TBD, likely `MultiQueryRetriever`.
 * `Exporter`: TBD, custom code.

 ### **`EngineCode`**
A RAG for providing context for the codebase of the chosen game engine.
 * `SourceData`: Game engine GitHub repository or local folder where the game engine is installed.
 * `SplittingStrategy`: Semantic or file-based. Files under 150 lines should be vectorized as they are, while larger files will need to be split at contextually convenient points, e.g. classes, functions, methods. Splitting of classes will have to ensure context to the rest of the class is maintained.
 * `EmbeddingModel`: TBD, likely a standard model.
 * `VectorStore`: Chroma DB.
 * `Manager`: Basic. Will only need to be initialized once since the game engine will not change during the project.
 * `Retriever`: TBD, likely `MultiQueryRetriever`.
 * `Exporter`: TBD, custom code.
