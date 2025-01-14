#!/usr/bin/env python3
import os, csv, sys, json, time, argparse, speedtest, subprocess

#Defaults
DEFAULT_FORMAT = "Averages last {0} days, from {1} test(s):\n\nPing: {2}\nDownload: {3}\nUpload: {4}"
DEFAULT_LOG_FILE = "~/.speedtest_history.json"
DEFAULT_NUM_DAYS = 7

#Help text for argparse
HELP_DESC = "A simple script for automating the process of keeping a log of speedtests and displaying their averages"
HELP_FORMAT = "The format string that will be output. Should be in python 3 curly bracket format. Arguments passed in are num_days, the number of found speedtests within the given range, ping, download, and upload, respectively. Not used if --silent is specified"
HELP_LOG_FILE = f"The file name to save all speedtest data in. Defaults to '{DEFAULT_LOG_FILE}'"
HELP_NUM_DAYS = f"How many days old a test must be within to be included in the average. Defaults to '{DEFAULT_NUM_DAYS}'"
HELP_RESET = "Clear the specified log file before running"
HELP_SILENT = "Do not output averages. If this is specified, --format is not used"
HELP_TEST = "Run a speedtest and add it to the log file. If this is not specified, only the averages are output"
HELP_VERBOSE = "Displays verbose output as the program runs. Primarily intended for debugging purposes"

#Version checker for log files
LOG_VERSION = "1.0"

#Constants for use in code
LOG_FILE_EXT = ".json"
MEGA_FACTOR = 1e6
PING_ROUND = 2
DOWN_ROUND = 2
UP_ROUND = 2
DAY_LENGTH = 86400


def main():
    """The main method. Pretty self-explanatory. In a self-contained function for convenience"""
    args = arg_parser().parse_args(sys.argv[1:])
    args.log_file = validate_log_file(args.log_file)
    if args.reset:
        clear_log(args.log_file, args.verbose)
    log_data = get_log_data(args.log_file, verbose=args.verbose)
    if args.test:
        log_data['tests'].append(run_speedtest(verbose=args.verbose))
        write_log(log_data, args.log_file)
    if not args.silent:
        show_averages(log_data['tests'], args.num_days, args.format)
    sys.exit(os.EX_OK)


def arg_parser():
    """Constructs an ArgumentParser object for this program and returns it"""
    parser = argparse.ArgumentParser(description=HELP_DESC)
    parser.add_argument('-f', '--format', default=DEFAULT_FORMAT, help=HELP_FORMAT)
    parser.add_argument('-l', '--log-file', default=DEFAULT_LOG_FILE, help=HELP_LOG_FILE)
    parser.add_argument('-n', '--num-days', default=DEFAULT_NUM_DAYS, help=HELP_NUM_DAYS)
    parser.add_argument('-r', '--reset', action='store_true', help=HELP_RESET)
    parser.add_argument('-s', '--silent', action='store_true', help=HELP_SILENT)
    parser.add_argument('-t', '--test', action='store_true', help=HELP_TEST)
    parser.add_argument('-v', '--verbose', action='store_true', help=HELP_VERBOSE)
    return parser


def validate_log_file(log_file_name):
    if not log_file_name.endswith(LOG_FILE_EXT):
        log_file_name += LOG_FILE_EXT
    return os.path.expanduser(log_file_name)

def clear_log(log_file_name, verbose=False):
    try:
        os.remove(log_file_name)
        if verbose:
            print("Log file '{log_file_name}' cleared")
    except FileNotFoundError:
        if verbose:
            print("No log file found to clear")
    except PermissionError:
        print(f"Error: Insufficient permissions to clear file: {log_file_name}")
        sys.exit(os.EX_NOPERM)


def get_log_data(log_file_name, verbose=False):
    """Loads log data from a given log file and decodes it as JSON"""
    try:
        with open(log_file_name, 'r') as log_file:
            log_data = json.loads(log_file.read())
            if not log_data['version'] == LOG_VERSION:
                print(f"Error: log version mismatch. Expected '{LOG_VERSION}', got '{log_data['version']}'")
    except PermissionError:
        print(f"Error: Insufficient permissions to read from file '{log_file_name}'")
        sys.exit(os.EX_NOPERM)
    except FileNotFoundError:
        if verbose:
            print("Log not found, generating new log data")
        log_data = {
            "version": LOG_VERSION,
            "tests": []
        }
    return log_data


def run_speedtest(verbose=False):
    """Runs a speedtest and returns the result as a dict, ready to be written to the log"""
    if verbose:
        print("Running speedtest...")
    try:
        start_time = time.time()
        st = speedtest.Speedtest()
        st.get_best_server()
        st.download()
        st.upload()
        end_time = time.time()
        if verbose:
            print(f"Speedtest completed in {end_time-start_time:.2f}s")
        results = st.results.dict()
        if results['download']==0 and results['upload']==0:
            print('Error: Speedtest packets are being blocked')
            sys.exit(os.EX_UNAVAILABLE)
        return {
            "timestamp": round(time.time()),
            "ping": round(results['ping'], PING_ROUND),
            "download": round(results['download']/MEGA_FACTOR, DOWN_ROUND),
            "upload": round(results['upload']/MEGA_FACTOR, UP_ROUND)
        }
    except speedtest.ConfigRetrievalError:
        print("Error: Speedtest was not able to run. Check network connection.")
        sys.exit(os.EX_TEMPFAIL)


def write_log(log_data, log_file_name):
    """Encodes the given object as JSON and outputs it to the given log file, overwriting any previous contents"""
    try:
        with open(log_file_name, 'w') as log_file:
            log_file.write(json.dumps(log_data, indent=4)+'\n')
    except PermissionError:
        print(f"Error: Insufficient permissions to write to file '{log_file_name}'")
        sys.exit(os.EX_CANTCREAT)


def show_averages(tests, num_days, format_str):
    """Averages the data from a list of tests, applies it to a given format string, and displays the results"""
    if len(tests) == 0:
        print("Error: No test data present. Run at least one time with the -t or --test command line flags to generate and log test data")
        sys.exit(os.EX_NOINPUT)
    sums = {
        "ping": 0,
        "download": 0,
        "upload": 0
    }
    results_used = 0
    for test in tests:
        if int(time.time())-test['timestamp'] < num_days*DAY_LENGTH:
            sums['ping'] += test['ping']
            sums['download'] += test['download']
            sums['upload'] += test['upload']
            results_used += 1
    avg = {
        "ping": round(sums['ping']/results_used, PING_ROUND),
        "download": round(sums['download']/results_used, DOWN_ROUND),
        "upload": round(sums['upload']/results_used, UP_ROUND)
    }
    print(format_str.format(num_days, results_used, avg['ping'], avg['download'], avg['upload']))


if __name__ == "__main__":
    main()
