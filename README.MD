# speedtest_avg

### Description

This is a simple python script intended to be run as a cron job that runs a speedtest (using the [speedtest-cli](https://pypi.org/project/speedtest-cli/) package) and keeps a running log of the average ping, upload, and download speeds over time.

### Usage

This program makes full use of Python's `argparse` package. As such, it is fully compliant with GNU command-line standard conventions and can output its usage with the command line argument `--help`. This help text is also copied below, in full.

```
usage: speedtest_avg [-h] [-f FORMAT] [-l LOG_FILE] [-n NUM_DAYS] [-r] [-s]
                     [-t] [-v]

A simple script for automating the process of keeping a log of speedtests and
displaying their averages

optional arguments:
  -h, --help            show this help message and exit
  -f FORMAT, --format FORMAT
                        The format string that will be output. Should be in
                        python 3 curly bracket format. Arguments passed in are
                        num_days, the number of found speedtests within the
                        given range, ping, download, and upload, respectively.
                        Not used if --silent is specified
  -l LOG_FILE, --log-file LOG_FILE
                        The file name to save all speedtest data in. Defaults
                        to '~/.speedtest_history.json'
  -n NUM_DAYS, --num-days NUM_DAYS
                        How many days old a test must be within to be included
                        in the average. Defaults to '7'
  -r, --reset           Clear the specified log file before running
  -s, --silent          Do not output averages. If this is specified, --format
                        is not used
  -t, --test            Run a speedtest and add it to the log file. If this is
                        not specified, only the averages are output
  -v, --verbose         Displays verbose output as the program runs. Primarily
                        intended for debugging purposes
```

### License

This software is licensed under [the unlicense](https://unlicense.org/). Do what you want.

### Support

If you discover any bugs in this script, please file a bug report right here on GitHub.

### Contributing

If you find a bug, feel free to file a bug report and I'll take care of it when I have the time. If you find a bug and feel like taking the time to fix it yourself, please make a pull request and odds are I'll be happy to accept it.
