import datetime
import logging

import azure.functions as func
from ..shared.db_provider import get_postgres_provider
from ..shared.db_access import ImageTagDataAccess, ImageInfo


def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()

    if mytimer.past_due:
        logging.info('The timer is past due!')

    data_access = ImageTagDataAccess(get_postgres_provider())
    # Get list of all images currently checked out, or last modified over n number of days/hours ago
    data_access.get_stale_images()  # TODO: Rename to something else if we don't need returns.
    # data_access.get_stale_checkedout_images() TODO:

    # Set those checked out to TAGGING_INCOMPLETE ???? TODO: Or do in db_access.
    # update_incomplete_images()

    logging.info('Python timer trigger function ran at %s', utc_timestamp)
