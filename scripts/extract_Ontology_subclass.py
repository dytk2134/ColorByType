#! /usr/bin/env python
# Contributed by Li-Mei Chiang <dytk2134 [at] gmail [dot] com> (2018)
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.

import sys
import re
import logging
import os

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.handlers:
    lh = logging.StreamHandler()
    lh.setFormatter(logging.Formatter('%(levelname)-8s %(message)s'))
    logger.addHandler(lh)

__version__ = '1.0.0'


def get_related_terms(ontology):
    # related_dict = {
    # 'SO:0000000': {'SO_ID': 'SO:0000000', 'SO_term': 'Sequence_Ontology', 'related_term': set()},
    # 'SO:XXXXXXX': {'SO_ID': 'SO:XXXXXXX', 'SO_term': 'A', 'related_term': set('B','C')}
    #  }
    related_dict = dict()
    for term in ontology:
        if term.id not in related_dict:
            related_dict[term.id] = {
                'SO_ID': term.id,
                'SO_term': term.name,
                'related_term': set()
            }
        # subclass
        related_dict[term.id]['related_term'].update(term.rchildren().name)

        for k in term.relations:
            # subclass of is_a and part_of
            if k.obo_name == 'is_a' or k.obo_name == 'is_part':
                related_dict[term.id]['related_term'].update(term.relations[k].rchildren().name)
        # someValuesFrom(part_of)
        if 'someValuesFrom' in term.other:
            # format: http://purl.obolibrary.org/obo/SO_0001790
            for part_of in term.other['someValuesFrom']:
                SO_ID = part_of.split('/')[-1].replace('_', ':')
                related_dict[term.id]['related_term'].update(ontology[SO_ID].rchildren().name)
    return related_dict


def main(args):
    import pronto
    ontology = pronto.Ontology(args.ontology)
    outfilename = os.path.join(args.outdir, 'OS_table.tsv')
    related_dict = get_related_terms(ontology)

    with open(outfilename, 'w') as out_f:
        if 'data-version' in ontology.meta:
            # data-version
            outline = '# %s\n' % (' '.join(ontology.meta['data-version']))
            out_f.write(outline)
        elif 'versionIRI' in ontology:
            # versionIRI
            outline = '# %s\n' % (' '.join(ontology.meta['versionIRI']))
            out_f.write(outline)

        # SO_ID SO_term related_term
        for SO_ID in related_dict:
            child_term_list = list()
            outlist = [related_dict[SO_ID]['SO_ID'], related_dict[SO_ID]['SO_term'], ','.join(related_dict[SO_ID]['related_term'])]
            outline = '\t'.join(outlist) + '\n'
            out_f.write(outline)
    out_f.close()
if __name__ == '__main__':
    import argparse
    from textwrap import dedent
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description=dedent("""\

    Quick start:
    %(prog)s -onto so.obo -out ColorByType/
    """))


    parser.add_argument('-onto', '--ontology', type=str, help='Ontology obo or owl files', required=True)
    parser.add_argument('-out', '--outdir', type=str, help='output directory', required=True)
    parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__)

    args = parser.parse_args()
    main(args)
