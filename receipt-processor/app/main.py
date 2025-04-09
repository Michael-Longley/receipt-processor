from fastapi import FastAPI, Request, Response, status
from app.ReceiptProcessor import ReceiptProcessor
from app.ReceiptDB import ReceiptDB
import logging

app = FastAPI()
receiptDB = ReceiptDB()
receiptProcessor = ReceiptProcessor(receiptDB)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.get("/")
def read_me():
    return {"coding_challenge_name": "receipt-processor", "link": "https://github.com/fetch-rewards/receipt-processor-challenge"}

@app.post("/receipts/process")
async def process_data(request: Request, response: Response):
    data = await request.json()
    receipt_id = receiptProcessor.process_receipts(data)
    if receipt_id == None:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"ERROR": "Invalid data shape"}
    return {"id": receipt_id}

@app.get("/receipts/{request_id}/points")
def get_receipt_points(request_id: str, response: Response):
    try:
        points = receiptProcessor.get_receipt_points(request_id)
        return {"points": points}
    except:
        logger.error(f'Invalid Key: %s', request_id)
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"ERROR": "Invalid Key"}

