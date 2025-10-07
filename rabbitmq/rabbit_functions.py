import aio_pika, asyncio, uuid, json
from rabbitmq import RabbitMQConnectionManager

async def consume_response(reply_queue, correlation_id: str, future: asyncio.Future):
    async def on_message(message: aio_pika.IncomingMessage) -> None:
        async with message.process():
            if message.correlation_id == correlation_id and not future.done():
                future.set_result(message.body)

    consumer_tag = await reply_queue.consume(on_message)
    return consumer_tag


async def send_message(channel, data, queue, reply_queue, correlation_id):
    await channel.default_exchange.publish(
        aio_pika.Message(body=data, reply_to=reply_queue.name,
                         correlation_id=correlation_id),
        routing_key=queue.name)


async def send_to_aggregator(data):
    loop = asyncio.get_running_loop()
    future = loop.create_future()
    correlation_id = str(uuid.uuid4())
    channel = await RabbitMQConnectionManager.get_channel()
    queue = await channel.declare_queue('report_aggregation_queue', durable=True)
    reply_queue = await channel.declare_queue('reply_report_aggregation_queue', durable=True)
    consumer_tag = await consume_response(reply_queue, correlation_id, future)
    new_data = {'data': data, 'content': 'Report'}
    await send_message(channel, json.dumps(new_data).encode(), queue, reply_queue, correlation_id)

    try:
        response = json.loads(await asyncio.wait_for(future, timeout=10))
        return response
    except asyncio.TimeoutError:
        print('Timeout error')
    finally:
        await reply_queue.cancel(consumer_tag)
