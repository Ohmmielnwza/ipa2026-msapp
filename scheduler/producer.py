"""Part 7: publish a router IP to the RabbitMQ jobs exchange."""

import argparse
import os

import pika


def produce(host="localhost", body="192.168.1.44"):
    credentials = pika.PlainCredentials(
        os.getenv("RABBITMQ_USERNAME", "guest"),
        os.getenv("RABBITMQ_PASSWORD", "guest"),
    )
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=host,
            port=int(os.getenv("RABBITMQ_PORT", "5672")),
            credentials=credentials,
        )
    )
    try:
        channel = connection.channel()
        channel.exchange_declare(exchange="jobs", exchange_type="direct")
        channel.queue_declare(queue="router_jobs")
        channel.queue_bind(
            queue="router_jobs",
            exchange="jobs",
            routing_key="check_interfaces",
        )
        channel.confirm_delivery()
        channel.basic_publish(
            exchange="jobs",
            routing_key="check_interfaces",
            body=body,
            mandatory=True,
        )
        print("Published job -> jobs -> router_jobs (check_interfaces)", flush=True)
    finally:
        connection.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("body", nargs="?", default="192.168.1.44")
    parser.add_argument("--host", default=os.getenv("RABBITMQ_HOST", "localhost"))
    args = parser.parse_args()
    produce(args.host, args.body)
