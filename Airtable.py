"""Airtable API Class"""
import os
import time
import collections
import requests
import json
from functools import reduce

Table = collections.namedtuple("Table", ["name", "status"])
Users = collections.namedtuple("User", ("id", "template"))


class Airtable:
    """TODO: remove once open-sourced"""

    URL = "https://api.airtable.com/v0/app9hPJHfEumurqCQ/"
    TABLE_URL = ""
    KEY = os.environ["AIRTABLE_API_KEY"]
    TABLES = []
    RECORDS = []
    TEMPLATES = {}
    PLACEHOLDERS = {}
    USER_ID = ""
    TEMPLATE_STRUCT = {}
    USERS = []

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
        if len(self.TEMPLATES) != 0:
            if title_id in self.TEMPLATES:
                template = self.TEMPLATES[title_id]
                return (template["title"], template["placeholders"])
            else:
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
                        self.TEMPLATES[title_id] = {
                            "title": title,
                            "placeholders": associated_placeholders,
                        }
                        return (title, associated_placeholders)

                    sess.close()
        else:
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
                    self.TEMPLATES[title_id] = {
                        "title": title,
                        "placeholders": associated_placeholders,
                    }
                    return (title, associated_placeholders)

                sess.close()

    def get_placeholder_info(self, placeholder_id):
        if len(self.PLACEHOLDERS) != 0:
            if placeholder_id in self.PLACEHOLDERS:
                placeholder = self.PLACEHOLDERS[placeholder_id]
                return placeholder
            else:
                self.set_table("Templates")
                with self._session() as sess:
                    sess.headers.update(self._auth)
                    resp = sess.get(f"{self.TABLE_URL}/{placeholder_id}")

                    if resp.ok:
                        data = resp.json()
                        placeholder = data.get("fields").get("Template Name")
                        self.PLACEHOLDERS[placeholder_id] = placeholder
                        return placeholder

                    sess.close()
        else:
            self.set_table("Templates")
            with self._session() as sess:
                sess.headers.update(self._auth)
                resp = sess.get(f"{self.TABLE_URL}/{placeholder_id}")

                if resp.ok:
                    data = resp.json()
                    placeholder = data.get("fields").get("Template Name")
                    self.PLACEHOLDERS[placeholder_id] = placeholder
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
        time_start = time.time()
        titles = []
        placeholders = []
        associated_placeholders = []
        TEMPLATE_STRUCT = {}

        if self.RECORDS is []:
            pass
        else:
            for record in self.RECORDS:
                if not record.get("fields"):
                    print(record)
                    continue
                user_id = record.get("fields").get("User ID")
                placeholders = record.get("fields").get("Templates")
                titles = record.get("fields").get("Titles")

                for title_id in titles:
                    (title, linked_placeholders) = self.get_title_info(title_id)
                    TEMPLATE_STRUCT[title] = []
                    for placeholder_id in linked_placeholders:
                        if placeholder_id in placeholders:
                            placeholder = self.get_placeholder_info(
                                placeholder_id
                            )
                            TEMPLATE_STRUCT[title].append(placeholder)
                self.USERS.append(Users(user_id, TEMPLATE_STRUCT))
                TEMPLATE_STRUCT = {}
        print(time_start - time.time())

    def show_user_template(self, user_id):
        """Duplicate User IDs are not allowed in our system"""
        return list(filter((lambda user: user.id == user_id), self.USERS))[0]

    def write_to_file(self):
        """merely dumping contents to a json file"""
        for user in self.USERS:
            with open(f"{user.id}.json", "w+") as json_file:
                json.dump(user.template, json_file)
                json_file.close()
