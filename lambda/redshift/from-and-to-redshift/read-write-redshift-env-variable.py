import os
import psycopg2
import psycopg2.extras
import sys


def lambda_handler(event, context):
  REDSHIFT_DATABASE = os.environ['REDSHIFT_DATABASE']
  REDSHIFT_USER = os.environ['REDSHIFT_USER']
  REDSHIFT_PASSWD = os.environ['REDSHIFT_PASSWD']
  REDSHIFT_PORT = os.environ['REDSHIFT_PORT']
  REDSHIFT_ENDPOINT = os.environ['REDSHIFT_ENDPOINT']
  REDSHIFT_QUERY = "SELECT TRIM(pgnsp.nspname) AS schema_name,\
       TRIM(pgci.relname) AS table_name,\
       TRIM(pgt.tableowner) AS table_owner,\
       TRUNC(pgci.relcreationtime) AS creation_date,\
       DATEDIFF(day, pgci.relcreationtime, getdate()) AS daysOld\
       FROM pg_class_info pgci\
       LEFT JOIN pg_namespace pgnsp ON pgci.relnamespace = pgnsp.oid\
       JOIN pg_tables pgt ON pgt.tablename = pgci.relname\
       WHERE pgci.reltype != 0\
       AND   TRIM(pgnsp.nspname) = 'scratch'\
       AND DATEDIFF(day, pgci.relcreationtime, getdate()) > '30'\
       ORDER BY 5 DESC"\

  
  try:
    conn = psycopg2.connect(
      dbname=REDSHIFT_DATABASE,
      user=REDSHIFT_USER,
      password=REDSHIFT_PASSWD,
      port=REDSHIFT_PORT,
      host=REDSHIFT_ENDPOINT)
  except Exception as ERROR:
    print("Connection Issue: " + str(ERROR))
    sys.exit(1)

  try:
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    #cursor=conn.cursor()
    cursor.execute(REDSHIFT_QUERY)
    records = cursor.fetchall()
    for row in records:
      cursor.execute("""INSERT INTO dw_pii.retention_tables_hist(schema_name,table_name,table_owner,creation_date,daysold) VALUES (%s, %s, %s, %s, %s)""",row)
      conn.commit()
      
    cursor.close()
    conn.commit()
    conn.close()
  except Exception as ERROR:
    print("Execution Issue: " + str(ERROR))
    sys.exit
  
    