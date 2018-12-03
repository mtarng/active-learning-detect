import logging
import json
import azure.functions as func

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
        raw_url_list = req_body["imageUrls"]
    except ValueError:
        return func.HttpResponse("ERROR: Unable to decode POST body", status_code=400)

    if not raw_url_list:
        return func.HttpResponse("ERROR: URL list empty.", status_code=401)

    try:
        img_url_list = set(raw_url_list)  # Check to ensure image URLs sent by client are all unique.
        # TODO: Handle subsets of queue writes that fail
        queue_image_urls_to_onboard(img_url_list, user_name)

        return func.HttpResponse(
            status_code=200,
            headers=DEFAULT_RETURN_HEADER,
            body=json.dumps(img_url_list)
        )
    except Exception as e:
        logging.error("ERROR: Could not add image urls to onboarding queue. Exception: " + str(e))
        return func.HttpResponse("ERROR: Could not add image urls in url list={0} to onboarding queue. "
                                 "Exception={1}".format(raw_url_list, e), status_code=500)