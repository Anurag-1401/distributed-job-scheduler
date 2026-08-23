"""Single-command launcher.

Runs Alembic migrations against Supabase PostgreSQL and then starts one FastAPI/Uvicorn
process. The FastAPI lifespan starts the scheduler and configured logical workers in
that same process.
"""

import uvicorn
import argparse
import subprocess
import sys


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dev",
        action="store_true",
        help="Run with auto-reload enabled",
    )
    args = parser.parse_args()

    subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        check=True,
    )

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=args.dev,
    )


if __name__ == "__main__":
    main()












51-4f37-b1b0-b84c434d55db | duration=15988ms
2026-08-23 22:39:18,532 INFO app.services.jobs JOB CLAIMED | job=36d608f6-de5c-41f4-9bbb-f8533e3158f3 | worker=app-worker-3 | attempt=1   
2026-08-23 22:39:19,208 INFO app.workers.worker JOB CLAIMED BY POLLER | worker=app-worker-3 | job=36d608f6-de5c-41f4-9bbb-f8533e3158f3    
2026-08-23 22:39:19,209 INFO app.workers.worker EXECUTE START | worker=app-worker-3 | job=36d608f6-de5c-41f4-9bbb-f8533e3158f3
2026-08-23 22:39:19,401 INFO app.workers.worker EXECUTE COMPLETE | job=99932756-a4e4-45fe-9320-012a43b5508b | worker=app-worker-1
2026-08-23 22:39:19,875 INFO app.services.jobs EXECUTION STARTED | job=8cdfbb5f-8271-4a8c-974a-8f6633e8ea0d | execution=db2c9a63-b947-43f1-8289-75dc1df0b1cd | worker=app-worker-3      
2026-08-23 22:39:20,274 INFO app.workers.worker TASK START | job=8cdfbb5f-8271-4a8c-974a-8f6633e8ea0d | type=sleep
2026-08-23 22:39:20,621 INFO app.services.jobs JOB CREATED | id=9a2ca5a0-f49d-4cb1-94ef-cf0695c54403 | queue=85fe3385-c6e2-48a4-b16f-245125c95030 | state=QUEUED
2026-08-23 22:39:22,517 INFO app.services.jobs JOB CLAIMED | job=9a2ca5a0-f49d-4cb1-94ef-cf0695c54403 | worker=app-worker-1 | attempt=1   
INFO:     127.0.0.1:56330 - "POST /api/v1/jobs HTTP/1.1" 201 Created
2026-08-23 22:39:23,151 INFO app.workers.worker JOB CLAIMED BY POLLER | worker=app-worker-1 | job=9a2ca5a0-f49d-4cb1-94ef-cf0695c54403    
2026-08-23 22:39:23,152 INFO app.workers.worker EXECUTE START | worker=app-worker-1 | job=9a2ca5a0-f49d-4cb1-94ef-cf0695c54403
2026-08-23 22:39:23,278 INFO app.workers.worker TASK SUCCESS | job=8cdfbb5f-8271-4a8c-974a-8f6633e8ea0d
2026-08-23 22:39:24,805 INFO app.services.jobs JOB COMPLETED | job=1fb3b8d8-c441-4d53-bad8-d8273bdd5a96 | execution=05bf2cc9-1e5d-4547-856c-a1af2b78b117 | duration=14021ms
2026-08-23 22:39:25,264 INFO app.services.jobs JOB CLAIMED | job=de688f88-10ed-4b05-b977-200b31609f1a | worker=app-worker-3 | attempt=1   
2026-08-23 22:39:25,780 INFO app.workers.worker EXECUTE COMPLETE | job=1fb3b8d8-c441-4d53-bad8-d8273bdd5a96 | worker=app-worker-2
2026-08-23 22:39:25,991 INFO app.workers.worker JOB CLAIMED BY POLLER | worker=app-worker-3 | job=de688f88-10ed-4b05-b977-200b31609f1a    
2026-08-23 22:39:25,992 INFO app.workers.worker EXECUTE START | worker=app-worker-3 | job=de688f88-10ed-4b05-b977-200b31609f1a
2026-08-23 22:39:28,265 INFO app.services.jobs EXECUTION STARTED | job=36d608f6-de5c-41f4-9bbb-f8533e3158f3 | execution=f94291ec-4444-4b04-913b-a134579cc819 | worker=app-worker-3      
2026-08-23 22:39:28,610 INFO app.workers.worker TASK START | job=36d608f6-de5c-41f4-9bbb-f8533e3158f3 | type=echo
2026-08-23 22:39:28,611 INFO app.workers.worker TASK SUCCESS | job=36d608f6-de5c-41f4-9bbb-f8533e3158f3
2026-08-23 22:39:29,516 INFO app.services.jobs JOB CREATED | id=869c93b4-5f24-4023-b04c-114d46b8ff63 | queue=c30cbb6a-c0a5-4115-b89c-327ee10f8924 | state=QUEUED
2026-08-23 22:39:30,633 INFO app.services.jobs JOB CLAIMED | job=869c93b4-5f24-4023-b04c-114d46b8ff63 | worker=app-worker-1 | attempt=1   
2026-08-23 22:39:31,702 INFO app.workers.worker JOB CLAIMED BY POLLER | worker=app-worker-1 | job=869c93b4-5f24-4023-b04c-114d46b8ff63    
2026-08-23 22:39:31,702 INFO app.workers.worker EXECUTE START | worker=app-worker-1 | job=869c93b4-5f24-4023-b04c-114d46b8ff63
INFO:     127.0.0.1:56330 - "POST /api/v1/jobs HTTP/1.1" 201 Created
2026-08-23 22:39:32,076 INFO app.services.jobs EXECUTION STARTED | job=9a2ca5a0-f49d-4cb1-94ef-cf0695c54403 | execution=7687b96d-71fc-49e9-84ae-a17ca0b8218f | worker=app-worker-1      
2026-08-23 22:39:32,580 INFO app.workers.worker TASK START | job=9a2ca5a0-f49d-4cb1-94ef-cf0695c54403 | type=sleep
2026-08-23 22:39:34,595 INFO app.services.jobs EXECUTION STARTED | job=de688f88-10ed-4b05-b977-200b31609f1a | execution=86bcfcea-eafc-4b5a-ae73-3463016c22e5 | worker=app-worker-3      
2026-08-23 22:39:35,039 INFO app.workers.worker TASK START | job=de688f88-10ed-4b05-b977-200b31609f1a | type=echo
2026-08-23 22:39:35,039 INFO app.workers.worker TASK SUCCESS | job=de688f88-10ed-4b05-b977-200b31609f1a
2026-08-23 22:39:35,581 INFO app.workers.worker TASK SUCCESS | job=9a2ca5a0-f49d-4cb1-94ef-cf0695c54403
2026-08-23 22:39:37,694 INFO app.services.jobs JOB COMPLETED | job=36d608f6-de5c-41f4-9bbb-f8533e3158f3 | execution=f94291ec-4444-4b04-913b-a134579cc819 | duration=9789ms
2026-08-23 22:39:38,640 INFO app.services.jobs JOB COMPLETED | job=8cdfbb5f-8271-4a8c-974a-8f6633e8ea0d | execution=db2c9a63-b947-43f1-8289-75dc1df0b1cd | duration=19200ms
2026-08-23 22:39:38,920 INFO app.workers.worker EXECUTE COMPLETE | job=36d608f6-de5c-41f4-9bbb-f8533e3158f3 | worker=app-worker-3
2026-08-23 22:39:40,166 INFO app.workers.worker EXECUTE COMPLETE | job=8cdfbb5f-8271-4a8c-974a-8f6633e8ea0d | worker=app-worker-3
2026-08-23 22:39:40,948 INFO app.services.jobs JOB CREATED | id=35c22381-039a-4f13-9251-e394e2ba75c2 | queue=c30cbb6a-c0a5-4115-b89c-327ee10f8924 | state=QUEUED
2026-08-23 22:39:41,698 INFO app.services.jobs EXECUTION STARTED | job=869c93b4-5f24-4023-b04c-114d46b8ff63 | execution=60fd6101-bd6d-4dd9-af93-a2d84c3dd0f9 | worker=app-worker-1      
2026-08-23 22:39:42,077 INFO app.workers.worker TASK START | job=869c93b4-5f24-4023-b04c-114d46b8ff63 | type=flaky_task
2026-08-23 22:39:42,077 ERROR app.workers.worker JOB EXECUTION FAILED | job=869c93b4-5f24-4023-b04c-114d46b8ff63 | worker=app-worker-1    
Traceback (most recent call last):
  File "D:\Development\distributed-job-scheduler\backend\app\workers\worker.py", line 219, in execute_claimed
    result = await execute_task(
             ^^^^^^^^^^^^^^^^^^^
    ...<2 lines>...
    )
    ^
  File "D:\Development\distributed-job-scheduler\backend\app\tasks.py", line 52, in execute_task
    raise ValueError(f"Unsupported task type: {task_type}")
