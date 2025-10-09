import asyncio
from rabbitmq.to_aggregator import RabbitMQConnectionManager
from rabbitmq.rbmq_functions import consume_queue


async def main():
    channel = await RabbitMQConnectionManager.get_channel()

    # Список очередей, на которые подписываемся
    queues = ["report_queue"]

    # Запускаем слушателей параллельно
    await asyncio.gather(*(consume_queue(q, channel) for q in queues))


if __name__ == "__main__":
    asyncio.run(main())
