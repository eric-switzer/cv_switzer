"""Parse XML bibliographic data from NASA ADS
-> arbitrary format for authors, title, journal etc.
The example here is auid1 style.
"""
import xml.etree.ElementTree as ET
import unicodedata
import string
import re

trans_journal = {}
trans_journal["The Astrophysical Journal,"] = "ApJ"
trans_journal["The Astrophysical Journal Letters,"] = "ApJL"
trans_journal["The Astrophysical Journal Supplement,"] = "ApJS"
trans_journal["Physical Review D,"] = "PRD"
trans_journal["Physical Review Letters,"] = "PRL"
trans_journal["Nuclear Physics B Supplement,"] = "Nuc. Phys. B Supp."
trans_journal["Journal of Cosmology and Astroparticle Physics,"] = "JCAP"
trans_journal["Monthly Notices of the Royal Astronomical Society: Letters,"] = "MNRASL"
trans_journal["Monthly Notices of the Royal Astronomical Society,"] = "MNRAS"
trans_journal["Proceedings of the SPIE,"] = "Proc. SPIE"
trans_journal["Astrophysics Source Code Library,"] = "ADS Software"
trans_journal["Proquest Dissertations And Theses"] = "PhD Thesis"
trans_journal["Journal of Low Temperature Physics"] = "J. Low Temp. Phys."
trans_journal["Applied Optics"] = "Applied Optics"
trans_journal["arXiv"] = "arXiv"

# Identify local authors
author_id = {}
author_id["Wollack"] = "ewollack"
author_id["Moseley"] = "hmoseley"
author_id["Chervenak"] = "jchervenak"
author_id["Switzer"] = "eswitzer"


def translate_journal(journal):
    for full_name, abbr in trans_journal.iteritems():
        if full_name in journal:
            return abbr

    return None


def auid_name(namedict):
    """convert to NASA AUID format"""

    if "." not in namedict['first']:
        namedict['first'] = "%s." % namedict['first'][0]

    try:
        if "." not in namedict['middle']:
            namedict['middle'] = "%s." % namedict['middle'][0]

        nameentry = "%s, %s%s" % (namedict['last'], namedict['first'],
                            namedict['middle'])
    except:
        nameentry = "%s, %s" % (namedict['last'], namedict['first'])

    authid = None
    for lastname, nameid in author_id.iteritems():
        if lastname in nameentry:
            authid = nameid

    if authid is not None:
        return "%s|%s" % (authid, nameentry)
    else:
        return nameentry


def parse_name(name):
    name = name.replace("~", " ")
    namesplit = name.split(', ')
    last = namesplit[0].strip()
    first = string.lstrip(namesplit[1])
    parsed_name = {}
    firstsplit = first.split(" ")
    firstname = firstsplit[0].strip()
    if len(firstsplit) == 2:
        middlename = firstsplit[1].strip()
    else:
        middlename = None

    parsed_name['first'] = firstname
    parsed_name['middle'] = middlename
    parsed_name['last'] = last

    return parsed_name


tree = ET.parse('biblio.xml')
root = tree.getroot()
outfile = open("biblio.auid1", "w")

prefix = "{http://ads.harvard.edu/schema/abs/1.1/abstracts}"
record_token = prefix + "record"
for record in root.findall(prefix + "record"):

    title = record.find(prefix + 'title').text
    bibcode = record.find(prefix + 'bibcode').text
    journal = record.find(prefix + 'journal').text
    pubdate = record.find(prefix + 'pubdate').text
    year = re.sub("[^0-9]", "", pubdate)

    try:
        title = unicodedata.normalize("NFKD",
                            title).encode('ascii', 'ignore')
    except TypeError:
        pass

    try:
        volume = record.find(prefix + 'volume').text
    except AttributeError:
        volume = ""

    try:
        page = record.find(prefix + 'page').text
    except AttributeError:
        page = ""

    authorlist = []
    for author in record.findall(prefix + "author"):
        parsed_name = auid_name(parse_name(author.text))
        try:
            parsed_name = unicodedata.normalize("NFKD",
                            parsed_name).encode('ascii', 'ignore')
        except TypeError:
            pass

        authorlist.append(parsed_name)

    journal_abbr = translate_journal(journal)
    authstring = ", ".join(authorlist)
    main_entry = "%s\n\"%s\", %s" % (bibcode, title, authstring)
    pubinfo = "%s, %s, %s, %s" % (year, journal_abbr, volume, page)
    outfile.write("%s, %s\n\n" % (main_entry, pubinfo))

outfile.close()
