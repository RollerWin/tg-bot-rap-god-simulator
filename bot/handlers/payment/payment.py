import os
from dotenv import load_dotenv
from yoomoney import Authorize

load_dotenv()

Authorize(
      client_id= os.getenv("YOOMONEY_CLIENT_ID"),
      redirect_uri="https://t.me/ytvideotestbot",
      scope=["account-info",
             "operation-history",
             "operation-details",
             "incoming-transfers",
             "payment-p2p",
             "payment-shop",
             ]
      )
