import streamlit as st
from langchain_community.vectorstores.neo4j_vector import Neo4jVector
from llm import llm, embeddings
from langchain.chains import RetrievalQA


# Neo4j Vector Store setup
neo4jvector = Neo4jVector.from_existing_index(
    embeddings,
    url=st.secrets["NEO4J_URI"],
    username=st.secrets["NEO4J_USERNAME"],
    password=st.secrets["NEO4J_PASSWORD"],
    index_name="PokemonIndex",  # Adjusted index name
    node_label="Pokemon",
    text_node_property="description",
    embedding_node_property="descriptionEmbedding",
    retrieval_query="""
RETURN
    node.description AS text,
    score,
    {
        name: node.name,
        types: [ (type)-[:HAS_TYPE]->(node) | type.name ],
        abilities: [ (ability)-[:HAS_ABILITY]->(node) | ability.name ],
        attacks: [ (attack)-[:LEARNS]->(node) | attack.name ],
        evolutions: [ (evolution)-[:EVOLVES_TO]->(node) | evolution.name ]
    } AS metadata
"""
)

retriever = neo4jvector.as_retriever()

kg_qa = RetrievalQA.from_chain_type(
    llm,
    chain_type="stuff",
    retriever=retriever,
)

def kg_qa_tool(input_str):
    print(f"Input to Vector Search tool: {input_str}")
    try:
        response = kg_qa({"query": input_str})
        print(f"Response from Vector Search tool: {response}")

        # Ensure the response is a string
        response_content = response.get("result", "")
        if not isinstance(response_content, str):
            response_content = str(response_content)

        return response_content
    except Exception as e:
        print(f"Error in Vector Search tool: {e}")
        return "An error occurred while processing your request."
