from pyspark.sql import SparkSession
from pyspark.sql.functions import sum, col

import os

PRODUCTION = True if ("PRODUCTION" in os.environ) else False
DATABASE_IP = "prodavnicaDatabase" if ("PRODUCTION" in os.environ) else "localhost"
DATABASE_PORT = "3306" if ("PRODUCTION" in os.environ) else "3307"
builder = SparkSession.builder.appName("Statistika")

if not PRODUCTION:
    builder = builder.master("local[*]").config(
        "spark.driver.extraClassPath",
        "mysql-connector-j-8.0.33.jar"
    )

spark = builder.getOrCreate()
spark.sparkContext.setLogLevel("ERROR")

proizvod_data_frame = spark.read \
    .format("jdbc") \
    .option("driver", "com.mysql.cj.jdbc.Driver") \
    .option("url", f"jdbc:mysql://{DATABASE_IP}:{DATABASE_PORT}/prodavnica") \
    .option("dbtable", "prodavnica.proizvod") \
    .option("user", "root") \
    .option("password", "root") \
    .load()

narudzbina_data_frame = spark.read \
    .format("jdbc") \
    .option("driver", "com.mysql.cj.jdbc.Driver") \
    .option("url", f"jdbc:mysql://{DATABASE_IP}:{DATABASE_PORT}/prodavnica") \
    .option("dbtable", "prodavnica.narudzbina") \
    .option("user", "root") \
    .option("password", "root") \
    .load()

pripada_narudzbini_data_frame = spark.read \
    .format("jdbc") \
    .option("driver", "com.mysql.cj.jdbc.Driver") \
    .option("url", f"jdbc:mysql://{DATABASE_IP}:{DATABASE_PORT}/prodavnica") \
    .option("dbtable", "prodavnica.pripada_narudzbini") \
    .option("user", "root") \
    .option("password", "root") \
    .load()


joined_df = pripada_narudzbini_data_frame.join(narudzbina_data_frame, pripada_narudzbini_data_frame["narudzbina_id"] ==
                                               narudzbina_data_frame["id"])


status_2_df = joined_df.filter(joined_df["status"] == 2)
result_status_2 = proizvod_data_frame.join(status_2_df, status_2_df["proizvod_id"] == proizvod_data_frame["id"])


result_status_2 = result_status_2.groupBy(proizvod_data_frame["ime"]).agg(
    sum(col("kolicina")).alias("sold")
)

status_1_df = joined_df.filter(joined_df["status"] != 2)
result_status_1 = proizvod_data_frame.join(status_1_df, status_1_df["proizvod_id"] == proizvod_data_frame["id"])


result_status_1 = result_status_1.groupBy(proizvod_data_frame["ime"]).agg(
    sum(col("kolicina")).alias("waiting")
)

dict2 = result_status_2.rdd.collectAsMap()
dict1 = result_status_1.rdd.collectAsMap()

dict = {}

# Show the results
for key, value in dict2.items():
    list = [value]
    if key in dict1:
        list.append(dict1[key])
    else:
        list.append(0)
    dict[key] = list
for key, value in dict1.items():
    if key not in dict:
        list = [0, value]
        dict[key] = list


with open("output1.txt", "w") as file:
    for key, value in dict.items():
        file.write(f"{key} {value[0]} {value[1]}\n")

spark.stop()
