#!/usr/bin/env python
import os
import sys
import mongoengine as me

me.connect(db='phytos')


class Phytochemical(me.Document):
    """Model for plants and phytochemicals that are inside this plants"""
    name = me.StringField(max_length=511, required=True, unique=True)
    classes = me.ListField(
        me.StringField(max_length=255), required=False)
    synonyms = me.ListField(me.StringField(max_length=255), required=False)
    p_names = me.ListField(me.StringField(max_length=255), required=False)
    p_families = me.ListField(
        me.StringField(max_length=255), required=False)
    p_com_names = me.ListField(me.StringField(
        max_length=255), required=False)
    p_syns = me.ListField(me.StringField(
        max_length=255), required=False)
    chebi_ids = me.ListField(me.StringField(max_length=255), required=False)
    pubchem_ids = me.ListField(me.StringField(max_length=255), required=False)
    drugbank_ids = me.ListField(me.StringField(max_length=255), required=False)
    pharmgkb_ids = me.ListField(me.StringField(max_length=255), required=False)
    repository = me.StringField(max_length=255, required=False)
    repository_ids = me.ListField(
        me.StringField(max_length=255), required=False)

    meta = {
        'indexes': [{
            'fields': [
                '$name', '$synonyms', '$p_names', '$p_com_names',
                '$p_syns', '$p_families', '$classes'],
            'default_language': 'english',
            'weights': {
                'name': 10,
                'synonyms': 10,
                'p_names': 10,
                'p_com_names': 10,
                'p_syns': 10,
                'p_families': 7,
                'classes': 5}
        }]}

    def __unicode__(self):
        return self.name


def load_respect_phytos():
    repository = 'http://spectra.psc.riken.jp/'

    with open('data/phyto_drugbank.tsv', 'r') as f:
        for line in f:
            items = line.strip().split('\t')
            rep_ids = [items[0]]
            name = items[1]
            classes = items[2].split('|')
            pubchem_ids = []
            pub = items[3].split(' ')
            plant_name = items[4]
            if len(pub) == 3 and pub[0] == 'PUBCHEM':
                pub_id = pub[2]
                pubchem_ids.append(pub_id)
            chebi_ids = items[5].split('|')
            db_ids = items[6].split('|')
            if chebi_ids[0] == '.':
                chebi_ids = []
            if db_ids[0] == '.':
                db_ids = []
            ph = None
            try:
                ph = Phytochemical.objects.get(name=name)
            except Phytochemical.DoesNotExist:
                ph = Phytochemical(name=name)
            ph.repository = repository
            ph.repository_ids = rep_ids
            for cl in classes:
                if cl != '.' and cl not in ph.classes:
                    ph.classes.append(cl)
            for pub_id in pubchem_ids:
                if pub_id != '.' and pub_id not in ph.pubchem_ids:
                    ph.pubchem_ids.append(pub_id)
            for ch_id in chebi_ids:
                if ch_id != '.' and ch_id not in ph.chebi_ids:
                    ph.chebi_ids.append(ch_id)
            if plant_name != '.' and plant_name not in ph.p_names:
                ph.p_names.append(plant_name)
            for db_id in db_ids:
                if db_id not in ph.drugbank_ids:
                    ph.drugbank_ids.append(db_id)
            ph.save()


def load_dukes_phytos():
    repository = 'Dr. Dukes Phytochemicals'

    with open('data/dukesphyto_drugbank.tsv', 'r') as f:
        for line in f:
            items = line.strip().split('\t')
            name = items[0]
            classes = items[1].split('|')
            names = items[2].split('|')
            p_names = []
            p_families = []
            p_syns = []
            for p_name in names:
                pn = p_name.split(';')
                if pn[0]:
                    p_names.append(pn[0])
                if pn[1]:
                    p_syns.append(pn[1])
                if pn[2]:
                    p_families.append(pn[2])
            pubchem_ids = items[3].split('|')
            chebi_ids = items[4].split('|')
            db_ids = items[5].split('|')
            ph = None
            try:
                ph = Phytochemical.objects.get(name=name)
            except Phytochemical.DoesNotExist:
                ph = Phytochemical(name=name)
            ph.repository = repository
            ph.classes = classes
            ph.pubchem_ids = pubchem_ids
            if pubchem_ids[0] == '.':
                ph.pubchem_ids = []
            ph.chebi_ids = chebi_ids
            if chebi_ids[0] == '.':
                ph.chebi_ids = []
            ph.drugbank_ids = db_ids
            if db_ids[0] == '.':
                ph.drugbank_ids = []
            ph.p_names = p_names
            ph.p_families = p_families
            ph.p_syns = p_syns
            # print ph.p_syns
            # print ph.drugbank_ids
            ph.save()


