import os
import logging
import json

from azure.storage.queue import QueueService, QueueMessageFormat
from azure.storage.blob import BlockBlobService

# TODO: When Azure function configuration supports, move this into an app setting
# Double check that this matches "queueName" in onboardingqueueprocessor's function.json
ONBOARD_QUEUE = "onboardqueue"


def queue_image_urls_to_onboard(img_url_list, user_name):
    queue_service = __get_onboarding_queue_service()

    for image_url in img_url_list:
        msg_body = {
            "imageUrl": image_url,
            "userName": user_name
        }
        body_str = json.dumps(msg_body)

        queue_service.put_message(ONBOARD_QUEUE, body_str)


def __get_onboarding_queue_service():
    # Queue service for perm storage and queue
    queue_service = QueueService(account_name=os.getenv('STORAGE_ACCOUNT_NAME'),
                                 account_key=os.getenv('STORAGE_ACCOUNT_KEY'))
    queue_service.encode_function = QueueMessageFormat.text_base64encode
    return queue_service


def get_perm_storage_service():
    return BlockBlobService(account_name=os.getenv('STORAGE_ACCOUNT_NAME'),
                            account_key=os.getenv('STORAGE_ACCOUNT_KEY'))


# TODO: Modify this function to return a JSON string that contains a "succeeded" list and a "failed" list.
def copy_images_to_permanent_storage(image_id_url_map, copy_source, copy_destination, blob_service):
    # Create a dictionary to store map of new permanent image URLs to image ID's
    update_urls_dictionary = {}

    # Copy images from temporary to permanent storage and delete them.
    for key, value in image_id_url_map.items():
        original_image_url = key
        original_blob_name = original_image_url.split("/")[-1]
        file_extension = os.path.splitext(original_image_url)[1]
        image_id = value
        new_blob_name = (str(image_id) + file_extension)

        # Verbose logging for testing
        logging.debug("Original image name: " + original_blob_name)
        logging.debug("Image ID: " + str(image_id))
        logging.debug("New blob name: " + new_blob_name)

        # Create the blob URLs
        source_blob_path = blob_service.make_blob_url(copy_source, original_blob_name)
        destination_blob_path = blob_service.make_blob_url(copy_destination, new_blob_name)

        # Copy blob from temp storage to permanent storage
        try:
            logging.debug("Now copying file from temporary to permanent storage...")
            logging.debug("Source path: " + source_blob_path)
            logging.debug("Destination path: " + destination_blob_path)
            blob_service.copy_blob(copy_destination, new_blob_name, source_blob_path)
            logging.debug("Done.")

            # Add ImageId and permanent storage url to new dictionary to be sent to update function
            update_urls_dictionary[image_id] = destination_blob_path

            # Delete the file from temp storage once it's been copied
            logging.debug("Now deleting image " + original_blob_name + " from temp storage container.")
            try:
                blob_service.delete_blob(copy_source, original_blob_name)
                logging.debug("Blob " + original_blob_name + " has been deleted successfully")
            except Exception as e:
                logging.error("ERROR: Deletion of blob " + original_blob_name + " failed. Exception: " + str(e))
                update_urls_dictionary.clear()
                return update_urls_dictionary

        except Exception as e:
            logging.error("ERROR: Copy of blob " + original_blob_name + " failed.  Exception: " + str(e))
            update_urls_dictionary.clear()
            return update_urls_dictionary

    return update_urls_dictionary
