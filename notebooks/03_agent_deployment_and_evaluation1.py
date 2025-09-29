# Databricks notebook source
# MAGIC %md
# MAGIC # 🤖 Telco Billing Agent Deployment & Evaluation
# MAGIC
# MAGIC This notebook orchestrates the **deployment pipeline** for an AI agent designed to answer customer billing queries for a telecommunications provider.
# MAGIC
# MAGIC It extends the auto-generated code from the Databricks AI Playground with an additional **synthetic evaluation component**, allowing for a more rigorous and repeatable assessment of the agent’s quality using a curated FAQ knowledge base.
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ## 📋 Notebook Overview
# MAGIC
# MAGIC This notebook performs the following steps:
# MAGIC
# MAGIC 1. **Define the agent**
# MAGIC 2. **Log the agent**: Wraps the agent (from the `agent` notebook) as an MLflow model along with configuration and resource bindings.
# MAGIC 3. **Synthetic Evaluation**: Generates a set of realistic and adversarial queries from the FAQ dataset to evaluate agent performance using the Agent Evaluation framework.
# MAGIC 4. **Register to Unity Catalog**: Stores the model centrally for governance and discovery.
# MAGIC 5. **Deploy to Model Serving**: Deploys the agent to a Databricks model serving endpoint for interactive and production use.
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ## 🧠 Evaluation with Synthetic Questions
# MAGIC
# MAGIC Using the `generate_evals_df()` API, this notebook constructs a diverse set of evaluation prompts from the billing FAQ knowledge base. These include:
# MAGIC
# MAGIC - Realistic billing-related user queries
# MAGIC - Edge cases like irrelevant or sensitive questions (to test refusal behavior)
# MAGIC - Multiple user personas (e.g., customers, agents)
# MAGIC
# MAGIC This process helps verify that the deployed agent:
# MAGIC
# MAGIC - Understands the domain context (billing)
# MAGIC - Retrieves accurate answers from the knowledge base
# MAGIC - Appropriately ignores irrelevant or sensitive queries
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ## 🔧 Prerequisites
# MAGIC
# MAGIC Before running this notebook:
# MAGIC
# MAGIC - Update and validate the `config.yml` to define agent tools, LLM endpoints, and system prompt.
# MAGIC - Run the `agent` notebook to define and test your agent.
# MAGIC - Ensure the `faq_index` and `billing_faq_dataset` are available and correctly formatted in Unity Catalog.
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ## 📦 Outputs
# MAGIC
# MAGIC - A registered and deployed agent model in Unity Catalog
# MAGIC - A set of evaluation metrics stored in MLflow
# MAGIC - A live model endpoint ready for testing in AI Playground or production integration
# MAGIC

# COMMAND ----------

# DBTITLE 1,Install Libraries
# MAGIC %pip install -U -qqqq mlflow-skinny[databricks] langgraph==0.3.4 databricks-langchain databricks-agents==1.0.1 uv
# MAGIC dbutils.library.restartPython()

# COMMAND ----------

# MAGIC %run "./000-config"

# COMMAND ----------

import yaml
from yaml.representer import SafeRepresenter

class LiteralString(str):
    pass

def literal_str_representer(dumper, data):
    return dumper.represent_scalar("tag:yaml.org,2002:str", data, style='|')

yaml.add_representer(LiteralString, literal_str_representer)

# COMMAND ----------

# Prompt
system_prompt = """You are a Billing Support Agent assisting users with billing inquiries.

Guidelines:
- First, check FAQ Search before requesting any details.
- If an FAQ answer exists, return it immediately.
- If no FAQ match, request the customer_id before retrieving billing details.
- Do not disclose confidential information like names, emails, device_id.

Process:
1. Run FAQ Search -> If an answer exists, return it.
2. If no FAQ match, ask for the customer_id and use the relevant tool(s) to fetch billing details.
3. If missing details (e.g., timeframe), ask clarifying questions.

Keep responses polite, professional, and concise.
"""

# COMMAND ----------