ValueError: Unsupported task type: flaky_task 
INFO:     127.0.0.1:56330 - "POST /api/v1/jobs HTTP/1.1" 201 Created
2026-08-23 22:39:44,227 INFO app.services.jobs JOB COMPLETED | job=de688f88-10ed-4b05-b977-200b31609f1a | execution=86bcfcea-eafc-4b5a-ae73-3463016c22e5 | duration=10051ms
2026-08-23 22:39:44,409 INFO app.services.jobs JOB COMPLETED | job=9a2ca5a0-f49d-4cb1-94ef-cf0695c54403 | execution=7687b96d-71fc-49e9-84ae-a17ca0b8218f | duration=12707ms
2026-08-23 22:39:45,218 INFO app.services.jobs JOB CLAIMED | job=35c22381-039a-4f13-9251-e394e2ba75c2 | worker=app-worker-2 | attempt=1   
2026-08-23 22:39:45,393 INFO app.workers.worker EXECUTE COMPLETE | job=de688f88-10ed-4b05-b977-200b31609f1a | worker=app-worker-3
2026-08-23 22:39:45,610 INFO app.workers.worker EXECUTE COMPLETE | job=9a2ca5a0-f49d-4cb1-94ef-cf0695c54403 | worker=app-worker-1
2026-08-23 22:39:45,877 INFO app.workers.worker JOB CLAIMED BY POLLER | worker=app-worker-2 | job=35c22381-039a-4f13-9251-e394e2ba75c2    
2026-08-23 22:39:45,877 INFO app.workers.worker EXECUTE START | worker=app-worker-2 | job=35c22381-039a-4f13-9251-e394e2ba75c2
2026-08-23 22:39:50,099 WARNING app.services.jobs JOB RETRYING | job=869c93b4-5f24-4023-b04c-114d46b8ff63 | attempt=1 | delay=2s
2026-08-23 22:39:50,809 INFO app.services.jobs JOB CREATED | id=1d604a5b-310e-47c0-ae94-58d4148fda37 | queue=5e7502d2-de4c-4131-8aaa-2ba6472ce04a | state=QUEUED
2026-08-23 22:39:52,567 INFO app.services.jobs JOB CLAIMED | job=1d604a5b-310e-47c0-ae94-58d4148fda37 | worker=app-worker-2 | attempt=1   
2026-08-23 22:39:53,157 INFO app.workers.worker JOB CLAIMED BY POLLER | worker=app-worker-2 | job=1d604a5b-310e-47c0-ae94-58d4148fda37    
2026-08-23 22:39:53,158 INFO app.workers.worker EXECUTE START | worker=app-worker-2 | job=1d604a5b-310e-47c0-ae94-58d4148fda37
INFO:     127.0.0.1:56330 - "POST /api/v1/jobs HTTP/1.1" 201 Created
2026-08-23 22:39:55,238 INFO app.services.jobs JOB CLAIMED | job=869c93b4-5f24-4023-b04c-114d46b8ff63 | worker=app-worker-3 | attempt=2   
2026-08-23 22:39:55,828 INFO app.workers.worker JOB CLAIMED BY POLLER | worker=app-worker-3 | job=869c93b4-5f24-4023-b04c-114d46b8ff63    
2026-08-23 22:39:55,829 INFO app.workers.worker EXECUTE START | worker=app-worker-3 | job=869c93b4-5f24-4023-b04c-114d46b8ff63
2026-08-23 22:39:56,067 INFO app.services.jobs EXECUTION STARTED | job=35c22381-039a-4f13-9251-e394e2ba75c2 | execution=b01840f0-cc3b-4eaa-b943-1e40d6b29d1e | worker=app-worker-2      
2026-08-23 22:39:56,480 INFO app.workers.worker TASK START | job=35c22381-039a-4f13-9251-e394e2ba75c2 | type=failure_simulation
2026-08-23 22:39:56,480 ERROR app.workers.worker JOB EXECUTION FAILED | job=35c22381-039a-4f13-9251-e394e2ba75c2 | worker=app-worker-2    
Traceback (most recent call last):
  File "D:\Development\distributed-job-scheduler\backend\app\workers\worker.py", line 219, in execute_claimed
    result = await execute_task(
             ^^^^^^^^^^^^^^^^^^^
    ...<2 lines>...
    )
    ^
  File "D:\Development\distributed-job-scheduler\backend\app\tasks.py", line 52, in execute_task
    raise ValueError(f"Unsupported task type: {task_type}")
ValueError: Unsupported task type: failure_simulation
2026-08-23 22:39:59,208 INFO app.services.jobs EXECUTION STARTED | job=1d604a5b-310e-47c0-ae94-58d4148fda37 | execution=697b0a96-c060-4073-8e0c-c5f3f63eb99c | worker=app-worker-2      
2026-08-23 22:39:59,805 INFO app.workers.worker TASK START | job=1d604a5b-310e-47c0-ae94-58d4148fda37 | type=echo
2026-08-23 22:39:59,806 INFO app.workers.worker TASK SUCCESS | job=1d604a5b-310e-47c0-ae94-58d4148fda37
INFO:     127.0.0.1:56330 - "POST /api/v1/jobs HTTP/1.1" 201 Created
2026-08-23 22:40:02,480 INFO app.services.jobs EXECUTION STARTED | job=869c93b4-5f24-4023-b04c-114d46b8ff63 | execution=9a3e5b6e-f219-43ab-8e00-cd429c2c059f | worker=app-worker-3      
2026-08-23 22:40:03,021 INFO app.workers.worker TASK START | job=869c93b4-5f24-4023-b04c-114d46b8ff63 | type=flaky_task
2026-08-23 22:40:03,022 ERROR app.workers.worker JOB EXECUTION FAILED | job=869c93b4-5f24-4023-b04c-114d46b8ff63 | worker=app-worker-3    
Traceback (most recent call last):
  File "D:\Development\distributed-job-scheduler\backend\app\workers\worker.py", line 219, in execute_claimed
    result = await execute_task(
             ^^^^^^^^^^^^^^^^^^^
    ...<2 lines>...
    )
    ^
  File "D:\Development\distributed-job-scheduler\backend\app\tasks.py", line 52, in execute_task
    raise ValueError(f"Unsupported task type: {task_type}")
