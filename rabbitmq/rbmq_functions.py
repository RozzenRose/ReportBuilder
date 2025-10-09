import aio_pika, json
from logic.report_builder import get_report
from .to_aggregator import send_message


async def handle_message(message: aio_pika.IncomingMessage, channel: aio_pika.Channel):
    async with message.process():
        body = message.body
        correlation_id = message.correlation_id
        reply_to = message.reply_to

        if not reply_to or not correlation_id:
            print("Пропущено сообщение без reply_to/correlation_id")
            return

        data = json.loads(body.decode())
        result = await get_report(data)
        await send_message(channel=channel, data=result, queue=reply_to,
                           reply_queue=None, correlation_id=correlation_id)

        print(f"Ответ отправлен в {reply_to} с correlation_id {correlation_id}")


async def consume_queue(queue_name: str, channel: aio_pika.Channel):
    queue = await channel.declare_queue(queue_name, durable=True)
    async with queue.iterator() as queue_iter:
        async for message in queue_iter:
            await handle_message(message, channel)
