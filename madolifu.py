import requests
import sys
from help import help
from os import makedirs
from os.path import isdir, isfile
from bs4 import BeautifulSoup
from cryptography.fernet import Fernet

ext = (".zip", ".rar", ".txt", ".pdf", ".docx", ".mobi", ".epub", ".cb7", ".cba", ".cbr", ".cbt", ".cbz", ".doc")
avoid = ("Read", "Report", "/")
dicLinks = {}
linkNames = []
finalLinks = []
user = ''
passw = ''


def loginfo_enc(user, passw):
    key = Fernet.generate_key()
    file = open("key.key", "wb")
    file.write(key)
    file.close()

    f = Fernet(key)
    enc_str = user + "/" + passw
    enc_str = f.encrypt(enc_str.encode())

    file = open("logInfo.py", "wb")
    file.write(enc_str)
    file.close()


def get_session():
    if isfile("key.key") and isfile("logInfo.py"):
        file = open("key.key", "rb")
        key = file.readline()
        file.close()

        f = Fernet(key)
        file = open("logInfo.py", "rb")
        dec_str = f.decrypt(file.readline())
        file.close()
        dec_str = dec_str.decode("UTF-8")
        dec_str = dec_str.split("/")
        s = requests.Session()
        s.auth = (dec_str[0], dec_str[1])
        return s


def link_scrapper(url, session):
    source = session.get(url.strip())
    if source and source.status_code == 200:
        soup = BeautifulSoup(source.content, 'lxml')
        title = soup.find("span", class_="title")
        name = title.text
        table = soup.find("div", class_="table-outer")
        tbody = table.find('tbody')
        links = tbody.find_all('a')
        for link in links:
            linkH = "https://manga.madokami.al" + link.get('href')
            linkT = link.text
            if not linkT.endswith(avoid) and linkH.endswith(ext):
                dicLinks[linkT] = linkH

        return dicLinks, name.strip()
    else:
        print("ERROR. The website can't be reached. Here are some possible solutions: ")
        print("-Re-enter your login info.")
        print("-Check your internet connection.")
        print("-Try to enter to the site through a browser. Maybe the site is down.")


def selection(sel):
    if sel == "all":
        selNumb = list(range(len(linkNames)))
    else:
        sel = sel.split(", ")
        selNumb = []
        for i in sel:
            if i.isalnum():
                selNumb.append(int(i) - 1)
            elif "-" in i:
                i = i.split("-")
                tempList = list(range(int(i[0]) - 1, int(i[1])))
                selNumb = selNumb + tempList

    finalLinks = []
    for i in selNumb:
        finalLinks.append(linkNames[i])

    return finalLinks


def download_path(path):
    if isdir(path):
        file = open("config.ini", "w")
        file.write(f"Download Path={path}\\")
        file.close()
    else:
        print("The folder can't be accessed or doesn't exist. Please try again.")


def get_path():
    while True:
        if isfile("config.ini"):
            file = open("config.ini", "r")
            path = file.readline()
            path = path.split("=")
            return path[-1]
        else:
            download_path("Enter download folder: ")


def download_folder(path):
    if not isdir(path):
        makedirs(path)


def downloader():
    path_folder = get_path().strip() + name + "\\"
    download_folder(path_folder)
    for link in finalLinks:
        path = path_folder + link
        download(dicLinks[link], path, link)
    return


def download(url, filename, name):
    print(f"Downloading {name}")
    with open(filename, 'wb') as f:
        response = session.get(url, stream=True)
        total = response.headers.get('content-length')

        if total is None:
            f.write(response.content)
        else:
            downloaded = 0
            total = int(total)
            for data in response.iter_content(chunk_size=max(int(total/1000), 1024*1024)):
                downloaded += len(data)
                f.write(data)
                done = int(50*downloaded/total)
                sys.stdout.write('\r|{}{}| {}%'.format('█' * done, '.' * (50-done), done*2))
                sys.stdout.flush()
    sys.stdout.write('\n')


while not isfile("logInfo.py") or not isfile("key.key"):
    loginfo_enc(input("Enter user: "), input("Enter password: "))

while not isfile("config.ini"):
    download_path(input("Enter download folder: "))

session = get_session()
print("Welcome! Enter 'help' if you have any problem.")
while True:
    command = str(input(">>")).lower().strip()
    if command == "download":
        dicLinks, name = link_scrapper(input("Enter an url: "), session)
        linkNames = list(dicLinks.keys())
        linkNames.sort(key=str.lower)
        count = 0
        for i in linkNames:
            count += 1
            print(f"[{count}] {i}")

        print("\nIndividual selection: '2, 3, 4'. Bulk selection: '2-4, 9-10'. Combination: '2, 4-7, 9, 11, 13-15'")
        print("To download every file: 'all'")
        finalLinks = selection(input("Select what you want to download: "))
        downloader()
        dicLinks = {}
        linkNames = []
        finalLinks = []
        print("Done. Remember to enter 'help' for more information.")

    elif command == "change password":
        loginfo_enc(input("Enter user: "), input("Enter password: "))

    elif command == "change download folder":
        download_path(input("Enter download folder: "))

    elif command == "help":
        help("default")

    elif command == "quit":
        break

    elif command == "mr egg":
        help("mr egg")

    elif command == "discworld":
        help("discworld")

    else:
        print("Not a valid command")



















