### **For downloading and parsing the necessary data**
- Please execute the init.py.
This will create the folder /data/parsed_data with all XML files.

## **Setting Up Neo4j with XML Data**

### **1. Install Neo4j**
- Download and install Neo4j from [Neo4j's official website](https://neo4j.com/download/).
- Start Neo4j and create a new database.

### **2. Install Python Libraries**
- Install the Neo4j Python driver:
  ```
  pip install neo4j
  ```
### **3. Configure the Script**
Update the uri, user, and password variables in the script to match your Neo4j database settings.
Set the path to your XML files in the folder_path variable.
###4. Run the Script
Execute the Python script to parse XML files and import data into Neo4j:
```
python parseXML.py
```

### **5. Verify Data**
Open Neo4j Browser at http://localhost:7474 to check and query your imported data.

## **Setting up the CHatbot with Streamlit and Neo4J**

### **1. Configure OpenAI key::**

- Obtain an API key from OpenAI


### **2. Set up secrets.toml:**
- Create a .streamlit folder in your project root
- Inside .streamlit, create a secrets.toml file
- Add the following to secrets.toml:
```
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USERNAME = "your_username"
NEO4J_PASSWORD = "your_password"
OPENAI_API_KEY = "your_openai_api_key"
OPENAI_MODEL = "gpt-3.5-turbo"
```


### **3. Start Streamlit::**


Open a terminal in your project directory
Run the command:
```
streamlit run chatbot/bot.py
```








