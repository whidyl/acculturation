
class Account(object):
    def __init__(self, username, password):
        self.passw = password
        self.user = username
    def printUser(self):
        print(self.user)

myAccount = Account('dylan', '1234')
myAccount.printUser()
myAccount2 = Account('mike', 'password')
myAccount2.printUser()
table = [
[1,2,3],
[1,2,3],
[1,2,4],
[2,3,4]
]
print(table)