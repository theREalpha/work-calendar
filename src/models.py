class User:
    def __init__(self, username:str, email:str, sessionID:str=None):
        self.username = username
        self.email = email
        self.sessionID = sessionID

    def __str__(self):
        return f"{self.username}({self.email})"
    def __repr__(self):
        return f"{self.username}({self.email})"
    def __eq__(self, value: object) -> bool:
        return value.email== self.email

class Record:
    def __init__(self, rec):
        self.id= rec['$id']['value']
        self.username= rec['表示用氏名']['value']
        self.email= rec['氏名']['value'][0]['code']
        self.clockIn= rec['出勤時刻']['value']
        self.clockOut= rec['退勤時刻']['value']
        self.date= rec['日付']['value']
        self.workMode= rec['勤務休暇']['value']
        self.raw = rec
        
    def __str__(self):
        return f"{self.username}({self.email})\t| {self.date} | {self.workMode} |\nIn:\t {self.clockIn}\nOut:\t{self.clockOut}"
    def __repr__(self):
        return f"{self.username}({self.email})\t| {self.date} | {self.workMode} |\nIn:\t {self.clockIn}\nOut:\t{self.clockOut}"
    def __eq__(self,value: object)->bool:
        return self.id==value.id
    def toDict(self):
        return self.__dict__