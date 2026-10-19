"""Part 10: consume one unacknowledged message at a time."""

import os
import time
import pika
from callback import callback
from database import connect_database


def consume(host):
    mode = os.getenv("ROUTER_MODE", "ssh")
    if mode not in {"demo", "ssh"}:
        raise ValueError("ROUTER_MODE must be demo or ssh")
    client, db = connect_database()
    try:
        while True:
            connection = None
            try:
                connection = pika.BlockingConnection(
                    pika.ConnectionParameters(
                        host=host,
                        credentials=pika.PlainCredentials(
                            os.environ["RABBITMQ_USERNAME"],
                            os.environ["RABBITMQ_PASSWORD"],
                        ),
                        heartbeat=120,
                        blocked_connection_timeout=60,
                    )
                )
                channel = connection.channel()
                channel.exchange_declare(exchange="jobs", exchange_type="direct")
                channel.queue_declare(queue="router_jobs")
                channel.queue_bind(
                    queue="router_jobs", exchange="jobs", routing_key="check_interfaces"
                )
                channel.basic_qos(prefetch_count=1)
                channel.basic_consume(
                    queue="router_jobs",
                    auto_ack=False,
                    on_message_callback=lambda ch, m, p, b: callback(ch, m, p, b, db),
                )
                print(f"Worker ready; mode={mode}; waiting for router_jobs", flush=True)
                if mode == "demo":
                    print("DEMO: simulated router CLI; no SSH connection", flush=True)
                channel.start_consuming()
            except KeyboardInterrupt:
                break
            except pika.exceptions.AMQPError as error:
                print(f"RabbitMQ: {type(error).__name__}; retry in 5s", flush=True)
                time.sleep(5)
            finally:
                if connection is not None and connection.is_open:
                    connection.close()
    finally:
        client.close()
