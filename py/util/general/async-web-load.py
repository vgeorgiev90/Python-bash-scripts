#!/usr/bin/python3.7

import click
import asyncio
import time
import requests

@click.command()
@click.option("--concurent", "-c", default=10, help="Concurent connections")
@click.option("--requests", "-r", default=50, help="Number of requests")
@click.argument("url")
def cli(url, requests, concurent):
    main(url, requests, concurent)


def fetch(url):
    started_at = time.monotonic()
    response = requests.get(url)
    request_time = time.monotonic() - started_at
    return {"status_code": response.status_code, "request_time": request_time}

async def worker(name, queue, results):
    loop = asyncio.get_event_loop()
    while True:
        url = await queue.get()
        #print(f"{name} - Fetching {url}")
        future_result = loop.run_in_executor(None, fetch, url)
        result = await future_result
        results.append(result)
        queue.task_done()


async def distribute_work(url, requests, concurent, results):
    queue = asyncio.Queue()

    for _ in range(requests):
        queue.put_nowait(url)

    tasks = []
    for i in range(concurent):
        task = asyncio.create_task(worker(f"worker-{i+1}", queue, results))
        tasks.append(task)

    started_at = time.monotonic()
    await queue.join()

    total_time = time.monotonic() - started_at
    for task in tasks:
        task.cancel()

    print(f"{concurent} workers took {total_time:.2f} seconds to complete {len(results)} requests")



def main(url, requests, concurent):
    results = []
    asyncio.run(distribute_work(url, requests, concurent, results))
    for result in results:
        if result['status_code'] != 200:
            print(result)

cli()
