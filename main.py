import telegram
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler
from pathlib import Path
import re
from collections import Counter
from Chatbot.config import api_key, chat_id
from pymongo import MongoClient
from DataBase.config import MONGO_URL, MONGO_DB_NAME
from Chatbot.get_time import get_weekday, get_now_time, get_now_date, get_next_day, now, get_n_day_weekday
from datetime import datetime, timedelta

BASE_DIR = Path(__file__).resolve().parent
# print('base dir is..', BASE_DIR)

client = MongoClient(MONGO_URL)
db = client['DS']
bot = telegram.Bot(token=api_key)

info_message = '''
공강이 에게 빈 강의실 정보를 물어봐보세요. 

- 지금 사용할 수 있는 빈 강의실을 알고 싶다면 : 지금 + <사용할 강의실 이름>
- 나중에 사용할 수 있는 빈 강의실을 알고 싶다면 : 사용할 날짜(형식: Month/Day) + <사용할 강의실 이름>
example1) 지금 차235 비었어?
example2) 10/5 차320 가능한 시간대 알려줘
'''


def start(update, context):
    bot.send_message(chat_id, text='안녕하세요! 저는 덕성여대 빈 강의실 정보를 알려주는 송강이 아닌 공강이 챗봇입니다.')  # 사용자가 채팅방에 입장시 인사말
    bot.send_message(chat_id=update.effective_chat_id, text=info_message)


# updater
updater = Updater(token=api_key, use_context=True)
dispatcher = updater.dispatcher
# 주기적으로 텔레그램 서버에 접속 해 chatbot 으로부터 새로운 메시지가 존재하면 받아오는 명령어
updater.start_polling()


def handler(update, context):
    user_text = update.message.text  # 사용자가 보낸 메세지를 user_text 변수에 저장합니다.
    # chat_id= update.message.chat_id

    if '뭐해' in user_text:
        bot.send_message(chat_id, text='자연어 처리에 대해 공부중이에요.')  # 답장보내기
    elif '지금' in user_text:  # 지금(v)차235(v)비었어? # 띄어쓰기 필수
        # print(get_now_time())
        place = user_text.split()[1]
        if db.inform.find_one({'강의실': place}):
            class_time = db.inform.find_one({'강의실': place})['강의시간']
            new_class_time = class_time.replace("'", '').replace("[", '').replace("]", '').replace(" ", '')
            # print(new_class_time)
            class_list = new_class_time.split(',')  # 리스트 자료형

            test = []
            alpha_list = []  # 강의 교시인 알파벳 추출
            lec_time_list = []

            if get_weekday() in new_class_time:  # 문자열
                # if '화' in new_class_time:             # 주말이면 db에 없는 데이터라 임의로 요일 지정
                # 리스트의 인덱스를 찾은 후 알파벳을 찾아 디비의 정보와 비교
                for i in range(len(class_list)):
                    if get_weekday() in class_list[i]:
                        test.append(class_list[i])
                for i in test:
                    if len(i) == 4:
                        for j in range(len(i)):
                            if j == 1:
                                alpha_list.append(i[j])
                            elif j == 3:
                                alpha_list.append(i[j])
                    elif len(i) == 2:
                        for l in range(len(i)):
                            if l == 1:
                                alpha_list.append(i[l])

                for a in alpha_list:
                    lec_time = db.inform.find_one({'교시': a})['시간']
                    lec_time_list.append(lec_time)
                # for s in lec_time_list:
                #     print('s is', s)
                bot.send_message(chat_id,
                                 text=f"입력 하신 {place}의 강의 시간은 {lec_time_list}입니다. 이를 제외한 시간은 빈 강의실로 사용 가능 합니다.")
    elif '10' in user_text:  # 10/5 차320 쓸 수 있어?
        # 1003 날짜별 발화처리-> 시간대별은 1004에 하기로! 근데 코드는 위에 로직과 비슷할듯(2시-> db의 어느 교시에 해당하는지 비교)
        input_date = user_text.split()[0]

        date_list = input_date.split('/')
        mon = int(date_list[0])
        day = int(date_list[1])

        test = datetime(2022, mon, day)
        # print(type(test))
        n_day = get_next_day(test)
        # print('n_day is', type(n_day))

        place = user_text.split()[1]

        if db.inform.find_one({'강의실': place}):
            class_time = db.inform.find_one({'강의실': place})['강의시간']
            new_class_time = class_time.replace("'", '').replace("[", '').replace("]", '').replace(" ", '')
            # print(new_class_time)
            class_list = new_class_time.split(',')  # 리스트 자료형

            test = []
            alpha_list = []
            lec_time_list = []
            if get_n_day_weekday(n_day) in new_class_time:
                # 리스트의 인덱스를 찾은 후 알파벳을 찾아 디비의 정보와 비교
                for i in range(len(class_list)):
                    if get_n_day_weekday(n_day) in class_list[i]:
                        test.append(class_list[i])
                for i in test:
                    if len(i) == 4:
                        for j in range(len(i)):
                            if j == 1:
                                alpha_list.append(i[j])
                            elif j == 3:
                                alpha_list.append(i[j])
                    elif len(i) == 2:
                        for l in range(len(i)):
                            if l == 1:
                                alpha_list.append(i[l])

                for a in alpha_list:
                    lec_time = db.inform.find_one({'교시': a})['시간']
                    lec_time_list.append(lec_time)
                # for s in lec_time_list:
                #     print('s is', s)
                bot.send_message(chat_id,
                                 text=f"입력 하신 {n_day} 의 {place} 강의 시간은 {lec_time_list} 입니다. 이를 제외한 시간은 빈 강의실로 사용 가능 합니다.")

    elif '누구야' in user_text:
        bot.send_message(chat_id, text='저는 덕성여대 빈 강의실 정보를 알려주는 송강이 아닌 공강이 챗봇입니다 😄')
    elif '누가' in user_text:
        bot.send_message(chat_id, text='저는 소프트웨어 캡스톤 디자인의 유니콘팀에 의해 만들어졌어요~ 🤖')
    else:
        bot.send_message(chat_id, text='아직 수집되지 않은 정보에요.')


start_handler = CommandHandler('start', start)
echo_handler = MessageHandler(Filters.text,
                              handler)  # chatbot에게  메세지를 전송하면,updater를 통해 필터링된 text가 handler로 전달이 된다. -> 가장 중요하고, 계속해서 수정할 부분

dispatcher.add_handler(start_handler)
dispatcher.add_handler(echo_handler)
