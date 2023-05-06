from helpers.mongodb import get_version, set_version
from helpers.version import version as current_version
import sys


def versions_eq(left, right):
    left_l = list()
    for e in left.strip().split('.'):
        try:
            left_l.append(int(e))
        except Exception:
            left_l.append(e)
    right_l = list()
    for e in right.strip().split('.'):
        try:
            right_l.append(int(e))
        except Exception:
            right_l.append(e)
    while len(left_l) < 4:
        left_l.append(0)
    while len(right_l) < 4:
        right_l.append(0)
    for i in range(4):
        if not isinstance(left_l[i], int) == isinstance(right_l[i], int):  # works even if both are str, the result is True
            return False
        if not left_l[i] == right_l[i]:
            return False
    return True


def versions_lt(left, right):
    left_l = list()
    for e in left.strip().split('.'):
        try:
            left_l.append(int(e))
        except Exception:
            left_l.append(e)
    right_l = list()
    for e in right.strip().split('.'):
        try:
            right_l.append(int(e))
        except Exception:
            right_l.append(e)
    while len(left_l) < 4:
        left_l.append(0)
    while len(right_l) < 4:
        right_l.append(0)
    for i in range(4):
        if isinstance(left_l[i], str) and isinstance(right_l[i], int):
            return True
        if isinstance(left_l[i], int) and isinstance(right_l[i], str):
            return False
        if left_l[i] < right_l[i]:
            return True
        if left_l[i] > right_l[i]:
            return False
    return False


def versions_gt(left, right):
    left_l = list()
    for e in left.strip().split('.'):
        try:
            left_l.append(int(e))
        except Exception:
            left_l.append(e)
    right_l = list()
    for e in right.strip().split('.'):
        try:
            right_l.append(int(e))
        except Exception:
            right_l.append(e)
    while len(left_l) < 4:
        left_l.append(0)
    while len(right_l) < 4:
        right_l.append(0)
    for i in range(4):
        if isinstance(left_l[i], str) and isinstance(right_l[i], int):
            return False
        if isinstance(left_l[i], int) and isinstance(right_l[i], str):
            return True
        if left_l[i] > right_l[i]:
            return True
        if left_l[i] < right_l[i]:
            return False
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


def test_compares():
    print('Success' if versions_eq('1.1.1', '1.1.1') is True else 'Fail')
    print('Success' if versions_eq('1.1.1.alpha1', '1.1.1.alpha1') is True else 'Fail')
    print('Success' if versions_eq('1.1.1', '1.1.1.1') is False else 'Fail')
    print('Success' if versions_lt('1.1.1', '1.1.1.1') is True else 'Fail')
    print('Success' if versions_lt('1.1.1.1', '1.1.1') is False else 'Fail')
    print('Success' if versions_lt('1.1.1', '1.1.1') is False else 'Fail')
    print('Success' if versions_gt('1.1.1.1', '1.1.1') is True else 'Fail')
    print('Success' if versions_gt('1.1.1', '1.1.1') is False else 'Fail')
    print('Success' if versions_gt('1.1.1', '1.1.1.1') is False else 'Fail')
    print('Success' if versions_lte('1.1.1', '1.1.1.1') is True else 'Fail')
    print('Success' if versions_lte('1.1.1.1', '1.1.1') is False else 'Fail')
    print('Success' if versions_lte('1.1.1', '1.1.1') is True else 'Fail')
    print('Success' if versions_gte('1.1.1.1', '1.1.1') is True else 'Fail')
    print('Success' if versions_gte('1.1.1', '1.1.1') is True else 'Fail')
    print('Success' if versions_gte('1.1.1', '1.1.1.1') is False else 'Fail')
    print('Success' if versions_lt('1.2.0.alpha1', '1.2.0') is True else 'Fail')
    print('Success' if versions_lt('1.2.0.alpha1', '1.2.0.beta1') is True else 'Fail')
    print('Success' if versions_lt('1.2.0.alpha1', '1.2.0.alpha2') is True else 'Fail')
    print('Success' if versions_lt('1.2.0.beta1', '1.2.0') is True else 'Fail')
    print('Success' if versions_gt('1.2.0', '1.2.0.alpha1') is True else 'Fail')
    print('Success' if versions_gt('1.2.0.beta1', '1.2.0.alpha1') is True else 'Fail')
    print('Success' if versions_gt('1.2.0.alpha2', '1.2.0.alpha1') is True else 'Fail')
    print('Success' if versions_gt('1.2.0', '1.2.0.beta1') is True else 'Fail')


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
