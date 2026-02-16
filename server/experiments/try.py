from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import FastEmbedEmbeddings
from collections import Counter

db = Chroma(
    collection_name="imci_handbook",
    persist_directory="./vector_store/imci_handbook_db",
    embedding_function=FastEmbedEmbeddings()
)

data = db.get(include=["metadatas"])
metas = data["metadatas"]

print("Total docs:", len(metas))

print("Age Group Distribution:")
print(Counter([m["age_group"] for m in metas]))

print("\nSymptom Category Distribution:")
print(Counter([m["symptom_category"] for m in metas]))

print("\nSection Type Distribution:")
print(Counter([m["section_type"] for m in metas]))

print("\nSeverity Distribution:")
print(Counter([m["severity_hint"] for m in metas]))