ValueError: Unsupported task type: flaky_task 
2026-08-23 22:40:05,728 INFO app.services.jobs JOB COMPLETED | job=1d604a5b-310e-47c0-ae94-58d4148fda37 | execution=697b0a96-c060-4073-8e0c-c5f3f63eb99c | duration=6931ms
2026-08-23 22:40:05,919 WARNING app.services.jobs JOB RETRYING | job=35c22381-039a-4f13-9251-e394e2ba75c2 | attempt=1 | delay=2s
2026-08-23 22:40:06,620 INFO app.workers.worker EXECUTE COMPLETE | job=1d604a5b-310e-47c0-ae94-58d4148fda37 | worker=app-worker-2
2026-08-23 22:40:08,098 INFO app.services.jobs JOB CREATED | id=cedade29-50ec-4be6-b96c-a6250eb953ba | queue=5e7502d2-de4c-4131-8aaa-2ba6472ce04a | state=QUEUED
2026-08-23 22:40:08,913 INFO app.services.jobs JOB CREATED | id=1b611295-6401-4974-828f-96577dbc7e25 | queue=5e7502d2-de4c-4131-8aaa-2ba6472ce04a | state=QUEUED
2026-08-23 22:40:09,629 INFO app.services.jobs JOB CREATED | id=aaaa2779-476b-4f45-8ecb-4c40da913fb8 | queue=5e7502d2-de4c-4131-8aaa-2ba6472ce04a | state=QUEUED
2026-08-23 22:40:09,800 INFO app.services.jobs JOB CLAIMED | job=35c22381-039a-4f13-9251-e394e2ba75c2 | worker=app-worker-3 | attempt=2   
2026-08-23 22:40:10,171 INFO app.services.jobs JOB CREATED | id=49d92df7-2ad7-4ae7-a152-1a8cb4280b9c | queue=5e7502d2-de4c-4131-8aaa-2ba6472ce04a | state=QUEUED
2026-08-23 22:40:10,403 INFO app.workers.worker JOB CLAIMED BY POLLER | worker=app-worker-3 | job=35c22381-039a-4f13-9251-e394e2ba75c2    
2026-08-23 22:40:10,403 INFO app.workers.worker EXECUTE START | worker=app-worker-3 | job=35c22381-039a-4f13-9251-e394e2ba75c2
2026-08-23 22:40:10,823 INFO app.services.jobs JOB CREATED | id=c5327c40-d3fd-41cb-9e1f-ed71237ceb2b | queue=5e7502d2-de4c-4131-8aaa-2ba6472ce04a | state=QUEUED
2026-08-23 22:40:11,367 INFO app.services.jobs JOB CREATED | id=e361c82b-a28d-4786-ba3d-5a30bfd02a47 | queue=5e7502d2-de4c-4131-8aaa-2ba6472ce04a | state=QUEUED
2026-08-23 22:40:12,089 INFO app.services.jobs JOB CREATED | id=5921da86-a697-4610-af0c-5f7b87f94151 | queue=5e7502d2-de4c-4131-8aaa-2ba6472ce04a | state=QUEUED
2026-08-23 22:40:12,280 WARNING app.services.jobs JOB RETRYING | job=869c93b4-5f24-4023-b04c-114d46b8ff63 | attempt=2 | delay=4s
2026-08-23 22:40:12,608 INFO app.services.jobs JOB CREATED | id=7bba80de-8a57-4407-914e-d7c41f2c4575 | queue=5e7502d2-de4c-4131-8aaa-2ba6472ce04a | state=QUEUED
2026-08-23 22:40:12,728 INFO app.services.jobs JOB CLAIMED | job=8af70e82-0c2a-4b3d-981b-2af905ed93a2 | worker=app-worker-1 | attempt=1   
2026-08-23 22:40:13,193 INFO app.services.jobs JOB CREATED | id=9224cb93-fb33-4304-a3e7-015c07cadf35 | queue=5e7502d2-de4c-4131-8aaa-2ba6472ce04a | state=QUEUED
2026-08-23 22:40:13,390 INFO app.workers.worker JOB CLAIMED BY POLLER | worker=app-worker-1 | job=8af70e82-0c2a-4b3d-981b-2af905ed93a2    
2026-08-23 22:40:13,391 INFO app.workers.worker EXECUTE START | worker=app-worker-1 | job=8af70e82-0c2a-4b3d-981b-2af905ed93a2
2026-08-23 22:40:13,713 INFO app.services.jobs JOB CREATED | id=a50a33f5-84de-4e32-9aad-aefd554d96b2 | queue=5e7502d2-de4c-4131-8aaa-2ba6472ce04a | state=QUEUED
2026-08-23 22:40:14,277 INFO app.services.jobs JOB CREATED | id=7796d375-975c-479a-8d76-3a8799da04f6 | queue=5e7502d2-de4c-4131-8aaa-2ba6472ce04a | state=QUEUED
2026-08-23 22:40:16,127 INFO app.services.jobs JOB CLAIMED | job=093a1ab9-36e7-4f9f-9108-0cf9b6c978cd | worker=app-worker-2 | attempt=1   
2026-08-23 22:40:16,782 INFO app.workers.worker JOB CLAIMED BY POLLER | worker=app-worker-2 | job=093a1ab9-36e7-4f9f-9108-0cf9b6c978cd    
2026-08-23 22:40:16,782 INFO app.workers.worker EXECUTE START | worker=app-worker-2 | job=093a1ab9-36e7-4f9f-9108-0cf9b6c978cd
INFO:     127.0.0.1:56330 - "POST /api/v1/jobs/batch HTTP/1.1" 201 Created
2026-08-23 22:40:19,155 INFO app.services.jobs JOB CLAIMED | job=869c93b4-5f24-4023-b04c-114d46b8ff63 | worker=app-worker-1 | attempt=3   
2026-08-23 22:40:19,375 INFO app.services.jobs EXECUTION STARTED | job=35c22381-039a-4f13-9251-e394e2ba75c2 | execution=0910d86d-2299-4c4e-8a96-f6b0664c05f7 | worker=app-worker-3      
2026-08-23 22:40:19,718 INFO app.workers.worker JOB CLAIMED BY POLLER | worker=app-worker-1 | job=869c93b4-5f24-4023-b04c-114d46b8ff63    
2026-08-23 22:40:19,719 INFO app.workers.worker EXECUTE START | worker=app-worker-1 | job=869c93b4-5f24-4023-b04c-114d46b8ff63
2026-08-23 22:40:19,848 INFO app.workers.worker TASK START | job=35c22381-039a-4f13-9251-e394e2ba75c2 | type=failure_simulation
2026-08-23 22:40:19,848 ERROR app.workers.worker JOB EXECUTION FAILED | job=35c22381-039a-4f13-9251-e394e2ba75c2 | worker=app-worker-3    
Traceback (most recent call last):
  File "D:\Development\distributed-job-scheduler\backend\app\workers\worker.py", line 219, in execute_claimed
    result = await execute_task(
             ^^^^^^^^^^^^^^^^^^^
    ...<2 lines>...
    )
    ^
  File "D:\Development\distributed-job-scheduler\backend\app\tasks.py", line 52, in execute_task
    raise ValueError(f"Unsupported task type: {task_type}")
