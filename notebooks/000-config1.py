# Databricks notebook source
# MAGIC %md
# MAGIC # Configuration Parameters
# MAGIC Please change as required.

# COMMAND ----------

# DBTITLE 1,Initialize Config Dictionary If Not Present
if 'config' not in locals():
  config = {}

# COMMAND ----------

# MAGIC %md 
# MAGIC ### Data Catalog configs

# COMMAND ----------

# DBTITLE 1,Set Catalog and Database in Config Dictionary
# Catalog and database
# Change the Catalog and database name as per your requirements

config['catalog'] = 'telco_billing_catalog'
config['database'] = 'telco_billing_db'

# COMMAND ----------

# MAGIC %md 
# MAGIC ### Key configurations for the data generation 

# COMMAND ----------

# DBTITLE 1,Set Data Generation Configuration Parameters
# Data Generation Configs

config['UNIQUE_CUSTOMERS'] = 50000
config['CUSTOMER_MIN_VALUE'] = 1000
config['DEVICE_MIN_VALUE'] = 1000000000
config['SUBSCRIBER_NUM_MIN_VALUE'] = 1000000000
config['UNIQUE_PLANS'] = 10 # Number of unique plans are 10 in the Github dataset. If you need to change this value, you will need to change the billing plan dataset as well.
config['PLAN_MIN_VALUE'] = 1


config['AVG_EVENTS_PER_CUSTOMER'] = 10

config['shuffle_partitions_requested'] = 8
config['partitions_requested'] = 8
config['NUM_DAYS']=365 # number of days to generate data for
config['MB_100'] = 50000000 # Max bytes transferred
config['K_1'] = 100000 # Min bytes transferred
config['start_dt']="2024-01-01 00:00:00" 
config['end_dt']="2024-12-31 11:59:59"




# COMMAND ----------

# MAGIC %md
# MAGIC ### Agent configuration parameters

# COMMAND ----------

# DBTITLE 1,Set Agent Configuration Parameters in Config Dictionary
# Agent Configs
config['agent_name'] = 'ai_billing_agent'
config['VECTOR_SEARCH_ENDPOINT_NAME'] = 'vector-search-telco-billing'
config['vector_search_index'] = 'faq_indx1'
config['embedding_model_endpoint_name'] = 'databricks-gte-large-en'  # This is default enbedding model and needs to be updated for your environment
config['llm_endpoint']="databricks-claude-3-7-sonnet" # This is default token based pricing endpoint and needs to be updated based on your requirement
config['warehouse_id']="148ccb90800933a1" # This is the warehouse id and need to be updated for your environment

# Tools 
config['tools_billing_faq'] = config['catalog']+'.'+config['database']+'.billing_faq'
config['tools_billing'] = config['catalog']+'.'+config['database']+'.lookup_billing'
config['tools_items'] = config['catalog']+'.'+config['database']+'.lookup_billing_items'
config['tools_plans'] = config['catalog']+'.'+config['database']+'.lookup_billing_plans'
config['tools_customer'] = config['catalog']+'.'+config['database']+'.lookup_customer'