from helpers.mongodb import get_version, set_version
from helpers.version import version as current_version
import sys


def versions_eq(left, right):
    left = left.strip().split('.')
    right = right.strip().split('.')
    while len(left) < 4:
        left.append(0)
    while len(right) < 4:
        right.append(0)
    for i in range(4):
        if not int(left[i]) == int(right[i]):
            return False
    return True


def versions_lt(left, right):
    left = left.strip().split('.')
    right = right.strip().split('.')
    while len(left) < 4:
        left.append(0)
    while len(right) < 4:
        right.append(0)
    for i in range(4):
        if int(left[i]) < int(right[i]):
            return True
    return False


def versions_gt(left, right):
    left = left.strip().split('.')
    right = right.strip().split('.')
    while len(left) < 4:
        left.append(0)
    while len(right) < 4:
        right.append(0)
    for i in range(4):
        if int(left[i]) > int(right[i]):
            return True
    return False


def versions_lte(left, right):
    if versions_eq(left, right):
        return True
    if versions_lt(left, right):
        return True
    return False


def versions_gte(left, right):
    if versions_eq(left, right):
        return True
    if versions_gt(left, right):
        return True
    return False


def run():
    db_version = get_version()
    if db_version is None:
        # new install nothing todo
        print('Versioning detected a new install!')
        set_version(current_version)
        return
    if versions_eq(db_version, current_version):
        # nothing todo allready the desired version
        print(f'Versioning detected the DB matches the current version {current_version}')
        return
    if versions_gt(db_version, current_version):
        # error DB is on a newer version that software, better just terminate
        print('Versioning detected the Database is on a newer Version than the software provides! Exiting...')
        sys.exit(0)

    print(f'Versioning performing upgrade from v{db_version} to v{current_version}')
    # here could now be done updates on the DB structure if this is required in the future

    set_version(current_version)
