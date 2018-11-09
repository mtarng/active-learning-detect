import logging

import azure.functions as func
import json

from ..shared import db_access_v1 as DB_Access  # To be deprecated for v2
from ..shared.vott_parser import create_starting_vott_json

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    imageCount = req.params.get('imageCount')
    # user_id = int(req.params.get('userId')) To be used for db_access_v2
    # setup response object
    headers = {
        "content-type": "application/json"
    }
    if not imageCount:
        return func.HttpResponse(
            status_code=400,
            headers=headers,
            body=json.dumps({"error": "image count not specified"})
        )
    else:
        # setup response object
        connection = DB_Access.get_connection()
        # TODO: images need more meaningful data than just download urls
        image_urls = DB_Access.get_images_for_tagging(connection, imageCount)

        # TODO: Build vott_parser json
        vott_json = create_starting_vott_json(image_urls)

        return_body_json = {"imageUrls": image_urls, "vottJson": vott_json}

        content = json.dumps(return_body_json)
        return func.HttpResponse(
            status_code=200, 
            headers=headers, 
            body=content
        )