import pika

queue_dedicated_received_messages = 'ded_rx_msg'
queue_dedicated_state_changes = 'ded_st_chg'
mq_connection = None
mq_channel = None


def _get_channel():
    global mq_connection
    global mq_channel
    if mq_connection is None:
        mq_connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost', port='5672'))
    if mq_channel is None:
        mq_channel = mq_connection.channel()
        mq_channel.queue_declare(queue=queue_dedicated_received_messages)
        mq_channel.queue_declare(queue=queue_dedicated_state_changes)
    return mq_channel


def consume_dedicated_received_messages(callback_func):
    """
    callback_func needs to take func, params, ch and delivery_tag as arguments
    """
    def _callback_func(ch, method, properties, body):
        func, params = body.decode()
        callback_func(func=func, params=params, ch=ch, delivery_tag=method.delivery_tag)
    channel = _get_channel()
    channel.basic_consume(queue=queue_dedicated_received_messages, on_message_callback=_callback_func, auto_ack=False, exclusive=True)
    channel.basic_qos(prefetch_count=1)
    channel.start_consuming()


def send_dedicated_received_message(func, params=None):
    channel = _get_channel()
    channel.basic_publish(exchange='', routing_key=queue_dedicated_received_messages, body=(func, params))


def consume_dedicated_state_changes(callback_func, timeout=1):
    """
    callback_func needs to take timeout, new_state, ch and delivery_tag as arguments
    """
    channel = _get_channel()
    try:
        for method, properties, body in channel.consume(
                queue=queue_dedicated_state_changes, auto_ack=False, exclusive=True, inactivity_timeout=timeout):
            if method is None and properties is None and body is None:
                callback_func(timeout=True, new_state=None, ch=channel, delivery_tag=None)
            else:
                callback_func(timeout=False, new_state=body.decode(), ch=channel, delivery_tag=method.delivery_tag)
    except Exception:
        channel.cancel()


def send_dedicated_state_changes(new_state):
    channel = _get_channel()
    channel.basic_publish(exchange='', routing_key=queue_dedicated_state_changes, body=new_state)
