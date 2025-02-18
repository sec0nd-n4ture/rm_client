from db_client.db_client import DBClient, UPDATE_CHECK_DELAY
from win_precise_time import sleep, time
from threading import Thread, Lock
from info_provider.job import Job


class InfoProvider(Thread):
    def __init__(self, db_client: DBClient) -> None:
        super().__init__(daemon=True)
        self.jobs: list[Job] = []
        self.db_client = db_client
        self.joblist_lock = Lock()

    def run(self) -> None:
        self.__execute_jobs()

    def __execute_jobs(self):
        t1 = time()
        while True:
            t2 = time()
            if (t2 - t1) >= UPDATE_CHECK_DELAY:
                self.db_client.update_check()
                t1 = t2
            with self.joblist_lock:
                job_count = len(self.jobs)
                for _ in range(job_count):
                    self.jobs.pop(0).execute()
            sleep(0.1)

    def submit_job(self, job: Job):
        with self.joblist_lock:
            self.jobs.append(job)