catalog = config['catalog']
schema = config['database']
llm_endpoint = config['llm_endpoint']
embedding_model_endpoint_name = config['embedding_model_endpoint_name']
warehouse_id = config['warehouse_id']
vector_search_index = f"{config['catalog']}.{config['database']}.{config['vector_search_index']}"
tools_billing_faq = config['tools_billing_faq'] 
tools_billing = config['tools_billing']
tools_items = config['tools_items']
tools_plans = config['tools_plans']
tools_customer = config['tools_customer']
agent_name = config['agent_name']
agent_prompt = LiteralString(system_prompt)

# COMMAND ----------

yaml_data = {
    "catalog": catalog,
    "schema": schema,
    "llm_endpoint": llm_endpoint,
    "embedding_model_endpoint_name": embedding_model_endpoint_name,
    "warehouse_id": warehouse_id,
    "vector_search_index": vector_search_index,
    "tools_billing_faq": tools_billing_faq,
    "tools_billing": tools_billing,
    "tools_items": tools_items,
    "tools_plans": tools_plans,
    "tools_customer": tools_customer,
    "agent_name": agent_name,
    "agent_prompt": agent_prompt
}

with open("config.yaml", "w") as f:
    yaml.dump(yaml_data, f, default_flow_style=False, sort_keys=False)


# COMMAND ----------

# MAGIC %md ## Define the agent in code
# MAGIC Below we define our agent code in a single cell, enabling us to easily write it to a local Python file for subsequent logging and deployment using the `%%writefile` magic command.
# MAGIC
# MAGIC For more examples of tools to add to your agent, see [docs](https://learn.microsoft.com/azure/databricks/generative-ai/agent-framework/agent-tool).

# COMMAND ----------

