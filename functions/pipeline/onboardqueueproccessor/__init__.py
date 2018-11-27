import os
import json
import logging
import azure.functions as func

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
        # TODO: Change message to json with img-url and userName.
        img_url = msg.get_body().decode('utf-8')
        image_object_list = build_objects_from_url(img_url)
    except Exception as e:
        logging.error("ERROR: Could not build image object list. Exception: " + str(e))

    try:
        data_access = ImageTagDataAccess(get_postgres_provider())
        # TODO: Add username to queue message and consume
        user_id = data_access.create_user("queueuser")

        logging.debug("Add new images to the database, and retrieve a dictionary ImageId's mapped to ImageUrl's")
        image_id_url_map = data_access.add_new_images(image_object_list, user_id)

        copy_source = os.getenv('SOURCE_CONTAINER_NAME')
        copy_destination = os.getenv('DESTINATION_CONTAINER_NAME')

        # Create blob service for storage account
        blob_service = BlockBlobService(account_name=os.getenv('STORAGE_ACCOUNT_NAME'),
                                        account_key=os.getenv('STORAGE_ACCOUNT_KEY'))

        # Copy images to permanent storage and get a dictionary of images for which to update URLs in DB.
        # TODO: Prefer to have this function return a JSON blob as a string containing a list of successes
        # and a list of failures.  If the list of failures contains any items, return a status code other than 200.
        update_urls_dictionary = copy_images_to_permanent_storage(image_id_url_map, copy_source, copy_destination,
                                                                  blob_service)

        # If the dictionary of images is empty, this means a faiure occurred in a copy/delete operation.
        # Otherwise, dictionary contains permanent image URLs for each image ID that was successfully copied.
        if not update_urls_dictionary:
            logging.error("ERROR: Image copy/delete operation failed. Check state of images in storage.")
        else:
            logging.debug("Now updating permanent URLs in the DB...")
            data_access.update_image_urls(update_urls_dictionary, user_id)

            # content = json.dumps({"imageUrls": list(update_urls_dictionary.values())})
            logging.debug("success onboarding.")
    except Exception as e:
        logging.error("Exception: " + str(e))


# Given a list of image URL's, build an ImageInfo object for each, and return a list of these image objects.
def build_objects_from_url(image_url):
    image_object_list = []
    # Split original image name from URL
    original_filename = image_url.split("/")[-1]
    # Create ImageInfo object (def in db_access.py)

    with Image.open(urlopen(image_url)) as img:
        width, height = img.size
    image = ImageInfo(original_filename, image_url, height, width)
    # Append image object to the list
    image_object_list.append(image)
    return image_object_list
