from datetime import datetime, timedelta, time
from textwrap import dedent

import pytz
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.sensors.time_sensor import TimeSensorAsync

TZ = pytz.timezone("America/New_York")
PYTHON_PATH = "/Users/NovdanoDY/opt/anaconda3/envs/coffee-recipe/bin/python"

default_args = {
    'owner': 'novdano',
    'depends_on_past': False,
    'email': ['novdanody@gmail.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 1,
    'retry_delta': timedelta(minutes=2),
    # 'queue': 'bash_queue',
    # 'pool': 'backfill',
    # 'priority_weight': 10,
    # 'end_date': datetime(2016, 1, 1),
    # 'wait_for_downstream': False,
    # 'dag': dag,
    # 'sla': timedelta(hours=2),
    # 'execution_timeout': timedelta(seconds=300),
    # 'on_failure_callback': some_function,
    # 'on_success_callback': some_other_function,
    # 'on_retry_callback': another_function,
    # 'sla_miss_callback': yet_another_function,
    # 'trigger_rule': 'all_success'
}
with DAG('coffee_data', default_args=default_args,
         description="Gather Coffee Financial Data from Different Sources",
         schedule_interval="0 0 * * 1,2,3,4,5",
         start_date=datetime(2022, 2, 8),
         catchup=False,
         tags=['coffee_data'],
         user_defined_filters={
            'localtz': lambda d: TZ.fromutc(d),
         },
         ) as dag:
    # start_time = time(13, 15, tzinfo=pytz.timezone('America/New_York'))
    # sensor_start = TimeSensorAsync(task_id='start', target_time=start_time)

    task1 = BashOperator(task_id='print_date', bash_command='date')
    task2 = BashOperator(task_id='collect_data_kc1',
                         retries=1,
                         bash_command='%s -m scripts.run_populate_data '
                                      '--source nasdaq --tag CHRIS/ICE_KC1' % PYTHON_PATH)
    task3 = BashOperator(task_id='collect_data_arabica',
                         retries=1,
                         bash_command='%s -m scripts.run_populate_data '
                                      '--source nasdaq --tag ODA/PCOFFOTM_USD' % PYTHON_PATH)

    task2.doc_md = dedent(
        """
        #### Task Documentation
        THIS COLLECTS KC1 DATA FROM NASDAQ ICE
        """
    )

    task3.doc_md = dedent(
        """
        #### Task Documentation
        THIS COLLECTS Arabica data from NASDAQ Open Data for Africa
        """
    )

    dag.doc_md = dedent(
        """
        This DAG defines which job runs, and what data is populated 
        """
    )

    task1 >> [task2, task3]
