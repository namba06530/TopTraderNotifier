import uuid
from data.bybit_api import *

# Create Order
endpoint = "/spot/v3/private/order"
method = "POST"
orderLinkId = uuid.uuid4().hex
params = '{"symbol":"BTCUSDT","orderType":"Market","side":"Buy","orderLinkId":"' + orderLinkId + '","orderQty":"1","orderPrice":"25000","timeInForce":"GTC"}';
HTTP_Request(endpoint, method, params, "Create")

# Get Order List
endpoint = "/spot/v3/private/order"
method = "GET"
params = 'orderLinkId=' + orderLinkId
HTTP_Request(endpoint, method, params, "List")

# Cancel Order
endpoint = "/spot/v3/private/cancel-order"
method = "POST"
params = '{"orderLinkId":"' + orderLinkId + '"}'
HTTP_Request(endpoint, method, params, "Cancel")
