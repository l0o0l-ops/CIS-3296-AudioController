from bleak import BleakScanner, BleakClient
import asyncio

class CommandLibrary:

    
    
    def __init__(self, client, ready_event, PYBRICKS_COMMAND_EVENT_CHAR_UUID):
        self.client = client
        self.ready_event = ready_event
        self.PYBRICKS_COMMAND_EVENT_CHAR_UUID = PYBRICKS_COMMAND_EVENT_CHAR_UUID

    # Shorthand for sending some data to the hub.
    async def send(self, data):
        # Wait for hub to say that it is ready to receive data.
        await self.ready_event.wait()
        # Prepare for the next ready event.
        self.ready_event.clear()
        # Send the data to the hub.
        await self.client.write_gatt_char(
            self.PYBRICKS_COMMAND_EVENT_CHAR_UUID,
            b"\x06" + data,  # prepend "write stdin" command (0x06)
            response=True
        )




    async def move_forward(self,time):
        
        
        await self.send(b"fwd")
        await asyncio.sleep(time)
        await self.send(b"stp")

    async def move_backward(self,time):
        
        
        await self.send(b"mob")
        await asyncio.sleep(time)
        await self.send(b"stp")

    async def bye(self):
        await self.send(b"bye")


    async def turn_right(self, time):
        await self.send(b"tur")
        await asyncio.sleep(2)
        await self.send(b"mof")
        await asyncio.sleep(time)
        await self.send(b"mos")
        await self.send(b"res")

        

    async def turn_left(self, time):
        await self.send(b"tul")
        await asyncio.sleep(2)
        await self.send(b"mof")
        await asyncio.sleep(time)
        await self.send(b"mos")
        await self.send(b"res")
    


    async def grab(self):
        await self.send(b"grb")
        
        # self.motor_d.run_target(300, 360)
        # wait(500)
        # self.motor_b.run(-200)
        # wait(1000)
        # self.motor_b.stop()
        # wait(500)
        # self.motor_d.run_target(300, 0)
        

       








