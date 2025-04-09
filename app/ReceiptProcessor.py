import math
import uuid
import logging
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ReceiptProcessor:
    db = None

    def __init__(self, mainDB):
        self.db = mainDB

    def generate_uuid(self):
        """
        By abstracting this, it will be easier to replace with logic around tying to a custoemr in the future.
        """
        return uuid.uuid4()

    def calculate_points(self, retailer, date, time, items, total):
        """
        Calculate the total number of points for a given set of data from a receipt.

        Parameters:
        retailer : The name of the retailer
        date : The date of the transaction
        time : The time of checkout
        items [JSON]: Purchase information
        total : Total value of receipt

        Returns:
        int : Total points earned from a receipt
        """
        totalPoints = 0
        # One point for every alphanumeric character in the retailer name.
        cleanedRetailer = re.sub(r'[^A-Za-z0-9]', '', retailer)
        retailer_points = len(cleanedRetailer)
        logger.info(f'Retailer Name Points: %s', str(retailer_points))
        totalPoints += retailer_points
        # 50 points if the total is a round dollar amount with no cents.
        dollarPoints = 0
        if int(total.split(".")[1]) == 0:
            dollarPoints = 50
        totalPoints += dollarPoints
        logger.info(f'Whole Dollar Points: %s', str(dollarPoints))
        # 25 points if the total is a multiple of 0.25
        quarterPoints = 0
        if int(total.split(".")[1]) % 25 == 0:
            quarterPoints = 25
        totalPoints += quarterPoints
        logger.info(f'.25 Mutliplier: %s', str(quarterPoints))
        # 5 points for every two items on the receipt
        itemCountPoints = (len(items) // 2) * 5
        totalPoints += itemCountPoints
        logger.info(f'Item Count Points: %s', str(itemCountPoints))
        # If the trimmed length of the item description is a multiple of 3, multiply the price by 0.2 and round up to the nearest integer. The result is the number of points earned
        itemPoints = 0
        for item in items:
            if len((item["shortDescription"]).strip()) % 3 == 0:
                itemPoints += math.ceil(float(item["price"]) * 0.2)
        totalPoints += itemPoints
        logger.info(f'Total Item Points: %s', str(itemPoints))
        # 6 points if the day in the purchase date is odd
        oddDayPoints = 0
        if int(date.split("-")[2]) % 2 != 0: # Middle element of date is not even
            oddDayPoints = 6
        totalPoints += oddDayPoints
        logger.info(f'Purchase Date is odd: %s', str(oddDayPoints))
        # 10 points if the time of purchase is after 2:00pm and before 4:00pm
        eveningPoints = 0
        if int(time.split(":")[0]) >= 14 and int(time.split(":")[0]) < 16:
            eveningPoints = 10
        totalPoints += eveningPoints
        logger.info(f'Purchase Time is btwn 2pm and 4pm: %s', str(eveningPoints))
        logger.info(f'Total Points: %s', str(totalPoints))
        return totalPoints

    def process_json(self, data):
        """
        JSON Processor to take the raw data and change to individual attributes
        
        Parameters:
        data (json): Raw JSON receipt data

        Returns:
        Tuple (retailer, date, time, list, double): Touple containing the important receipt information for point calculation.
        """
        return (data["retailer"], data["purchaseDate"], data["purchaseTime"], data["items"], data["total"])

    def process_receipts(self, data):
        """
        /receipts/process endpoint
        
        Parameters:
        data (json): The raw JSON data from the POST request

        Returns: 
        UUID: The UUID for the receipt for use in lookup later.
        """
        try:
            logger.info(f'Processing Receipt Data')
            (retailer, date, time, items, total) = self.process_json(data)
        except:
            logger.info(f'Failed to process receipt, invalid data format')
            return None
        logger.info(f'Calculating Receipt Points')
        points = self.calculate_points(retailer, date, time, items, total)
        id = self.generate_uuid()
        logger.info(f'Saving Receipt to DB')
        self.db.insert_receipt_data(id, points)
        return id
        
    def get_receipt_points(self, id):
        """
        /receipts/id/points endpoint

        Parameters:
        id: The id to read from the database

        Returns: 
        int: Points earned for the receipt.
        """
        return self.db.get_points(id)