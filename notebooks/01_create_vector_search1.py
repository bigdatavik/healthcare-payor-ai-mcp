# Databricks notebook source
# MAGIC %md
# MAGIC # 🧠 Create and Test Vector Search Index from Billing FAQ Data
# MAGIC
# MAGIC This notebook walks through the end-to-end process of preparing a **vector search index** based on a synthetic FAQ dataset related to telecom billing.
# MAGIC
# MAGIC We use Databricks Vector Search to enable high-accuracy semantic retrieval of FAQ entries, forming the foundation for downstream use cases such as retrieval-augmented generation (RAG) and agent-based question answering.
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ## 📌 Key Steps in This Notebook
# MAGIC
# MAGIC 1. **Generate a Billing FAQ Dataset**  
# MAGIC    Create a synthetic dataset of frequently asked billing questions and answers, and save it as a Delta table in Unity Catalog.
# MAGIC
# MAGIC 2. **Configure & Create Vector Search Index**  
# MAGIC    - Enable change data feed on the Delta table  
# MAGIC    - Create a delta sync index using a specified embedding model  
# MAGIC    - Wait for the index to become ready
# MAGIC
# MAGIC 3. **Test the Vector Search**  
# MAGIC    Run a similarity search using a sample query (`"Can I change my bill due date?"`) and return the top matching FAQ entries.
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ## 🧰 Requirements
# MAGIC
# MAGIC - Unity Catalog enabled and configured
# MAGIC - Databricks Vector Search endpoint (configured and shared)
# MAGIC - A valid embedding model endpoint (e.g., `databricks-gte-large-en`)
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC This notebook sets the foundation for using semantic search over unstructured customer support data and can easily be integrated with RAG agents or evaluation pipelines.

# COMMAND ----------

# DBTITLE 1,Update Databricks SDK and Vector Search Library
# MAGIC %pip install -U --quiet databricks-sdk==0.28.0 databricks-vectorsearch 
# MAGIC dbutils.library.restartPython()

# COMMAND ----------

# MAGIC %run "./000-config"

# COMMAND ----------

# DBTITLE 1,Setup Vector Search Index Configuration
CATALOG = config['catalog']
SCHEMA = config['database']
VS_INDX = config['vector_search_index']

VECTOR_SEARCH_ENDPOINT_NAME = config['VECTOR_SEARCH_ENDPOINT_NAME']
embedding_model_endpoint_name = config['embedding_model_endpoint_name']
vs_index_fullname = f"{CATALOG}.{SCHEMA}.{VS_INDX}"

# COMMAND ----------

# DBTITLE 1,Create Billing FAQ Dataset and Save as Delta Table
import pandas as pd
from pyspark.sql import SparkSession

# Create a Pandas DataFrame from the CSV-like input
faq_data = [
    (1, "Q: How is my bill calculated? A: Your bill includes your monthly plan fee, additional charges for extra services, taxes, and any applicable discounts. A detailed breakdown is available in your MyTelco account."),
    (2, "Q: Why is my bill higher than usual? A: Your bill may be higher due to extra data usage, international calls, roaming charges, or a recent plan change. Check the usage details in the MyTelco app."),
    (3, "Q: What happens if I don’t pay my bill on time? A: Late payments may incur a penalty and could lead to service suspension. Reconnection fees may apply. Set up autopay to avoid these issues."),
    (4, "Q: How can I set up autopay for my bill? A: Enable autopay by logging into your MyTelco account, navigating to the billing section, and selecting 'Set Up Autopay'."),
    (5, "Q: How do I dispute a charge on my bill? A: If you believe there's an incorrect charge, contact customer support within 30 days of receiving your bill. Provide supporting details for review."),
    (6, "Q: Can I get a refund for overcharges? A: Refunds for overcharges may be available depending on the case. Contact customer support for a review, and any approved refunds will be credited to your next bill."),
    (7, "Q: Why was I charged a late payment fee? A: Late fees apply when payments are made after the due date. Check your bill for the due date and ensure timely payments to avoid these charges."),
    (8, "Q: How do I check my data usage? A: You can check your real-time data usage in the MyTelco app or by logging into your account online."),
    (9, "Q: Why do I see a roaming charge on my bill? A: Roaming charges apply when using your phone outside your network’s coverage. Check your plan settings or enable roaming notifications to avoid unexpected charges."),
    (10, "Q: Can I change my bill due date? A: Yes, you can request a bill due date change by contacting customer support or modifying it in your account settings.")
]

