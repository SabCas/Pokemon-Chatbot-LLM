from langchain_community.vectorstores.neo4j_vector import Neo4jVector

def retrieve_vectors_from_neo4j(index_name):
    try:
        vector_store = Neo4jVector()  # Instantiate if necessary
        vectors = vector_store.from_existing_index(index_name)
        return vectors
    except ValueError as e:
        print(f"Error retrieving vectors: {e}")
        return None

index_name = "pokemonDescriptionsIndex"  # Replace with your actual vector index name
vectors = retrieve_vectors_from_neo4j(index_name)

if vectors:
    print(f"Retrieved {len(vectors)} vectors from '{index_name}'")
else:
    print(f"Failed to retrieve vectors from '{index_name}'")
