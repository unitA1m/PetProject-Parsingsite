import json
import requests
import fake_useragent
from bs4 import BeautifulSoup as bs
import datetime

user = fake_useragent.UserAgent().random
header = {
    'user-agent': user
}
today = datetime.datetime.now().strftime("%Y-%m-%d")

link = "https://guap.ru/rasp/"
data = [93, 330,14]
result = []
for i in data:
    responce = requests.get(f'{link}/?g={i}', headers=header).text
    soup = bs(responce, 'lxml')

    current_day = None
    current_lesson = None

    for element in soup.find("div", class_="result").children:
        if element.name == "h3":
            current_day = element.text
        elif element.name == "h4":
            parts = element.text.split(" (")
            current_lesson = {
                "lesson_number": parts[0],
                "time": parts[1][:-1]
            }
        elif element.name == "div" and element.get("class") == ["study"]:
            b_element = element.find('b')
            number= element.findAll('b')
            next_text = element.text
            week=number
            teacher_element = element.find("a", href=lambda href: href and "?p=" in href)
            teacher_name = teacher_element.text if teacher_element else ""

            # Определяем тип занятия
            lesson_type = ""

            if len(number) == 1:
                if b_element:
                    if "ЛР" in b_element.text:
                        lesson_type = "ЛР"
                    elif "ПР" in b_element.text:
                        lesson_type = "ПР"
                    elif "Л" in b_element.text:
                        lesson_type = "Л"
                    elif "КП" in b_element.text:
                        lesson_type = "КП"
                    elif "КР" in b_element.text:
                        lesson_type = "КР"
            else:
                number = element.findAll('b')[1].text
                if number:
                    if "ЛР" in number:
                        lesson_type = "ЛР"
                    elif "ПР" in number:
                        lesson_type = "ПР"
                    elif "Л" in number:
                        lesson_type = "Л"
                    elif "КП" in number:
                        lesson_type = "КП"
                    elif "КР" in number:
                        lesson_type = "КР"

            # Определяем название предмета
            lesson_name = ""
            if next_text:
                parts = next_text.split(" - ", 1)
                lesson_name = next_text.strip().split(" –")[1]

            week_type = ""
            if len(week) == 1:
                week_type = "каждую неделю"
            else:
                week = element.findAll('b')[0].text
                if "▲" in week:
                    week_type = "верхняя (нечетная)"
                elif "▼" in week:
                    week_type = "нижняя (четная)"


            lesson_info = {
                "day": current_day,
                "lesson_number": current_lesson["lesson_number"],
                "time": current_lesson["time"],
                "week_type":week_type,
                "lesson_type": lesson_type,
                "lesson_name": lesson_name,
                "location": element.find("em").text.strip(" –"),
                "teacher": teacher_name,
                "groups": [group.text for group in element.find_all("a", href=lambda href: href and "?g=" in href)]
            }
            result.append(lesson_info)
    print(f"Группа записана в файл!")


with open(f"pair{today}.json", mode="w" , encoding="utf-8") as file:
    json.dump(result, file, ensure_ascii=False, indent=4)

print(f"Json- файл 'pair{today}.json' успешно создан!")