# Convert to Pandas then Spark DataFrame
pdf = pd.DataFrame(faq_data, columns=["index", "faq"])
spark_df = SparkSession.builder.getOrCreate().createDataFrame(pdf)

# Save as a Delta table
spark_df.write.format("delta").mode("overwrite").saveAsTable(f"{CATALOG}.{SCHEMA}.billing_faq_dataset")

# COMMAND ----------

# DBTITLE 1,SELECT All Columns from Billing FAQ Dataset
sql_query = f"""
SELECT * FROM `{CATALOG}`.`{SCHEMA}`.`billing_faq_dataset`
"""
display(spark.sql(sql_query))

# COMMAND ----------

# DBTITLE 1,Create Vector Search Endpoint with Databricks Client
from databricks.vector_search.client import VectorSearchClient
from databricks.sdk.errors import ResourceAlreadyExists, AlreadyExists, ResourceConflict

client = VectorSearchClient()

try:
    client.create_endpoint_and_wait(
        name=VECTOR_SEARCH_ENDPOINT_NAME,
        endpoint_type="STANDARD"
    )
except Exception as e:
    msg = str(e)
    if '"error_code":"ALREADY_EXISTS"' in msg or "status_code 409" in msg:
        print(f"Endpoint {VECTOR_SEARCH_ENDPOINT_NAME} already exists. Continuing...")
    else:
        raise

# COMMAND ----------

# DBTITLE 1,Initialize Vector Search Client
from databricks.vector_search.client import VectorSearchClient
from databricks.sdk import WorkspaceClient
import databricks.sdk.service.catalog as c
import time

# Initialize the Vector Search Client with the option to disable the notice.
vsc = VectorSearchClient(disable_notice=True)


# COMMAND ----------

# DBTITLE 1,Create and Sync Vector Search Index for FAQ Dataset
# This allows us to create a vector search index on the table
sql_query = f"""
ALTER TABLE `{CATALOG}`.`{SCHEMA}`.`billing_faq_dataset` 
SET TBLPROPERTIES (delta.enableChangeDataFeed = true)
"""
spark.sql(sql_query)

vs_index = vs_index_fullname
source_table = f"{CATALOG}.{SCHEMA}.billing_faq_dataset"

primary_key = "index"
embedding_source_column = "faq"

print(f"Creating index {vs_index} on endpoint {VECTOR_SEARCH_ENDPOINT_NAME}...")

# Create a new delta sync index on the vector search endpoint.
# This index is created from a source Delta table and is kept in sync with the source table.
try:
  index = vsc.create_delta_sync_index(
    endpoint_name=VECTOR_SEARCH_ENDPOINT_NAME,  # The name of the vector search endpoint.
    index_name=vs_index,  # The name of the index to create.
    source_table_name=source_table,  # The full name of the source Delta table.
    pipeline_type="TRIGGERED",  # The type of pipeline to keep the index in sync with the source table.
    primary_key=primary_key,  # The primary key column of the source table.
    embedding_source_column=embedding_source_column,  # The column to use for generating embeddings.
    embedding_model_endpoint_name=embedding_model_endpoint_name  # The name of the embedding model endpoint.
  )
  # Wait for index to come online. Expect this command to take several minutes.
  while not index.describe().get('status').get('detailed_state').startswith('ONLINE'):
    print("Waiting for index to be ONLINE...")
    time.sleep(5)
    
  print(f"index {vs_index} on table {source_table} is ready")
  
except Exception as e:
    msg = str(e)
    if '"error_code":"RESOURCE_ALREADY_EXISTS"' in msg or "status_code 409" in msg:
        print(f"Index {vs_index} already exists. Continuing...")
    else:
        raise

# COMMAND ----------

# DBTITLE 1,Demonstration of Similarity Search Using Vector Search Index
# Similarity Search

# Define the query text for the similarity search.
query_text = "Can I change my bill due date"

# Perform a similarity search on the vector search index.
results = vsc.get_index(VECTOR_SEARCH_ENDPOINT_NAME, vs_index_fullname).similarity_search(
  query_text=query_text,
  columns=['index', 'faq'],
  query_type='hybrid',
  num_results=5)  # Specify the number of results to return.

results

# COMMAND ----------

