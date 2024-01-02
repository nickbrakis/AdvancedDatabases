from pyspark.sql import SparkSession
from pyspark.sql.functions import year, avg, to_date, unix_timestamp, from_unixtime, count, round, udf, min
from pyspark.sql.types import FloatType, DoubleType
from geopy.distance import geodesic

# Create a Spark session
spark = SparkSession.builder.getOrCreate()

# Load the CSV file
df = spark.read.csv('datasets/Crime_Data_from_2010_to_2019.csv', inferSchema=True, header=True)
# Load the second CSV file
df2 = spark.read.csv('datasets/Crime_Data_from_2020_to_Present.csv', inferSchema=True, header=True)
# Merge the two DataFrames
crime_df = df.union(df2)
# Extract the year
stations_df = spark.read.csv('datasets/LAPD_Police_Stations.csv', header=True, inferSchema=True)


# Filter out records referring to Null Island
crime_df = crime_df.filter((crime_df['LAT'] != 0) & (crime_df['LON'] != 0))

# Filter data for gun-related crimes
crime_df = crime_df.filter(crime_df['Weapon Used Cd'].startswith('1'))

# UDF to calculate distance
def calculate_distance(lat1, lon1, lat2, lon2):
    return geodesic((lat1, lon1), (lat2, lon2)).km

udf_calculate_distance = udf(calculate_distance, DoubleType())
# Calculate distance

# Cross join the datasets
cross_df = crime_df.crossJoin(stations_df)
# Calculate the distance between each crime and police station
cross_df = cross_df.withColumn('distance', udf_calculate_distance(cross_df['LAT'], cross_df['LON'], cross_df['Y'], cross_df['X']))
# Find the nearest police station for each crime
nearest_df = cross_df.groupBy('DR_NO').agg(min('distance').alias('min_distance'))
# Join the nearest police station back to the original dataframe
df = crime_df.join(nearest_df, crime_df['DR_NO'] == nearest_df['DR_NO'])

# Convert the 'DATE_OCC' column to a date type
df = df.withColumn('Date', to_date(from_unixtime(unix_timestamp(df['Date Rptd'], 'dd/MM/yyyy hh:mm:ss a'))))
# Calculate average distance per year
df = df.withColumn('year', year(df['Date']))
# Filter out NULL values of 'year'
df = df.filter(df['year'].isNotNull())
# Calculate average distance per year and count the number of crimes
result = df.groupBy('year').agg(round(avg('min_distance'),3).alias('average_distance'), count('*').alias('#'))
# Sort by year
result = result.sort('year')

result.show()