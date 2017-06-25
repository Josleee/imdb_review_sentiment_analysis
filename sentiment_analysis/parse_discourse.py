import os.path
import re
import traceback

import paths
import utils.rst_lib
import utils.rst_lib
import utils.serialize
import utils.utils
from segmentation.segmenter import Segmenter
from treebuilder.build_tree_greedy import GreedyTreeBuilder


class DiscourseParser:
    def __init__(self, file_name, feature_sets='FengHirst',
                 verbose=False, seg=False, output=True, SGML=True, edus=False):
        """
        This is Hilda's segmentation module

        :param feature_sets:
        :param verbose:
        :param seg:
        :param output:
        :param SGML:
        :param edus:
        """

        self.verbose = verbose
        self.seg = seg
        self.output = output
        self.SGML = SGML
        self.edus = edus
        self.file_name = file_name

        self.segmenter = None
        self.dependencies = True
        self.max_iters = 0
        self.feature_sets = feature_sets
        self.smg_tree = None
        self.summary = None

        try:
            self.segmenter = Segmenter(_model_path=os.path.join(paths.SEG_MODEL_PATH),
                                       _model_file="training.scaled.model",
                                       _scale_model_file="bin_scale",
                                       _name="segmenter",
                                       verbose=self.verbose, dependencies=self.dependencies)

        except Exception, e:
            print "*** Loading Segmentation module failed..."
            if self.segmenter is not None:
                self.segmenter.unload()
            raise

        self.tree_builder = None
        try:
            if self.feature_sets == 'FengHirst':
                self.tree_builder = GreedyTreeBuilder(_model_path=paths.TREE_BUILD_MODEL_PATH,
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
            if self.tree_builder is not None:
                self.tree_builder.unload()
            raise

    def unload(self):
        if self.segmenter is not None:
            self.segmenter.unload()
        if self.tree_builder is not None:
            self.tree_builder.unload()

    def parse(self, file_name=None):
        if not file_name:
            file_name = self.file_name

        if not os.path.exists(file_name):
            print '%s does not exist.' % file_name
            return

        print 'Parsing %s' % file_name

        try:
            text = open(file_name).read()
            text = re.sub('\.', '.<s>', text)
            text = re.sub('<s> *<p>', '<p>', text)

            sentences = []
            for para_text in text.split('<p>'):
                # sents = filter(None, re.split('[.?]+', para_text))
                # ref_sents = []
                # for sent in sents:
                #     ref_sents.append(sent.strip() + '.')
                sents = para_text.strip().split('<s>')

                sentences.extend(sents)

            ''' Step 1: segment the each sentence into EDUs '''
            edus = None
            (trees, deps, cuts, edus) = self.segmenter.do_segment(text, edus)
            escaped_edus = self.segmenter.get_escaped_edus(trees, cuts, edus)
            print 'Finished segmentation, segmented into %d EDUs' % len(edus)

            ''' Step 2: build text-level discourse tree '''
            if not self.seg:
                parse_trees = self.tree_builder.build_tree((trees, deps, cuts, edus), "pouet", paths.MODEL_PATH)
                print 'Finished tree building'

                if not parse_trees:
                    print "No tree could be built..."

                    if self.tree_builder is not None:
                        self.tree_builder.unload()
                    return

                # Unescape the parse tree
                if parse_trees and len(parse_trees):
                    pt = parse_trees[0]

                    for i in range(len(escaped_edus)):
                        pt.__setitem__(pt.leaf_treeposition(i), '_!%s!_' % escaped_edus[i])

                    self.smg_tree = utils.utils.print_SGML_tree(pt)
                    self.summary = utils.utils.print_summary(pt)

        except Exception, e:
            print traceback.print_exc()
            if self.segmenter is not None:
                self.segmenter.unload()
            if self.tree_builder is not None:
                self.tree_builder.unload()
            raise

    def get_smg_tree(self):
        return self.smg_tree

    def get_summary(self):
        return self.summary


if __name__ == '__main__':
    parser = DiscourseParser('../data/to_be_analysed/review3.txt')
    parser.parse()
    for ds in parser.get_summary():
        print ds
    parser.unload()
