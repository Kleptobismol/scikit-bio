"""
Stockholm format (:mod:`skbio.io.format.stockholm`)
===================================================

.. currentmodule:: skbio.io.format.stockholm

The Stockholm format is a multiple sequence alignment format written in Markup
as opposed to a simple text-based format. Data is stored on separate lines,
each with a unique data 'name' preceding it. The alignment can just contain
data, or contain data and related metadata.

An example Stockholm file, taken from [1]_:

.. code-block:: none

    # STOCKHOLM 1.0
    #=GF ID    UPSK
    #=GF SE    Predicted; Infernal
    #=GF SS    Published; PMID 9223489
    #=GF RN    [1]
    #=GF RM    9223489
    #=GF RT    The role of the pseudoknot at the 3' end of turnip yellow mosaic
    #=GF RT    virus RNA in minus-strand synthesis by the viral RNA-dependent \
RNA
    #=GF RT    polymerase.
    #=GF RA    Deiman BA, Kortlever RM, Pleij CW;
    #=GF RL    J Virol 1997;71:5990-5996.
    AF035635.1/619-641             UGAGUUCUCGAUCUCUAAAAUCG
    M24804.1/82-104                UGAGUUCUCUAUCUCUAAAAUCG
    J04373.1/6212-6234             UAAGUUCUCGAUCUUUAAAAUCG
    M24803.1/1-23                  UAAGUUCUCGAUCUCUAAAAUCG
    #=GC SS_cons                   .AAA....<<<<aaa....>>>>
    //

Format Support
==============
**Has Sniffer: Yes**

**State: Experimental as of 0.4.0-dev.**

+------+------+---------------------------------------------------------------+
|Reader|Writer|                          Object Class                         |
+======+======+===============================================================+
|Yes   |No    |:mod:`skbio.alignment.TabularMSA`                              |
+------+------+---------------------------------------------------------------+

Format Specification
====================
The Stockholm format contains two types of data. The first can contain raw DNA,
RNA, or Protein data and the second is comprised of associated metadata.
Raw data lines begin with an associated 'name', which
often times is an id comprised of letters and numbers, such as
'M24804.1/82-104' ([1]_). After the id and a few tab characters,
the data is displayed. Metadata lines, however, begin with a '#' and a
two-letter marker which describes the metadata type, for example '#=GF' (see
Metadata Types). Each metadata line also contains an extra two-letter feature,
such as 'AS' or 'CC' which tells what type of data it precedes. All metadata
is optional.

Metadata Types
++++++++++++++
GF
--
Data relating to the multiple sequence alignment as a whole, such as authors or
number of sequences in the alignment. Starts with #=GF followed by a feature
and data relating to the feature. Typically comes first in a Stockholm file.
For example:

.. code-block:: none

    #=GF DE CBS domain

Example taken from [2]_.

GS
--
Data relating to a specific sequence in the multiple sequence alignment.
Starts with #=GS followed by the sequence name followed by a feature and data
relating to the feature. Typically comes second in a Stockholm file.
For example:

.. code-block:: none

    #=GS O83071/259-312 AC O83071

Example taken from [2]_.

GC
--
Data relating to the columns of the multiple sequence alignment as a whole.
Starts with #=GC followed by a feature and data relating to the feature.
Typically comes at the end of the multiple sequence alignment.
For example:

.. code-block:: none

    #=GC SS_cons            CCCCCHHHHHHHHHHHHH..EEEEEEEE....EEEEEEEEEEH

Example taken from [2]_.

GR
--
Data relating to the columns of a specific sequence in a multiple sequence
alignment. Starts with #=GR followed by the sequence name followed by a feature
and data relating to the feature. Typically comes after the data line it
relates to.
For example:

.. code-block:: none

    #=GR O31698/18-71 SS    CCCHHHHHHHHHHHHHHH..EEEEEEEE....EEEEEEEEHHH

Example taken from [2]_.

Examples
========
Suppose we have a Stockholm file:

>>> import skbio.io
>>> from io import StringIO
>>> from skbio import RNA, TabularMSA
>>> fs = '\\n'.join([
...         '# STOCKHOLM 1.0',
...         '#=GF RA    Deiman BA, Kortlever RM, Pleij CW;',
...         '#=GF RL    J Virol 1997;71:5990-5996.',
...         'AF035635.1/619-641             UGAGUUCUCGAUCUCUAAAAUCG',
...         'M24804.1/82-104                UGAGUUCUCUAUCUCUAAAAUCG',
...         'J04373.1/6212-6234             UAAGUUCUCGAUCUUUAAAAUCG',
...         'M24803.1/1-23                  UAAGUUCUCGAUCUCUAAAAUCG',
...         '#=GC SS_cons                   .AAA....<<<<aaa....>>>>',
...         '//'
...     ])
>>> fh = StringIO(fs)
>>> msa = skbio.io.read(fh, into=TabularMSA, constructor=RNA)
>>> msa # doctest: +NORMALIZE_WHITESPACE
TabularMSA[RNA]
-------------------------------------------------
Metadata:
'RA': '   Deiman BA, Kortlever RM, Pleij CW;'
'RL': '   J Virol 1997;71:5990-5996.'
Positional metadata:
'SS_cons': <dtype: object>
Stats:
sequence count: 4
position count: 23
-------------------------------------------------
UGAGUUCUCGAUCUCUAAAAUCG
UGAGUUCUCUAUCUCUAAAAUCG
UAAGUUCUCGAUCUUUAAAAUCG
UAAGUUCUCGAUCUCUAAAAUCG

References
==========
.. [1] https://en.wikipedia.org/wiki/Stockholm_format
.. [2] http://sonnhammer.sbc.su.se/Stockholm.html
"""

