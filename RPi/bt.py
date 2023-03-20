import bluetooth
import time

import hike

WATCH_BT_MAC = 'XX:XX:XX:XX:XX:XX'
WATCH_BT_PORT = 1

class HubBluetooth:
    """Handles Bluetooth pairing and synchronization with the Watch.

    Attributes:
        connected: A boolean indicating if the connection is currently established with the Watch.
        sock: the socket object created with bluetooth.BluetoothSocket(),
              through which the Bluetooth communication is handled.
    """

    connected = False
    sock = None
    
    def wait_for_connection(self):
        """Synchronous function continuously trying to connect to the Watch by 2 sec intervals.
        If a connection has been made, it sends the watch a `c` ASCII character as a confirmation.
        """

        if not self.connected:
            # try to connect every sec while connection is made
            while True:
                print("Waiting for connection...")
                try:
                    self.sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
                    self.sock.connect((WATCH_BT_MAC, WATCH_BT_PORT))
                    self.sock.settimeout(2)
                    self.connected = True
                    self.sock.send('c')
                    print("Connected to Watch!")
                    break
                except bluetooth.btcommon.BluetoothError:
                    time.sleep(1)
                except Exception as e:
                    print(e)
                    print("Hub: Error occured while trying to connect to the Watch.")

            print("Hub: Established Bluetooth connection with Watch!")
        print("WARNING Hub: the has already connected via Bluetooth.")

    def synchronize(self, callback):
        """Continuously tries to receive data from an established connection with the Watch.

        If receives data, then transforms it to a list of `hike.HikeSession` object.
        After that, calls the `callback` function with the transformed data.
        Finally sends a `r` as a response to the Watch for successfully processing the
        incoming data.

        If does not receive data, then it tries to send `c` as a confirmation of the established
        connection at every second to inform the Watch that the Hub is able to receive sessions.

        Args:
            callback: One parameter function able to accept a list[hike.HikeSession].
                      Used to process incoming sessions arbitrarly

        Raises:
            KeyboardInterrupt: to be able to close a running application.
        """
        print("Synchronizing with watch...")
        remainder = b''
        while True:
            try:
                chunk = self.sock.recv(1024)

                messages = chunk.split(b'\n')
                messages[0] = remainder + messages[0]
                remainder = messages.pop()

                if len(messages):
                    try:
                        print(f"received messages: {messages}")

                        sessions = HubBluetooth.messages_to_sessions(messages)
                        callback(sessions)
                        self.sock.send('r')

                        print(f"Saved. 'r' sent to the socket!")

                    except (AssertionError, ValueError) as e:
                        print(e)
                        print("WARNING: Receiver -> Message was corrupted. Aborting...")

            except KeyboardInterrupt:
                self.sock.close()
                raise KeyboardInterrupt("Shutting down the receiver.")

            except bluetooth.btcommon.BluetoothError as bt_err:
                if bt_err.errno == 11: # connection down
                    print("Lost connection with the watch.")
                    self.connected = False
                    self.sock.close()
                    break
                elif bt_err.errno == None: # possibly occured by socket.settimeout
                    self.sock.send('c')
                    print("Reminder has been sent to the Watch about the attempt of the synchronization.")

    @staticmethod
    def messages_to_sessions(messages: list[bytes]) -> list[hike.HikeSession]:
        """Transforms multiple incoming messages to a list of hike.HikeSession objects.

        Args:
            messages: list of bytes, in the form of the simple protocol between
                      the Hub and the Watch.

        Returns:
            list[hike.HikeSession]: a list of hike.HikeSession objects representing the
                                    interpreted messages.
        """

        return list(map(HubBluetooth.mtos, messages))

    @staticmethod
    def mtos(message: bytes) -> hike.HikeSession:
        """Transforms a single message into a hike.HikeSession object.

        A single message is in the following format with 0->inf number of latitude and longitude pairs:
            id;steps;km;lat1,long1;lat2,long2;...;\\n

        For example:
            b'4;2425;324;64.83458747762428,24.83458747762428;...,...;\\n'

        Args:
            message: bytes to transform.

        Returns:
            hike.HikeSession: representing a hiking session from transforming a message.

        Raises:
            AssertionError: if the message misses information, or if it is badly formatted.
        """
        m = message.decode('utf-8')

        # filtering because we might have a semi-column at the end of the message, right before the new-line character
        parts = list(filter(lambda p: len(p) > 0, m.split(';')))
        assert len(parts) >= 3, f"MessageProcessingError -> The incoming message doesn't contain enough information: {m}"

        hs = hike.HikeSession()
        hs.id     = int(parts[0])
        hs.steps  = int(parts[1])
        hs.km     = float(parts[2])

        def cvt_coord(c):
            sc = c.split(',')
            assert len(sc) == 2, f"MessageProcessingError -> Unable to process coordinate: {c}"
            return float(sc[0]), float(sc[1])

        if len(parts) > 3:
            hs.coords = map(cvt_coord, parts[3:])

        return hs
