import time
import arrow
import json
from requests import get, post
import matplotlib.pyplot as plt

from Config import TIMEZONE, TelegramAPI, PASSWORD, STATUS_UPDATE_TIME, TELEGRAM_CHAT_ID, BackendAPI, STATUS_RESET_TIME
from DataBase import DataBase

db = DataBase()

INDEXER_NAMES = ["Username", "Studio", "Project", "Short Username", "Forum", "Cloud Game"]


def get_status():
    try:
        total_data = json.loads(open('count.json', 'r').read())
        working_at = json.loads(open('status.json', 'r').read())
        upserts_today_username = int(open('upserts_count/username_upserts.txt', 'r').read())
        upserts_today_studio = int(open('upserts_count/studio_upserts.txt', 'r').read())
        upserts_today_project = int(open('upserts_count/project_upserts.txt', 'r').read())
        upserts_today_short_usernames = int(open('upserts_count/short_username_upserts.txt', 'r').read())
        upserts_today_forum = int(open('upserts_count/forum_upserts.txt', 'r').read())
        upserts_today_cloud = int(open('upserts_count/cloud_game_upserts.txt', 'r').read())
        data = {
            "Error": False,
            "ServerStatus": "Online",
            "TotalUsersData": total_data,
            "UpsertsToday": {"UsernameIndexer": upserts_today_username, "StudioIndexer": upserts_today_studio,
                             "ProjectIndexer": upserts_today_project,
                             "ShortUsernameIndexer": upserts_today_short_usernames, "ForumIndexer": upserts_today_forum,
                             "CloudGameIndexer": upserts_today_cloud},
            "Indexers": [{
                "Username": working_at["Username"]
            }, {
                "Project": working_at["Project"]
            }, {
                "Studio": working_at["Studio"]
            }, {
                "ShortUsername": working_at["ShortUsername"]
            }, {
                "Forum": working_at["Forum"]
            }, {
                "CloudGame": working_at["CloudGame"]
            }]
        }
    except:
        data = {"Error": True, "Info": "An error occurred. Please try again later after 5-10 minutes"}
    return data


def send_telegram_message(content):
    return get(
        f"{TelegramAPI}sendMessage",
        params={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": content,
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
        },
    )


def send_telegram_photo(file_name):
    return post(
        f"{TelegramAPI}sendPhoto",
        params={"chat_id": TELEGRAM_CHAT_ID},
        files={"photo": open(file_name, "rb")}
    )


def set_status_thread():
    while True:
        try:
            get(f"{BackendAPI}set_status?password={PASSWORD}&data={json.dumps(get_status())}")
            time.sleep(STATUS_UPDATE_TIME)
        except Exception as E:
            print("SET STATUS:", E)


def create_status_history(date, data):
    return get(f"{BackendAPI}set_history?password={PASSWORD}&date={date}&data={json.dumps(data)}")

def calculate_growth(ndate, nd):
    new_date = ndate
    old_date = new_date.shift(days=-2).strftime("%d/%m/%Y")
    try:
        old_data = get(f"{BackendAPI}get_history?password={PASSWORD}&date={old_date}").json()
        u = sum(list(nd['UpsertsToday'].values())) - sum(list(old_data['UpsertsToday'].values()))
        ug = f"{u:,}"
        if u > 0:
            ug = "+" + ug
        upserts_growth = ug
        u = nd['TotalUsersData']['Count'] - old_data['TotalUsersData']['Count']
        gc = f"{u:,}"
        if u != 0:
            gc = f"+{u:,}"
        count_growth = gc
        return [True, upserts_growth, count_growth]
    except Exception as E:
        print("DAILY GROWTH:", E)
        return [False, 0, 0]


