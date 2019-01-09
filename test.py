from Airtable import Airtable

a = Airtable()
a.set_table("Users")
a.get_records()
a.build_user_template()
a.write_to_file()
