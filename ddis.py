#!/usr/bin/env python
import os
import sys
import xml.etree.ElementTree as ET


def main(*args, **kwargs):
    tree = ET.parse('data/drugbank.xml')
    root = tree.getroot()
    print len(root)
    # fddi = open('drug-drug-interactions.tsv', 'w')
    # ffdi = open('food-drug-interactions.tsv', 'w')
    # for child in root:
    #     db_id = child.find('{http://www.drugbank.ca}drugbank-id[@primary]').text
    #     db_id = db_id.encode('utf-8')
    #     ddis = child.find('{http://www.drugbank.ca}drug-interactions')
    #     for ddi in ddis:
    #         d_id = ddi.find('{http://www.drugbank.ca}drugbank-id').text
    #         name = ddi.find('{http://www.drugbank.ca}name').text
    #         desc = ddi.find('{http://www.drugbank.ca}description').text
    #         fddi.write(db_id + '\t' + d_id.encode('utf-8') + '\t' + name.encode('utf-8') + '\t' + desc.encode('utf-8') + '\n')
    #     fdis = child.find('{http://www.drugbank.ca}food-interactions')
    #     for fdi in fdis:
    #         food = fdi.text.encode('utf-8')
    #         ffdi.write(db_id + '\t' + food + '\n')
    # fddi.close()
    # ffdi.close()

if __name__ == '__main__':
    main(*sys.argv)
