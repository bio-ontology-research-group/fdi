#!/usr/bin/env python
import os
import sys


def load_chebi_pubchem_map():
    data = dict()
    with open('data/CID-Synonym-filtered', 'r') as f:
        for line in f:
            line = line.strip().split('\t')
            pub_id = line[0]
            if pub_id not in data:
                data[pub_id] = {'chebi': list(), 'db': list()}
            syn = line[1]
            if syn.startswith("CHEBI:"):
                data[pub_id]['chebi'].append(syn)
            elif syn.startswith("DB") and len(syn) == 7:
                data[pub_id]['db'].append(syn)
    return data


def main(*args, **kwargs):
    # pub_chebis_dict = load_chebi_pubchem_map()
    # with open('data/pubchem_drugbank.tsv', 'w') as f:
    #     for pub_id, m in pub_chebis_dict.iteritems():
    #         if len(m['db']) > 0:
    #             f.write(pub_id + '\t' + m['db'][0])
    #             for i in range(1, len(m['db'])):
    #                 f.write('|' + m['db'][i])
    #             f.write('\t')
    #             if len(m['chebi']) > 0:
    #                 f.write(m['chebi'][0])
    #                 for i in range(1, len(m['chebi'])):
    #                     f.write('|' + m['chebi'][i])
    #             else:
    #                 f.write('.')
    #             f.write('\n')

    with open('data/pubchem_drugbank.tsv', 'r') as f:
        with open('data/pubchem_drugbank_filtered.tsv', 'w') as fw:
            for line in f:
                items = line.strip().split('\t')
                items = items[1].split('|')
                ok = False
                for db in items:
                    if db[2:].isdigit():
                        ok = True
                if ok:
                    fw.write(line)


if __name__ == '__main__':
    main(*sys.argv)
