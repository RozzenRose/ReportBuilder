import asyncio
import aio_pika, json
from aio_pika import Message
from report_builder import get_report
from rabbitmq import RabbitMQConnectionManager


async def main():
    # Подключаемся к RabbitMQ
    channel = await RabbitMQConnectionManager.get_channel()

    # Подписываемся на очередь запросов
    queue = await channel.declare_queue("report_queue", durable=True)

    async with queue.iterator() as queue_iter:
        async for message in queue_iter:
            async with message.process():
                # Берём тело и метаданные
                body = message.body
                correlation_id = message.correlation_id
                reply_to = message.reply_to
                data = json.loads(body.decode())

                if not reply_to or not correlation_id:
                    print("Пропущено сообщение без reply_to/correlation_id")
                    continue
                #print(data)
                # Обрабатываем сообщение
                result = await get_report(data)

                # Отправляем результат в очередь reply_to
                await channel.default_exchange.publish(
                    Message(
                        body=result,
                        correlation_id=correlation_id
                    ),
                    routing_key=reply_to
                )

                print(f"Ответ отправлен в {reply_to} с correlation_id {correlation_id}")


if __name__ == "__main__":
    asyncio.run(main())
