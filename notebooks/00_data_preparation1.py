# Databricks notebook source
# MAGIC %run "./000-config"

# COMMAND ----------

# MAGIC %md ##Data Generation for the Demo
# MAGIC
# MAGIC For this solution accelerator, we will use data generator. The datasets include:
# MAGIC
# MAGIC - billing_plans: Telcos provide multiple billing plans to their consumers. These are representative plans for this solution accelarator.
# MAGIC - customers: Telco customer master data including attributes like customer_id, name, phone number, email etc
# MAGIC - billing_items: The detailed billing items including device_id, event type (data, call or text), call duration, data transferred, event timestamp etc
# MAGIC - invoice: Telco billing invoice for the customer
# MAGIC   
# MAGIC The invoice is based on:
# MAGIC   - cost per MB of internet activity
# MAGIC   - cost per minute of call for each of the call categories
# MAGIC   - cost per message
# MAGIC   
# MAGIC Internet activitity will be priced per MB transferred
# MAGIC
# MAGIC Phone calls will be priced per minute or partial minute.
# MAGIC
# MAGIC Messages will be priced per actual counts
# MAGIC
# MAGIC For simplicity, we'll ignore the free data, messages and calls threshold in most plans and the complexity
# MAGIC of matching devices to customers and telecoms operators - our goal here is to show generation of join
# MAGIC ready data, rather than full modelling of phone usage invoicing.

# COMMAND ----------

# MAGIC %md ## Databricks Labs Data Generator 
# MAGIC  Generating synthetic data is complex, however we have leveraged [Databricks Labs Data Generator ](https://github.com/databrickslabs/dbldatagen/tree/master)for the data generation. In fact, the labs project had a good [example](https://github.com/databrickslabs/dbldatagen/blob/master/dbldatagen/datasets/multi_table_telephony_provider.py) for telco which is reused for this solution. We highly recommend to use the labs project for synthetic data generation.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Install data generator package

# COMMAND ----------

# MAGIC %pip install dbldatagen

# COMMAND ----------

# MAGIC %md
# MAGIC ## Create a catalog and a database
# MAGIC We create a catalog and a database (schema) to store the delta tables for our data.

# COMMAND ----------

catalog = config['catalog']
db = config['database']

# Ensure the catalog exists, create it if it does not
# _ = spark.sql(f"CREATE CATALOG IF NOT EXISTS {catalog}")
# Ensure the schema exists within the specified catalog, create it if it does not
_ = spark.sql(f"CREATE SCHEMA IF NOT EXISTS {catalog}.{db}")
# _ = spark.sql(f"CREATE VOLUME IF NOT EXISTS {catalog}.{db}.{volume}")


# COMMAND ----------

# MAGIC %md
# MAGIC ## Configurations for data generation

# COMMAND ----------

UNIQUE_CUSTOMERS = config['UNIQUE_CUSTOMERS']
CUSTOMER_MIN_VALUE = config['CUSTOMER_MIN_VALUE']
DEVICE_MIN_VALUE = config['DEVICE_MIN_VALUE']
SUBSCRIBER_NUM_MIN_VALUE = config['SUBSCRIBER_NUM_MIN_VALUE']
UNIQUE_PLANS = config['UNIQUE_PLANS']
PLAN_MIN_VALUE = config['PLAN_MIN_VALUE']

AVG_EVENTS_PER_CUSTOMER = config['AVG_EVENTS_PER_CUSTOMER']

shuffle_partitions_requested = config['shuffle_partitions_requested']
partitions_requested = config['partitions_requested']
NUM_DAYS=config['NUM_DAYS'] 
MB_100 = config['MB_100']
K_1 = config['K_1']
start_dt=config['start_dt']
end_dt=config['end_dt']
vector_search_index=config['catalog']

llm_endpoint=config['llm_endpoint']
warehouse_id=config['warehouse_id']

# COMMAND ----------

# MAGIC %md 
# MAGIC ### Create billing plans table 
# MAGIC Billing plans represent various subscription options offered by the telecom provider to their customers. This dataset specifically focuses on plans available under contractual agreements. Due to its small size, the sample dataset has been uploaded to Git and imported into a Delta table.

# COMMAND ----------

from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType, DecimalType

