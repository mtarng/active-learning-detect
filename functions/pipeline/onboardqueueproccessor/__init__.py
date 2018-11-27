import os
import logging

import azure.functions as func

def main(msg: func.QueueMessage) -> None:
    logging.info('Python queue trigger function processed a queue item: %s',
                 msg.get_body().decode('utf-8'))

    # messageText = open(os.environ["inputMessage"]).read()
    # logging.info("queue message text: " + messageText)
