# coding=utf-8

import sys
import calendar
import time

from argparse import ArgumentParser
from elasticsearch import Elasticsearch, Urllib3HttpConnection, NotFoundError


ES_TIMEOUT = 3600


class ArgumentError(Exception):
    pass


def validate_arguments(args):
    pass


def parse_arguments():
    parser = ArgumentParser()
    parser.add_argument('command')
    parser.add_argument('-d', '--debug', action='store_true')
    parser.add_argument('--host', type=str, default='127.0.0.1:9200')
    parser.add_argument('--repository-name', type=str, required=True)
    parser.add_argument('--repository-path', type=str, required=True)
    parser.add_argument('--snapshot-name', type=str, required=True)
    parser.add_argument('--index-name', type=str, required=True)
    parser.add_argument('--index-target-name', type=str, required=True)
    args = parser.parse_args()
    validate_arguments(args)
    return args


def cmd_list(service, repository):
    response = service.get(repository=repository, snapshot='_all')
    snapshots = response['snapshots']
    print('Number of snapshots found: {}'.format(len(snapshots)))
    for item in snapshots:
        print('- Snapshot "{}" taken in {} (state {}, indices: "{}", failures: {})'.format(item['snapshot'], item['start_time'], item['state'], ', '.join(item['indices']), len(item['failures'])))
    return 0

# creates index snapshot (and previously creates repo if not existing)

# this currently breaks if the repo does not exist, be sure to do createrepo before it
def cmd_create(service, repository, path, snapshot, index):
    r = []
    try:
        r = service.get_repository(repository=repository)
    except NotFoundError as exception:
        print('Repository {} does not exist and it is going to be created now'.format(repository))
        repository_settings = {
            'type': 'fs',
            'settings': {
                'location': path,
                'compress': False,
            },
        }
        r = service.create_repository(repository=repository, body=repository_settings)
    repository_path = r[repository]['settings']['location']
    if path != repository_path:
        raise Exception('Given repository path doesn\'t match current location\nCurrent: {}\nGiven: {}'.format(repository_path, path))
    print('The repository {} looks okay (path={})'.format(repository, repository_path))
    response = service.create(repository=repository, snapshot=snapshot, wait_for_completion=True, body={'indices': index})
    if response['snapshot']['state'] != 'SUCCESS':
        raise Exception('Snapshot just created is in a bad state: {}'.format(response))
    return 0

# create elasticsearch repo (not a snapshot)

def cmd_createrepo(service, repository, path):
    repository_settings = {
        'type': 'fs',
        'settings': {
            'location': path,
            'compress': False,
        },
    }
    r = service.create_repository(repository=repository, body=repository_settings)
    return 0


def cmd_restore(service, repository, snapshot, index, index_target):
    r = []
    try:
        r = service.get_repository(repository=repository)
    except NotFoundError as exception:
        print('Repository {} does not exist'.format(r))
        raise exception
    # Restore snapshot
    response = service.restore(repository=repository, snapshot=snapshot, wait_for_completion=True, body={
        'indices': index,
        'rename_pattern': index,
        'rename_replacement': index_target,
    })
    try:
        failed = response['snapshot']['shards']['failed']
        if failed > 0:
            raise Exception('At least a shard failed during restoration: {}'.format(response))
    except KeyError as e:
        print('Restoration seemed to have failed: {}'.format(response))
        raise e
    return 0


def main():
    try:
        args = parse_arguments()
    except ArgumentError as e:
        return e
    es = Elasticsearch(args.host, connection_class=Urllib3HttpConnection, timeout=ES_TIMEOUT)
    ss = es.snapshot

    # TODO - Use subcommands
    # https://docs.python.org/3/library/argparse.html#sub-commands
    # http://chase-seibert.github.io/blog/2014/03/21/python-multilevel-argparse.html
    if args.command == 'list':
        return cmd_list(service=ss, repository=args.repository_name)
    elif args.command == 'create':
        return cmd_create(service=ss, repository=args.repository_name, path=args.repository_path, snapshot=args.snapshot_name, index=args.index_name)
    elif args.command == 'createrepo':
        return cmd_createrepo(service=ss, repository=args.repository_name, path=args.repository_path)
    elif args.command == 'restore':
        return cmd_restore(service=ss, repository=args.repository_name, snapshot=args.snapshot_name, index=args.index_name, index_target=args.index_target_name)
    else:
        raise ArgumentError('Unknown command, try "create" or "list"')


if __name__ == '__main__':
    sys.exit(main())
