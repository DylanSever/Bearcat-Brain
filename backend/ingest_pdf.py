#dylan sever
#2/6/2026
#allows the ingestion of PDFs (specifically a c++ book for this project), chunk them by each page, and sves them into the vector database (chromaDB) for the ai to search.
import chromadb #vector database
import os
import uuid # generating unique ids for chunks
from pypdf import PdfReader # reads PDFs

#chroma db steup - path to files, resource locations, name of complete collection
DB_PATH = "./bearcat_db"
SOURCE_FOLDER = "./source_documents"
COLLECTION_NAME = "cpp_curriculum"

def ingest_pdfs():
    # function that will scan folder for PDFs, read them, and index it into the ChromaDB
    print(f"Connecting to database at {DB_PATH}...")
    #connect to DB
    client = chromadb.PersistentClient(path=DB_PATH)
    #find collection of material
    collection = client.get_or_create_collection(name=COLLECTION_NAME)

    if not os.path.exists(SOURCE_FOLDER):
        print(f"Error: Folder '{SOURCE_FOLDER}' not found.")
        return

    print(f"Scanning '{SOURCE_FOLDER}' for PDFs only...")
    pdf_count = 0
    #loop for filenames in folder to find PDFs
    for filename in os.listdir(SOURCE_FOLDER):
        if filename.endswith(".pdf"):
            file_path = os.path.join(SOURCE_FOLDER, filename)
            print(f"\nProcessing: {filename}")
    #open the PDF
            try:
                reader = PdfReader(file_path)
                total_pages = len(reader.pages)
    #read each page to ingest it
                for i, page in enumerate(reader.pages):
                    text = page.extract_text()
    #skip blank pages
                    if not text or not text.strip():
                        continue
   #allows for AI to know where the text came from
                    final_text =f"Source: {filename}, Page {i+1}\n\n{text}"
   #save to database
                    collection.upsert(
                        documents=[final_text],
                        metadatas=[{"source": filename, "page": i+1, "type":"pdf"}],
                        ids=[str(uuid.uuid4())]
                    )

                    print(f"      > Ingested Page {i+1}/{total_pages}", end='\r')
                pdf_count +=1
                print(f"      > Finished {filename}!               ")
            except Exception as e:
                print(f"\n    x Error reading {filename}: {e}")

    print(f"\n\nMission Complete.")
    print(f"Total documents in memory: {collection.count()}")

if __name__ == "__main__":
    ingest_pdfs()
