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


def make_biblist():
    biblio = process_bibfile("switzer.bib")

    for ads_tag in biblio.records:
        entry = biblio.records[ads_tag]
        print ads_tag, entry['title']


def lookup_month(month):
    lookup = {"jan": 1, "feb": 2, "mar": 3, "apr": 4, \
              "may": 5, "jun": 6, "jul": 7, "aug": 8, \
              "sep": 9, "oct": 10, "nov": 11, "dec": 12}

    try:
        val = lookup[month]
    except KeyError:
        val = None

    return val


def main():
    biblio = process_bibfile("switzer.bib")

    # read the requested selected bib and order
    ads_list = []
    for bibitem in fileinput.input():
        ads_tag = bibitem.split()[0]
        entry = biblio.records[ads_tag]

        try:
            year = entry['issued']['literal']
        except KeyError:
            year = None

        try:
            month = entry['month']
        except KeyError:
            month = None

        num_month = lookup_month(month)

        ads_list.append((year, num_month, ads_tag))
        #print ads_tag, year, month, num_month

    ads_list = sorted(ads_list)
    ads_list = [item[2] for item in ads_list]
    print ads_list

    for ads_tag in ads_list:
        entry = biblio.records[ads_tag]
        print entry


if __name__ == "__main__":
    #make_biblist()
    main()