# Define the schema for the JSON data
schema = StructType([
    StructField("Plan_key", IntegerType(), True),
    StructField("Plan_id", StringType(), True),
    StructField("Plan_name", StringType(), True),
    StructField("contract_in_months", IntegerType(), True),
    StructField("monthly_charges_dollars", DoubleType(), True),
    StructField("Calls_Text", StringType(), True),
    StructField("Internet_Speed_MBPS", StringType(), True),
    StructField("Data_Limit_GB", StringType(), True),
    StructField("Data_Outside_Allowance_Per_MB", DoubleType(), True),
    StructField("Roam_Data_charges_per_MB", DoubleType(), True),
    StructField("Roam_Call_charges_per_min", DoubleType(), True),
    StructField("Roam_text_charges", DoubleType(), True),
    StructField("International_call_charge_per_min", DoubleType(), True),
    StructField("International_text_charge", DoubleType(), True)
])

# Get the billing dataset path and import the data into a delta table with the specified schema
current_workspace_path = dbutils.notebook.entry_point.getDbutils().notebook().getContext().notebookPath().get()
data_dir_path = "/".join(current_workspace_path.split("/")[:-1]) + "/data"
df_plans = spark.read.format("json").schema(schema).load("file:/Workspace/" + data_dir_path + "/billing_plans.json")

# Write the DataFrame to a Delta table
df_plans.write.format("delta").mode("overwrite").option("overwriteSchema", "true").saveAsTable(f"{catalog}.{db}.billing_plans")

# COMMAND ----------

display(df_plans)

# COMMAND ----------

# MAGIC %md 
# MAGIC ### Generate customer, billing items and invoice datasets 
# MAGIC Customer, Billing items and Invoice tables are generated using data generator and loaded in the delta tables

# COMMAND ----------

# MAGIC %md ###Lets model our customers
# MAGIC
# MAGIC Device is used as the the foreign key. For more details around the data generation, please refer Databricks Labs project.
# MAGIC

# COMMAND ----------

import dbldatagen as dg
import pyspark.sql.functions as F

shuffle_partitions_requested = 8
partitions_requested = 1

spark.conf.set("spark.sql.shuffle.partitions", shuffle_partitions_requested)
spark.conf.set("spark.sql.execution.arrow.pyspark.enabled", "true")
spark.conf.set("spark.sql.execution.arrow.maxRecordsPerBatch", 20000)


spark.catalog.clearCache()  # clear cache so that if we run multiple times to check performance, we're not relying on cache
shuffle_partitions_requested = 8
partitions_requested = 8
data_rows = UNIQUE_CUSTOMERS

customer_dataspec = (dg.DataGenerator(spark, rows=data_rows, partitions=partitions_requested)
            .withColumn("customer_id","decimal(10)", minValue=CUSTOMER_MIN_VALUE, uniqueValues=UNIQUE_CUSTOMERS)
            .withColumn("customer_name", template=r"\\w \\w|\\w a. \\w")  
           
            # use the following for a simple sequence
            #.withColumn("device_id","decimal(10)", minValue=DEVICE_MIN_VALUE, uniqueValues=UNIQUE_CUSTOMERS)
                     
            .withColumn("device_id","decimal(10)",  minValue=DEVICE_MIN_VALUE, 
                        baseColumn="customer_id", baseColumnType="hash")

            .withColumn("phone_number","decimal(10)",  minValue=SUBSCRIBER_NUM_MIN_VALUE, 
                        baseColumn=["customer_id", "customer_name"], baseColumnType="hash")

            # for email, we'll just use the formatted phone number
            .withColumn("email","string",  format="subscriber_%s@myoperator.com", baseColumn="phone_number")
            .withColumn("plan", "int", minValue=PLAN_MIN_VALUE, uniqueValues=UNIQUE_PLANS, random=True)
            .withColumn("contract_start_dt", "date", data_range=dg.DateRange("2023-01-01 00:00:00",
                                                                             "2024-12-31 11:59:59",
                                                                             "days=1"),
                        random=True)
            )

df_customers = (customer_dataspec.build()
                .dropDuplicates(["device_id"])
                .dropDuplicates(["phone_number"])
                .orderBy("customer_id")
                .cache()
               )

# Write the DataFrame to a Delta table
df_customers.write.format("delta").mode("overwrite").option("overwriteSchema", "true").saveAsTable(f"{catalog}.{db}.customers")

# COMMAND ----------

# MAGIC %md ###Lets model our billing events
# MAGIC
# MAGIC Billing events like data usage, calls and texts are generated for this solution. 

# COMMAND ----------

import dbldatagen as dg



spark.catalog.clearCache()  # clear cache so that if we run multiple times to check performance, we're not relying on cache


data_rows = AVG_EVENTS_PER_CUSTOMER * UNIQUE_CUSTOMERS * NUM_DAYS