def map_common_names():
    plant_names = dict()
    with open('data/plants.txt', 'r') as f:
        for line in f:
            line = line.strip()
            items = line.split("\",\"")
            items[-1] = items[-1][:-1]
            name = items[2].split(' ')
            sci_name = name[0]
            if name[1][0].islower():
                sci_name += ' ' + name[1]
            sci_name = sci_name.lower()
            com_name = items[-2].lower()
            family = items[-1].lower()
            plant_names[sci_name] = (com_name, family)

    phytos = Phytochemical.objects.all()
    for ph in phytos:
        for name in ph.p_names:
            name = name.lower()
            if name in plant_names:
                c_name = plant_names[name][0]
                if c_name not in ph.p_com_names:
                    ph.p_com_names.append(c_name)
                family = plant_names[name][1]
                if family not in ph.p_families:
                    ph.p_families.append(family)
        ph.save()


def map_ingredients_phytos():
    with open('data/ingrs.txt', 'r') as f:
        with open('data/ingrs-phytos.txt', 'w') as fw:
            for line in f:
                query = line.strip()
                phytos = Phytochemical.objects.search_text(
                    query).order_by('$text_score')[:5]
                names = []
                chebi_ids = []
                pubchem_ids = []
                db_ids = []
                for ph in phytos:
                    names.append(ph.name.encode("utf-8"))
                    chebi_ids += ph.chebi_ids
                    pubchem_ids += ph.pubchem_ids
                    db_ids = db_ids + ph.drugbank_ids
                fw.write(query + '\t')
                chebi_ids = list(set(chebi_ids))
                pubchem_ids = list(set(pubchem_ids))
                db_ids = list(set(db_ids))
                if names:
                    fw.write(names[0])
                    for name in names[1:]:
                        fw.write('|' + name)
                else:
                    fw.write('.')
                fw.write('\t')

                if chebi_ids:
                    fw.write(chebi_ids[0])
                    for chebi_id in chebi_ids[1:]:
                        fw.write('|' + chebi_id)
                else:
                    fw.write('.')
                fw.write('\t')

                if pubchem_ids:
                    fw.write(pubchem_ids[0])
                    for pub_id in pubchem_ids[1:]:
                        fw.write('|' + pub_id)
                else:
                    fw.write('.')
                fw.write('\t')

                if db_ids:
                    fw.write(db_ids[0])
                    for db_id in db_ids[1:]:
                        fw.write('|' + db_id)
                else:
                    fw.write('.')
                fw.write('\n')


def count_results():
    db_ids = set()
    with open('data/ing-phytos.txt', 'r') as f:
        for line in f:
            items = line.strip().split('\t')
            if items[1] != '.':
                drugbank_ids = set(items[1].split('|'))
                db_ids |= drugbank_ids

    with open('data/ingrs-phytos.txt', 'r') as f:
        for line in f:
            items = line.strip().split('\t')
            if items[1] != '.':
                drugbank_ids = set(items[1].split('|'))
                db_ids |= drugbank_ids

    print len(db_ids)
    # with open('data/recipe_phyto_drugs.txt', 'w') as f:
    #     for db_id in db_ids:
    #         f.write(db_id + '\n')


def main(*args, **kwargs):
    # load_respect_phytos()
    # load_dukes_phytos()
    # map_common_names()
    # map_ingredients_phytos()
    count_results()

if __name__ == '__main__':
    main(*sys.argv)
