
import asyncio
import logging
import websockets
from datetime import datetime
import os

from ocpp.routing import on
from ocpp.v201 import ChargePoint as cp
from ocpp.v201 import call_result
from ocpp.v201.enums import RegistrationStatusType

logging.basicConfig(level=logging.INFO)


class ChargePoint(cp):
    def __init__(self, charge_point_id, websocket, msg_file):
        super().__init__(charge_point_id, websocket)
        self.msg_file = msg_file

    async def write_to_file(self, message):
        try:
            file_exists = os.path.exists(self.msg_file)

            # Open the file in append mode (create if not exists)
            with open(self.msg_file, 'a') as file:
                # If the file is newly created, add a header
                if not file_exists:
                    file.write("Timestamp - Message\n")

                file.write(f"{datetime.utcnow().isoformat()} - {message}\n")
                file.close()
        except Exception as e:
            logging.error(f"Error writing to file: {e}")

    async def on_disconnect(self, *args, **kwargs):
        
        # Close the file when the connection is lost
        pass  # You can add any additional cleanup logic here

    @on('BootNotification')
    async def on_boot_notification(self, charging_station, reason, **kwargs):
       
        
        self.charging_station= charging_station
        # custom_data = charging_station.get('chargingStation', {}).get('customData', {})
        # vendor_id = custom_data.get('vendorId', None)
       
        # print(f"Vendor ID: {vendor_id}")
        
        await self.write_to_file(charging_station)

        return call_result.BootNotificationPayload(
            current_time=datetime.utcnow().isoformat(),
            interval=20,
            status=RegistrationStatusType.accepted,
            #customData= charging_station["customData"]
        )


async def on_connect(websocket, path):
    """ For every new charge point that connects, create a ChargePoint
    instance and start listening for messages.
    """
    try:
        requested_protocols = websocket.request_headers[
            'Sec-WebSocket-Protocol']
    except KeyError:
        logging.info("Client hasn't requested any Subprotocol. "
                 "Closing Connection")
        return await websocket.close()

    if websocket.subprotocol:
        logging.info("Protocols Matched: %s", websocket.subprotocol)
    else:
        # In the websockets lib if no subprotocols are supported by the
        # client and the server, it proceeds without a subprotocol,
        # so we have to manually close the connection.
        logging.warning('Protocols Mismatched | Expected Subprotocols: %s,'
                        ' but client supports  %s | Closing connection',
                        websocket.available_subprotocols,
                        requested_protocols)
        return await websocket.close()

    charge_point_id = path.strip('/')
    msg_file = f"received_messages_{charge_point_id}.txt"
    print("Current Working Directory:", os.getcwd())
    print("Resolved File Path:", os.path.abspath(msg_file))
    
    cp = ChargePoint(charge_point_id, websocket, msg_file)

    await cp.start()


async def main():
    server = await websockets.serve(
        on_connect,
        '192.168.60.5',
        9005,
        subprotocols=['ocpp2.0.1']
    )
    logging.info("WebSocket Server Started")
    await server.wait_closed()

if __name__ == '__main__':
    asyncio.run(main())