import logging

import azure.functions as func
import json

from ..shared.vott_parser import create_starting_vott_json
from ..shared.db_provider import get_postgres_provider
from ..shared.db_access import ImageTagDataAccess

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    image_count = int(req.params.get('imageCount'))
    user_id = int(req.params.get('userId'))

    # setup response object
    headers = {
        "content-type": "application/json"
    }
    if not user_id:
        return func.HttpResponse(
            status_code=401,
            headers=headers,
            body=json.dumps({"error": "invalid userId given or omitted"})
        )
    elif not image_count:
        return func.HttpResponse(
            status_code=400,
            headers=headers,
            body=json.dumps({"error": "image count not specified"})
        )
    else:
        # DB configuration
        data_access = ImageTagDataAccess(get_postgres_provider())

        image_urls = list(data_access.get_new_images(image_count, user_id))

        # TODO: change parser to accept dict, or maybe object with tagging data later...
        # TODO: Build vott starting json
        # TODO: Populate starting json with tags, if any exist... (precomputed or retagging?)
        vott_json = create_starting_vott_json(image_urls)

        return_body_json = {"imageUrls": image_urls, "vottJson": vott_json}

        content = json.dumps(return_body_json)
        return func.HttpResponse(
            status_code=200, 
            headers=headers, 
            body=content
        )
