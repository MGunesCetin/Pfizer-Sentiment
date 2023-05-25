import pandas as pd
import psutil
import time
from pymongo import MongoClient
import mysql.connector

class DatabasePerformanceAnalyzer:
    """
    A class for analyzing the performance of different databases.
    """

    def __init__(self):
        """
        Initializes the DatabasePerformanceAnalyzer class.

        Attributes:
        - mongo_client (MongoClient): MongoDB client instance.
        - mongo_db (MongoDB): MongoDB database instance.
        - mongo_collection (MongoDB Collection): MongoDB collection instance.
        - mysql_connection (MySQL Connection): MySQL database connection instance.
        - dataframe (pandas DataFrame): Data to be inserted into databases.
        """
        self.mongo_client = MongoClient('mongodb://localhost:27017/')
        self.mongo_db = self.mongo_client['Twitter']
        self.mongo_collection = self.mongo_db['SuicideData']
        
        self.mysql_connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='root',
            database='twitter_sent'
        )
        
        self.dataframe = pd.read_csv('PFV_op.csv')

    def measure_cpu_utilization(self):
        """
        Measures the CPU utilization.

        Returns:
        - float: CPU utilization percentage.
        """
        return psutil.cpu_percent()

    def measure_memory_utilization(self):
        """
        Measures the memory utilization.

        Returns:
        - float: Memory utilization percentage.
        """
        return psutil.virtual_memory().percent

    def insert_data_to_mongodb(self):
        """
        Inserts data into MongoDB collection.

        Returns:
        - float: Time taken for insertion in seconds.
        """
        start = time.time()
        self.mongo_collection.insert_many(self.dataframe.to_dict('records'))
        end = time.time()
        return end - start

    def insert_data_to_mysql(self):
        """
        Inserts data into MySQL database.

        Returns:
        - float: Time taken for insertion in seconds.
        """
        start = time.time()
        cursor = self.mysql_connection.cursor()
        for _, row in self.dataframe.iterrows():
            query = "INSERT INTO PFV ( label, Date) VALUES ( %s, %s)"
            values = (row['label'], row['Date'])
            cursor.execute(query, values)
        self.mysql_connection.commit()
        cursor.close()
        end = time.time()
        return end - start

    def run_test(self):
        """
        Runs the performance test.

        Prints CPU utilization, memory utilization, MongoDB insertion time, and MySQL insertion time.
        """
        cpu_utilization = self.measure_cpu_utilization()
        memory_utilization = self.measure_memory_utilization()
        mongodb_insertion_time = self.insert_data_to_mongodb()
        mysql_insertion_time = self.insert_data_to_mysql()

        print("CPU Utilization: {}%".format(cpu_utilization))
        print("Memory Utilization: {}%".format(memory_utilization))
        print("MongoDB Insertion Time: {} seconds".format(mongodb_insertion_time))
        print("MySQL Insertion Time: {} seconds".format(mysql_insertion_time))

if __name__ == '__main__':
    analyzer = DatabasePerformanceAnalyzer()
    analyzer.run_test()
