import json

from ..shared.db_provider import DatabaseInfo, PostGresProvider
from ..shared.db_access_v2 import ImageTag, ImageTagDataAccess
from ..shared import vott_json_parser as Vott_json_parser

import azure.functions as func

# Create list of ImageTag objects to write to db for given image_id
def __create_ImageTag_list(image_id, tags_list):
    image_tags = []
    for tag in tags_list:
        image_tags.append(ImageTag(image_id, tag['x1'], tag['x2'], tag['y1'], tag['y2'], tag['classes']))
    return image_tags

def main(req: func.HttpRequest) -> func.HttpResponse:
    try:

        vott_json = req.get_json()
        upload_data = Vott_json_parser.process_vott_json(vott_json)
        user_id = int(req.params.get('userId'))
        upload_data['userId'] = user_id

        # TODO: Configure via env configs/util?
        # DB configuration
        db_config = DatabaseInfo("", "", "", "")
        data_access = ImageTagDataAccess(PostGresProvider(db_config))

        # Update tagged images
        ids_to_tags = upload_data["imageIdToTags"]

        all_imagetags = []
        for image_id in ids_to_tags.keys():
            if ids_to_tags[image_id]:
                all_imagetags.extend(__create_ImageTag_list(image_id, ids_to_tags[image_id]))

        # Update all visited images with tags and set state to completed
        data_access.update_tagged_images(all_imagetags, user_id)

        # Update visited but no tags identified images
        data_access.update_completed_untagged_images(upload_data["imagesVisitedNoTag"], user_id)

        # Update unvisited/incomplete images
        data_access.update_incomplete_images(upload_data["imagesNotVisited"], user_id)

        return func.HttpResponse(
            body=json.dumps(upload_data),
            status_code=200,
            headers={
                "content-type": "application/json"
            }
        )
    except Exception as e:
        return func.HttpResponse(
            "exception:" + str(e),
            status_code=500
        )