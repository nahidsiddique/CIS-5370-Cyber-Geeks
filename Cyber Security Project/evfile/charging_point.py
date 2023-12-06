import asyncio

from ocpp.v201.enums import RegistrationStatusType
import logging
import websockets

from ocpp.v201 import call
from ocpp.v201 import ChargePoint as cp

logging.basicConfig(level=logging.INFO)


class ChargePoint(cp):

    async def send_boot_notification(self):
        request = call.BootNotificationPayload(
            charging_station={
                'model': 'Tesla V3',
                'vendor_name': 'Tesla',
                'customData': {
                                'vendorId': '3.4',
                                 'color': 'blue',
                                'capacity': 20
                            },
                
            },
            reason="LocalReset"
           
            
        )
        response = await self.call(request)

        if response.status == RegistrationStatusType.accepted:
            print("Connected to central system.")
            
        while True:
                
                user_input =input("Enter your next Msg:")
                
                if user_input !='close':
                    car_voltage =int(input("Enter Car Voltage:"))
                    if car_voltage >= 100:
                        print('Your Battery is fully charged')
                    request = call.BootNotificationPayload(
                    charging_station={
                            'model': 'Tesla V3',
                            'vendor_name': 'Tesla',
                            'customData': {
                                        'vendorId': '3.4',
                                        'color': 'blue',
                                        'capacity': car_voltage
                            }
                        },
                    reason=user_input
                        
                    )
                    response = await self.call(request)             
                    print("Received the 2nd msg successfully")
                else:
                    break


async def main():
    async with websockets.connect(
            'ws://192.168.60.5:9005/CP_1',
            subprotocols=['ocpp2.0.1']
    ) as ws:
        cp = ChargePoint('CP_1', ws)

        await asyncio.gather(cp.start(), cp.send_boot_notification())


if __name__ == '__main__':
    asyncio.run(main())