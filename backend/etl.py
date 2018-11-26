from glob import glob
import zipfile
import os
import os.path
import traceback
# import xml.etree.ElementTree as ET
# from xbrl_parser import xbrl_parse
from edinet_xbrl.edinet_xbrl_parser import EdinetXbrlParser
from bs4 import BeautifulSoup
import re

p = re.compile('<style type="text\/css">.*?<\/style>')
p2 = re.compile('<ix:header>[\s\S]*?<\/ix:header>')
p3 = re.compile('<\?xml.*?>')
p4 = re.compile('<html.*?>')
p5 = re.compile('<head>(.|\s)*?<\/head>')
p6 = re.compile('<ix:(header|nonNumeric).*?>')
p7 = re.compile('<\/ix:(header|nonNumeric)>')
#p = re.compile('<.*?>.*?<\/.*?>')



def parse(content):
    content = p.sub('', content)
    content = p2.sub('', content)
    soup = BeautifulSoup(content, "lxml")
    content = soup.getText()
    return content


def extract_html(html):
    html = p.sub('', html)
    html = p2.sub('', html)
    html = p3.sub('', html)
    html = p4.sub('', html)
    html = p5.sub('', html)
    html = p6.sub('', html)
    html = p7.sub('', html)
    html = html.replace("</body>","").replace("<body>","").replace("</html>","")
    return html


def extract(fn, code):
    dir = fn.replace("zip","")
    print(fn)
    with zipfile.ZipFile(fn) as existing_zip:
        existing_zip.extractall(dir)
    items = []
    values = []
    return extract_dir(dir, items, values)




def extract_dir(dir, items, values):
    parser = EdinetXbrlParser()
    for path in glob(dir + "/*"):
        if os.path.isdir(path):
            items, values = extract_dir(path, items, values)
            continue
        ext = path.split(".")[-1]

        if path.endswith("_ixbrl.htm"):
            f = open(path)
            html = f.read()
            f.close()
            p = path.replace(dir, "").replace("/","")[:7]
            part = int(p) if p.isdecimal() else 9999999
            values.append({"value":html, "part":part})
        elif ext == "xbrl":
            xbrl = parser.parse_file(path)
            for key in xbrl.get_keys():
                for v in xbrl.get_data_list(key):
                    s = v.get_value()
                    if not s:
                        continue
                    tris = s.replace("\n", "")
                    items.append({"key":key, "value":s, "ishtml": (tris.startswith("<") and tris.endswith(">")) or (tris.startswith("&lt;") and tris.endswith("&gt;") ) })

    return items, values





"""
def extract_file(path):
    try:
        s = ""
        f = open(path)
        # if path.endswith("xml"):
        #     s = xml_to_s(path)
        if path.endswith("htm"):
            s = html_to_s(f.read())
        elif path.endswith("xsd"):
            s = xsd_to_s(f.read())
        elif path.endswith("xbrl"):
            s = xbrl_to_s(f.read())
        elif path.endswith("csv"):
            s = csv_to_s(f.read())
        f.close()
    except:
        print(traceback.format_exc())
        print(path)

    return s

# def xml_to_s(xml_path):
    # tree = ET.parse(xml_path)


def html_to_s(html):
    pass

def xsd_to_s(xsd):
    pass

def xbrl_to_s(xbrl):
    pass

def csv_to_s(csv):
    pass
"""
