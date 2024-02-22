import json

from flask import Flask
from flask import Response
import os
import subprocess

application = Flask(__name__)


@application.route("/database", methods=["GET"])
def database():
    os.environ["SPARK_APPLICATION_PYTHON_LOCATION"] = "/app/database.py"

    os.environ[
        "SPARK_SUBMIT_ARGS"] = "--driver-class-path /app/mysql-connector-j-8.0.33.jar --jars /app/mysql-connector-j-8.0.33.jar"

    result = subprocess.check_output(["/template.sh"])
    rezultat = []
    with open("output1.txt", "r") as file:
        for line in file:
            args = line.split()
            p = {
                "name": args[0],
                "sold": int(args[1]),
                "waiting": int(args[2])
            }
            rezultat.append(p)
    konacno = {
        "statistics": rezultat
    }
    return Response(json.dumps(konacno), status=200)


@application.route("/database1", methods=["GET"])
def database1():
    os.environ["SPARK_APPLICATION_PYTHON_LOCATION"] = "/app/database1.py"

    os.environ[
        "SPARK_SUBMIT_ARGS"] = "--driver-class-path /app/mysql-connector-j-8.0.33.jar --jars /app/mysql-connector-j-8.0.33.jar"

    result = subprocess.check_output(["/template.sh"])
    rezultat = []
    with open("output2.txt", "r") as file:
        for line in file:
            rezultat.append(line.split()[0])
    konacno = {
        "statistics": rezultat
    }
    return Response(json.dumps(konacno), status=200)


if __name__ == "__main__":
    application.run(debug=True, port=5006, host="0.0.0.0")
