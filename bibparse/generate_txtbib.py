import re
import bib
import fileinput


def process_bibfile(filename):
    bibfile = open(filename)

    data = ""
    for line in bibfile:
        line = line.rstrip()
        data += line + "\n"

    data = bib.clear_comments(data)
    biblio = bib.Bibparser(data)
    biblio.parse()

    return biblio


def lookup_month(month):
    lookup = {"jan": 1, "feb": 2, "mar": 3, "apr": 4, \
              "may": 5, "jun": 6, "jul": 7, "aug": 8, \
              "sep": 9, "oct": 10, "nov": 11, "dec": 12}

    try:
        val = lookup[month]
    except KeyError:
        val = None

    return val


def extract_name(name_entry):
    last_name = name_entry['family']
    last_name = re.sub('[{}]', '', last_name)
    last_name = last_name.strip()

    try:
        first_initials = name_entry['given']
        first_initials = first_initials.replace("~", " ")
        fullname = "%s %s" % (first_initials, last_name)
    except KeyError:
        fullname = last_name

    return fullname

def format_article_txt(entry):
    #print entry['title']
    author_list = entry['author']
    author_list = [extract_name(item) for item in author_list]

    if (("Collaboration" not in author_list[-1]) and \
        len(author_list) > 2):
        author_list[-1] = "and " + author_list[-1]

    author_list = ", ".join(author_list)
    entry['author_list'] = author_list

    bibitem = '\"%(title)s\", %(author_list)s' % entry
    if "journal" in entry:
        bibitem += ', %(journal)s' % entry

        if entry['journal'].lower() == 'arxiv':
            bibitem += ' (%(eprint)s)' % entry

        if "volume" in entry:
            bibitem += ', %(volume)s' % entry

        if "eid" in entry:
            bibitem += ', %(eid)s' % entry
        elif "page" in entry:
            eid = entry['page']
            eid = eid.split('-')[0]
            bibitem += ', %s' % eid

    # handle SPIE proceedings
    if "series" in entry:
        bibitem += ', %(series)s' % entry

        if "eid" in entry:
            bibitem += ', %(eid)s' % entry

    if "school" in entry:
        bibitem += ', PhD thesis, %(school)s' % entry

    if "issued" in entry:
        year = entry['issued']['literal']
        bibitem += ' (%s)' % year

    bibitem += '.\n'

    #print "-" * 80
    print bibitem
    #for (k, v) in entry.iteritems():
    #    print k, v


def ordered_list(biblio_dict, ads_ids):
    ads_list = []
    for ads_tag in ads_ids:
        entry = biblio_dict[ads_tag]

        try:
            year = entry['issued']['literal']
        except KeyError:
            year = None

        try:
            month = entry['month']
        except KeyError:
            month = None

        num_month = lookup_month(month)

        ads_list.append((int(year), int(num_month), ads_tag))
        #print ads_tag, year, month, num_month

    ads_list = sorted(ads_list, reverse=True)
    ads_list = [item[2] for item in ads_list]
    return ads_list


def make_biblist():
    biblio = process_bibfile("switzer.bib")

    ads_list = ordered_list(biblio.records, biblio.records.keys())

    for ads_tag in ads_list:
        entry = biblio.records[ads_tag]
        print ads_tag, entry['title']


def main():
    biblio = process_bibfile("switzer.bib")

    # read the requested selected bib and order
    ads_list = []
    for bibitem in fileinput.input():
        if bibitem[0] == "#":
            #print "skipping", bibitem
            continue

        ads_tag = bibitem.split()[0]
        ads_list.append(ads_tag)

    ads_list = ordered_list(biblio.records, ads_list)

    for ads_tag in ads_list:
        entry = biblio.records[ads_tag]
        format_article_txt(entry)


if __name__ == "__main__":
    #make_biblist()
    main()
