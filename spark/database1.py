from pyspark.sql import SparkSession
from pyspark.sql.functions import sum

import os

PRODUCTION = True if ("PRODUCTION" in os.environ) else False
DATABASE_IP = "prodavnicaDatabase" if ("PRODUCTION" in os.environ) else "localhost"
DATABASE_PORT = "3306" if ("PRODUCTION" in os.environ) else "3307"
builder = SparkSession.builder.appName("Statistika1")

if not PRODUCTION:
    print('tu sam')
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

pripada_kategoriji_data_frame = spark.read \
    .format("jdbc") \
    .option("driver", "com.mysql.cj.jdbc.Driver") \
    .option("url", f"jdbc:mysql://{DATABASE_IP}:{DATABASE_PORT}/prodavnica") \
    .option("dbtable", "prodavnica.pripada_kategoriji") \
    .option("user", "root") \
    .option("password", "root") \
    .load()
kategorija_proizvoda_data_frame = spark.read \
    .format("jdbc") \
    .option("driver", "com.mysql.cj.jdbc.Driver") \
    .option("url", f"jdbc:mysql://{DATABASE_IP}:{DATABASE_PORT}/prodavnica") \
    .option("dbtable", "prodavnica.kategorija_proizvoda") \
    .option("user", "root") \
    .option("password", "root") \
    .load()

join_condition = [
    narudzbina_data_frame["id"] == pripada_narudzbini_data_frame["narudzbina_id"],
    pripada_narudzbini_data_frame["proizvod_id"] == proizvod_data_frame["id"],
    proizvod_data_frame["id"] == pripada_kategoriji_data_frame["proizvod_id"],
    pripada_kategoriji_data_frame["kategorija_id"] == kategorija_proizvoda_data_frame["id"]
]

joined_data_frame = narudzbina_data_frame.join(
    pripada_narudzbini_data_frame, join_condition[0]
).join(
    proizvod_data_frame, join_condition[1]
).join(
    pripada_kategoriji_data_frame, join_condition[2]
).join(
    kategorija_proizvoda_data_frame, join_condition[3]
)

filtered_data_frame = joined_data_frame.filter(narudzbina_data_frame["status"] == 2)
aggregated_data_frame = filtered_data_frame.groupBy(kategorija_proizvoda_data_frame["naziv"].alias("kn_naziv")).agg(sum("kolicina").alias("kolicina_sum"))
sorted_data_frame = aggregated_data_frame.orderBy(aggregated_data_frame["kolicina_sum"].desc(), aggregated_data_frame["kn_naziv"])
sorted_data_frame.show()
naziv_column = sorted_data_frame.select("kn_naziv")
values = [row[0] for row in naziv_column.collect()]

naziv_column1 = kategorija_proizvoda_data_frame.select("naziv")
values1 = [row[0] for row in naziv_column1.collect()]
values1.sort()
for c in values1:
    if c not in values:
        values.append(c)
with open("output2.txt", "w") as file:
    for c in values:
        file.write(f"{c}\n")

spark.stop()
