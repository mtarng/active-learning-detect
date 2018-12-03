import os
import logging
import json
import azure.functions as func

from azure.storage.blob import BlockBlobService
from ..shared.onboarding import queue_image_urls_to_onboard

DEFAULT_RETURN_HEADER = {"content-type": "application/json"}


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
        storage_account = req_body["storageAccount"]
        storage_account_key = req_body["storageAccountKey"]
        storage_container = req_body["storageContainer"]
    except ValueError:
        return func.HttpResponse("ERROR: Unable to decode POST body", status_code=400)

    if not storage_container or not storage_account or not storage_account_key:
        return func.HttpResponse("ERROR: storage container/account/key/queue not specified.", status_code=401)

    # Create blob service for storage account (retrieval source)
    blob_service = BlockBlobService(account_name=storage_account,
                                    account_key=storage_account_key)

    try:
        img_url_list = []
        for blob_object in blob_service.list_blobs(storage_container):
            # TODO: create signed urls
            img_url_list.append(blob_service.make_blob_url(storage_container, blob_object.name))

            queue_image_urls_to_onboard(img_url_list, user_name)

        return func.HttpResponse(
            status_code=200,
            headers=DEFAULT_RETURN_HEADER,
            body=json.dumps(img_url_list)
        )
    except Exception as e:
        logging.error("ERROR: Could not add image urls to onboarding queue. Exception: " + str(e))
        return func.HttpResponse("ERROR: Could not add image url in storage_container={0} to onboarding queue. "
                                 "Exception={1}".format(storage_container, e), status_code=500)
