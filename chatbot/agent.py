from langchain.agents import AgentExecutor, create_react_agent
from langchain import hub
from langchain.tools import Tool
from llm import llm
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain.prompts import PromptTemplate
from chatbot.tools.vector import kg_qa_tool
from chatbot.tools.cipher import cypher_qa_tool



agent_prompt = PromptTemplate.from_template("""
You are a Pokemon expert providing information about Pokemon.
Be as helpful as possible and return as much information as possible.
Do not answer any questions that do not relate to Pokemon, their types, abilities, attacks, or evolutions.

Do not answer any questions using your pre-trained knowledge, only use the information provided in the context.

TOOLS:
------

You have access to the following tools:

{tools}

To use a tool, please use the following format:

```
Thought: Do I need to use a tool? Yes
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
```

When you have a response to say to the Human, or if you do not need to use a tool, you MUST use the format:

```
Thought: Do I need to use a tool? No
Final Answer: [your response here]
```

Begin!

Previous conversation history:
{chat_history}

New input: {input}
{agent_scratchpad}
""")

def general_chat_tool(input_str):
    print(f"Input to General Chat tool: {input_str}")
    try:
        response = llm.invoke(input_str)
        print(f"Response from General Chat tool: {response}")

        # Check the type of the response
        print(f"Type of response: {type(response)}")

        # Check if the response is of the expected type
        if hasattr(response, 'content'):
            return response.content
        else:
            return str(response)
        
    except Exception as e:
        print(f"Error in General Chat tool: {e}")
        return "Error occurred"


tools = [
    Tool.from_function(
        name="General Chat",
        description="For general chat not covered by other tools",
        func=general_chat_tool,
        return_direct=True
    ),
    Tool.from_function(
        name="Vector Search Index",  # (1)
        description="Provides information about Pokemon description using Vector Search, showing similarities", # (2)
        func = kg_qa_tool, # (3)
        return_direct=True
    ),
    Tool.from_function(
        name="Graph Cypher QA Chain",  # (1)
        description="Provides information about Movies including their Actors, Directors and User reviews", # (2)
        func = cypher_qa_tool, # (3)
        return_direct=True
    ),
]


memory = ConversationBufferWindowMemory(
    memory_key='chat_history',
    k=5,
    return_messages=True,
)

#agent_prompt = hub.pull("hwchase17/react-chat")
agent = create_react_agent(llm, tools, agent_prompt)
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    memory=memory,
    verbose=True
)




def generate_response(prompt):
    """
    Create a handler that calls the Conversational agent
    and returns a response to be rendered in the UI
    """
    print("generate_response called with prompt: ", prompt)
    response = agent_executor.invoke({"input": prompt})
    print(response["output"])

    return response['output']



