import requests
import base64
import re
import concurrent.futures
from bs4 import BeautifulSoup
from urllib3.exceptions import ReadTimeoutError


def get_proxies(urls):
    proxies = []
    for url in urls:
        r = requests.get(url)
        soup = BeautifulSoup(r.content, "html.parser")
        if url == "https://free-proxy-list.net/":
            table = soup.find("tbody")
            for row in table:
                if row.find_all("td")[4].text == 'elite proxy':
                    proxy = ":".join(
                        [row.find_all("td")[0].text, row.find_all("td")[1].text]
                    )
                    proxies.append(proxy)
                else:
                    pass

        elif url == "https://advanced.name/freeproxy":
            table = soup.find("tbody")
            rows = table.find_all("tr")
            for row in rows:
                if 'ELITE' in row.find_all('td')[3].text:
                    proxy = ":".join(
                        [
                            base64.b64decode(row.find_all("td")[1]["data-ip"]).decode(
                                "utf-8"
                            ),
                            base64.b64decode(row.find_all("td")[2]["data-port"]).decode(
                                "utf-8"
                            ),
                        ]
                    )
                    proxies.append(proxy)
                else:
                    pass

        elif url == "http://free-proxy.cz/en/":
            table = soup.find("tbody")
            for row in table.find_all("tr"):
                try:
                    if row.find_all('td')[6].text == 'High anonymity':
                        codejs = row.find_all("script")[0].text
                        encode = re.findall(r'"(.*?)"', codejs)[0]
                        if encode is not None:
                            decode = base64.b64decode(encode).decode("utf-8")
                            proxy = ":".join([decode, row.find_all("td")[1].text])
                            proxies.append(proxy)
                    else:
                        pass
                except IndexError:
                    continue

        elif url == "https://www.freeproxy.world/":
            table = soup.find("tbody")
            for row in table.find_all("tr"):
                try:
                    if row.find_all('td')[6].text == 'High':
                        proxy = ":".join(
                            [
                                row.find_all("td", class_="show-ip-div")[0].text.strip(),
                                row.find_all("td")[1].text.strip(),
                            ]
                        )
                        proxies.append(proxy)
                    else:
                        pass
                except IndexError:
                    continue

    print(proxies, len(proxies))
    return proxies


def check_proxy(proxy):
    headers = {
        "User-Agent": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; Googlebot/2.1; +http://www.google.com/bot.html) Chrome/W.X.Y.Z Safari/537.36"
    }
    try:
        r = requests.get(
            "https://www.portalinmobiliario.com/",
            headers=headers,
            proxies={"http": proxy, "https": proxy},
            timeout=2,
        )
        if r.status_code == 200:
            return proxy
        else:
            return
    except requests.ConnectionError:
        pass
    except requests.ReadTimeout:
        pass
    except ReadTimeoutError:
        pass
    except TimeoutError:
        pass


def main():
    url = [
        "https://free-proxy-list.net/",
        "https://advanced.name/freeproxy",
        #"http://free-proxy.cz/en/", Siempre entrega la misma lista
        "https://www.freeproxy.world/"
    ]  
    proxies = get_proxies(url)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        proxy = executor.map(check_proxy, proxies)

    proxy_list = list(proxy)
    proxy_work = []
    for p in proxy_list:
        if p is not None:
            format_p = ''.join(['http://', p])
            proxy_work.append(format_p)
    return proxy_work


proxies = main()
nombre_archivo = 'proxies.text'
with open(nombre_archivo, 'w') as archivo:
    for proxy in proxies:
        archivo.write(proxy + "\n")

