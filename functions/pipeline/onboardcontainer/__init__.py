import os
import logging
import json
import azure.functions as func

from azure.storage.blob import BlockBlobService
from azure.storage.queue import QueueService
DEFAULT_RETURN_HEADER= { "content-type": "application/json"}


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    user_name = req.params.get('userName')

    if not user_name:
        return func.HttpResponse(
            status_code=401,
            headers=DEFAULT_RETURN_HEADER,
            body=json.dumps({"error": "invalid userName given or omitted"})
        )

    try:
        req_body = req.get_json()
        logging.debug(req.get_json())
        # Assuming within same storage account for now... TODO: Cross region/Subscriptions?
        # TODO: Directory support?
        storage_account = req_body["storageAccount"]
        storage_account_key = req_body["storageAccountKey"]
        storage_container = req_body["storageContainer"]
        onboard_queue = req_body["onboardQueue"]
    except ValueError:
        return func.HttpResponse("ERROR: Unable to decode POST body", status_code=400)

    if not storage_container or not storage_account or not storage_account_key or not onboard_queue:
        return func.HttpResponse("ERROR: storage container/account/key/queue not specified.", status_code=401)

    # TODO: Get list of all items inside storage_container
    # TODO: limit by file types/postfix?

    # Create blob service for storage account
    # blob_service = BlockBlobService(account_name=os.getenv('STORAGE_ACCOUNT_NAME'),
    #                                 account_key=os.getenv('STORAGE_ACCOUNT_KEY'))
    blob_service = BlockBlobService(account_name=storage_account,
                                    account_key=storage_account_key)

    queue_service = QueueService(account_name=storage_account, account_key=storage_account_key)

    try:
        blob_list = []
        for blob_object in blob_service.list_blobs(storage_container):
            blob_list.append(blob_service.make_blob_url(storage_container, blob_object.name))

        for image_url in blob_list:
            queue_service.put_message(onboard_queue, image_url)

        return func.HttpResponse(
            status_code=200,
            headers=DEFAULT_RETURN_HEADER,
            body=json.dumps(blob_list)
        )
    except Exception as e:
        logging.error("ERROR: Could not build blob object list. Exception: " + str(e))
        return func.HttpResponse("ERROR: Could not get list of blobs in storage_container={0}. Exception={1}".format(
            storage_container, e), status_code=500)