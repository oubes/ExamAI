# ---- Imports ---- #
from sqlalchemy import text
from db.base import Base
from db.session import engine

from db.models.identity import *
from db.models.academic import *
from db.models.assessment import *
from db.models.knowledge import *


# ---------- Init DB ---------- #
async def init_db():

    # ---- Begin Transaction ---- #
    async with engine.begin() as conn:

        # ---- Extensions ---- #
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm"))

        # ---- Create Tables ---- #
        await conn.run_sync(Base.metadata.create_all)

        # ---- Search Vector Function (Generic) ---- #
        await conn.execute(text("""
        CREATE OR REPLACE FUNCTION update_search_vector()
        RETURNS trigger AS $$
        BEGIN
            NEW.search_vector := to_tsvector('english', COALESCE(NEW.search_text, ''));
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """))

        # ---- Trigger: Questions ---- #
        await conn.execute(text("""
        DO $$ BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname='question_search_vector_trigger') THEN
                ALTER TABLE questions ADD COLUMN IF NOT EXISTS search_text text;
                CREATE TRIGGER question_search_vector_trigger
                BEFORE INSERT OR UPDATE ON questions
                FOR EACH ROW
                EXECUTE FUNCTION update_search_vector();
            END IF;
        END $$;
        """))

        # ---- Trigger: Knowledge Base ---- #
        await conn.execute(text("""
        DO $$ BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname='kb_search_vector_trigger') THEN
                ALTER TABLE knowledge_base ADD COLUMN IF NOT EXISTS search_text text;
                CREATE TRIGGER kb_search_vector_trigger
                BEFORE INSERT OR UPDATE ON knowledge_base
                FOR EACH ROW
                EXECUTE FUNCTION update_search_vector();
            END IF;
        END $$;
        """))

        # ---- Trigger: Model Answers ---- #
        await conn.execute(text("""
        DO $$ BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname='model_answer_search_vector_trigger') THEN
                ALTER TABLE model_answers ADD COLUMN IF NOT EXISTS search_text text;
                CREATE TRIGGER model_answer_search_vector_trigger
                BEFORE INSERT OR UPDATE ON model_answers
                FOR EACH ROW
                EXECUTE FUNCTION update_search_vector();
            END IF;
        END $$;
        """))