#!/usr/bin/env python
import os
import sys


def collect_respect_data():
    respect_db_dir = 'data/respect/'
    data = list()
    for filename in os.listdir(respect_db_dir):
        pm_id = '.'
        name = '.'
        classes = []
        link = '.'
        sample = '.'
        with open(respect_db_dir + filename, 'r') as f:
            for line in f:
                line = line.strip().split(': ')
                value = '.'
                if len(line) > 1:
                    value = line[1].strip()
                    value = value if value != '' else '.'
                if line[0] == 'ACCESSION':
                    pm_id = value
                elif line[0] == 'CH$NAME':
                    name = value
                elif line[0] == 'CH$COMPOUND_CLASS':
                    classes.append(value)
                elif line[0] == 'CH$LINK':
                    link = value
                elif line[0] == 'SP$SAMPLE':
                    sample = value
        data.append((pm_id, name, classes, link, sample))
    with open('data/respect.tsv', 'w') as f:
        for item in data:
            f.write(item[0] + '\t' + item[1] + '\t')
            if len(item[2]) > 0:
                f.write(item[2][0])
                for it in item[2][1:]:
                    f.write('|' + it)
            else:
                f.write('.')
            f.write('\t' + item[3] + '\t' + item[4] + '\n')


def load_data():
    respect_db_file = 'data/respect.tsv'
    data = list()
    with open(respect_db_file, 'r') as f:
        for line in f:
            line = line.strip().split('\t')
            if len(line) != 5:
                print line
            data.append(line)
    return data


def is_cas_number(id):
    nums = id.split('-')
    if len(nums) != 3:
        return False
    for num in nums:
        if not num.isdigit():
            return False
    return True


def load_chebi_cas_map():
    data = dict()
    with open('data/database_accession.tsv', 'r') as f:
        next(f)
        for line in f:
            line = line.strip().split('\t')
            chebi_id = line[1]
            link_type = line[3]
            cas_id = line[4]
            if link_type == 'CAS Registry Number':
                if cas_id not in data:
                    data[cas_id] = set()
                data[cas_id].add('CHEBI:' + chebi_id)

    data_pub = dict()
    with open('data/CID-Synonym-filtered', 'r') as f:
        for line in f:
            line = line.strip().split('\t')
            chebi_id = None
            cas = None
            syn = line[1]
            if syn.startswith("CHEBI:"):
                chebi_id = syn
            if is_cas_number(syn):
                cas = syn
            pub_id = line[0]
            if pub_id not in data_pub:
                data_pub[pub_id] = (list(), list())
            if cas:
                data_pub[pub_id][0].append(cas)
            if chebi_id:
                data_pub[pub_id][1].append(chebi_id)
    for pub_id, val in data_pub.iteritems():
        cas, chebi_ids = val
        if chebi_ids:
            for cas_id in cas:
                if cas_id not in data:
                    data[cas_id] = set()
                data[cas_id] |= set(chebi_ids)
    return data


def load_chebi_pubchem_map():
    data = dict()
    with open('data/CID-Synonym-filtered', 'r') as f:
        for line in f:
            line = line.strip().split('\t')
            chebi_id = line[1]
            if not chebi_id.startswith("CHEBI:"):
                continue
            pub_id = line[0]
            if pub_id not in data:
                data[pub_id] = list()
            data[pub_id].append(chebi_id)
    return data


def map_chebi():
    chebis_dict = load_chebi_cas_map()
    pub_chebis_dict = load_chebi_pubchem_map()
    data = load_data()
    with open('data/phytochebi.tsv', 'w') as f:
        for item in data:
            cas = item[3].split(' ')
            chebis = list()
            if len(cas) == 2 and cas[0] == 'CAS':
                cas_id = cas[1]
                if cas_id in chebis_dict:
                    chebis = list(chebis_dict[cas_id])
            elif len(cas) == 3 and cas[0] == 'PUBCHEM':
                pub_id = cas[2]
                if pub_id in pub_chebis_dict:
                    chebis = list(pub_chebis_dict[pub_id])
            f.write(
                item[0] + '\t' + item[1] + '\t' +
                item[2] + '\t' + item[3] + '\t' + item[4] + '\t')
            if chebis:
                f.write(chebis[0])
                for chebi in chebis[1:]:
                    f.write('|' + chebi)
            else:
                f.write('.')
            f.write('\n')


def map_drugbank():
    chebi = dict()
    pubchem = dict()
    with open('data/chebi-drugbank.txt', 'r') as f:
        for line in f:
            items = line.strip().split(' ')
            if items[0] not in chebi:
                chebi[items[0]] = set()
            chebi[items[0]].add(items[1])
    with open('data/pubchem_drugbank_chebi.tsv', 'r') as f:
        for line in f:
            items = line.strip().split('\t')
            pub_id = items[0]
            db_ids = items[1].split('|')
            chebi_ids = items[2].split('|')
            if chebi_ids[0] != '.':
                for chebi_id in chebi_ids:
                    if chebi_id not in chebi:
                        chebi[chebi_id] = set()
                    for db_id in db_ids:
                        chebi[chebi_id].add(db_id)
            pubchem[pub_id] = db_ids

    with open('data/phytochebi.tsv', 'r') as f:
        with open('data/phyto_drugbank.tsv', 'w') as fw:
            for line in f:
                line = line.strip()
                fw.write(line + '\t')
                items = line.split('\t')
                db_ids = set()
                pub = items[3].split(' ')
                if len(pub) == 3 and pub[0] == 'PUBCHEM':
                    pub_id = pub[2]
                    if pub_id in pubchem:
                        for db_id in pubchem[pub_id]:
                            db_ids.add(db_id)
                chebi_ids = items[5].split('|')
                for chebi_id in chebi_ids:
                    if chebi_id in chebi:
                        for db_id in chebi[chebi_id]:
                            db_ids.add(db_id)
                db_ids = list(db_ids)
                if len(db_ids) > 0:
                    fw.write(db_ids[0])
                    for db_id in db_ids[1:]:
                        fw.write('|' + db_id)
                else:
                    fw.write('.')
                fw.write('\n')


def main(*args, **kwargs):
    # collect_respect_data()
    map_drugbank()

if __name__ == '__main__':
    main(*sys.argv)
