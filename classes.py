import re
import mysql.connector

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="chen",
    database="chtdttt"
)

class ConvertData:
    """
    Truy vấn và xử lý dữ liệu
    """
    def __init__(self):
        self.resultbenh = []
        self.resulttrieutrung = []
        self.resultfc = []
        self.resultbc = []
        self.resulttt = []

    def convertbenh(self, animal):
        """
        Lấy dữ liệu bảng bệnh
        """
        dbbenh = mydb.cursor()
        dbbenh.execute("SELECT * FROM chtdttt.benh where status = %s;",(animal,))
        benh = dbbenh.fetchall()
        dirbenh = {}
        for i in benh:
            dirbenh['idbenh'] = i[0]
            dirbenh['tenBenh'] = i[1]
            dirbenh["nguyennhan"] = i[2]
            dirbenh['loikhuyen'] = i[3]
            self.resultbenh.append(dirbenh)
            dirbenh = {}

    def converttrieuchung(self,animal):
        """
        Lấy dữ liệu từ bảng trieuchung
        """
        dbtrieuchung = mydb.cursor()
        dbtrieuchung.execute("SELECT * FROM chtdttt.trieuchung where status = %s;",(animal,))
        trieuchung = dbtrieuchung.fetchall()
        dirtrieuchung = {}
        # resulttrieuchung=[]
        for i in trieuchung:
            dirtrieuchung['idtrieuchung'] = i[0]
            dirtrieuchung['noidung'] = i[1]
            self.resulttrieutrung.append(dirtrieuchung)
            dirtrieuchung = {}

    def getfc(self, animal):
        """
        Lấy luật
        """
        f = open("rules.txt")
        lines = f.readlines()
       
        if animal == "1":
            desired_lines = lines[2:23]
        else:
            desired_lines = lines[39:62]
        for line in desired_lines:
            self.resultfc.append(line)
        return self.resultfc
    def getbc(self, animal):
        f = open("rules.txt")
        lines = f.readlines()
       
        if animal == "1":
            desired_lines = lines[63:76]
        else:
            desired_lines = lines[24:37]
        for line in desired_lines:
            self.resultbc.append(line)
        return self.resultbc
    def get_benh_by_id(self, id_benh):
        """
        Tìm bệnh dựa trên id
        """
        for i in self.resultbenh:
            if i["idbenh"] == id_benh:
                return i
        return 0

    def get_trieuchung_by_id(self, id_trieuchung):
        for i in self.resulttrieutrung:
            if i["idtrieuchung"] == id_trieuchung:
                return i
        return 0
  

class Validate:
    def __init__(self) -> None:
        pass

    def validate_input_number_form(self,value):
        while (1):
            valueGetRidOfSpace = ''.join(value.split(' '))
            check = valueGetRidOfSpace.isnumeric()
            if (check):
                return valueGetRidOfSpace
            else:
                print("-->Chatbot: Vui lòng nhập 1 số dương")
                value = input()


    def validate_binary_answer(self, value):
        acceptance_answer_lst = ['1', 'y', 'yes', 'co', 'có']
        decline_answer_lst = ['0', 'n', 'no', 'khong', 'không']
        value = value+''
        while (1):
            if (value) in acceptance_answer_lst:
                return True
            elif value in decline_answer_lst:
                return False
            else:
                print(
                    "-->Chatbot: Câu trả lời không hợp lệ. Vui lòng nhập lại câu trả lời")
                value = input()


def searchindexrule(rule,goal):
    """
    Tìm vị trí các rule có bệnh là goal
    """
    index=[]
    for i in rule:
        if goal in i:
            index.append(rule.index(i))
    return index
def get_s_in_d(answer,goal,rule,d,flag):
    """
    Lấy các triệu chứng theo sự suy diễn để giảm thiểu câu hỏi
    và  đánh dấu các luật đã được duyệt qua để bỏ qua những luật có cùng cùng câu hỏi vào
    """
    result=[]
    index=[]
    if flag==1:
        for i in range(len(rule)):
            if (rule[i][0]==goal) and (answer in rule[i]) and (i in d):
                for j in rule[i]:
                    if j[0]=='S':
                        result.append(j)
                        # result=set()
    else:
        for i in range(len(rule)):
            if (rule[i][0]==goal) and (answer in rule[i]): index.append(i)
            if (rule[i][0]==goal) and (answer not in rule[i]) and (i in d):
                for j in rule[i]:
                    if j[0]=='S':
                        result.append(j)        

    return sorted(set(result)),index

def get_all_rules_in_d(d, rule):
    result = []

    for i in rule:
        if d in i:
            matches = [x for x in i.split('->')[0].split(',')]
            result.append(matches)
    return sorted(set(result))