spark.conf.set("spark.sql.shuffle.partitions", shuffle_partitions_requested)
spark.conf.set("spark.sql.execution.arrow.pyspark.enabled", "true")
spark.conf.set("spark.sql.execution.arrow.maxRecordsPerBatch", 20000)


# use random seed method of 'hash_fieldname' for better spread - default in later builds
events_dataspec = (dg.DataGenerator(spark, rows=data_rows, partitions=partitions_requested, randomSeed=42,
                                    randomSeedMethod="hash_fieldname")
             # use same logic as per customers dataset to ensure matching keys - but make them random
            .withColumn("device_id_base", "decimal(10)", minValue=CUSTOMER_MIN_VALUE, uniqueValues=UNIQUE_CUSTOMERS,
                        random=True, omit=True)
            .withColumn("device_id", "decimal(10)",  minValue=DEVICE_MIN_VALUE,
                        baseColumn="device_id_base", baseColumnType="hash")

            # use specific random seed to get better spread of values
            .withColumn("event_type", "string",  values=["call_mins_local", "data_local", "data_roaming", "call_mins_roaming", "texts_roaming", "call_mins_international", "texts_local", "texts_international"],
                                                weights=[100, 100, 1, 0.5, 0.6, 2,20,2], random=True)

            # use Gamma distribution for skew towards short calls
            .withColumn("base_minutes","decimal(7,2)",  minValue=1.0, maxValue=5.0, step=0.1,
                        distribution=dg.distributions.Gamma(shape=1.5, scale=2.0), random=True, omit=True)
                   
            # use Gamma distribution for skew towards short transfers
            .withColumn("base_bytes_transferred","decimal(12)",  minValue=K_1, maxValue=MB_100, 
                        distribution=dg.distributions.Gamma(shape=0.75, scale=2.0), random=True, omit=True)
                   
            .withColumn("minutes", "decimal(7,2)", baseColumn=["event_type", "base_minutes"],
                        expr="""
                              case when event_type in ("call_mins_local", "call_mins_roaming", "call_mins_international") then base_minutes
                              else 0
                              end
                               """)
            .withColumn("bytes_transferred", "decimal(12)", baseColumn=["event_type", "base_bytes_transferred"],
                        expr="""
                              case when event_type in ("data_local", "data_roaming") then base_bytes_transferred
                              else 0
                              end
                               """)
                   
            .withColumn("event_ts", "timestamp", data_range=dg.DateRange(start_dt,
                                                                             end_dt,
                                                                             "seconds=1"),
                        random=True)
                   
            )

df_events = (events_dataspec.build()
               )

# COMMAND ----------

# MAGIC %md ###Billing Items
# MAGIC
# MAGIC Now generate events for generating billing items by joining the datasets customer, billing plans and events.

# COMMAND ----------

# Join the customer dataframe with the billing plans based on plan_key
df_customer_pricing = df_customers.join(df_plans, df_plans.Plan_key == df_customers.plan)

# COMMAND ----------

# remove events before the contract start date
df_billing_items = df_events.alias("events") \
    .join(df_customer_pricing.alias("pricing"), df_events.device_id == df_customer_pricing.device_id) \
    .where(df_events.event_ts >= df_customer_pricing.contract_start_dt) \
    .select("events.*", "pricing.contract_start_dt") 
    
# Write the DataFrame to a Delta table
df_billing_items.write.format("delta").mode("overwrite").option("overwriteSchema", "true").saveAsTable(f"{catalog}.{db}.billing_items")

# COMMAND ----------

# MAGIC %md ###Billing Invoices
# MAGIC
# MAGIC Now generate monthly invoices based on the billing items and other master datasets

# COMMAND ----------

# MAGIC %md let's compute our summary information

# COMMAND ----------

import pyspark.sql.functions as F


# # lets compute the summary minutes messages and bytes transferred
df_enriched_events = (df_billing_items
                      .withColumn("texts_roaming", F.expr("case when event_type='texts_roaming' then 1 else 0 end"))
                      .withColumn("texts_international", F.expr("case when event_type='texts_international' then 1 else 0 end"))
                      .withColumn("call_mins_roaming", F.expr("case when event_type='call_mins_roaming' then cast(ceil(minutes) as decimal(18,3)) else 0.0 end"))
                      .withColumn("call_mins_international", F.expr("case when event_type='call_mins_international' then cast(ceil(minutes) as decimal(18,3)) else 0.0 end"))
                      .withColumn("data_local", F.expr("case when event_type='data_local' then cast(ceil(bytes_transferred) as decimal(30,3)) else 0.0 end"))
                      .withColumn("data_roaming", F.expr("case when event_type='data_roaming' then cast(ceil(bytes_transferred) as decimal(30,3)) else 0.0 end"))
                     )

