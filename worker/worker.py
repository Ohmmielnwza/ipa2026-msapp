"""Part 13: start a worker using the Compose service hostname."""

import os
from consumer import consume

if __name__ == "__main__":
    consume(os.getenv("RABBITMQ_HOST", "rabbitmq"))
