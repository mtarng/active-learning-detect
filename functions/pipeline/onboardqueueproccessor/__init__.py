import os
import json
import logging
import azure.functions as func
import urllib.parse

from urllib.request import urlopen

from PIL import Image
from ..shared.db_provider import get_postgres_provider
from ..shared.db_access import ImageTagDataAccess, ImageInfo
from ..shared.onboarding import copy_images_to_permanent_storage
from azure.storage.blob import BlockBlobService


def main(msg: func.QueueMessage) -> None:
    logging.info('Python queue trigger function processed a queue item: %s',
                 msg.get_body().decode('utf-8'))

    result = json.dumps({
        'id': msg.id,
        'body': msg.get_body().decode('utf-8'),
        'expiration_time': (msg.expiration_time.isoformat()
                            if msg.expiration_time else None),
        'insertion_time': (msg.insertion_time.isoformat()
                           if msg.insertion_time else None),
        'time_next_visible': (msg.time_next_visible.isoformat()
                              if msg.time_next_visible else None),
        'pop_receipt': msg.pop_receipt,
        'dequeue_count': msg.dequeue_count
    })

    logging.info(result)

    try:
        msg_json = json.loads(msg.get_body().decode('utf-8'))
        img_url = urllib.parse.quote(msg_json["imageUrl"], safe=':/')
        user_name = msg_json["userName"]

        image_object_list = []
        # Split original image name from URL
        original_filename = img_url.split("/")[-1]
        # Create ImageInfo object (def in db_access.py)

        with Image.open(urlopen(img_url)) as img:
            width, height = img.size

        image = ImageInfo(original_filename, img_url, height, width)
        # Append image object to the list
        image_object_list.append(image)

        data_access = ImageTagDataAccess(get_postgres_provider())
        user_id = data_access.create_user(user_name)

        logging.debug("Add new images to the database, and retrieve a dictionary ImageId's mapped to ImageUrl's")
        image_id_url_map = data_access.add_new_images(image_object_list, user_id)

        copy_destination = os.getenv('DESTINATION_CONTAINER_NAME')

        # Create blob service for storage account
        blob_service = BlockBlobService(account_name=os.getenv('STORAGE_ACCOUNT_NAME'),
                                        account_key=os.getenv('STORAGE_ACCOUNT_KEY'))

        # Copy images to permanent storage and get a dictionary of images for which to update URLs in DB.
        # and a list of failures.  If the list of failures contains any items, return a status code other than 200.
        # TODO: image-id and image size here.

        image_id = list(image_id_url_map.values())[0] # TODO: This is hacky as hell.
        new_blob_name = str(image_id) + ".png" # TODO: this is also hacky and needs to be corrected

        response = urlopen(img_url)

        # response.status == 200
        imagebytes = response.read()

        blob_create_response = blob_service.create_blob_from_bytes(copy_destination, new_blob_name, imagebytes)
        update_urls_dictionary = {}
        update_urls_dictionary[image_id] = blob_service.make_blob_url(copy_destination, new_blob_name)


        # Otherwise, dictionary contains permanent image URLs for each image ID that was successfully copied.
        if not blob_create_response:
            logging.error("ERROR: Image copy/delete operation failed. Check state of images in storage.")
        else:
            logging.debug("Now updating permanent URLs in the DB...")
            data_access.update_image_urls(update_urls_dictionary, user_id)

            # content = json.dumps({"imageUrls": list(update_urls_dictionary.values())})
            logging.debug("success onboarding.")
    except Exception as e:
        logging.error("Exception: " + str(e))
