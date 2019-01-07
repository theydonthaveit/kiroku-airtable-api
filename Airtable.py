"""Airtable API Class"""
import os
import collections
import requests
import json

Table = collections.namedtuple("Table", ("name", "status"))


class Airtable:
    """TODO: remove once open-sourced"""

    URL = "https://api.airtable.com/v0/app9hPJHfEumurqCQ/"
    TABLE_URL = ""
    KEY = os.environ["AIRTABLE_API_KEY"]
    TABLES = []
    RECORDS = []
    TITLES = []
    TITLE_IDS = []
    PLACEHOLDERS = []
    PLACEHOLDERS_IDS = []
    USER_ID = ""
    JSON_STRUCT = {}

    def __init__(self, url=URL, key=KEY):
        self.url = url
        self.key = key
        self._auth = {"Authorization": f"Bearer {key}"}

    def __repr__(self):
        return f"Airtable({self.url}, {self.key})"

    def _session(self):
        return requests.Session()

    def add_table(self, table):
        return self.TABLES.append(Table(table, "active"))

    def set_table(self, table):
        self.TABLE_URL = f"{self.url}{table}"

    def active_table(self):
        return self.TABLE_URL

    def get_title_info(self, title_id):
        self.set_table("Titles")
        with self._session() as sess:
            sess.headers.update(self._auth)
            resp = sess.get(f"{self.TABLE_URL}/{title_id}")

            if resp.ok:
                data = resp.json()
                title = data.get("fields").get("Title")
                associated_placeholders = data.get("fields").get(
                    "Templates", []
                )
                return (title, associated_placeholders)

            sess.close()

    def get_placeholder_info(self, placeholder_id):
        self.set_table("Templates")
        with self._session() as sess:
            sess.headers.update(self._auth)
            resp = sess.get(f"{self.TABLE_URL}/{placeholder_id}")

            if resp.ok:
                data = resp.json()
                placeholder = data.get("fields").get("Template Name")
                return placeholder

            sess.close()

    def get_records(self):
        with self._session() as sess:
            sess.headers.update(self._auth)

            def _pagination(offset=None):
                resp = sess.get(
                    self.TABLE_URL
                    if offset is None
                    else f"{self.TABLE_URL}?offset={offset}"
                )

                if resp.ok:
                    data = resp.json()
                    records = data.get("records", [])
                    offset = data.get("offset")

                    if offset is not None:
                        self.RECORDS = [*self.RECORDS, *records]
                        return _pagination(offset)
                    else:
                        self.RECORDS = [*self.RECORDS, *records]
                        return
                else:
                    print(resp.status_code)

            _pagination()
            sess.close()

    def show_records(self):
        return self.RECORDS

    def build_user_template(self):
        titles = []
        placeholders = []
        associated_placeholders = []

        if self.RECORDS is []:
            pass
        else:
            for record in self.RECORDS:
                self.USER_ID = record.get("fields").get("User ID")
                titles = record.get("fields").get("Titles")
                placeholders = record.get("fields").get("Templates")

        for title_id in titles:
            # if title_id in self.TITLE_IDS:
            #     title = self.TITLES[title_id]
            (title, associated_placeholders) = self.get_title_info(title_id)
            self.JSON_STRUCT[title] = []

            for assc_placeholder_id in associated_placeholders:
                if assc_placeholder_id in placeholders:
                    placeholder = self.get_placeholder_info(assc_placeholder_id)
                    self.JSON_STRUCT[title].append(placeholder)

            # self.TITLE_IDS.append(title_id)
            # self.TITLES.append({title_id: title})

    def show_user_template(self):
        return self.JSON_STRUCT

    def write_to_file(self):
        with open(f"{self.USER_ID}.json", "w") as json_file:
            json.dump(self.JSON_STRUCT, json_file)