def updates_thread():
    while True:
        current_time = arrow.now(TIMEZONE)
        current_hour = current_time.strftime("%H")
        current_minute = current_time.strftime("%M")
        current_second = current_time.strftime("%S")
        if f"{current_minute}:{current_second}" == "00:00":
            try:
                data = get_status()
                total_data = data['TotalUsersData']
                d = arrow.get(total_data['UpdateTimestamp'], tzinfo=TIMEZONE)
                s = ""
                for i in range(0, len(INDEXER_NAMES)):
                    s += f"<b>{INDEXER_NAMES[i]}:</b> <pre>{list(data['UpsertsToday'].values())[i]:,}</pre>\n"
                message = f"""Hourly <b>({current_time.strftime('%d/%m/%Y %H:%M')})</b> status update for <b>SUI API</b>:\n\n<b>Total Users Count:</b> <pre>{total_data['Count']:,}</pre> (last updated {d.humanize()})\n<b>Total Upserts Count:</b> <pre>{sum(list(data['UpsertsToday'].values())):,}</pre>\n\n<b>Upserts Today:</b>\n{s}"""
                send_telegram_message(message)
            except Exception as E:
                print("UPDATES THREAD 1:", E)
                message = f"""<b>An error occurred while sending hourly update:</b> <pre>{E}</pre>"""
                send_telegram_message(message)
        if f"{current_hour}:{current_minute}:{current_second}" == STATUS_RESET_TIME + ":00":
            try:
                db.connect_server()
                db.update_documents_count()
                data = get_status()
                total_data = data['TotalUsersData']
                d = arrow.get(total_data['UpdateTimestamp'], tzinfo=TIMEZONE)
                c = create_daily_chart(data, current_time.shift(days=-1).strftime('%d/%m/%Y'))
                growth = calculate_growth(current_time, data)
                if growth[0] == False:
                    message = f"""<b>An error occurred while calculating the daily growth!</b>\n\nMaybe the data was insufficient..."""
                    send_telegram_message(message)
                message = f"""Daily status update for <b>SUI API</b> Indexers on <b>{current_time.shift(days=-1).strftime('%d/%m/%Y')}</b>:\n\n<b>Total Users Count:</b> <pre>{total_data['Count']:,}</pre> (last updated {d.humanize()})\n<b>Total Upserts Count:</b> <pre>{sum(list(data['UpsertsToday'].values())):,}</pre>\n\n<b>Upserts Growth:</b> <pre>{growth[1]}</pre>\n<b>Users Count Growth:</b> <pre>{growth[2]}</pre>"""
                send_telegram_message(message)
                if c[0]:
                    send_telegram_photo("charts/bar.png")
                if c[1]:
                    send_telegram_photo("charts/pie.png")
                create_status_history(current_time.shift(days=-1).strftime('%d/%m/%Y'), get_status())
                files = ["username", "studio", "project", "short_username", "forum", "cloud_game"]
                for file in files:
                    with open(f"upserts_count/{file}_upserts.txt", "w") as f:
                        f.write("0")
                get(f"{BackendAPI}set_status?password={PASSWORD}&data={json.dumps(get_status())}")
            except Exception as E:
                print("UPDATES THREAD 2:", E)
                message = f"""<b>An error occurred while resetting daily status:</b> <pre>{E}</pre>"""
                send_telegram_message(message)
        time.sleep(1)

def create_daily_chart(d, date):
    data = d["UpsertsToday"]
    keys = INDEXER_NAMES
    values = list(data.values())

    # Make Bar Chart
    try:
        plt.bar(keys, values, width=0.5)
        plt.xlabel("Indexers")
        plt.ylabel("No. of upserts")
        plt.title(f"SUI API: {date} - No. of upserts done by the indexers")
        plt.savefig("charts/bar.png", bbox_inches="tight")
        plt.close()
        bar_success = True
    except:
        bar_success = False

    # Make Pie Chart
    try:
        plt.pie(values, labels=keys)
        plt.savefig("charts/pie.png", bbox_inches="tight")
        plt.close()
        pie_success = True
    except:
        pie_success = False
    return [bar_success, pie_success]
