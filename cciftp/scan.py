import os
import sys

from ftplib import FTP


class EsaCciFtpDataSource:
    def __init__(self,
                 ftp_host='anon-ftp.ceda.ac.uk',
                 ftp_dir='neodc/esacci',
                 ftp_tac_filename='esacci_terms_and_conditions.txt'):
        self.host = ftp_host
        self.dir_name = ftp_dir
        self.tac_filename = ftp_tac_filename

    def get_terms_and_conditions(self):
        ftp = FTP(self.host)
        ftp.login()
        ftp.cwd(self.dir_name)
        lines = []
        ftp.retrlines('RETR %s' % self.tac_filename, callback=lines.append)
        ftp.quit()
        return '\n'.join(lines)

    def scan_to(self, target_dir, start_dir, max_depth):
        ftp = FTP(self.host)
        ftp.login()

        target_path = '%s/%s' % (target_dir, 'esa_cci_ftp_tree')
        if start_dir:
            target_path = '%s/%s' % (target_path, start_dir)

        if not os.path.exists(target_path):
            os.makedirs(target_path)

        with open(os.path.join(target_dir, 'esa_cci_ftp_index.txt'), 'w') as index_file:
            self._rec_dir_scan(ftp,
                               index_file,
                               target_path,
                               '%s/%s' % (self.dir_name, start_dir) if start_dir else self.dir_name,
                               0, max_depth)

        ftp.quit()

    def _rec_dir_scan(self, ftp, index_file, target_path, dir_name, level, max_level):
        ftp.cwd(dir_name)
        content = list(ftp.mlsd(facts=['type', 'size', 'modify']))
        indent = (level * '  ')
        file_size_sum = 0
        current_size = 0
        for name, facts in content:
            t = facts.get('type', None)
            if t == 'dir':
                line = indent + name + '/'
                print(line)
                index_file.write(line + '\n')
                target_dir = os.path.join(target_path, name)
                if not os.path.exists(target_dir):
                    os.mkdir(target_dir)
                if max_level is None or level < max_level:
                    current_size = self._rec_dir_scan(ftp, index_file, target_dir, name, level + 1, max_level)
            elif t == 'file':
                line = indent + name
                print(line)
                index_file.write(line + '\n')
                current_size = int(facts.get('size', '0'))
            else:
                continue

            with open(os.path.join(target_path, name + '.info'), 'w') as fp:
                fp.write(facts.get('modify', '') + ',' + str(current_size))

            file_size_sum += current_size

        ftp.cwd('..')
        return file_size_sum


def main(args=sys.argv[1:]):
    import argparse
    parser = argparse.ArgumentParser(description="Scan the ESA CCI Portal's FPT tree.")
    parser.add_argument('target_dir', metavar='TARGET', type=str, default='.', nargs='?',
                        help='Target directory to which the scan results will be written. '
                             'Default is current directory.')
    parser.add_argument('-s', '--start_dir', metavar='START', type=str, nargs=1, action='store',
                        help='directory within the FTP directory from which to start scanning')
    parser.add_argument('-d', '--max_depth', metavar='NUM', type=int, nargs=1, action='store',
                        help='maximum directory scanning depth')
    parser.add_argument('-t', '--toc_only', action='store_true',
                        help='print out terms and conditions and exit')

    args = parser.parse_args(args)

    data_source = EsaCciFtpDataSource()

    if args.toc_only:
        tac = data_source.get_terms_and_conditions()
        print()
        print(tac)
        print()
    else:
        target_dir = args.target_dir
        if not os.path.exists(target_dir):
            print('error: invalid target directory:', target_dir)
            exit(1)
        start_dir = args.start_dir[0] if args.start_dir is not None else ''
        max_depth = args.max_depth[0] if args.max_depth is not None else None
        print('Scanning %s/** to %s' % (start_dir, args.target_dir))
        data_source.scan_to(target_dir, start_dir, max_depth)


if __name__ == '__main__':
    main()
