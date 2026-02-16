import os
import re
import shutil

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import FastEmbedEmbeddings

from metadata_extractor import extract_metadata


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
# MAIN BUILDER
# ==============================

from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing


def build_vector_db(pdf_path, persist_directory, reset_db=False):

    if reset_db and os.path.exists(persist_directory):
        print("🗑 Resetting existing vector database...")
        shutil.rmtree(persist_directory)

    print("📖 Loading PDF...")
    loader = PyPDFLoader(pdf_path)
    pages = loader.load()

    full_text = "\n".join([p.page_content for p in pages])

    print("✂️ Hybrid chunking...")
    chunks = hybrid_chunking(full_text)

    print(f"✅ Total chunks: {len(chunks)}")

    print("🧠 Extracting metadata using multiprocessing...")

    max_workers = max(1, multiprocessing.cpu_count() - 1)

    metadata_results = []

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(extract_metadata, chunk): chunk for chunk in chunks}

        for i, future in enumerate(as_completed(futures), 1):
            metadata = future.result()
            metadata_results.append(metadata)
            print(f"   Metadata processed {i}/{len(chunks)}")

    print("📦 Creating documents...")

    documents = []
    for chunk, metadata in zip(chunks, metadata_results):
        metadata["source"] = "IMCI Handbook"

        documents.append(
            Document(
                page_content=chunk,
                metadata=metadata
            )
        )

    embeddings = FastEmbedEmbeddings()

    print("🧠 Creating Chroma DB...")

    db = Chroma(
        collection_name="imci_handbook",
        embedding_function=embeddings,
        persist_directory=persist_directory
    )

    print("⚙️ Adding documents to Chroma (single-threaded safe insert)...")

    db.add_documents(documents)

    db.persist()

    print("🎉 IMCI Vector DB (Parallel Processed) successfully built!")
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
        reset_db=True   # Automatically clears old DB
    )
