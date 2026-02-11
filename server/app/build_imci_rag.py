import os
import re
import math
import multiprocessing
from concurrent.futures import ThreadPoolExecutor, as_completed

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import FastEmbedEmbeddings


# ==============================
# SECTION SPLITTING
# ==============================

def split_by_sections(text):
    pattern = r"\n(?=[A-Z][A-Z\s\-]{5,}\n)|\n(?=\d+\.\s+[A-Z])"
    sections = re.split(pattern, text)
    return [s.strip() for s in sections if s.strip()]


def hybrid_chunking(text, max_chunk_size=800, overlap=150):
    sections = split_by_sections(text)

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=max_chunk_size,
        chunk_overlap=overlap,
        separators=["\n\n", "\n", ".", " "]
    )

    final_chunks = []

    for section in sections:
        if len(section) <= max_chunk_size:
            final_chunks.append(section)
        else:
            final_chunks.extend(splitter.split_text(section))

    return final_chunks


# ==============================
# BATCH PROCESSING
# ==============================

def batch_documents(chunks, batch_size):
    for i in range(0, len(chunks), batch_size):
        yield chunks[i:i + batch_size]


# ==============================
# MAIN BUILDER
# ==============================

def build_vector_db(pdf_path, persist_directory,
                    batch_size=64,
                    max_workers=None):

    if max_workers is None:
        max_workers = max(1, multiprocessing.cpu_count() - 1)

    print(f"🚀 Using {max_workers} CPU workers")

    print("📖 Loading PDF...")
    loader = PyPDFLoader(pdf_path)
    pages = loader.load()

    full_text = "\n".join([p.page_content for p in pages])

    print("✂️ Hybrid chunking...")
    chunks = hybrid_chunking(full_text)

    print(f"✅ Total chunks: {len(chunks)}")

    documents = [
        Document(page_content=chunk, metadata={"source": "IMCI Handbook"})
        for chunk in chunks
    ]

    embeddings = FastEmbedEmbeddings()

    print("🧠 Creating Chroma DB...")
    db = Chroma(
        embedding_function=embeddings,
        persist_directory=persist_directory
    )

    print("⚙️ Embedding + inserting in batches...")

    with ThreadPoolExecutor(max_workers=max_workers) as executor:

        futures = []

        for batch in batch_documents(documents, batch_size):
            futures.append(executor.submit(db.add_documents, batch))

        total_batches = len(futures)

        for i, future in enumerate(as_completed(futures), 1):
            future.result()
            print(f"📦 Batch {i}/{total_batches} inserted")

    db.persist()
    print("🎉 Vector DB successfully built and persisted!")


# ==============================
# RUN
# ==============================

if __name__ == "__main__":

    PDF_PATH = r"C:\Users\91733\Desktop\Medgemma\server\data\imci_handbook.pdf"
    PERSIST_DIR = "./vector_store/imci_handbook_db"

    os.makedirs("./vector_store", exist_ok=True)

    build_vector_db(
        pdf_path=PDF_PATH,
        persist_directory=PERSIST_DIR,
        batch_size=64
    )
