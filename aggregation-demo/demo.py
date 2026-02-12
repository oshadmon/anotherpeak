import argparse
from mapping_mqtt import mqtt_mapping
from data_generator import data_generator

def main():
    parse = argparse.ArgumentParser()
    parse.add_argument("conn", type=str, default=None, help="REST connection information")
    parse.add_argument("--boat-side", type=str, choices=["DLB", "DLT"], default="DLB", help="Boat side")
    args = parse.parse_args()

    mqtt_mapping(conn=args.conn)
    data_generator(conn=args.conn, boat_side=args.boat_side)


if __name__ == "__main__":
    main()

