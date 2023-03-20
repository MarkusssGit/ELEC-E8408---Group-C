import time
import sqlite3

import hike
import db
import bt

hubdb = db.HubDatabase()
hubbt = bt.HubBluetooth()

def process_sessions(sessions: list[hike.HikeSession]):
    """Callback function to process sessions.

    Calculates the calories for a hiking session.
    Saves the session into the database.

    Args:
        sessions: list of `hike.HikeSession` objects to process
    """

    for s in sessions:
        s.calc_kcal()
        hubdb.save(s)

def main():
    print("Starting Bluetooth receiver.")
    try:
        while True:
            hubbt.wait_for_connection()
            hubbt.synchronize(callback=process_sessions)
            
    except KeyboardInterrupt:
        print("CTRL+C Pressed. Shutting down the server...")

    except Exception as e:
        print(f"Unexpected shutdown...")
        print(f"ERROR: {e}")
        hubbt.sock.close()
        raise e

if __name__ == "__main__":
    main()