# ----------------------------------------------------------------------------
# Copyright (c) 2013--, scikit-bio development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
# ----------------------------------------------------------------------------

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from collections import OrderedDict, namedtuple

from skbio.alignment import TabularMSA
from skbio.sequence import Protein
from skbio.io import create_format, StockholmFormatError

stockholm = create_format('stockholm')
_SeqData = namedtuple("SeqData", ["seq", "metadata", "pos_metadata"])


@stockholm.sniffer()
def _stockholm_sniffer(fh):
    # Smells a Stockholm file if the first line contains 'Stockholm' and the
    # version number.
    try:
        line = next(fh)
    except StopIteration:
        return False, {}
    if line[:15] == "# STOCKHOLM 1.0":
        return True, {}

    return False, {}


@stockholm.reader(TabularMSA)
def _stockholm_to_tabular_msa(fh, constructor=Protein):
    # Uses OrderedDict() to make sure dna_data isn't arranged randomly
    dna_data = OrderedDict()
    # Creates SeqData class to store all sequence data and make code more
    # readable
    metadata = {}
    positional_metadata = {}
    seqs = []

    # Retrieves data from file, reads first so that data order will be kept
    # consistent.
    for line in fh:
        if is_data_line(line):
            dna_data = _parse_stockholm_line_data(line, dna_data)
    fh.seek(0)

    # Retrieves metadata from file
    for line in fh:
        if line.startswith("#=GF"):
            metadata = _parse_stockholm_line_gf(line, metadata)
        elif line.startswith("#=GS"):
            dna_data = _parse_stockholm_line_gs(line, dna_data)
        elif line.startswith("#=GR"):
            dna_data = _parse_stockholm_line_gr(line, dna_data)
        elif line.startswith('#=GC'):
            positional_metadata = _parse_stockholm_line_gc(line,
                                                           positional_metadata)

    for key in dna_data.keys():
        # Sets blank dictionaries and lists to None instead
        # Note: _replace is not a private function, see
        # https://docs.python.org/2/library/collections.html#namedtuple-
        # factory-function-for-tuples-with-named-fields
        if not dna_data[key].metadata:
            dna_data[key] = dna_data[key]._replace(metadata=None)
        if not dna_data[key].pos_metadata:
            dna_data[key] = dna_data[key]._replace(pos_metadata=None)
        # Adds each sequence to the MSA data
        seqs.append(constructor(dna_data[key].seq,
                                metadata=dna_data[key].metadata,
                                positional_metadata=(dna_data
                                                     [key].pos_metadata)))

    if not seqs:
        raise StockholmFormatError("No data present in file.")
    if not positional_metadata:
        positional_metadata = None
    # Constructs TabularMSA
    return TabularMSA(seqs, metadata=metadata,
                      positional_metadata=positional_metadata,
                      index=list(dna_data.keys()))


def _parse_stockholm_line_gf(line, metadata):
    """Takes ``#=GF`` line and returns parsed data."""
    line = _remove_newline(line.split(' ', 2))
    gf_feature = line[1]
    gf_feature_data = line[2]
    if gf_feature in metadata.keys():
        metadata[gf_feature] = metadata[gf_feature] + ' ' + gf_feature_data
    else:
        metadata[gf_feature] = gf_feature_data
    return metadata


def _parse_stockholm_line_gs(line, dna_data):
    """Takes ``#=GS`` line and returns parsed data."""
    line = _remove_newline(line.split(' ', 3))
    data_seq_name = line[1]
    gs_feature = line[2]
    if data_seq_name in dna_data.keys():
        if not dna_data[data_seq_name].metadata:
            dna_data[data_seq_name].metadata[gs_feature] = line[3]
    else:
        raise StockholmFormatError("Markup line references nonexistent "
                                   "data %r." % data_seq_name)
    return dna_data


def _parse_stockholm_line_gr(line, dna_data):
    """Takes ``#=GR`` line and returns parsed data."""
    line = _remove_newline(line.split())
    data_seq_name = line[1]
    gr_feature = line[2]
    if data_seq_name in dna_data.keys():
        if gr_feature in dna_data[data_seq_name].pos_metadata.keys():
            raise StockholmFormatError("Found duplicate GR label %r associated"
                                       " with data label %r" % (gr_feature,
                                                                data_seq_name))
        dna_data[data_seq_name].pos_metadata[gr_feature] = list(line[3])
    else:
        raise StockholmFormatError("Markup line references nonexistent "
                                   "data %r." % data_seq_name)
    return dna_data


def _parse_stockholm_line_gc(line, positional_metadata):
    """Takes ``#=GC`` line and returns parsed data."""
    line = _remove_newline(line.split())
    gc_feature = line[1]
    if gc_feature in positional_metadata.keys():
        raise StockholmFormatError("Found duplicate GC label %r."
                                   % (gc_feature))
    positional_metadata[gc_feature] = list(line[2])
    return positional_metadata


def _parse_stockholm_line_data(line, dna_data):
    """Takes data line and returns parsed data."""
    line = line.split()
    data_seq_name = line[0]
    if data_seq_name not in dna_data.keys():
        dna_data[data_seq_name] = _SeqData(seq=line[1], metadata={},
                                           pos_metadata={})
    elif data_seq_name in dna_data.keys():
        raise StockholmFormatError("Found multiple data lines under same "
                                   "name: %r" % data_seq_name)
    return dna_data


def _remove_newline(line):
    """Removes '\n' from line and returns line."""
    n_line = line[len(line)-1]
    if '\n' in n_line:
        line[len(line)-1] = n_line.rstrip('\n')
    return line


def is_data_line(line):
    return not (line.startswith("#") or line.startswith("//") or
                line.isspace())