ValueError: Unsupported task type: failure_simulation
2026-08-23 22:40:20,130 INFO app.services.jobs EXECUTION STARTED | job=8af70e82-0c2a-4b3d-981b-2af905ed93a2 | execution=24609190-a723-4bd0-bb80-9fd7fd2ec95b | worker=app-worker-1      
2026-08-23 22:40:20,633 INFO app.workers.worker TASK START | job=8af70e82-0c2a-4b3d-981b-2af905ed93a2 | type=echo
2026-08-23 22:40:20,633 INFO app.workers.worker TASK SUCCESS | job=8af70e82-0c2a-4b3d-981b-2af905ed93a2
2026-08-23 22:40:22,742 INFO app.services.jobs JOB CLAIMED | job=49d92df7-2ad7-4ae7-a152-1a8cb4280b9c | worker=app-worker-3 | attempt=1   
2026-08-23 22:40:23,568 INFO app.workers.worker JOB CLAIMED BY POLLER | worker=app-worker-3 | job=49d92df7-2ad7-4ae7-a152-1a8cb4280b9c    
2026-08-23 22:40:23,569 INFO app.workers.worker EXECUTE START | worker=app-worker-3 | job=49d92df7-2ad7-4ae7-a152-1a8cb4280b9c
2026-08-23 22:40:24,314 INFO app.services.jobs EXECUTION STARTED | job=093a1ab9-36e7-4f9f-9108-0cf9b6c978cd | execution=21b1f094-1537-4ebb-ba0d-290ed2a7db3b | worker=app-worker-2      
2026-08-23 22:40:24,704 INFO app.workers.worker TASK START | job=093a1ab9-36e7-4f9f-9108-0cf9b6c978cd | type=echo
2026-08-23 22:40:24,704 INFO app.workers.worker TASK SUCCESS | job=093a1ab9-36e7-4f9f-9108-0cf9b6c978cd
2026-08-23 22:40:25,219 INFO app.services.jobs JOB CREATED | id=9cf20d14-763b-4a83-87a6-973ef74482d8 | queue=c0b7845b-da15-468b-872a-f1ef4faa1793 | state=SCHEDULED
2026-08-23 22:40:26,559 INFO app.services.jobs JOB CLAIMED | job=5921da86-a697-4610-af0c-5f7b87f94151 | worker=app-worker-1 | attempt=1   
2026-08-23 22:40:27,128 INFO app.workers.worker JOB CLAIMED BY POLLER | worker=app-worker-1 | job=5921da86-a697-4610-af0c-5f7b87f94151    
2026-08-23 22:40:27,129 INFO app.workers.worker EXECUTE START | worker=app-worker-1 | job=5921da86-a697-4610-af0c-5f7b87f94151
INFO:     127.0.0.1:56330 - "POST /api/v1/jobs HTTP/1.1" 201 Created
2026-08-23 22:40:27,657 INFO app.services.jobs EXECUTION STARTED | job=869c93b4-5f24-4023-b04c-114d46b8ff63 | execution=50ba1f72-cf31-4316-bfaa-cc9fde88ee07 | worker=app-worker-1      
2026-08-23 22:40:28,006 INFO app.workers.worker TASK START | job=869c93b4-5f24-4023-b04c-114d46b8ff63 | type=flaky_task
2026-08-23 22:40:28,006 ERROR app.workers.worker JOB EXECUTION FAILED | job=869c93b4-5f24-4023-b04c-114d46b8ff63 | worker=app-worker-1    
Traceback (most recent call last):
  File "D:\Development\distributed-job-scheduler\backend\app\workers\worker.py", line 219, in execute_claimed
    result = await execute_task(
             ^^^^^^^^^^^^^^^^^^^
    ...<2 lines>...
    )
    ^
  File "D:\Development\distributed-job-scheduler\backend\app\tasks.py", line 52, in execute_task
    raise ValueError(f"Unsupported task type: {task_type}")
ValueError: Unsupported task type: flaky_task 
2026-08-23 22:40:29,707 INFO app.services.jobs JOB COMPLETED | job=8af70e82-0c2a-4b3d-981b-2af905ed93a2 | execution=24609190-a723-4bd0-bb80-9fd7fd2ec95b | duration=10004ms
2026-08-23 22:40:30,836 INFO app.services.jobs JOB CLAIMED | job=a50a33f5-84de-4e32-9aad-aefd554d96b2 | worker=app-worker-3 | attempt=1   
2026-08-23 22:40:30,855 INFO app.workers.worker EXECUTE COMPLETE | job=8af70e82-0c2a-4b3d-981b-2af905ed93a2 | worker=app-worker-1
2026-08-23 22:40:31,422 INFO app.workers.worker JOB CLAIMED BY POLLER | worker=app-worker-3 | job=a50a33f5-84de-4e32-9aad-aefd554d96b2    
2026-08-23 22:40:31,422 INFO app.workers.worker EXECUTE START | worker=app-worker-3 | job=a50a33f5-84de-4e32-9aad-aefd554d96b2
2026-08-23 22:40:32,181 INFO app.services.jobs EXECUTION STARTED | job=49d92df7-2ad7-4ae7-a152-1a8cb4280b9c | execution=f1837952-0cba-4c37-813b-bab6a23f3718 | worker=app-worker-3      
2026-08-23 22:40:32,748 INFO app.workers.worker TASK START | job=49d92df7-2ad7-4ae7-a152-1a8cb4280b9c | type=echo
2026-08-23 22:40:32,748 INFO app.workers.worker TASK SUCCESS | job=49d92df7-2ad7-4ae7-a152-1a8cb4280b9c
2026-08-23 22:40:33,385 INFO app.services.jobs JOB CLAIMED | job=aaaa2779-476b-4f45-8ecb-4c40da913fb8 | worker=app-worker-2 | attempt=1   
2026-08-23 22:40:34,606 INFO app.workers.worker JOB CLAIMED BY POLLER | worker=app-worker-2 | job=aaaa2779-476b-4f45-8ecb-4c40da913fb8    
2026-08-23 22:40:34,607 INFO app.workers.worker EXECUTE START | worker=app-worker-2 | job=aaaa2779-476b-4f45-8ecb-4c40da913fb8
2026-08-23 22:40:34,844 INFO app.services.jobs JOB COMPLETED | job=093a1ab9-36e7-4f9f-9108-0cf9b6c978cd | execution=21b1f094-1537-4ebb-ba0d-290ed2a7db3b | duration=10949ms
2026-08-23 22:40:35,784 WARNING app.services.jobs JOB RETRYING | job=35c22381-039a-4f13-9251-e394e2ba75c2 | attempt=2 | delay=4s
2026-08-23 22:40:35,786 INFO app.workers.worker EXECUTE COMPLETE | job=093a1ab9-36e7-4f9f-9108-0cf9b6c978cd | worker=app-worker-2
2026-08-23 22:40:38,092 INFO app.services.jobs JOB CLAIMED | job=e361c82b-a28d-4786-ba3d-5a30bfd02a47 | worker=app-worker-1 | attempt=1   
2026-08-23 22:40:38,707 INFO app.workers.worker JOB CLAIMED BY POLLER | worker=app-worker-1 | job=e361c82b-a28d-4786-ba3d-5a30bfd02a47    
2026-08-23 22:40:38,708 INFO app.workers.worker EXECUTE START | worker=app-worker-1 | job=e361c82b-a28d-4786-ba3d-5a30bfd02a47
2026-08-23 22:40:39,706 INFO app.services.jobs EXECUTION STARTED | job=5921da86-a697-4610-af0c-5f7b87f94151 | execution=7cb6a752-3409-4b4d-bd54-550484654852 | worker=app-worker-1      
2026-08-23 22:40:40,163 INFO app.workers.worker TASK START | job=5921da86-a697-4610-af0c-5f7b87f94151 | type=echo
2026-08-23 22:40:40,164 INFO app.workers.worker TASK SUCCESS | job=5921da86-a697-4610-af0c-5f7b87f94151
INFO:     127.0.0.1:56330 - "POST /api/v1/jobs/9cf20d14-763b-4a83-87a6-973ef74482d8/cancel HTTP/1.1" 200 OK
2026-08-23 22:40:42,362 INFO app.services.jobs JOB CLAIMED | job=35c22381-039a-4f13-9251-e394e2ba75c2 | worker=app-worker-3 | attempt=3   
2026-08-23 22:40:42,999 INFO app.workers.worker JOB CLAIMED BY POLLER | worker=app-worker-3 | job=35c22381-039a-4f13-9251-e394e2ba75c2    
2026-08-23 22:40:42,999 INFO app.workers.worker EXECUTE START | worker=app-worker-3 | job=35c22381-039a-4f13-9251-e394e2ba75c2
2026-08-23 22:40:43,175 INFO app.services.jobs EXECUTION STARTED | job=a50a33f5-84de-4e32-9aad-aefd554d96b2 | execution=145e24c5-035e-4236-99f5-67aa5f4f1575 | worker=app-worker-3      
2026-08-23 22:40:43,558 INFO app.workers.worker TASK START | job=a50a33f5-84de-4e32-9aad-aefd554d96b2 | type=echo
2026-08-23 22:40:43,558 INFO app.workers.worker TASK SUCCESS | job=a50a33f5-84de-4e32-9aad-aefd554d96b2
2026-08-23 22:40:43,955 INFO app.services.jobs JOB COMPLETED | job=49d92df7-2ad7-4ae7-a152-1a8cb4280b9c | execution=f1837952-0cba-4c37-813b-bab6a23f3718 | duration=12233ms
2026-08-23 22:40:45,017 INFO app.workers.worker EXECUTE COMPLETE | job=49d92df7-2ad7-4ae7-a152-1a8cb4280b9c | worker=app-worker-3
2026-08-23 22:40:45,616 INFO app.services.jobs JOB CLAIMED | job=9224cb93-fb33-4304-a3e7-015c07cadf35 | worker=app-worker-2 | attempt=1   
2026-08-23 22:40:46,174 INFO app.workers.worker JOB CLAIMED BY POLLER | worker=app-worker-2 | job=9224cb93-fb33-4304-a3e7-015c07cadf35    
2026-08-23 22:40:46,175 INFO app.workers.worker EXECUTE START | worker=app-worker-2 | job=9224cb93-fb33-4304-a3e7-015c07cadf35
2026-08-23 22:40:47,756 INFO app.services.jobs EXECUTION STARTED | job=aaaa2779-476b-4f45-8ecb-4c40da913fb8 | execution=95a33911-6e60-48b7-9cd6-9233107137e4 | worker=app-worker-2      
2026-08-23 22:40:48,215 INFO app.workers.worker TASK START | job=aaaa2779-476b-4f45-8ecb-4c40da913fb8 | type=echo
2026-08-23 22:40:48,215 INFO app.workers.worker TASK SUCCESS | job=aaaa2779-476b-4f45-8ecb-4c40da913fb8
2026-08-23 22:40:49,501 INFO app.services.jobs JOB CLAIMED | job=1b611295-6401-4974-828f-96577dbc7e25 | worker=app-worker-1 | attempt=1   
2026-08-23 22:41:03,262 INFO app.services.jobs EXECUTION STARTED | job=e361c82b-a28d-4786-ba3d-5a30bfd02a47 | execution=64a85875-32b7-4bfd-8830-212258347d58 | worker=app-worker-1      
2026-08-23 22:41:03,454 ERROR app.services.jobs JOB DEAD LETTER | job=869c93b4-5f24-4023-b04c-114d46b8ff63 | attempts=3
2026-08-23 22:41:03,669 INFO app.workers.worker TASK START | job=e361c82b-a28d-4786-ba3d-5a30bfd02a47 | type=echo
2026-08-23 22:41:03,669 INFO app.workers.worker TASK SUCCESS | job=e361c82b-a28d-4786-ba3d-5a30bfd02a47
2026-08-23 22:41:03,854 INFO app.workers.worker JOB CLAIMED BY POLLER | worker=app-worker-1 | job=1b611295-6401-4974-828f-96577dbc7e25    
2026-08-23 22:41:03,855 INFO app.workers.worker EXECUTE START | worker=app-worker-1 | job=1b611295-6401-4974-828f-96577dbc7e25
2026-08-23 22:41:05,532 INFO app.services.jobs JOB CREATED | id=03bdc0f7-6ed8-4c12-88cd-5f447620f6e4 | queue=5e7502d2-de4c-4131-8aaa-2ba6472ce04a | state=QUEUED
2026-08-23 22:41:06,049 INFO app.services.jobs JOB COMPLETED | job=5921da86-a697-4610-af0c-5f7b87f94151 | execution=7cb6a752-3409-4b4d-bd54-550484654852 | duration=26767ms
2026-08-23 22:41:06,970 INFO app.workers.worker EXECUTE COMPLETE | job=5921da86-a697-4610-af0c-5f7b87f94151 | worker=app-worker-1
INFO:     127.0.0.1:56330 - "POST /api/v1/jobs HTTP/1.1" 201 Created
2026-08-23 22:41:09,330 INFO app.services.jobs EXECUTION STARTED | job=35c22381-039a-4f13-9251-e394e2ba75c2 | execution=7eea153b-c885-4d9d-80ff-be84accada4a | worker=app-worker-3      
2026-08-23 22:41:09,670 INFO app.services.jobs JOB CLAIMED | job=03bdc0f7-6ed8-4c12-88cd-5f447620f6e4 | worker=app-worker-2 | attempt=1   
2026-08-23 22:41:09,729 INFO app.workers.worker TASK START | job=35c22381-039a-4f13-9251-e394e2ba75c2 | type=failure_simulation
2026-08-23 22:41:09,729 ERROR app.workers.worker JOB EXECUTION FAILED | job=35c22381-039a-4f13-9251-e394e2ba75c2 | worker=app-worker-3    
Traceback (most recent call last):
  File "D:\Development\distributed-job-scheduler\backend\app\workers\worker.py", line 219, in execute_claimed
    result = await execute_task(
             ^^^^^^^^^^^^^^^^^^^
    ...<2 lines>...
    )
    ^
  File "D:\Development\distributed-job-scheduler\backend\app\tasks.py", line 52, in execute_task
    raise ValueError(f"Unsupported task type: {task_type}")
