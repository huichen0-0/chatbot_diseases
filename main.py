import os
import sys
from backward_chaining import BackwardChaining
from forward_chaining import ForwardChaining
from classes import *
from fuzzywuzzy import fuzz
# biến khởi tạo
list_symptom_of_person = []  # list các triệu chứng người dùng đưa ra
luat_tien = []
luat_lui = []
db = ConvertData()
def get_data(animal):
    db.convertbenh(animal)  # bang benh
    db.converttrieuchung(animal)  # bang trieu chung
    db.getfc(animal)
    db.getbc(animal)
    luat_lui = db.getbc(animal)
    luat_tien = db.getfc(animal)
#################################################
# 1. câu hỏi chào hỏi
def cauhoi1():
    print("-->Chatbot: Xin chào, tôi là chatbot tư vấn bệnh cho gia súc gia cầm!")
    print("-->Chatbot: Bạn muốn chúng tôi tư vấn cho (Nhập số thứ tự của con vật):")
    print("1. Lợn")
    print("2. Gà")
    answer = Validate.validate_input_number_form(input())
    print(f'-->User: Câu trả lời của tôi là {answer}')
    if answer == "1" or answer == "0":
        get_data(answer)
    else:
        print('-->Chatbot: Vui lòng nhập 1 số từ 0 tới 1')
#################################################################
# 2. Thu thập triệu chứng người dùng cung cấp
def cauhoi2(list_symptom_of_person):
    
    while (1):
        
        print('-->Chatbot: Vui lòng nhập vào 1 triệu chứng mà bạn nhận thấy! Nhập 0 nếu bạn không muốn nhập thêm')
        answer = input()
        print(f'-->User: Câu trả lời của tôi là {answer}')
        #Có 3 triệu chứng trở lên thì mới dừng hỏi
        if(len(list_symptom_of_person)>=3 and answer=='0'):
            break
        # Lấy các câu tương đối gần đúng dựa trên độ tương đồng fuzzy
        threshold = 80
        trieuchung_timduoc = {}
        for trieuchung in db.resulttrieutrung:
            similarity_score = fuzz.ratio(answer, trieuchung["noidung"])
            if similarity_score >= threshold:
                trieuchung_timduoc.append(trieuchung)

        # Hiển thị kết quả
        if trieuchung_timduoc:
            print("-->Chatbot: Triệu chứng bạn nêu là cái nào dưới đây ?(Nhập số thứ tự triệu chứng)")
            count = 1
            for trieuchung in trieuchung_timduoc:
                if (trieuchung not in list_symptom_of_person):
                    print(f'{count}. {trieuchung["noidung"]} \n')
                    count += 1
            print("0. Không có triệu chứng nào ở trên\n -------------Câu trả lời của bạn--------------")
            answer = Validate.validate_input_number_form(input())
            print(f'-->User: Câu trả lời của tôi là {answer}')
            if (answer == '0'):
                break
            elif (int(answer) < 0 or int(answer) > trieuchung_timduoc.__len__()):
                print('-->Chatbot: Vui lòng nhập 1 số trong phạm vi ở trên!')
                continue
            else:
                list_symptom_of_person.append(trieuchung_timduoc[int(answer)-1])
                print(f'-->Chatbot: Danh sách mã các triệu chứng thu được:')
                print([i['idtrieuchung'] for i in list_symptom_of_person])
        else:
            print("-->Chatbot: Không tìm thấy triệu chứng bạn nhập! Vui lòng nhập lại!")
             
    return list_symptom_of_person
################################################################
# 3 phần suy diễn tiến
def forward_chaining(rule, fact, goal, file_name,person):
    fc = ForwardChaining(rule, fact, None, file_name)

    list_predicted_disease = [i for i in fc.facts if i[0] == "D"]
    print(
        f'-->Chatbot: Chúng tôi dự đoán vật nuôi của bạn có thể bị bệnh :', end=" ")
    for i in list_predicted_disease:
        temp = db.get_benh_by_id(i)
        print(temp['tenBenh'], end=', ')
    print()
    
    print(
        f'-->Chatbot: Trên đây là chuẩn đoán sơ bộ của chúng tôi. Tiếp theo, chúng tôi sẽ hỏi bạn một số câu hỏi để đưa ra kết quả chính xác.', end=" ")
    return list_predicted_disease