# ["data_local", "data_roaming", "call_mins_roaming", "texts_roaming", "call_mins_international", "texts_international"]
df_enriched_events.createOrReplaceTempView("telephony_events")

df_summary = spark.sql("""select device_id, 
                                 concat(extract(year FROM event_ts),"-",lpad(extract(month FROM event_ts),2,'0')) as event_month,
                                 round(sum(data_local) / (1028*1028), 3) as data_local_mb, 
                                 round(sum(data_roaming) / (1028*1028), 3) as data_roaming_mb, 
                                 sum(texts_roaming) as texts_roaming,
                                 sum(texts_international) as texts_international,
                                 sum(call_mins_roaming) as call_mins_roaming,
                                 sum(call_mins_international) as call_mins_international, 
                                 count(device_id) as event_count
                                 from telephony_events
                                 group by 1,2
                          
""")
# .write.format("delta").mode("overwrite").saveAsTable()

df_summary.createOrReplaceTempView("event_summary")


# COMMAND ----------

# MAGIC %md let's create a summary temp view

# COMMAND ----------

df_customer_summary = (df_customer_pricing.join(df_summary,df_customer_pricing.device_id == df_summary.device_id )
                       .createOrReplaceTempView("customer_summary"))

# COMMAND ----------

# MAGIC %md
# MAGIC Now generate the invoices

# COMMAND ----------

df_invoices = spark.sql(
    """select customer_id, 
       customer_name, 
       event_month, 
       phone_number, 
       email, 
       plan_name,      
       contract_start_dt, 
       contract_in_months, 
       monthly_charges_dollars as monthly_charges, 
       Calls_Text, 
       Internet_Speed_MBPS, 
       Data_Limit_GB, 
       Data_Outside_Allowance_Per_MB, 
       Roam_Data_charges_per_MB, 
       Roam_Call_charges_per_min, 
       Roam_text_charges, 
       International_text_charge,
       International_call_charge_per_min,
       data_local_mb,
       data_roaming_mb,
       call_mins_roaming,
       texts_roaming,
       call_mins_international,
       texts_international,
       case 
           when Data_Limit_GB != 'UNLIMITED' 
           then case 
                    when (data_local_mb - cast(Data_Limit_GB as double) * 1028) > 0
                    then cast((data_local_mb - cast(Data_Limit_GB as double) * 1028) * Data_Outside_Allowance_Per_MB as decimal(18,2))   
                    else 0 
                end
           else 0 
       end as data_charges_outside_allowance,
       case 
           when data_roaming_mb > 0 
           then cast(data_roaming_mb * Roam_Data_charges_per_MB as decimal(18,2))
           else 0 
       end as roaming_data_charges,
       case 
           when call_mins_roaming > 0 
           then cast(ceiling(call_mins_roaming) * Roam_Call_charges_per_min as decimal(18,2))
           else 0 
       end as roaming_call_charges,
       case 
           when texts_roaming > 0 
           then cast(texts_roaming * Roam_text_charges as decimal(18,2))
           else 0 
       end as roaming_text_charges,
       case 
           when call_mins_international > 0 
           then cast(ceiling(call_mins_international) * International_call_charge_per_min as decimal(18,2))
           else 0 
       end as international_call_charges,
       case 
           when texts_international > 0 
           then cast(texts_international * International_text_charge as decimal(18,2))
           else 0 
       end as international_text_charges,
       monthly_charges_dollars + data_charges_outside_allowance + roaming_data_charges + roaming_call_charges + roaming_text_charges + international_call_charges + international_text_charges as total_charges
from customer_summary

"""
)

# COMMAND ----------

# Write the DataFrame to a Delta table
df_invoices.write.format("delta").mode("overwrite").option("overwriteSchema", "true").saveAsTable(f"{catalog}.{db}.invoice")

# COMMAND ----------

ui_functions_path=config['catalog']+"."+config['database']
print(ui_functions_path)

# COMMAND ----------

content = f"""
agent_prompt: |
  You are a Billing Support Agent assisting users with billing inquiries.

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

llm_endpoint: "{llm_endpoint}"
warehouse_id: "{warehouse_id}"
vector_search_index: "{ui_functions_path}.faq_index"
uc_functions:
  - "{ui_functions_path}.*"
"""

# COMMAND ----------

with open('config.yml', "w") as f:
    f.write(content)

# COMMAND ----------

