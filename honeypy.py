#Libraries
import argparse
import sys #parsing command line arguments
from ssh_honeypot import * #importing the honeypot function from the module
# Parse Arguments

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SSH Honeypot")
    parser.add_argument('-a', '--address', type=str,required=True)
    parser.add_argument('-p', '--port', type=int, required=True)
    parser.add_argument('-u', '--username', type=str)
    parser.add_argument('-pw', '--password', type=str)

    parser.add_argument('-s', '--ssh', action='store_true')
    parser.add_argument('-w', '--http', action='store_true')

    #stores all the arguments above in args
    args = parser.parse_args()

    try:

        if args.ssh:
            print("[*] Starting SSH Honeypot...")
            honeypot(args.address, args.port, args.username, args.password)
        elif args.http:
            print("[*] Starting HTTP Honeypot...")
            pass
        else:
            print("error: Please specify a honeypot type (SSH or HTTP) using -s or -w flags.")
    except KeyboardInterrupt:
        print("\n[*] Shutting down honeypot...")
        sys.exit(0)
            
            

    