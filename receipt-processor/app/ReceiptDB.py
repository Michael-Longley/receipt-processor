import logging
"""
This is a placeholder receipt database which was added to esily be replaced with a persistent database.
"""

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ReceiptDB:
    receipt_db = {}
    def insert_receipt_data(self, uuid, points):
        self.receipt_db[str(uuid)] = points
        logger.info(f'UUID Added: %s', str(uuid))
    
    def get_points(self, uuid):
        logger.info(f'Getting UUID: %s', str(uuid))
        return self.receipt_db[uuid]