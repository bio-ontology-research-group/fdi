#!/usr/bin/env python
import os
import sys


def aggr_data():
    names = dict()
    family = dict()
    synonym = dict()

    with open('data/dukes/FNFTAX.csv', 'r') as f:
        next(f)
        for line in f:
            items = line.strip().split('\",\"')
            plant_id = items[0][1:]
            names[plant_id] = items[1]
            family[plant_id] = items[14]
            synonym[plant_id] = items[15]
    data_names = dict()
    with open('data/dukes/FARMACY.csv', 'r') as f:
        next(f)
        for line in f:
            items = line.strip().split('\",\"')
            plant_id = items[0][1:]
            chem = items[1]
            if chem not in data_names:
                data_names[chem] = set()
            if plant_id in names:
                data_names[chem].add(plant_id)

    data_classes = dict()
    with open('data/dukes/FARMACY_NEW.csv', 'r') as f:
        next(f)
        for line in f:
            items = line.strip().split('\",\"')
            plant_id = items[0][1:]
            chem = items[1]
            chem_class = items[2]
            if chem not in data_names:
                data_names[chem] = set()
            data_names[chem].add(plant_id)
            if chem_class:
                if chem not in data_classes:
                    data_classes[chem] = set()
                data_classes[chem].add(chem_class)
    with open('data/dukesphyto.tsv', 'w') as f:
        for chem, name_ids in data_names.iteritems():
            f.write(chem + '\t')
            if chem in data_classes:
                classes = list(data_classes[chem])
                f.write(classes[0])
                for cl in classes[1:]:
                    f.write('|' + cl)
            else:
                f.write('.')
            f.write('\t')
            name_ids = list(name_ids)
            f.write(
                names[name_ids[0]] + ';' +
                synonym[name_ids[0]] + ';' + family[name_ids[0]])
            for name_id in name_ids[1:]:
                f.write(
                    '|' + names[name_id] + ';' +
                    synonym[name_id] + ';' + family[name_id])
            f.write('\n')


def map_pubchem():
    data = dict()
    with open('data/CID-Synonym-filtered', 'r') as f:
        for line in f:
            line = line.strip().split('\t')
            syn = line[1].strip().lower()
            pub_id = line[0]
            if syn not in data:
                data[syn] = list()
            data[syn].append(pub_id)

    with open('data/dukesphyto_pubchem.tsv', 'w') as fw:
        with open('data/dukesphyto.tsv', 'r') as f:
            for line in f:
                line = line.strip()
                items = line.split('\t')
                fw.write(line + '\t')
                chem = items[0].strip().lower()
                if chem in data:
                    pubs = data[chem]
                    fw.write(pubs[0])
                    for pub_id in pubs[1:]:
                        fw.write('|' + pub_id)
                else:
                    fw.write('.')
                fw.write('\n')

    return data


def map_chebi():
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

    with open('data/dukesphyto_chebi.tsv', 'w') as fw:
        with open('data/dukesphyto_pubchem.tsv', 'r') as f:
            for line in f:
                line = line.strip()
                items = line.split('\t')
                fw.write(line + '\t')
                pubchems = items[3].split('|')
                if pubchems[0] != '.':
                    chebis = list()
                    for pub_id in pubchems:
                        if pub_id in data:
                            for chebi in data[pub_id]:
                                chebis.append(chebi)
                    if chebis:
                        fw.write(chebis[0])
                        for chebi in chebis[1:]:
                            fw.write('|' + chebi)
                    else:
                        fw.write('.')
                else:
                    fw.write('.')
                fw.write('\n')

    return data


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

    with open('data/dukesphyto_chebi.tsv', 'r') as f:
        with open('data/dukesphyto_drugbank.tsv', 'w') as fw:
            for line in f:
                line = line.strip()
                items = line.split('\t')
                pub_ids = items[3].split('|')
                chebi_ids = items[4].split('|')
                fw.write(line + '\t')
                db_ids = set()
                for pub_id in pub_ids:
                    if pub_id in pubchem:
                        for db_id in pubchem[pub_id]:
                            db_ids.add(db_id)
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
    # aggr_data()
    # map_pubchem()
    # map_chebi()
    map_drugbank()

if __name__ == '__main__':
    main(*sys.argv)
