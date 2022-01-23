"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
 
Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so.
 
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

from airflow import DAG, settings
 
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from airflow.models import DAG, DagRun, TaskFail, TaskInstance
from airflow.providers.amazon.aws.hooks.s3 import S3Hook

import csv, re
from io import StringIO
from airflow.models import Variable
from os import getenv
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.postgres_operator import PostgresOperator
##Mention S3 Bucket and MWAA Env##
# Get Args
MAX_AGE_IN_DAYS = 2
S3_BUCKET = ''
S3_KEY = 'mwaa_status/{0}/files/export/{1}.csv' 
MWAA_ENV_NAME = ''


OBJECTS_TO_EXPORT = [
    [DagRun,DagRun.execution_date], 
    [TaskFail,TaskFail.execution_date], 
    [TaskInstance, TaskInstance.execution_date],
]
 
def export_db_fn(**kwargs):
    ti = kwargs['ti']
    session = settings.Session()
    print("session: ",str(session))
 
    oldest_date = days_ago(MAX_AGE_IN_DAYS)
    print("oldest_date: ",oldest_date)
    s3_hook = S3Hook()
    s3_client = s3_hook.get_conn()
    for x in OBJECTS_TO_EXPORT:
        query = session.query(x[0]).filter(x[1] >= days_ago(MAX_AGE_IN_DAYS))
        print("type",type(query))
        allrows=query.all()
        name=re.sub("[<>']", "", str(x[0]))
        print(name,": ",str(allrows))
        if len(allrows) > 0:
            outfileStr=""
            f = StringIO(outfileStr)
            w = csv.DictWriter(f, vars(allrows[0]).keys())
            w.writeheader()
            for y in allrows:
                w.writerow(vars(y))
            outkey = S3_KEY.format(MWAA_ENV_NAME, name[6:])
            print("outkey:" + outkey)
            table_name=outkey.split(".",4)
            s3_client.put_object(Bucket=S3_BUCKET, Key=outkey, Body=f.getvalue())
            print("table_name:"+table_name[3])
            ti.xcom_push(key=table_name[3], value=outkey)
           
           
  
 
with DAG(dag_id="db_export_dag",schedule_interval='*/15 * * * *', catchup=False, start_date=days_ago(1),max_active_runs=1) as dag:
    export_db = PythonOperator(
        task_id="export_db",
        python_callable=export_db_fn,
        provide_context=True     
    )
    

start = DummyOperator(
    task_id='Start',
    dag=dag)
end = DummyOperator(
    task_id='End',
    dag=dag)

    
start >> export_db >> end