ValueError: Unsupported task type: failure_simulation
2026-08-23 22:41:09,744 INFO app.services.jobs JOB COMPLETED | job=a50a33f5-84de-4e32-9aad-aefd554d96b2 | execution=145e24c5-035e-4236-99f5-67aa5f4f1575 | duration=27027ms
2026-08-23 22:41:10,271 INFO app.workers.worker JOB CLAIMED BY POLLER | worker=app-worker-2 | job=03bdc0f7-6ed8-4c12-88cd-5f447620f6e4    
2026-08-23 22:41:10,272 INFO app.workers.worker EXECUTE START | worker=app-worker-2 | job=03bdc0f7-6ed8-4c12-88cd-5f447620f6e4
2026-08-23 22:41:10,682 INFO app.workers.worker EXECUTE COMPLETE | job=a50a33f5-84de-4e32-9aad-aefd554d96b2 | worker=app-worker-3
2026-08-23 22:41:12,574 INFO app.services.jobs EXECUTION STARTED | job=9224cb93-fb33-4304-a3e7-015c07cadf35 | execution=c3887016-b012-4adc-85ee-4420dd3dc1e7 | worker=app-worker-2      
2026-08-23 22:41:12,931 INFO app.workers.worker TASK START | job=9224cb93-fb33-4304-a3e7-015c07cadf35 | type=echo
2026-08-23 22:41:12,932 INFO app.workers.worker TASK SUCCESS | job=9224cb93-fb33-4304-a3e7-015c07cadf35
2026-08-23 22:41:13,320 INFO app.services.jobs JOB COMPLETED | job=aaaa2779-476b-4f45-8ecb-4c40da913fb8 | execution=95a33911-6e60-48b7-9cd6-9233107137e4 | duration=26056ms
2026-08-23 22:41:14,544 INFO app.workers.worker EXECUTE COMPLETE | job=aaaa2779-476b-4f45-8ecb-4c40da913fb8 | worker=app-worker-2
2026-08-23 22:41:16,943 INFO app.services.jobs JOB CLAIMED | job=c5327c40-d3fd-41cb-9e1f-ed71237ceb2b | worker=app-worker-1 | attempt=1   
2026-08-23 22:41:17,204 INFO app.services.jobs JOB COMPLETED | job=e361c82b-a28d-4786-ba3d-5a30bfd02a47 | execution=64a85875-32b7-4bfd-8830-212258347d58 | duration=27321ms
2026-08-23 22:41:17,562 INFO app.workers.worker JOB CLAIMED BY POLLER | worker=app-worker-1 | job=c5327c40-d3fd-41cb-9e1f-ed71237ceb2b    
2026-08-23 22:41:17,562 INFO app.workers.worker EXECUTE START | worker=app-worker-1 | job=c5327c40-d3fd-41cb-9e1f-ed71237ceb2b
2026-08-23 22:41:18,272 INFO app.services.jobs EXECUTION STARTED | job=1b611295-6401-4974-828f-96577dbc7e25 | execution=e0de16f1-7937-43db-adb2-70fc1ee13980 | worker=app-worker-1      
2026-08-23 22:41:18,641 INFO app.workers.worker EXECUTE COMPLETE | job=e361c82b-a28d-4786-ba3d-5a30bfd02a47 | worker=app-worker-1
2026-08-23 22:41:18,642 INFO app.workers.worker TASK START | job=1b611295-6401-4974-828f-96577dbc7e25 | type=echo
2026-08-23 22:41:18,643 INFO app.workers.worker TASK SUCCESS | job=1b611295-6401-4974-828f-96577dbc7e25
2026-08-23 22:41:19,192 INFO app.services.jobs JOB CREATED | id=cda2563e-be23-4be4-bee2-9bff201838f6 | queue=5e7502d2-de4c-4131-8aaa-2ba6472ce04a | state=QUEUED
2026-08-23 22:41:20,870 INFO app.services.jobs JOB CLAIMED | job=cda2563e-be23-4be4-bee2-9bff201838f6 | worker=app-worker-2 | attempt=1   
INFO:     127.0.0.1:56330 - "POST /api/v1/jobs HTTP/1.1" 201 Created
2026-08-23 22:41:21,333 ERROR app.services.jobs JOB DEAD LETTER | job=35c22381-039a-4f13-9251-e394e2ba75c2 | attempts=3
2026-08-23 22:41:21,463 INFO app.workers.worker JOB CLAIMED BY POLLER | worker=app-worker-2 | job=cda2563e-be23-4be4-bee2-9bff201838f6    
2026-08-23 22:41:21,463 INFO app.workers.worker EXECUTE START | worker=app-worker-2 | job=cda2563e-be23-4be4-bee2-9bff201838f6
2026-08-23 22:41:23,638 INFO app.services.jobs JOB COMPLETED | job=9224cb93-fb33-4304-a3e7-015c07cadf35 | execution=c3887016-b012-4adc-85ee-4420dd3dc1e7 | duration=11476ms
2026-08-23 22:41:30,723 INFO app.workers.worker EXECUTE COMPLETE | job=9224cb93-fb33-4304-a3e7-015c07cadf35 | worker=app-worker-2
2026-08-23 22:41:31,570 INFO app.services.jobs JOB CLAIMED | job=7bba80de-8a57-4407-914e-d7c41f2c4575 | worker=app-worker-1 | attempt=1   
2026-08-23 22:41:32,140 INFO app.workers.worker JOB CLAIMED BY POLLER | worker=app-worker-1 | job=7bba80de-8a57-4407-914e-d7c41f2c4575    
2026-08-23 22:41:32,140 INFO app.workers.worker EXECUTE START | worker=app-worker-1 | job=7bba80de-8a57-4407-914e-d7c41f2c4575
2026-08-23 22:41:32,803 INFO app.services.jobs EXECUTION STARTED | job=c5327c40-d3fd-41cb-9e1f-ed71237ceb2b | execution=eef483a9-6bef-466d-97c1-23a32f42c8f2 | worker=app-worker-1      
2026-08-23 22:41:33,385 INFO app.workers.worker TASK START | job=c5327c40-d3fd-41cb-9e1f-ed71237ceb2b | type=echo
2026-08-23 22:41:33,385 INFO app.workers.worker TASK SUCCESS | job=c5327c40-d3fd-41cb-9e1f-ed71237ceb2b
2026-08-23 22:41:34,577 INFO app.services.jobs JOB COMPLETED | job=1b611295-6401-4974-828f-96577dbc7e25 | execution=e0de16f1-7937-43db-adb2-70fc1ee13980 | duration=16809ms
2026-08-23 22:41:35,140 INFO app.services.jobs EXECUTION STARTED | job=03bdc0f7-6ed8-4c12-88cd-5f447620f6e4 | execution=69d92393-d05c-4577-8984-353ebf998010 | worker=app-worker-2      
2026-08-23 22:41:35,534 INFO app.workers.worker TASK START | job=03bdc0f7-6ed8-4c12-88cd-5f447620f6e4 | type=data_processing
2026-08-23 22:41:35,534 INFO app.workers.worker TASK SUCCESS | job=03bdc0f7-6ed8-4c12-88cd-5f447620f6e4
2026-08-23 22:41:35,540 INFO app.workers.worker EXECUTE COMPLETE | job=1b611295-6401-4974-828f-96577dbc7e25 | worker=app-worker-1
2026-08-23 22:41:37,075 INFO app.services.jobs JOB CREATED | id=cd939c1a-85d4-41e2-9123-94f4fef31af8 | queue=5e7502d2-de4c-4131-8aaa-2ba6472ce04a | state=QUEUED
2026-08-23 22:41:37,520 INFO app.services.jobs JOB CLAIMED | job=7796d375-975c-479a-8d76-3a8799da04f6 | worker=app-worker-2 | attempt=1   
2026-08-23 22:41:38,107 INFO app.workers.worker JOB CLAIMED BY POLLER | worker=app-worker-2 | job=7796d375-975c-479a-8d76-3a8799da04f6    
2026-08-23 22:41:38,108 INFO app.workers.worker EXECUTE START | worker=app-worker-2 | job=7796d375-975c-479a-8d76-3a8799da04f6
INFO:     127.0.0.1:56330 - "POST /api/v1/jobs HTTP/1.1" 201 Created
2026-08-23 22:41:39,478 INFO app.services.jobs EXECUTION STARTED | job=cda2563e-be23-4be4-bee2-9bff201838f6 | execution=f4259c4e-ad2f-4fff-ae3f-59b341f2e91e | worker=app-worker-2      
2026-08-23 22:41:39,905 INFO app.workers.worker TASK START | job=cda2563e-be23-4be4-bee2-9bff201838f6 | type=email_simulation
2026-08-23 22:41:39,905 INFO app.workers.worker TASK SUCCESS | job=cda2563e-be23-4be4-bee2-9bff201838f6
2026-08-23 22:41:40,855 INFO app.services.jobs JOB CLAIMED | job=cd939c1a-85d4-41e2-9123-94f4fef31af8 | worker=app-worker-1 | attempt=1   
2026-08-23 22:41:41,408 INFO app.workers.worker JOB CLAIMED BY POLLER | worker=app-worker-1 | job=cd939c1a-85d4-41e2-9123-94f4fef31af8    
2026-08-23 22:41:41,409 INFO app.workers.worker EXECUTE START | worker=app-worker-1 | job=cd939c1a-85d4-41e2-9123-94f4fef31af8
2026-08-23 22:41:42,338 INFO app.services.jobs EXECUTION STARTED | job=7bba80de-8a57-4407-914e-d7c41f2c4575 | execution=f1857609-3639-4eaf-baf8-c8554568d56c | worker=app-worker-1      
2026-08-23 22:41:42,546 INFO app.services.jobs JOB COMPLETED | job=c5327c40-d3fd-41cb-9e1f-ed71237ceb2b | execution=eef483a9-6bef-466d-97c1-23a32f42c8f2 | duration=10196ms
2026-08-23 22:41:42,729 INFO app.workers.worker TASK START | job=7bba80de-8a57-4407-914e-d7c41f2c4575 | type=echo
2026-08-23 22:41:42,729 INFO app.workers.worker TASK SUCCESS | job=7bba80de-8a57-4407-914e-d7c41f2c4575
2026-08-23 22:41:43,643 INFO app.workers.worker EXECUTE COMPLETE | job=c5327c40-d3fd-41cb-9e1f-ed71237ceb2b | worker=app-worker-1
2026-08-23 22:41:43,737 INFO app.services.jobs JOB COMPLETED | job=03bdc0f7-6ed8-4c12-88cd-5f447620f6e4 | execution=69d92393-d05c-4577-8984-353ebf998010 | duration=8970ms
2026-08-23 22:41:44,886 INFO app.workers.worker EXECUTE COMPLETE | job=03bdc0f7-6ed8-4c12-88cd-5f447620f6e4 | worker=app-worker-2
2026-08-23 22:41:46,844 INFO app.services.jobs JOB CLAIMED | job=f182941c-eb2f-40ff-a92f-0bb28c6e098f | worker=app-worker-2 | attempt=1   
2026-08-23 22:41:47,413 INFO app.workers.worker JOB CLAIMED BY POLLER | worker=app-worker-2 | job=f182941c-eb2f-40ff-a92f-0bb28c6e098f    
2026-08-23 22:41:47,414 INFO app.workers.worker EXECUTE START | worker=app-worker-2 | job=f182941c-eb2f-40ff-a92f-0bb28c6e098f
2026-08-23 22:41:47,490 INFO app.services.jobs JOB CREATED | id=765f181a-5d54-4c59-b90d-ce24a686b91e | queue=5e7502d2-de4c-4131-8aaa-2ba6472ce04a | state=QUEUED
2026-08-23 22:41:48,788 INFO app.services.jobs EXECUTION STARTED | job=7796d375-975c-479a-8d76-3a8799da04f6 | execution=ef2fa3d7-a692-4244-ad88-961a0526138c | worker=app-worker-2      
2026-08-23 22:41:49,190 INFO app.workers.worker TASK START | job=7796d375-975c-479a-8d76-3a8799da04f6 | type=echo
2026-08-23 22:41:49,190 INFO app.workers.worker TASK SUCCESS | job=7796d375-975c-479a-8d76-3a8799da04f6
INFO:     127.0.0.1:56330 - "POST /api/v1/jobs HTTP/1.1" 201 Created
2026-08-23 22:41:49,782 INFO app.services.jobs JOB COMPLETED | job=cda2563e-be23-4be4-bee2-9bff201838f6 | execution=f4259c4e-ad2f-4fff-ae3f-59b341f2e91e | duration=10716ms
2026-08-23 22:41:50,776 INFO app.workers.worker EXECUTE COMPLETE | job=cda2563e-be23-4be4-bee2-9bff201838f6 | worker=app-worker-2
2026-08-23 22:41:51,574 INFO app.services.jobs JOB CLAIMED | job=b2026bd7-f6a8-46c5-b468-bbf165ce02af | worker=app-worker-1 | attempt=1   
2026-08-23 22:41:52,156 INFO app.workers.worker JOB CLAIMED BY POLLER | worker=app-worker-1 | job=b2026bd7-f6a8-46c5-b468-bbf165ce02af    
2026-08-23 22:41:52,157 INFO app.workers.worker EXECUTE START | worker=app-worker-1 | job=b2026bd7-f6a8-46c5-b468-bbf165ce02af
2026-08-23 22:41:53,274 INFO app.services.jobs EXECUTION STARTED | job=cd939c1a-85d4-41e2-9123-94f4fef31af8 | execution=730f282e-b756-4961-b9a3-5fd282db3ff6 | worker=app-worker-1      
2026-08-23 22:41:53,630 INFO app.workers.worker TASK START | job=cd939c1a-85d4-41e2-9123-94f4fef31af8 | type=data_processing
2026-08-23 22:41:53,630 INFO app.workers.worker TASK SUCCESS | job=cd939c1a-85d4-41e2-9123-94f4fef31af8
2026-08-23 22:41:54,457 INFO app.services.jobs JOB COMPLETED | job=7bba80de-8a57-4407-914e-d7c41f2c4575 | execution=f1857609-3639-4eaf-baf8-c8554568d56c | duration=12527ms
2026-08-23 22:41:55,400 INFO app.workers.worker EXECUTE COMPLETE | job=7bba80de-8a57-4407-914e-d7c41f2c4575 | worker=app-worker-1
2026-08-23 22:41:55,586 INFO app.services.jobs JOB CLAIMED | job=765f181a-5d54-4c59-b90d-ce24a686b91e | worker=app-worker-2 | attempt=1   
2026-08-23 22:41:56,130 INFO app.workers.worker JOB CLAIMED BY POLLER | worker=app-worker-2 | job=765f181a-5d54-4c59-b90d-ce24a686b91e    
2026-08-23 22:41:56,131 INFO app.workers.worker EXECUTE START | worker=app-worker-2 | job=765f181a-5d54-4c59-b90d-ce24a686b91e
2026-08-23 22:41:57,119 INFO app.services.jobs EXECUTION STARTED | job=f182941c-eb2f-40ff-a92f-0bb28c6e098f | execution=65c3c5e3-bd34-4bca-b757-3d8e5e8dbfd5 | worker=app-worker-2      
2026-08-23 22:41:57,568 INFO app.workers.worker TASK START | job=f182941c-eb2f-40ff-a92f-0bb28c6e098f | type=echo
2026-08-23 22:41:57,568 INFO app.workers.worker TASK SUCCESS | job=f182941c-eb2f-40ff-a92f-0bb28c6e098f
2026-08-23 22:41:58,348 INFO app.services.jobs JOB CREATED | id=bed6243a-d35d-49d6-a042-15f88ab10b26 | queue=5e7502d2-de4c-4131-8aaa-2ba6472ce04a | state=QUEUED
2026-08-23 22:41:58,513 INFO app.services.jobs JOB COMPLETED | job=7796d375-975c-479a-8d76-3a8799da04f6 | execution=ef2fa3d7-a692-4244-ad88-961a0526138c | duration=10143ms
2026-08-23 22:41:59,716 INFO app.workers.worker EXECUTE COMPLETE | job=7796d375-975c-479a-8d76-3a8799da04f6 | worker=app-worker-2
INFO:     127.0.0.1:56330 - "POST /api/v1/jobs HTTP/1.1" 201 Created
2026-08-23 22:42:02,205 INFO app.services.jobs EXECUTION STARTED | job=b2026bd7-f6a8-46c5-b468-bbf165ce02af | execution=175ae09b-37de-450d-9fb9-7f4f9d3cf88c | worker=app-worker-1      
2026-08-23 22:42:02,579 INFO app.workers.worker TASK START | job=b2026bd7-f6a8-46c5-b468-bbf165ce02af | type=echo
2026-08-23 22:42:02,579 INFO app.workers.worker TASK SUCCESS | job=b2026bd7-f6a8-46c5-b468-bbf165ce02af
2026-08-23 22:42:02,679 INFO app.services.jobs JOB COMPLETED | job=cd939c1a-85d4-41e2-9123-94f4fef31af8 | execution=730f282e-b756-4961-b9a3-5fd282db3ff6 | duration=9749ms
2026-08-23 22:42:03,747 INFO app.workers.worker EXECUTE COMPLETE | job=cd939c1a-85d4-41e2-9123-94f4fef31af8 | worker=app-worker-1
2026-08-23 22:42:04,471 INFO app.services.jobs JOB CLAIMED | job=bed6243a-d35d-49d6-a042-15f88ab10b26 | worker=app-worker-2 | attempt=1   
2026-08-23 22:42:05,017 INFO app.workers.worker JOB CLAIMED BY POLLER | worker=app-worker-2 | job=bed6243a-d35d-49d6-a042-15f88ab10b26    
2026-08-23 22:42:05,018 INFO app.workers.worker EXECUTE START | worker=app-worker-2 | job=bed6243a-d35d-49d6-a042-15f88ab10b26
2026-08-23 22:42:06,310 INFO app.services.jobs JOB COMPLETED | job=f182941c-eb2f-40ff-a92f-0bb28c6e098f | execution=65c3c5e3-bd34-4bca-b757-3d8e5e8dbfd5 | duration=9591ms
2026-08-23 22:42:06,614 INFO app.services.jobs EXECUTION STARTED | job=765f181a-5d54-4c59-b90d-ce24a686b91e | execution=7fa99e11-4a51-419c-a2bc-04ae286ba066 | worker=app-worker-2      
2026-08-23 22:42:07,024 INFO app.workers.worker TASK START | job=765f181a-5d54-4c59-b90d-ce24a686b91e | type=email_simulation
2026-08-23 22:42:07,024 INFO app.workers.worker TASK SUCCESS | job=765f181a-5d54-4c59-b90d-ce24a686b91e
2026-08-23 22:42:07,284 INFO app.workers.worker EXECUTE COMPLETE | job=f182941c-eb2f-40ff-a92f-0bb28c6e098f | worker=app-worker-2
2026-08-23 22:42:09,526 INFO app.services.jobs JOB COMPLETED | job=b2026bd7-f6a8-46c5-b468-bbf165ce02af | execution=175ae09b-37de-450d-9fb9-7f4f9d3cf88c | duration=7693ms
2026-08-23 22:42:10,690 INFO app.workers.worker EXECUTE COMPLETE | job=b2026bd7-f6a8-46c5-b468-bbf165ce02af | worker=app-worker-1
2026-08-23 22:42:10,970 INFO app.services.jobs EXECUTION STARTED | job=bed6243a-d35d-49d6-a042-15f88ab10b26 | execution=6ec149b3-6230-4ee5-be36-543aa4c85af6 | worker=app-worker-2      
2026-08-23 22:42:11,509 INFO app.workers.worker TASK START | job=bed6243a-d35d-49d6-a042-15f88ab10b26 | type=data_processing
2026-08-23 22:42:11,509 INFO app.workers.worker TASK SUCCESS | job=bed6243a-d35d-49d6-a042-15f88ab10b26
2026-08-23 22:42:14,138 INFO app.services.jobs JOB COMPLETED | job=765f181a-5d54-4c59-b90d-ce24a686b91e | execution=7fa99e11-4a51-419c-a2bc-04ae286ba066 | duration=7933ms
2026-08-23 22:42:15,218 INFO app.workers.worker EXECUTE COMPLETE | job=765f181a-5d54-4c59-b90d-ce24a686b91e | worker=app-worker-2
2026-08-23 22:42:15,970 INFO app.services.jobs JOB COMPLETED | job=bed6243a-d35d-49d6-a042-15f88ab10b26 | execution=6ec149b3-6230-4ee5-be36-543aa4c85af6 | duration=5356ms
2026-08-23 22:42:16,926 INFO app.workers.worker EXECUTE COMPLETE | job=bed6243a-d35d-49d6-a042-15f88ab10b26 | worker=app-worker-2
2026-08-23 22:42:18,748 INFO app.services.jobs JOB CLAIMED | job=5be58300-5029-4361-9928-f57ea10afc4a | worker=app-worker-1 | attempt=1   
2026-08-23 22:42:19,274 INFO app.workers.worker JOB CLAIMED BY POLLER | worker=app-worker-1 | job=5be58300-5029-4361-9928-f57ea10afc4a    
2026-08-23 22:42:19,275 INFO app.workers.worker EXECUTE START | worker=app-worker-1 | job=5be58300-5029-4361-9928-f57ea10afc4a
2026-08-23 22:42:21,636 INFO app.services.jobs JOB CLAIMED | job=3520cd95-f37c-4ffe-be14-97b636c3a500 | worker=app-worker-1 | attempt=1   
2026-08-23 22:42:22,024 INFO app.services.jobs EXECUTION STARTED | job=5be58300-5029-4361-9928-f57ea10afc4a | execution=bac9a20b-56c6-452d-96f8-d3adba6a35af | worker=app-worker-1      
2026-08-23 22:42:22,289 INFO app.workers.worker JOB CLAIMED BY POLLER | worker=app-worker-1 | job=3520cd95-f37c-4ffe-be14-97b636c3a500    
2026-08-23 22:42:22,289 INFO app.workers.worker EXECUTE START | worker=app-worker-1 | job=3520cd95-f37c-4ffe-be14-97b636c3a500
2026-08-23 22:42:22,461 INFO app.workers.worker TASK START | job=5be58300-5029-4361-9928-f57ea10afc4a | type=echo
2026-08-23 22:42:22,461 INFO app.workers.worker TASK SUCCESS | job=5be58300-5029-4361-9928-f57ea10afc4a
2026-08-23 22:42:24,915 INFO app.services.jobs EXECUTION STARTED | job=3520cd95-f37c-4ffe-be14-97b636c3a500 | execution=972082ad-d1d4-4bce-921a-6447c18464eb | worker=app-worker-1      
2026-08-23 22:42:25,295 INFO app.workers.worker TASK START | job=3520cd95-f37c-4ffe-be14-97b636c3a500 | type=echo
2026-08-23 22:42:25,295 INFO app.workers.worker TASK SUCCESS | job=3520cd95-f37c-4ffe-be14-97b636c3a500
2026-08-23 22:42:26,798 INFO app.services.jobs JOB COMPLETED | job=5be58300-5029-4361-9928-f57ea10afc4a | execution=bac9a20b-56c6-452d-96f8-d3adba6a35af | duration=5168ms
2026-08-23 22:42:27,968 INFO app.workers.worker EXECUTE COMPLETE | job=5be58300-5029-4361-9928-f57ea10afc4a | worker=app-worker-1







     
[1/8] Authenticating test user...
      user=ab@gmail.com id=3afd3ab8-d047-4267-8520-47f575df8e2b
