import codecs
import subprocess

import sadisplay

from dhos_users_api.models import product, user

desc = sadisplay.describe([user.User, product.Product])
with codecs.open("docs/schema.plantuml", "w", encoding="utf-8") as f:
    f.write(sadisplay.plantuml(desc).rstrip() + "\n")

with codecs.open("docs/schema.dot", "w", encoding="utf-8") as f:
    f.write(sadisplay.dot(desc).rstrip() + "\n")

my_cmd = ["dot", "-Tpng", "docs/schema.dot"]
with open("docs/schema.png", "w") as outfile:
    subprocess.run(my_cmd, stdout=outfile)