# MAGIC %%writefile agent.py
# MAGIC from typing import Any, Generator, Optional, Sequence, Union
# MAGIC
# MAGIC import mlflow
# MAGIC from databricks_langchain import (
# MAGIC     ChatDatabricks,
# MAGIC     VectorSearchRetrieverTool,
# MAGIC     DatabricksFunctionClient,
# MAGIC     UCFunctionToolkit,
# MAGIC     set_uc_function_client,
# MAGIC )
# MAGIC from langchain_core.language_models import LanguageModelLike
# MAGIC from langchain_core.runnables import RunnableConfig, RunnableLambda
# MAGIC from langchain_core.tools import BaseTool
# MAGIC from langgraph.graph import END, StateGraph
# MAGIC from langgraph.graph.graph import CompiledGraph
# MAGIC from langgraph.graph.state import CompiledStateGraph
# MAGIC from langgraph.prebuilt.tool_node import ToolNode
# MAGIC from mlflow.langchain.chat_agent_langgraph import ChatAgentState, ChatAgentToolNode
# MAGIC from mlflow.pyfunc import ChatAgent
# MAGIC from mlflow.types.agent import (
# MAGIC     ChatAgentChunk,
# MAGIC     ChatAgentMessage,
# MAGIC     ChatAgentResponse,
# MAGIC     ChatContext,
# MAGIC )
# MAGIC from mlflow.models import ModelConfig
# MAGIC
# MAGIC mlflow.langchain.autolog()
# MAGIC
# MAGIC client = DatabricksFunctionClient()
# MAGIC set_uc_function_client(client)
# MAGIC
# MAGIC config = ModelConfig(development_config="config.yaml").to_dict()
# MAGIC
# MAGIC
# MAGIC ############################################
# MAGIC # Define your LLM endpoint and system prompt
# MAGIC ############################################
# MAGIC # LLM_ENDPOINT_NAME = LLM_ENDPOINT
# MAGIC llm = ChatDatabricks(endpoint=config['llm_endpoint'])
# MAGIC system_prompt = config['agent_prompt']
# MAGIC
# MAGIC ###############################################################################
# MAGIC ## Define tools for your agent, enabling it to retrieve data or take actions
# MAGIC ## beyond text generation
# MAGIC ## To create and see usage examples of more tools, see
# MAGIC ## https://learn.microsoft.com/azure/databricks/generative-ai/agent-framework/agent-tool
# MAGIC ###############################################################################
# MAGIC catalog = config['catalog']
# MAGIC schema = config['schema']
# MAGIC
# MAGIC tools = []
# MAGIC
# MAGIC # You can use UDFs in Unity Catalog as agent tools
# MAGIC uc_tool_names = [
# MAGIC     config['tools_billing_faq'],
# MAGIC     config['tools_billing'],
# MAGIC     config['tools_items'],
# MAGIC     config['tools_plans'],  
# MAGIC     config['tools_customer']
# MAGIC     ]
# MAGIC uc_toolkit = UCFunctionToolkit(function_names=uc_tool_names)
# MAGIC tools.extend(uc_toolkit.tools)
# MAGIC
# MAGIC #####################
# MAGIC ## Define agent logic
# MAGIC #####################
# MAGIC
# MAGIC
# MAGIC def create_tool_calling_agent(
# MAGIC     model: LanguageModelLike,
# MAGIC     tools: Union[Sequence[BaseTool], ToolNode],
# MAGIC     system_prompt: Optional[str] = None,
# MAGIC ) -> CompiledGraph:
# MAGIC     model = model.bind_tools(tools)
# MAGIC
# MAGIC     # Define the function that determines which node to go to
# MAGIC     def should_continue(state: ChatAgentState):
# MAGIC         messages = state["messages"]
# MAGIC         last_message = messages[-1]
# MAGIC         # If there are function calls, continue. else, end
# MAGIC         if last_message.get("tool_calls"):
# MAGIC             return "continue"
# MAGIC         else:
# MAGIC             return "end"
# MAGIC
# MAGIC     if system_prompt:
# MAGIC         preprocessor = RunnableLambda(
# MAGIC             lambda state: [{"role": "system", "content": system_prompt}]
# MAGIC             + state["messages"]
# MAGIC         )
# MAGIC     else:
# MAGIC         preprocessor = RunnableLambda(lambda state: state["messages"])
# MAGIC     model_runnable = preprocessor | model
# MAGIC
# MAGIC     def call_model(
# MAGIC         state: ChatAgentState,
# MAGIC         config: RunnableConfig,
# MAGIC     ):
# MAGIC         response = model_runnable.invoke(state, config)
# MAGIC
# MAGIC         return {"messages": [response]}
# MAGIC
# MAGIC     workflow = StateGraph(ChatAgentState)
# MAGIC
# MAGIC     workflow.add_node("agent", RunnableLambda(call_model))
# MAGIC     workflow.add_node("tools", ChatAgentToolNode(tools))
# MAGIC
# MAGIC     workflow.set_entry_point("agent")
# MAGIC     workflow.add_conditional_edges(
# MAGIC         "agent",
# MAGIC         should_continue,
# MAGIC         {
# MAGIC             "continue": "tools",
# MAGIC             "end": END,
# MAGIC         },
# MAGIC     )
# MAGIC     workflow.add_edge("tools", "agent")
# MAGIC
# MAGIC     return workflow.compile()
# MAGIC
# MAGIC
# MAGIC class LangGraphChatAgent(ChatAgent):
# MAGIC     def __init__(self, agent: CompiledStateGraph):
# MAGIC         self.agent = agent
# MAGIC
# MAGIC     def predict(
# MAGIC         self,
# MAGIC         messages: list[ChatAgentMessage],
# MAGIC         context: Optional[ChatContext] = None,
# MAGIC         custom_inputs: Optional[dict[str, Any]] = None,
# MAGIC     ) -> ChatAgentResponse:
# MAGIC         request = {"messages": self._convert_messages_to_dict(messages)}
# MAGIC
# MAGIC         messages = []
# MAGIC         for event in self.agent.stream(request, stream_mode="updates"):
# MAGIC             for node_data in event.values():
# MAGIC                 messages.extend(
# MAGIC                     ChatAgentMessage(**msg) for msg in node_data.get("messages", [])
# MAGIC                 )
# MAGIC         return ChatAgentResponse(messages=messages)
# MAGIC
# MAGIC     def predict_stream(
# MAGIC         self,
# MAGIC         messages: list[ChatAgentMessage],
# MAGIC         context: Optional[ChatContext] = None,
# MAGIC         custom_inputs: Optional[dict[str, Any]] = None,
# MAGIC     ) -> Generator[ChatAgentChunk, None, None]:
# MAGIC         request = {"messages": self._convert_messages_to_dict(messages)}
# MAGIC         for event in self.agent.stream(request, stream_mode="updates"):
# MAGIC             for node_data in event.values():
# MAGIC                 yield from (
# MAGIC                     ChatAgentChunk(**{"delta": msg}) for msg in node_data["messages"]
# MAGIC                 )
# MAGIC
# MAGIC
# MAGIC # Create the agent object, and specify it as the agent object to use when
# MAGIC # loading the agent back for inference via mlflow.models.set_model()
# MAGIC agent = create_tool_calling_agent(llm, tools, system_prompt)
# MAGIC AGENT = LangGraphChatAgent(agent)
# MAGIC mlflow.models.set_model(AGENT)

