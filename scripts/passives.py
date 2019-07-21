import requests
import json
import re

### NORMAL PASSIVES ###

url = "https://poedb.tw/us/json.php/Skilltree/keystone_list"
response = requests.get(url)
data = json.loads(response.content)

newData = {}

for passive in data["data"]:
    type = passive[0].encode('ascii','ignore').lower()
    mods = passive[2].encode('ascii','ignore')
    mods = mods.replace("</span>", "")
    mods = mods.replace("<span class='mod-value'>", "")
    modsList = mods.split("<br>")
    name = re.search("<a href='.*'>(.*?)<\/a>", passive[1]).group(1)

    actualModsList = []
    for m in modsList:
        if "<br/>" in m:
            m = m.split("<br/>")
            for m2 in m:
                actualModsList.append(m2)
        else:
            actualModsList.append(m)

    newData[name] = { "type": type, "passives": [ actualModsList ] }

### REGULAR PASSIVES ###

url = "https://pathofexile.gamepedia.com/index.php?title=List_of_basic_passive_skills"
response = requests.get(url)
html = ' '.join(response.content.split())

table = re.search(r'<table class="wikitable sortable">(.*?)<\/table>', html).group(1)
tbody = re.search(r'<tbody>(.*?)<\/tbody>', table).group(1)
trPattern = re.compile(r'<tr>(.*?)<\/tr>')

for m in re.finditer(trPattern, tbody):
    if not m.group(1):
        continue

    if "<th>" in m.group(1):
        continue

    row = m.group(1).encode('ascii','ignore')
    name = re.search(r'<a href=".*?" title=".*?">(.*?)</a>', row).group(1)
    passivesHtml = re.search(r'<td>(.*?)</td>', row).group(1)
    passiveAlt = passivesHtml.split("<hr />")
    passives = []
    for p in passiveAlt:
        passiveString = re.search(r'<span class="passive-line">(.*?) <span class="passive-hover">', p).group(1)
        result = passiveString.split("<br />")
        passives.append(result)

    newData[name] = { "type": "regular", "passives": passives }

with open("resource/passives.json", 'w') as f:
    json.dump(newData, f, indent=4, sort_keys=True)

### PASSIVE ADDITIONS ###

url = "https://poedb.tw/us/json.php/Legion/AlternatePassiveAdditions"
response = requests.get(url)
data = json.loads(response.content)

vaalData = []
newData = []

for passive in data["data"]:
    mod = re.search("<span class='item_magic'>(.*)<\/span>", passive[2]).group(1)
    mod = mod.replace("</span>", "")
    mod = mod.replace("<span class='mod-value'>", "").encode('ascii','ignore')
    mod = mod.replace("increased Effect of Curse", "increased Effect of your Curses")
    mod = mod.replace("increased Aura effect", "increased Effect of Non-Curse Auras from your Skills")
    mod = mod.replace("increased Aura Area of Effect", "increased Area of Effect of Aura Skills")
    mod = mod.replace("&ndash;", "-")

    if "increased Minion Damage" in mod:
        mod = mod.replace("increased Minion Damage", "increased Damage")
        mod = "Minions deal " + mod

    if "increased Minion Movement Speed" in mod:
        mod = mod.replace("increased Minion Movement Speed", "increased Movement Speed")
        mod = "Minions have " + mod

    if passive[0] == "Vaal":
        if not mod in vaalData:
            mod = mod.replace("1%", "(1-1)%")
            vaalData.append(mod)
    else:
        if not mod in newData:
            newData.append(mod)

with open("resource/passivesAdditions.json", 'w') as f:
    json.dump(newData, f, indent=4, sort_keys=True)

with open("resource/passivesVaalAdditions.json", 'w') as f:
    json.dump(vaalData, f, indent=4, sort_keys=True)

### ALTERNATE PASSIVES ###

url = "https://poedb.tw/us/json.php/Legion/AlternatePassiveSkills"
response = requests.get(url)
data = json.loads(response.content)

newData = {}

i = 0
for passive in data["data"]:
    name = passive[3].encode('ascii','ignore')
    type = passive[1].encode('ascii','ignore').lower()
    type = type.replace("<br>", "")
    mods = passive[4].encode('ascii','ignore')
    mods = mods.replace("</span>", "")
    mods = mods.replace("<span class='item_magic'>", "")
    mods = mods.replace("<span class='mod-value'>", "")
    modsList = mods.split("<br>")

    if type == "regular1regular2":
        type = "regular"

    modsList2 = []
    for m in modsList:
        if "<br/>" in m:
            m = m.split("<br/>")
            for m2 in m:
                modsList2.append(m2)
        else:
            modsList2.append(m)

    actualModsList = []
    for m in modsList2:
        if "<span class='item_description'>" in m:
            continue
        if "<span class='FlavourText'>" in m:
            continue
        if "<a class=" in m:
            continue
        m = m.replace("&ndash;", "-")
        m = m.replace("increased Effect of Curse", "increased Effect of your Curses")
        m = m.replace("increased Aura effect", "increased Effect of Non-Curse Auras from your Skills")
        m = m.replace("increased Aura Area of Effect", "increased Area of Effect of Aura Skills")
        m = m.replace("Supported Skills have ", "")
        m = m.replace("increased Spell Critical Strike Chance", "increased Critical Strike Chance for Spells")
        actualModsList.append(m)

    newData[name] = { "type": type, "passives": actualModsList }


with open("resource/passivesAlternatives.json", 'w') as f:
    json.dump(newData, f, indent=4, sort_keys=True)