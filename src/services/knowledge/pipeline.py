# ---- Imports ---- #
from pathlib import Path
from src.services.knowledge.reading.reader import PyMuPDFDocumentLoader
from src.services.knowledge.chunking.chunker import chunker
from src.domain.storage.services.upload_file import UploadService
from src.domain.knowledge.services.knowledge_base import KnowledgeBaseService
from src.infra.db.session import session_local
from uuid import UUID


# ---- Pdf Reader ---- #
pdf_reader = PyMuPDFDocumentLoader()

# ---- Upload Service ---- #
upload_service = UploadService()
knowledge_base_service = KnowledgeBaseService()

# ---- Session ---- #
session = session_local()

# ---- Knowledge Pipeline ---- #
class KnowledgePipeline:

    # ---- Run ---- #
    async def run(
        self,
        file_id: str,
        subject_id: str,
    ) -> list[dict]:

        # ---- Resolve Path ---- #
        file_info = upload_service.get_by_id(session, UUID(file_id))
        path = Path(file_info.path) # type: ignore

        # ---- Load Documents ---- #
        docs_loader = pdf_reader.load(file_path=path)


        # ---- Chunk Documents ---- #
        chunks = await chunker.chunk_documents(
            documents=docs_loader,
            doc_name=path.name,
        )
        
        payload = [
            {
                "subject_id": subject_id,
                "document_id": file_id,
                "chunk_index": chunk["chunk_index"],
                "content": chunk["content"],
                "summary": chunk["summary"],
                "embedding": chunk["embedding"],
            }
            for chunk in chunks
        ]
        
        knowledge_response = await knowledge_base_service.bulk_create(session, payload)

        return chunks


# ---- DI ---- #
knowledge_pipeline = KnowledgePipeline()