########################################################################
# 4 phần suy diễn lùi
def backward_chaining(luat_lui,list_symptom_of_person,list_predicted_disease,file_name ):
    rule=luat_lui
    fact_real=list_symptom_of_person_id
    benh=0
    for goal in list_predicted_disease:
        disease=db.get_benh_by_id(goal) #Chứa thông tin của bệnh có id == goal
        print(f"Chúng tôi đã có các triệu chứng ban đầu và có thể vật nuôi của bạn mắc bệnh {disease['tenBenh']}({goal}) , sau đây chúng tôi muốn hỏi bạn một vài câu hỏi để củng cố suy đoán của chúng tôi")
        #lấy tất cả triệu chứng trong bệnh (xuất hiện trong luật suy diễn lùi)
        all_s_in_D=get_all_rules_in_d(goal,rule)
        #Trừ triệu chứng đã được chứng minh
        all_s_in_D=sorted(set(all_s_in_D)-set(fact_real))

        d=searchindexrule(rule,goal)
        # kết luận trong trường hợp các luật trước đã suy ra được luôn
        b=BackwardChaining(rule,fact_real,goal,file_name) 
        
        if b.result1==True:# đoạn đầu
            print("Vật nuôi của bạn mắc bệnh {}- {}và chúng tôi sẽ gửi thêm thông tin về bệnh này cho bạn".format(goal,disease['tenBenh']))
            print(f"Lời khuyên")
            disease['loikhuyen']=disease['loikhuyen'].replace("/n","\n")
            print(f"{disease['loikhuyen']}")
            print("Cám ơn bạn đã sử dụng chat bot của chúng tôi")
            return goal,fact_real
        #Hỏi thêm để suy diễn lùi
        while(len(all_s_in_D)>0):
            #lấy triệu chứng chưa được chứng minh
            s=db.get_trieuchung_by_id(all_s_in_D[0])
            question=f"Bạn có thấy có triệu chứng {s['noidung']}({all_s_in_D[0]}) không?"
            print(question)
            answer = Validate.validate_binary_answer(input())
            
            print(f"answer: {answer}")
            
            if answer== True : #triệu chứng được chứng minh
                #Thêm vào fact rồi thực hiện suy diễn lùi
                fact_real.append(all_s_in_D[0]) 
                b=BackwardChaining(rule,fact_real,goal,file_name)

                list_no_result,lsD=get_s_in_d(all_s_in_D[0],goal,rule,d,1)
                d=sorted(set(d)-set(lsD))
                all_s_in_D=sorted(set(list_no_result)-set(fact_real))
                if b.result1==True:
                    benh=1
                    break
            if answer==False :
                list_no_result,lsD=get_s_in_d(all_s_in_D[0],goal,rule,d,0) #S01 S02 S03 S04 S05
                d=sorted(set(d)-set(lsD))
                all_s_in_D=sorted(set(list_no_result)-set(fact_real))
            if len(d)==0: 
                print(f"Có vẻ như vật nuôi của bạn không mắc bệnh {goal}-{disease['tenBenh']}")
                break
        if benh==1:
            print("Vật nuôi của bạn mắc bệnh {}- {}và chúng tôi sẽ gửi thêm thông tin về bệnh này cho bạn".format(goal,disease['tenBenh']))
            print(f"Lời khuyên")
            disease['loikhuyen']=disease['loikhuyen'].replace("/n","\n")
            print(f"{disease['loikhuyen']}")
            print("Cám ơn bạn đã sử dụng chat bot của chúng tôi")
            
            return goal,fact_real
    if benh==0:
        print(f"Vật nuôi của bạn không bị bệnh nào cả")
        return None, fact_real
#########################################################################
#5 hiển thị kết quả chuẩn đoán
def hienthi_ketluan(list_symptom_of_person_id,id_benh):

    benh=db.get_benh_by_id(id_benh)
    # print(benh)
    nguyen_nhan=benh['nguyennhan']
    loi_khuyen=benh['loikhuyen']
    print(f"""
        ***Chúng tôi nhận được các triệu chứng bạn đã gặp phải là : 
        {[db.get_trieuchung_by_id(i)["noidung"] for i in list_symptom_of_person_id]}
        ***Chúng tôi dự đoán bạn bị bệnh : {benh['tenBenh']}
        ***Nguyên nhân gây ra bệnh này là: 
        {nguyen_nhan}
        ***Lời khuyên của chúng tôi dành cho bạn:
        {loi_khuyen}
        ***Cám ơn vì đã dùng Chatbot
    """)
    
list_symptom_of_person = []  # list các đối tượng triệu chứng
list_symptom_of_person = cauhoi1()
list_symptom_of_person = cauhoi2(list_symptom_of_person)
print([i['idtrieuchung'] for i in list_symptom_of_person])
list_symptom_of_person_id = [i['idtrieuchung'] for i in list_symptom_of_person]
list_symptom_of_person_id = list(set(list_symptom_of_person_id))
list_symptom_of_person_id.sort()
list_predicted_disease = forward_chaining(luat_tien, list_symptom_of_person_id, None, 'ex')
print(list_predicted_disease)
if len(list_predicted_disease)==0 :
    print("Vật nuôi của bạn không có dấu hiệu cuả bệnh nào cả.Cám ơn bạn đã sử dụng ChatBot")
    sys.exit()
disease,list_symptom_of_person_id= backward_chaining(luat_lui,list_symptom_of_person_id,list_predicted_disease,"ex")

hienthi_ketluan(list_symptom_of_person_id,disease)
