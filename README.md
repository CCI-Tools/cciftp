# cciftp

Tool(s) that help staying up-to-date with ESA's CCI Data Portal's (http://cci.esa.int/) FTP tree.

Usage:

    usage: cci-ftp-scan [-h] [-s START] [-d NUM] [-t] [TARGET]
    
    Scan the ESA CCI Portal's FPT tree.
    
    positional arguments:
      TARGET                Target directory to which the scan results will be
                            written. Default is current directory.
    
    optional arguments:
      -h, --help            show this help message and exit
      -s START, --start_dir START
                            directory within the FTP directory from which to start
                            scanning
      -d NUM, --max_depth NUM
                            maximum directory scanning depth
      -t, --toc_only        print out terms and conditions and exit