# COMMAND ----------

# MAGIC %md
# MAGIC %md
# MAGIC ## Test the agent
# MAGIC
# MAGIC Interact with the agent to test its output. Since this notebook called `mlflow.langchain.autolog()` you can view the trace for each step the agent takes.
# MAGIC
# MAGIC Replace this placeholder input with an appropriate domain-specific example for your agent.

# COMMAND ----------

dbutils.library.restartPython()

# COMMAND ----------

from agent import AGENT

AGENT.predict({"messages": [{"role": "user", "content": "Hello, how can I pay my bill?"}]})

# COMMAND ----------

from agent import AGENT

AGENT.predict({"messages": [{"role": "user", "content": "Based on my usage in the last six months and my current contract, would you recommend keeping this plan or changing to another? My customer id is 4401"}]})

# COMMAND ----------

# MAGIC %md
# MAGIC ### Log the `agent` as an MLflow model
# MAGIC Determine Databricks resources to specify for automatic auth passthrough at deployment time
# MAGIC - **TODO**: If your Unity Catalog Function queries a [vector search index](https://learn.microsoft.com/azure/databricks/generative-ai/agent-framework/unstructured-retrieval-tools) or leverages [external functions](https://learn.microsoft.com/azure/databricks/generative-ai/agent-framework/external-connection-tools), you need to include the dependent vector search index and UC connection objects, respectively, as resources. See [docs](https://learn.microsoft.com/azure/databricks/generative-ai/agent-framework/log-agent#specify-resources-for-automatic-authentication-passthrough) for more details.
# MAGIC
# MAGIC Log the agent as code from the `agent.py` file. See [MLflow - Models from Code](https://mlflow.org/docs/latest/models.html#models-from-code).

# COMMAND ----------


import yaml
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# COMMAND ----------

# Determine Databricks resources to specify for automatic auth passthrough at deployment time
import mlflow
from agent import tools
from databricks_langchain import VectorSearchRetrieverTool
from mlflow.models.resources import (
    DatabricksFunction, 
    DatabricksServingEndpoint,
    DatabricksVectorSearchIndex
)
from pkg_resources import get_distribution
from unitycatalog.ai.langchain.toolkit import UnityCatalogTool

resources = [
    DatabricksServingEndpoint(endpoint_name=config['llm_endpoint']),
    DatabricksVectorSearchIndex(index_name=config['vector_search_index'])
]
for tool in tools:
    if isinstance(tool, VectorSearchRetrieverTool):
        resources.extend(tool.resources)
    elif isinstance(tool, UnityCatalogTool):
        # TODO: If the UC function includes dependencies like external connection or vector search, please include them manually.
        # See the TODO in the markdown above for more information.
        resources.append(DatabricksFunction(function_name=tool.uc_function_name))

