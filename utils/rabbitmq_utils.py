import json
import uuid

import pika


class RabbitMQ:
    def __init__(self, host='localhost', port=5672):
        self.host = host
        self.port = port
        self.connection = None
        self.channel = None

    def connect(self):
        try:
            self.connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=self.host, port=self.port)
            )
            self.channel = self.connection.channel()
            print("RabbitMQ connection established.")
        except Exception as e:
            raise Exception(f"Failed to connect to RabbitMQ: {str(e)}")

    def get_channel(self):
        """Return the RabbitMQ channel."""
        if not self.channel or self.channel.is_closed:
            self.connect()
        return self.channel

    def publish_message(self, queue_name, message):
        try:
            message = json.dumps(message)
            channel = self.get_channel()
            channel.queue_declare(queue=queue_name, durable=True)
            channel.basic_publish(exchange='', routing_key=queue_name, body=message)
        except Exception as e:
            raise Exception(f"Failed to publish message: {str(e)}")

    def close(self):
        if self.connection and self.connection.is_open:
            self.connection.close()
            print("RabbitMQ connection closed.")


def generate_message(user_id, start_minute, end_minute, video_url):
    return {
        "request_id": str(uuid.uuid4()),
        "user_id": user_id,
        "start_minute": start_minute,
        "end_minute": end_minute,
        "video_url": video_url
    }
