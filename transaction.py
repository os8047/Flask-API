import os
from pypaystack.transactions import Transaction

PAYSTACK_AUTHORIZATION_KEY = os.environ.get("PAYSTACK_AUTHORIZATION_KEY")
transaction = Transaction(authorization_key=PAYSTACK_AUTHORIZATION_KEY)
