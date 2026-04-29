# ---- Imports ---- #
from sqlalchemy.orm import Mapped,mapped_column
from sqlalchemy import BigInteger,Text,ForeignKey,Index
from sqlalchemy.dialects.postgresql import TSVECTOR
from pgvector.sqlalchemy import Vector
from db.base import Base


# ---------- Models ---------- #

# ---- Knowledge Base ---- #
class KnowledgeBase(Base):
    # ---- Table Name ---- #
    __tablename__="knowledge_base"

    # ---- Columns ---- #
    id:Mapped[int]=mapped_column(BigInteger,primary_key=True)
    subject_id:Mapped[int]=mapped_column(ForeignKey("subjects.id"))
    content:Mapped[str]=mapped_column(Text)
    embedding:Mapped[list[float]]=mapped_column(Vector(1024))

    search_vector=mapped_column(TSVECTOR)

    # ---- Indexes ---- #
    __table_args__=(
        Index("idx_kb_subject_id","subject_id"),
        Index("idx_kb_search_vector","search_vector",postgresql_using="gin"),
        Index("idx_kb_content_trgm","content",postgresql_using="gin",postgresql_ops={"content":"gin_trgm_ops"}),
    )