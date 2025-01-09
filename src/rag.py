import re

import chromadb

client = chromadb.PersistentClient(path="src/vdb/chroma_db_v2")
collection = client.get_collection("jira_collection_v2")

def clean_text(sentences):

    cleaned_sentences = []

    for sentence in sentences:
        sentence = sentence.replace("\n", " ").replace("\r", " ")
        cleaned_sentence = re.sub(r'[^A-Za-z0-9\s]', '', sentence)
        cleaned_sentence = cleaned_sentence.strip()
        cleaned_sentence = re.sub(r'\s+', ' ', cleaned_sentence)
        cleaned_sentences.append(cleaned_sentence)

    return cleaned_sentences

def rag_query(query, top_n=5, threshold=1.5):

        # Process results
    filtered_results = {
            "documents": [],
            "metadatas": [],
            "distances": [],
            "ids": []
        }

    try:
        query_clean = clean_text([query])[0]
        results = collection.query(query_texts=[query_clean], n_results=top_n)
        
        if len(results["metadatas"]) > 0:
            for idx, distance in enumerate(results["distances"][0]):
                print(f"distance found : {distance}")
                if distance <= threshold:
                    filtered_results["documents"].append(results["documents"][0][idx])
                    filtered_results["metadatas"].append(results["metadatas"][0][idx])
                    filtered_results["distances"].append(distance)
                    filtered_results["ids"].append(results["ids"][0][idx])

        return filtered_results

    except Exception as e:
        print(e)
        return
    
if __name__ == "__main__":

    question = "I want to annotate 100 images"
    top_sentences = rag_query(question, 5)

    print(top_sentences["metadatas"])
