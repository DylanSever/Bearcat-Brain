'''
Dylan Sever
1/28/2026
Data ingestion program for database
'''

import chromadb
import os
import uuid #unique chunk generation. don't want bloated files!

#define paths of materials and destionations

DB_PATH = "./bearcat_db"
SOURCE_FOLDER ="./source_documents"
COLLECTION_NAME = "cpp_curriculum"

#check for folder destination already existing. will help with adding more content
if not os.path.exists(SOURCE_FOLDER):
    os.makedirs(SOURCE_FOLDER)
    PRINT(f"Created folder '{SOURCE_FOLDER}' . Please put any files in there and run this again.")

#initialize chroma and connect
print("Connecting to the Bearcat Brain...")
client = chromadb.PersistentClient(path=DB_PATH)
collection = client.get_or_create_collection(name=COLLECTION_NAME)

#read in and process files
files_processed= 0
print(f"Scanning '{SOURCE_FOLDER}' for documents...")

for filename in os.listdir(SOURCE_FOLDER):
    if filename.endswith(".txt"):
        file_path = os.path.join(SOURCE_FOLDER, filename)

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text_content = f.read()
                #skip empty files
            if not text_content.strip():
                continue
#chunk data
            print(f"Ingesting: {filename}")

            collection.upsert(
                documents=[text_content],
                metadatas=[{"source": filename}],
                ids=[str(uuid.uuid4())] #random chunk ID
            )
            files_processed +=1
        except Exception as e:
            print(f"Error reading {filename}: {e}")
#show ingested files and DB collection
print(f"\n Success! Processed {files_processed} files.")
print(f"Total documents in memory: {collection.count()}")
