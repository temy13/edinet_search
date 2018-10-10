from glob import glob
import zipfile
import os
import os.path
import traceback
# import xml.etree.ElementTree as ET
# from xbrl_parser import xbrl_parse
from edinet_xbrl.edinet_xbrl_parser import EdinetXbrlParser
from bs4 import BeautifulSoup


def extract(fn, code):
    dir = fn.replace("zip","")
    with zipfile.ZipFile(fn) as existing_zip:
        existing_zip.extractall(dir)
    ds = []
    return extract_dir(dir, ds)


def extract_dir(dir, ds):
    parser = EdinetXbrlParser()
    for path in glob(dir + "/*"):
        if os.path.isdir(path):
            d = extract_dir(path, ds)
            continue
        ext = path.split(".")[-1]
        if not ext == "xbrl":
            continue
        print(path)
        xbrl = parser.parse_file(path)
        for key in xbrl.get_keys():
            print("key", key)
            for v in xbrl.get_data_list(key):
                s = v.get_value()
                if not s:
                    continue
                ds.append({"key":key, "value":s, "ishtml": s.startswith("<") and s.endswith(">")})
                # if not s:
                #     continue
                # s = s.replace("\n", "")
                # if s.startswith("<") and s.endswith(">"):
                #     soup = BeautifulSoup(s, "html.parser")
                # else:
                #     print(s)
    return ds





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