[2/8] Creating organization...
      organization=b0da3f73-36b2-408b-b693-e6e0dc409bdc
[3/8] Creating 3 projects...
      projects=3
[4/8] Creating queues with different priority/concurrency/retry policies...
      queues=6
[5/8] Creating immediate jobs with same and different priorities...
[6/8] Creating delayed/scheduled/cron jobs...
[7/8] Creating concurrency, retry, DLQ, flaky, batch, cancel and idempotency tests...       
[8/8] Writing manifest...

========== TEST DATA CREATED ==========       
Base URL          : http://localhost:8000     
Test user         : ab@gmail.com
Password          : 654321
Organization      : b0da3f73-36b2-408b-b693-e6e0dc409bdc
Projects          : 3
Queues            : 6
Job records       : 51
Batch parent      : cedade29-50ec-4be6-b96c-a6250eb953ba
Cancelled job     : 9cf20d14-763b-4a83-87a6-973ef74482d8
Idempotency IDs   : ['1d604a5b-310e-47c0-ae94-58d4148fda37', '1d604a5b-310e-47c0-ae94-58d4148fda37']
Priority rule     : POSITIVE ONLY; LOWER NUMBER = HIGHER PRIORITY
Highest priority  : 1

Job categories:
  batch_parent_cancelled             1        
  cancelled                          1        
  cron_template                      2        
  data_processing                    3        
  dead_letter                        1        
  delayed                            5        
  email_simulation                   2        
  idempotency_first                  1        
  idempotency_second_same_job        1        
  immediate_mixed_priority          12        
  immediate_same_priority            8        
  queue_concurrency_sleep            8        
  retry_then_success                 1        
  scheduled                          5        

========== EXECUTION TEST SUMMARY ==========  
Immediate         : same-priority + mixed-priority
Delayed           : 10/15/20/25/30 second delays
Scheduled         : 15/20/30/40/50 second schedules
CRON              : 2 recurring templates     
Concurrency       : 8 jobs on a queue limited to 1
Retry             : flaky job (fail once, then succeed)
DLQ               : permanent failure until retry exhaustion
Idempotency       : same key submitted twice  
Batch             : parent + child jobs       
Cancellation      : future delayed job cancelled immediately
Task handlers     : echo + sleep + data_processing + email_simulation

Manifest          : D:\Development\distributed-job-scheduler\backend\scripts\test_run_20260823_171200.json
=========================================