import json
import sys
import requests as requests
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import *


class FetchTabException(RuntimeError):
    pass


class ForbiddenFTException(FetchTabException):
    pass


class ResourceNotFoundFTException(FetchTabException):
    pass


class RateLimitExceededFTException(FetchTabException):
    pass


class HTTPErrorFTException(FetchTabException):
    pass


def fetch_tab(league, realm, account_name, poe_sessid, tab_index):
    """Fetch a single tab from GGG's API"""
    url = 'https://www.pathofexile.com/character-window/get-stash-items'
    data = {
        'accountName': account_name,
        'league': league,
        'realm': realm,
        'tabIndex': tab_index,
        'tabs': 0,
    }
    cookies = {
        'POESESSID': poe_sessid,
    }
    headers = {
        'user-agent': 'poe-stash-helper/0.0.1 trying to make something so I can find my blighted maps'
    }

    r = requests.post(url, data=data, cookies=cookies, headers=headers)
    if not r.ok:
        error_text = f'Got HTTP status {r.status_code}: {r.reason}'
        if r.status_code == 404:
            raise ResourceNotFoundFTException(error_text)
        raise HTTPErrorFTException(error_text)

    response = r.text
    parsed = json.loads(response)
    if 'error' in parsed:
        if parsed['error']['code'] == 6:
            raise ForbiddenFTException(
                f'Cannot access stash. Is your account_name/poe_sessid correct? Raw response: {response}')
        elif parsed['error']['code'] == 3:
            raise RateLimitExceededFTException(f'Raw response: {response}')
        elif parsed['error']['code'] == 1:
            raise ResourceNotFoundFTException(f'Raw response: {response}')
        else:
            raise FetchTabException(f'Unknown error received. Raw response: {response}')

    return parsed


class StashTool(QDialog):
    def __init__(self, parent=None):
        super(StashTool, self).__init__(parent)

        self.setWindowTitle("Stashifier")
        self.setWindowIcon(QIcon('icon.png'))

        self.le = QLineEdit()
        self.le.setObjectName("league")
        self.le.setText("SSF Standard")

        self.re = QLineEdit()
        self.re.setObjectName("realm")
        self.re.setText("pc")

        self.an = QLineEdit()
        self.an.setObjectName("accountname")
        self.an.setText("accountname")

        self.ps = QLineEdit()
        self.ps.setObjectName("poesession")
        self.ps.setText("poe session")

        self.rs = QLineEdit()
        self.rs.setObjectName("result")
        self.rs.setText("result")

        self.mr = QPushButton()
        self.mr.setObjectName("makerequest")
        self.mr.setText("make request")
        self.mr.clicked.connect(self.button_click)

        layout = QFormLayout()
        layout.addWidget(self.le)
        layout.addWidget(self.re)
        layout.addWidget(self.an)
        layout.addWidget(self.ps)
        layout.addWidget(self.mr)
        layout.addWidget(self.rs)
        self.setLayout(layout)

        # makeRequestButton.clicked(fetch_tab(league.text(), realm.text(), accountname.text(), poe_sessid.text(), 0))

    def button_click(self):
        self.rs.setText(str(fetch_tab(self.le.text(), self.re.text(), self.an.text(), self.ps.text(), 0)))


def main():
    app = QApplication([])
    stashtool = StashTool()
    stashtool.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
