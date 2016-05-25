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

    def scan_to(self, target_dir):
        ftp = FTP(self.host)
        ftp.login()

        target_path = os.path.join(target_dir, 'esa_cci_ftp_tree')
        if not os.path.exists(target_path):
            os.mkdir(target_path)

        with open(os.path.join(target_dir, 'esa_cci_ftp_index.txt'), 'w') as index_file:
            self._rec_dir_scan(ftp, index_file, target_path, self.dir_name, 0)

        ftp.quit()

    def _rec_dir_scan(self, ftp, index_file, target_path, dir_name, level):
        ftp.cwd(dir_name)
        content = list(ftp.mlsd(facts=['type', 'size', 'modify']))
        indent = (level * '  ')
        file_size_sum = 0
        for name, facts in content:
            t = facts.get('type', None)
            if t == 'dir':
                line = indent + name + '/'
                print(line)
                index_file.write(line + '\n')
                target_dir = os.path.join(target_path, name)
                if not os.path.exists(target_dir):
                    os.mkdir(target_dir)
                current_size = self._rec_dir_scan(ftp, index_file, target_dir, name, level + 1)
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
    parser.add_argument('target_dir', metavar='DIR', type=str, default='.', nargs='?',
                        help='Target directory to which the scan results will be written. '
                             'Default is current directory.')
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
        if not os.path.exists(args.target_dir):
            print('error: invalid target directory:', args.target_dir)
            exit(1)
        print('Scanning to', args.target_dir)
        data_source.scan_to(args.target_dir)


if __name__ == '__main__':
    main()
