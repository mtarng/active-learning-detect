import logging

import azure.functions as func
import json

from ..shared import db_access_v1 as DB_Access  # To be deprecated for v2
from ..shared.vott_parser import create_starting_vott_json
from ..shared.db_provider import DatabaseInfo, PostGresProvider
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
        # TODO: Configure via env configs/util for upload/download/onboard
        # DB configuration
        db_config = DatabaseInfo("", "", "", "")
        data_access = ImageTagDataAccess(PostGresProvider(db_config))

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
