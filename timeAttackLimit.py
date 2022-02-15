from helpers.GbxRemote import GbxRemote

host = '192.168.56.200'
port = 5000

sender = GbxRemote(host, port, 'SuperAdmin', 'SuperAdmin')
r = sender.callMethod('GetTimeAttackLimit')
print(r)
r = sender.callMethod('SetTimeAttackLimit', 300000)
print(r)