input_example = {
    "messages": [
        {
            "role": "user",
            "content": "Based on my usage in the last six months and my current contract, would you recommend keeping this plan or changing to another? My customer id is 4401"
        }
    ]
}

with mlflow.start_run():
    logged_agent_info = mlflow.pyfunc.log_model(
        name=config['agent_name'],
        python_model="agent.py",
        model_config='config.yaml',
        input_example=input_example,
        resources=resources,
        pip_requirements=[
            f"databricks-connect=={get_distribution('databricks-connect').version}",
            f"mlflow=={get_distribution('mlflow').version}",
            f"databricks-langchain=={get_distribution('databricks-langchain').version}",
            f"langgraph=={get_distribution('langgraph').version}",
        ],
    )

# COMMAND ----------

# MAGIC %md
# MAGIC ## Evaluate the agent with [Agent Evaluation](https://learn.microsoft.com/azure/databricks/generative-ai/agent-evaluation/)
# MAGIC
# MAGIC You can edit the requests or expected responses in your evaluation dataset and run evaluation as you iterate your agent, leveraging mlflow to track the computed quality metrics.

# COMMAND ----------

# TODO: Change to your FAQ table name
faq_table = (f"{config['catalog']}.{config['schema']}.billing_faq_dataset")

# COMMAND ----------

# DBTITLE 1,Generate Synthetic Evals with AI Assistant
# Use the synthetic eval generation API to get some evals
from databricks.agents.evals import generate_evals_df

# "Ghost text" for agent description and question guidelines - feel free to modify as you see fit.
agent_description = f"""
The agent is an AI assistant that answers questions about billing. Questions unrelated to billing are irrelevant. Include questions that are irrelevant or ask for sensitive data too to the test that the agent ignores them.  
"""
question_guidelines = f"""
# User personas
- Customer of a telco provider
- Customer support agent

# Example questions
- How can I set up autopay for my bill?

# Additional Guidelines
- Questions should be succinct, and human-like
"""

docs_df = (
    spark.table(faq_table)
    .withColumnRenamed("faq", "content")  
)
pandas_docs_df = docs_df.toPandas()
pandas_docs_df["doc_uri"] = pandas_docs_df["index"].astype(str)
evals = generate_evals_df(
    docs=pandas_docs_df,  # Pass your docs. They should be in a Pandas or Spark DataFrame with columns `content STRING` and `doc_uri STRING`.
    num_evals=20,  # How many synthetic evaluations to generate
    agent_description=agent_description,
    question_guidelines=question_guidelines,
)
display(evals)

# COMMAND ----------

import mlflow
from mlflow.genai.scorers import RelevanceToQuery, Safety, RetrievalRelevance, RetrievalGroundedness

eval_results = mlflow.genai.evaluate(
    data=evals.head(),
    predict_fn=lambda messages: AGENT.predict({"messages": messages}),
    scorers=[RelevanceToQuery(), Safety()], # add more scorers here if they're applicable
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Register the model to Unity Catalog
# MAGIC
# MAGIC Update the `catalog`, `schema`, and `model_name` below to register the MLflow model to Unity Catalog.

# COMMAND ----------

# DBTITLE 1,Register UC Model with MLflow in Databricks
mlflow.set_registry_uri("databricks-uc")

# TODO: define the catalog, schema, and model name for your UC model
UC_MODEL_NAME = f"{config['catalog']}.{config['schema']}.{config['agent_name']}" 

# register the model to UC
uc_registered_model_info = mlflow.register_model(model_uri=logged_agent_info.model_uri, name=UC_MODEL_NAME)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Deploy the agent

# COMMAND ----------

# DBTITLE 1,Deploy Model to Review App and Serving Endpoint
from databricks import agents
import mlflow

# Deploy the model to the review app and a model serving endpoint
agents.deploy(UC_MODEL_NAME, uc_registered_model_info.version)

# COMMAND ----------

