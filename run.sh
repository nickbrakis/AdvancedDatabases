#!/bin/bash
start-dfs.sh
start-yarn.sh
$SPARK_HOME/sbin/start-history-server.sh
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
venv-pack -o venv.tar.gz
export PYSPARK_PYTHON=./venv/bin/python
hdfs dfsadmin -safemode leave
spark-submit --archives venv.tar.gz#venv req_1.py
spark-submit --archives venv.tar.gz#venv query_1.py
spark-submit --archives venv.tar.gz#venv query_1_sql.py
spark-submit --archives venv.tar.gz#venv query_2.py
spark-submit --archives venv.tar.gz#venv query_2_rdd.py
spark-submit --archives venv.tar.gz#venv query_3.py
spark-submit --archives venv.tar.gz#venv query_3_joins.py broadcast
spark-submit --archives venv.tar.gz#venv query_3_joins.py merge
spark-submit --archives venv.tar.gz#venv query_3_joins.py shuffle_hash
spark-submit --archives venv.tar.gz#venv query_3_joins.py shuffle_replicate_nl
spark-submit --archives venv.tar.gz#venv query_4a.py
spark-submit --archives venv.tar.gz#venv query_4a_joins.py broadcast
spark-submit --archives venv.tar.gz#venv query_4a_joins.py merge
spark-submit --archives venv.tar.gz#venv query_4a_joins.py shuffle_hash
spark-submit --archives venv.tar.gz#venv query_4a_joins.py shuffle_replicate_nl
spark-submit --archives venv.tar.gz#venv query_4b.py
spark-submit --archives venv.tar.gz#venv query_4b_joins.py broadcast
spark-submit --archives venv.tar.gz#venv query_4b_joins.py merge
spark-submit --archives venv.tar.gz#venv query_4b_joins.py shuffle_hash
spark-submit --archives venv.tar.gz#venv query_4b_joins.py shuffle_replicate_nl
deactivate
rm -rf venv
rm venv.tar.gz
