from prep.syntax_parser import SyntaxParser
from segmentation.segmenter import Segmenter
from treebuilder.build_tree import TreeBuilder
from treebuilder.build_tree_greedy import GreedyTreeBuilder
from optparse import OptionParser

import paths
import os.path
import sys
import utils.utils
import re
import time
import nltk
import traceback
import utils.rst_lib
import subprocess
import utils.serialize
from trees.parse_tree import ParseTree
import math
import utils.rst_lib
from datetime import datetime


class DiscourseParser():
    def __init__(self, verbose, seg, output, SGML, edus, feature_sets='FengHirst'):
        ''' This is Hilda's segmentation module '''
        self.segmenter = None
        self.verbose = verbose
        self.seg = seg
        self.output = output
        self.SGML = SGML
        self.edus = edus
        self.dependencies = True
        self.max_iters = 0
        self.feature_sets = feature_sets

        initStart = time.time()
        try:
            self.segmenter = Segmenter(_model_path=os.path.join(paths.SEG_MODEL_PATH),
                                       _model_file="training.scaled.model",
                                       _scale_model_file="bin_scale",
                                       _name="segmenter",
                                       verbose=self.verbose, dependencies=self.dependencies)

        except Exception, e:
            print "*** Loading Segmentation module failed..."

            if not self.segmenter is None:
                self.segmenter.unload()
            raise

        self.treebuilder = None
        try:
            if self.feature_sets == 'FengHirst':
                self.treebuilder = GreedyTreeBuilder(_model_path=paths.TREE_BUILD_MODEL_PATH,
                                                     _bin_model_file=['struct/FengHirst/within_no_context.svmperf',
                                                                      'struct/FengHirst/above_no_context.svmperf'],
                                                     _bin_scale_model_file=None,
                                                     _mc_model_file=[
                                                         'label/FengHirst/within_label_nuclearity_no_context.multiclass',
                                                         'label/FengHirst/above_label_nuclearity_no_context.multiclass'],
                                                     _mc_scale_model_file=None,
                                                     _name="FengHirst", verbose=self.verbose,
                                                     use_contextual_features=False)

        except Exception, e:
            print "*** Loading Tree-building module failed..."
            print traceback.print_exc()

            if not self.treebuilder is None:
                self.treebuilder.unload()
            raise

        initEnd = time.time()
        print 'finished initialization in %.2f seconds' % (initEnd - initStart)

    def unload(self):
        if not self.segmenter is None:
            self.segmenter.unload()

        if not self.treebuilder is None:
            self.treebuilder.unload()

    def parse(self, filename):
        if not os.path.exists(filename):
            print '%s does not exist.' % filename
            return

        print 'parsing %s' % filename

        try:
            segStart = time.time()
            text = open(filename).read()
            text = re.sub('\.', '.<s>', text)
            text = re.sub('<s> *<p>', '<p>', text)

            # formatted_text = ''
            sentences = []
            for para_text in text.split('<p>'):
                # sents = filter(None, re.split('[.?]+', para_text))
                # ref_sents = []
                # for sent in sents:
                #     ref_sents.append(sent.strip() + '.')
                sents = para_text.strip().split('<s>')

                # formatted_text += ' '.join(sents) + '\n\n'
                # print formatted_text
                sentences.extend(sents)
                # sentences.extend(ref_sents)

            edus = None

            if self.edus:
                if not os.path.exists(filename + '.edus'):
                    print 'User specified EDU file ' + filename + '.edus' + ' no found!'
                    print 'Ignore "-E" option and conduct segmentation'
                    self.edus = False
                else:
                    fin = open(filename + '.edus')
                    edus = []
                    for line in fin:
                        line = line.strip()
                        if line != '':
                            line = re.sub('\</??edu\>', '', line)
                            edus.append(' '.join(nltk.word_tokenize(line)))
                    fin.close()

            ''' Step 1: segment the each sentence into EDUs '''

            (trees, deps, cuts, edus) = self.segmenter.do_segment(text, edus)
            escaped_edus = self.segmenter.get_escaped_edus(trees, cuts, edus)
            print 'finished segmentation, segmented into %d EDUs' % len(edus)

            segEnd = time.time()
            print 'finished segmentation in %.2f seconds' % (segEnd - segStart)

        except Exception, e:
            print "*** Segmentation failed ***"
            print traceback.print_exc()

            if not self.segmenter is None:
                self.segmenter.unload()

            if not self.treebuilder is None:
                self.treebuilder.unload()

            raise

        try:
            if not self.seg:
                ''' Step 2: build text-level discourse tree '''
                treeBuildStart = time.time()

                outfname = filename + ".%s" % ("tree" if not self.SGML else "dis")
                parse_trees = self.treebuilder.build_tree((trees, deps, cuts, edus), "pouet", paths.MODEL_PATH)

                print 'finished tree building'

                if parse_trees == []:
                    print "No tree could be built..."

                    if not self.treebuilder is None:
                        self.treebuilder.unload()

                    return -1

                # Unescape the parse tree
                if parse_trees and len(parse_trees):
                    pt = parse_trees[0]

                    # pt_edges = utils.utils.transform_to_ZhangShasha_tree(pt)
                    # pts.append(pt_edges)
                    for i in range(len(escaped_edus)):
                        # print i, escaped_edus[i], pt.leaves()[i]
                        pt.__setitem__(pt.leaf_treeposition(i), '_!%s!_' % escaped_edus[i])

                    print utils.utils.print_SGML_tree(pt)
                    out = pt.pprint() if not self.SGML else utils.utils.print_SGML_tree(pt)

                    print 'output tree building result to %s' % outfname

                    treeBuildEnd = time.time()

                    print utils.utils.print_summarization(pt)
                    print 'finished tree building in %.2f seconds' % (treeBuildEnd - treeBuildStart)

        except Exception, e:
            print traceback.print_exc()

            if not self.treebuilder is None:
                self.treebuilder.unload()
            raise

        print '==================================================='


if __name__ == '__main__':
    parser = DiscourseParser(verbose=False, seg=False, output=True, SGML=True, edus=False)
    file_path = '../data/to_be_analysed/review2.txt'
    dists = parser.parse(file_path)
    parser.unload()
