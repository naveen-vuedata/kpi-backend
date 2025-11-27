from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
import os
from typing import Dict
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from langchain.agents import create_agent


# LangChain imports - using the correct imports
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory, InMemoryChatMessageHistory

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not found in environment variables")

def getAPIKey() -> str:
    if( not api_key ):
        raise ValueError("API key is missing")
    return api_key
# -----------------------------------------------------------
# Initialize LLM
# -----------------------------------------------------------

llm = ChatOpenAI(
    model="gpt-4o",
    api_key=getAPIKey,
    temperature=0.3
)
DATABASE_URL = "postgresql://postgres:3sqBYmY6FNUhJn9s@db.kogmedbmshsetsmqelvp.supabase.co:5432/postgres"
db = SQLDatabase.from_uri(DATABASE_URL)
toolkit = SQLDatabaseToolkit(db=db, llm=llm)


tools = toolkit.get_tools()

# for tool in tools:
#     print(f"{tool.name}: {tool.description}\n")
# print(f"Dialect: {db.dialect}")
# print(f"Available tables: {db.get_usable_table_names()}")
# print(f'Sample output: {db.run("SELECT * FROM clients LIMIT 5;")}')

system_prompt = """
You are an agent designed to interact with a SQL database.
Given an input question, create a syntactically correct {dialect} query to run,
then look at the results of the query and return the answer. Unless the user
specifies a specific number of examples they wish to obtain, always limit your
query to at most {top_k} results.

You can order the results by a relevant column to return the most interesting
examples in the database. Never query for all the columns from a specific table,
only ask for the relevant columns given the question.

You MUST double check your query before executing it. If you get an error while
executing a query, rewrite the query and try again.

DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the
database.

To start you should ALWAYS look at the tables in the database to see what you
can query. Do NOT skip this step.

Then you should query the schema of the most relevant tables.
""".format(
    dialect=db.dialect,
    top_k=5,
)

agent = create_agent(
    llm,
    tools,
    system_prompt=system_prompt,
)

question = " give me KPI metric of project PRJ1000 and show me data insights in chart response "
config = {"configurable": {"thread_id": "1"}} 

for step in agent.stream(
    {"messages": [{"role": "user", "content": question}]},
    stream_mode="values",
):
    if "messages" in step:
        step["messages"][-1].pretty_print()
    elif "__interrupt__" in step: 
        print("INTERRUPTED:") 
        interrupt = step["__interrupt__"][0] 
        for request in interrupt.value["action_requests"]: 
            print(request["description"]) 
    else:
        pass