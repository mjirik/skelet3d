#! /usr/bin/python
# -*- coding: utf-8 -*-
"""
Modul is used for skeleton binary 3D data analysis
"""

# import sys
# import os.path
# path_to_script = os.path.dirname(os.path.abspath(__file__))
# sys.path.append(os.path.join(path_to_script, "../extern/dicom2fem/src"))

from loguru import logger
# import logging
# logger = logging.getLogger(__name__)

import traceback
import numpy as np
import scipy.ndimage
import scipy.interpolate
from io import open
import copy


class SkeletonAnalyser:
    """
    | Example:
    | skan = SkeletonAnalyser(data3d_skel, volume_data, voxelsize_mm)
    | stats = skan.skeleton_analysis()
    
    | data3d_skel: 3d array with skeleton as 1s and background as 0s
    | use_filter_small_objects: removing small objects
    | filter_small_threshold: threshold for small filtering

    :arg cut_wrong_skeleton: remove short skeleton edges to terminal
    :arg aggregate_near_nodes_distance: combine near nodes to one. Parameter 
    defines distance in mm.
    """

    def __init__(
        self,
        data3d_skel,
        volume_data=None,
        voxelsize_mm=[1, 1, 1],
        use_filter_small=False,
        filter_small_threshold=3,
        cut_wrong_skeleton=True,
        do_radius_calculation=True,
        aggregate_near_nodes_distance=0,
        debug_show=False
    ):
        # for not
        self.volume_data = volume_data
        self.voxelsize_mm = voxelsize_mm
        self.aggregate_near_nodes_distance = aggregate_near_nodes_distance
        self.do_radius_calculation = do_radius_calculation

        # get array with 1 for edge, 2 is node and 3 is terminal
        logger.debug("Generating sklabel...")
        if use_filter_small:
            data3d_skel = self.filter_small_objects(data3d_skel, filter_small_threshold)

        self.data3d_skel = data3d_skel

        # generate nodes and enges (sklabel)
        logger.debug("__skeleton_nodes, __generate_sklabel")
        skelet_nodes = self.__skeleton_nodes(data3d_skel)
        self.sklabel = self.__generate_sklabel(skelet_nodes)

        self.cut_wrong_skeleton = cut_wrong_skeleton
        self.curve_order = 2
        self.spline_smoothing = None
        self.debug_show=debug_show

        logger.debug(
            "Inited SkeletonAnalyser - voxelsize:"
            + str(voxelsize_mm)
            + " volumedata:"
            + str(volume_data is not None)
        )
        logger.debug("aggreg %s", self.aggregate_near_nodes_distance)
        # import ipdb; ipdb.set_trace() #  noqa BREAKPOINT
        self.shifted_zero = None
        self.shifted_sklabel = None
        self.stats = None
        self.branch_label = None

    def to_yaml(self, filename):
        if self.stats is None:
            logger.error("Run .skeleton_analysis() before .to_yaml()")
            return

        from ruamel.yaml import YAML

        yaml = YAML(typ="unsafe")
        with open(filename, "wt", encoding="utf-8") as f:
            yaml.dump(self.stats, f)

    def skeleton_analysis(self, guiUpdateFunction=None):
        """
        | Glossary:
        | element: line structure of skeleton connected to node on both ends. (index>0)
        | node: connection point of elements. It is one or few voxelsize_mm. (index<0)
        | terminal: terminal node
        """

        def updateFunction(num, length, part):
            if (
                int(length / 100.0) == 0
                or (num % int(length / 100.0) == 0)
                or num == length
            ):
                if guiUpdateFunction is not None:
                    guiUpdateFunction(num, length, part)
                logger.info(
                    "skeleton_analysis: processed "
                    + str(num)
                    + "/"
                    + str(length)
                    + ", part "
                    + str(part)
                )

        if self.cut_wrong_skeleton:
            updateFunction(0, 1, "cuting wrong skeleton")
            self.__cut_short_skeleton_terminal_edges()

        stats = {}
        len_edg = np.max(self.sklabel)
        len_node = np.min(self.sklabel)
        logger.debug("len_edg: " + str(len_edg) + " len_node: " + str(len_node))

        # init radius analysis
        logger.debug("__radius_analysis_init")
        if self.volume_data is not None and self.do_radius_calculation:
            skdst = self.__radius_analysis_init()

        # get edges and nodes that are near the edge. (+bounding box)
        logger.debug("skeleton_analysis: starting element_neighbors processing")
        self.elm_neigh = {}
        self.elm_box = {}
        for edg_number in list(range(len_node, 0)) + list(range(1, len_edg + 1)):
            self.elm_neigh[edg_number], self.elm_box[
                edg_number
            ] = self.__element_neighbors(edg_number)
            # update gui progress
            updateFunction(
                edg_number + abs(len_node) + 1,
                abs(len_node) + len_edg + 1,
                "generating node->connected_edges lookup table",
            )
        logger.debug("skeleton_analysis: finished element_neighbors processing")
        # clear unneeded data. IMPORTANT!!
        self.__clean_shifted()

        # get main stats
        logger.debug(
            "skeleton_analysis: starting processing part: length, radius, "
            + "curve and connections of edge"
        )
        # TODO switch A and B based on neighborhood maximal radius

        for edg_number in list(range(1, len_edg + 1)):
            # try:
                edgst = {}
                edgst.update(self.__connection_analysis(edg_number))
                if "nodeB_ZYX_mm" in edgst and "nodeA_ZYX_mm" in edgst:
                    edgst = self.__ordered_points_with_pixel_length(edg_number, edgst)
                    edgst = self.__edge_curve(edg_number, edgst)
                    edgst.update(self.__edge_length(edg_number, edgst))
                    edgst.update(self.__edge_vectors(edg_number, edgst))
                else:
                    logger.warning(f"No B point for edge ID {edg_number}. No length computation.")
                    self.show_label_neighborhood(edg_number)

                # edgst = edge_analysis(sklabel, i)
                if self.volume_data is not None and self.do_radius_calculation:
                    edgst["radius_mm"] = float(
                        self.__radius_analysis(edg_number, skdst)
                    )  # slow (this takes most of time)
                stats[edgst["id"]] = edgst

                # update gui progress
                updateFunction(
                    edg_number, len_edg, "length, radius, curve, connections of edge"
                )
            # except Exception as e:
            #     logger.warning(
            #         "Problem in connection analysis\n" + traceback.format_exc()
            #     )

        logger.debug(
            "skeleton_analysis: finished processing part: length, radius, "
            + "curve, connections of edge"
        )

        # @TODO dokončit
        logger.debug(
            "skeleton_analysis: starting processing part: angles of connected edges"
        )
        for edg_number in list(range(1, len_edg + 1)):
            try:
                if "nodeB_ZYX_mm" in edgst and "nodeA_ZYX_mm" in edgst:
                    edgst = stats[edg_number]
                    edgst.update(self.__connected_edge_angle(edg_number, stats))

                updateFunction(edg_number, len_edg, "angles of connected edges")
            except Exception as e:
                logger.warning("Problem in angle analysis\n" + traceback.format_exc())

        self.stats = stats
        logger.debug(
            "skeleton_analysis: finished processing part: angles of connected edges"
        )

        return stats

    def stats_as_dataframe(self):
        import pandas as pd
        import exsu.dili
        if self.stats is None:
            msg = "Run skeleton_analyser before stats_as_dataframe()"
            logger.error(msg)
            raise RuntimeError(msg)

        # import imtools.dili
        df = pd.DataFrame()
        for stats_key in self.stats:
            one_edge = copy.copy(self.stats[stats_key])
            k = "orderedPoints_mm_X"
            if k in one_edge:
                one_edge[k] = str(one_edge[k])
            k = "orderedPoints_mm_Y"
            if k in one_edge:
                one_edge[k] = str(one_edge[k])
            k = "orderedPoints_mm_Z"
            if k in one_edge:
                one_edge[k] = str(one_edge[k])
            k = "orderedPoints_mm"
            if k in one_edge:
                one_edge[k] = str(one_edge[k])
            # one_edge[]
            one_dct = exsu.dili.flatten_dict_join_keys(one_edge, simplify_iterables=True)
            # df_one = pd.DataFrame(one_dct)

            df_one = pd.DataFrame([list(one_dct.values())], columns=list(one_dct.keys()))
            df = df.append(df_one, ignore_index=True)
        return df



    def __remove_edge_from_stats(self, stats, edge):
        logger.debug("Cutting edge id:" + str(edge) + " from stats")
        edg_stats = stats[edge]

        connected_edgs = edg_stats["connectedEdgesA"] + edg_stats["connectedEdgesB"]

        for connected in connected_edgs:
            try:
                stats[connected]["connectedEdgesA"].remove(edge)
            except:
                pass

            try:
                stats[connected]["connectedEdgesB"].remove(edge)
            except:
                pass

        del stats[edge]

        return stats

    def __clean_shifted(self):
        del self.shifted_zero  # needed by __element_neighbors
        self.shifted_zero = None
        del self.shifted_sklabel  # needed by __element_neighbors
        self.shifted_sklabel = None
        # mozna fix kratkodobych potizi, ale skutecny problem byl jinde
        # try:
        #     del(self.shifted_zero) # needed by __element_neighbors
        # except:
        #     logger.warning('self.shifted_zero does not exsist')
        # try:
        #     del(self.shifted_sklabel) # needed by __element_neighbors
        # except:
        #     logger.warning('self.shifted_zero does not exsist')

    def show_label_neighborhood(self, elm, margin=3):
        wh = np.where(self.sklabel == elm)
        logger.trace(f"wh={wh}")
        x0 = np.max(wh[0])
        y0 = np.max(wh[1])
        z0 = np.max(wh[2])
        x1 = np.min(wh[0])
        y1 = np.min(wh[1])
        z1 = np.min(wh[2])

        sklabel_part = self.sklabel[
                       max(int(x0 - margin), 0):min(int(x1 + margin + 1), self.sklabel.shape[0]),
                       max(int(y0 - margin), 0):min(int(y1 + margin + 1), self.sklabel.shape[1]),
                       max(int(z0 - margin), 0):min(int(z1 + margin + 1), self.sklabel.shape[2]),
                       ]
        logger.debug(f"sklabel_part={sklabel_part}")
        if self.debug_show:
            import sed3
            ed = sed3.sed3(sklabel_part)
            ed.show()

    def __cut_short_skeleton_terminal_edges(self, cut_ratio=2.0):
        """
        cut_ratio = 2.0 -> if radius of terminal edge is 2x its lenght or more,
        remove it
        """

        def remove_elm(elm_id, elm_neigh, elm_box, sklabel):
            sklabel[sklabel == elm_id] = 0
            del elm_neigh[elm_id]
            del elm_box[elm_id]
            for elm in elm_neigh:
                elm_neigh[elm] = [x for x in elm_neigh[elm] if x != elm]
            return elm_neigh, elm_box, sklabel

        len_edg = np.max(self.sklabel)
        len_node = np.min(self.sklabel)
        logger.debug("len_edg: " + str(len_edg) + " len_node: " + str(len_node))

        # get edges and nodes that are near the edge. (+bounding box)
        logger.debug("skeleton_analysis: starting element_neighbors processing")
        self.elm_neigh = {}
        self.elm_box = {}
        for edg_number in list(range(len_node, 0)) + list(range(1, len_edg + 1)):
            self.elm_neigh[edg_number], self.elm_box[
                edg_number
            ] = self.__element_neighbors(edg_number)
        logger.debug("skeleton_analysis: finished element_neighbors processing")
        # clear unneeded data. IMPORTANT!!

        self.__clean_shifted()
        # remove edges+nodes that are not connected to rest of the skeleton
        logger.debug(
            "skeleton_analysis: Cut - Removing edges that are not"
            + " connected to rest of the skeleton (not counting its nodes)"
        )
        cut_elm_neigh = dict(self.elm_neigh)
        cut_elm_box = dict(self.elm_box)
        for elm in self.elm_neigh:
            elm = int(elm)
            if elm > 0:  # if edge
                conn_nodes = [i for i in self.elm_neigh[elm] if i < 0]
                conn_edges = []
                for n in conn_nodes:
                    if n in self.elm_neigh:
                        nn = self.elm_neigh[n]  # get neighbours elements of node
                    else:
                        logger.debug(f"Node {str(n)} not found! May be already deleted.")
                        continue

                    for (e) in (nn):  # if there are other edges connected to node add them to conn_edges
                        if e > 0 and e not in conn_edges and e != elm:
                            conn_edges.append(e)

                if (len(conn_edges) == 0):  # if no other edges are connected to nodes, remove from skeleton
                    logger.debug(f"removing edge {str(elm)} with its nodes {str(self.elm_neigh[elm])}")
                    for night in self.elm_neigh[elm]:
                        remove_elm(night, cut_elm_neigh, cut_elm_box, self.sklabel)
        self.elm_neigh = cut_elm_neigh
        self.elm_box = cut_elm_box

        # remove elements that are not connected to the rest of skeleton
        logger.debug("skeleton_analysis: Cut - Removing elements that are not connected to rest of the skeleton")
        cut_elm_neigh = dict(self.elm_neigh)
        cut_elm_box = dict(self.elm_box)
        for elm in self.elm_neigh:
            elm = int(elm)
            if len(self.elm_neigh[elm]) == 0:
                logger.debug(f"removing element {str(elm)}")
                remove_elm(elm, cut_elm_neigh, cut_elm_box, self.sklabel)
        self.elm_neigh = cut_elm_neigh
        self.elm_box = cut_elm_box

        # get list of terminal nodes
        logger.debug("skeleton_analysis: Cut - get list of terminal nodes")
        terminal_nodes = []
        for elm in self.elm_neigh:
            if elm < 0:  # if node
                conn_edges = [i for i in self.elm_neigh[elm] if i > 0]
                if len(conn_edges) == 1:  # if only one edge is connected
                    terminal_nodes.append(elm)

        # init radius analysis
        logger.debug("__radius_analysis_init")
        if self.volume_data is not None:
            skdst = self.__radius_analysis_init()

        # removes end terminal edges based on radius/length ratio
        logger.debug(
            "skeleton_analysis: Cut - Removing bad terminal edges based on"
            + " radius/length ratio"
        )
        cut_elm_neigh = dict(self.elm_neigh)
        cut_elm_box = dict(self.elm_box)
        for tn in terminal_nodes:
            te = [i for i in self.elm_neigh[tn] if i > 0][0]  # terminal edge
            radius = float(self.__radius_analysis(te, skdst))
            edgst = self.__connection_analysis(int(te))
            edgst = self.__ordered_points_with_pixel_length(edg_number, edg_stats=edgst)
            edgst.update(self.__edge_length(edg_number, edgst))
            length = edgst["lengthEstimation"]

            # logger.debug(str(radius / float(length))+" "+str(radius)+" "+str(length))
            if (radius / float(length)) > cut_ratio:
                logger.debug(f"removing edge {str(te)} with its terminal node.")
                remove_elm(elm, cut_elm_neigh, cut_elm_box, self.sklabel)
        self.elm_neigh = cut_elm_neigh
        self.elm_box = cut_elm_box

        self.__check_nodes_to_be_just_curve_from_elm_neig()

        # regenerate new nodes and edges from cut skeleton (sklabel)
        logger.debug("Regenerate new nodes and edges from cut skeleton")
        self.sklabel[self.sklabel != 0] = 1
        skelet_nodes = self.__skeleton_nodes(self.sklabel)
        self.sklabel = self.__generate_sklabel(skelet_nodes)

    def __check_nodes_to_be_just_curve_from_elm_neig(self):
        """
        Detect curve-like nodes from elm_neigh


        :return:
        """
        # check if some nodes are not forks but just curves
        logger.debug("skeleton_analysis: Cut - check if some nodes are not forks but just curves")
        for elm in self.elm_neigh:
            if elm < 0:
                conn_edges = [i for i in self.elm_neigh[elm] if i > 0]
                if len(conn_edges) == 2:
                    self.show_label_neighborhood(elm)
                    logger.debug(f"Node {str(elm)} is just a curve."+
                                 " It will be fixed automatically on on regeneration of skeleton nodes")
                    # wh = np.where(self.sklabel == elm)
                    # print(f"wh={wh}")
                    # x = wh[0][0]
                    # y = wh[1][0]
                    # z = wh[2][0]
                    #
                    # sklabel_part = self.sklabel[
                    #     int(x - 2):int(x + 3),
                    #     int(y - 2):int(y + 3),
                    #     int(z - 2):int(z + 3),
                    # ]
                    # print(f"sklabel_part={sklabel_part}")
                    # import sed3
                    # ed = sed3.sed3(sklabel_part)
                    # ed.show()
                    # print("slabel_part visualized")


    def __skeleton_nodes(self, data3d_skel, kernel=None):
        """
        Return 3d ndarray where 0 is background, 1 is skeleton, 2 is node
        and 3 is terminal node
        """

        if kernel is None:
            kernel = np.ones([3, 3, 3])

        mocnost = scipy.ndimage.filters.convolve(data3d_skel, kernel) * data3d_skel

        nodes = (mocnost > 3).astype(np.int8)
        terminals = ((mocnost == 2) | (mocnost == 1)).astype(np.int8)

        data3d_skel[nodes == 1] = 2
        data3d_skel[terminals == 1] = 3
        # maybe swap next two lines
        data3d_skel = self.__skeleton_nodes_aggregation(data3d_skel)
        data3d_skel = self.__remove_terminal_nodes_in_neghborhood_of_the_branching_node(data3d_skel)

        return data3d_skel

    def __remove_terminal_nodes_in_neghborhood_of_the_branching_node(self, data3d_skel, kernel=None):
        """
        Delete terminal nodes with 0 length edge.
                    #
                    #       T
                    #      N
                    #    EE EEE
        :param data3d_skel: ndimage 0-nothing, 1-edge, 2-nodes, 3-terminal
        :return:
        """
        if kernel is None:
            kernel = np.ones([3, 3, 3])

        # mocnost = scipy.ndimage.filters.convolve(data3d_skel, kernel) * data3d_skel

        nd_dil = scipy.ndimage.binary_dilation(data3d_skel == 2, kernel)
        # delete one
        data3d_skel[(nd_dil & (data3d_skel == 3)) > 0] = 0
        return data3d_skel

    def __skeleton_nodes_aggregation(self, data3d_skel):
        """

        aggregate near nodes
        """

        method = "auto"
        if self.aggregate_near_nodes_distance > 0:
            # d1_dbg = data3d_skel.copy()
            # sklabel_edg0, len_edg0 = scipy.ndimage.label(data3d_skel)

            # print('generate structure')
            structure = generate_binary_elipsoid(
                self.aggregate_near_nodes_distance / np.asarray(self.voxelsize_mm)
            )
            # print('perform dilation ', data3d_skel.shape)
            # import ipdb; ipdb.set_trace() #  noqa BREAKPOINT

            # TODO select best method
            # old simple method
            nd_dil = scipy.ndimage.binary_dilation(data3d_skel == 2, structure)

            # per partes method even slower
            # nd_dil = self.__skeleton_nodes_aggregation_per_each_node(data3d_skel==2, structure)
            data3d_skel[nd_dil & data3d_skel > 0] = 2
            # sklabel_edg1, len_edg1 = scipy.ndimage.label(data3d_skel)
            # import ipdb; ipdb.set_trace() #  noqa BREAKPOINT
            # import sed3
            # ed = sed3.sed3(data3d_skel)
            # ed.show()

        return data3d_skel

    def __skeleton_nodes_aggregation_per_each_node(self, data3d_skel2, structure):
        node_list = np.nonzero(data3d_skel2)
        nlz = zip(node_list[0], node_list[1], node_list[2])
        for node_xyz in nlz:
            data3d_skel2 = self.__node_dilatation(data3d_skel2, node_xyz, structure)

        return data3d_skel2

    def __node_dilatation(self, data3d_skel2, node_xyz, structure):
        """
        this function is called for each node
        """
        border = structure.shape

        xlim = [
            max(0, node_xyz[0] - border[0]),
            min(data3d_skel2.shape[0], node_xyz[0] + border[0]),
        ]
        ylim = [
            max(0, node_xyz[1] - border[1]),
            min(data3d_skel2.shape[1], node_xyz[1] + border[1]),
        ]
        zlim = [
            max(0, node_xyz[2] - border[2]),
            min(data3d_skel2.shape[2], node_xyz[2] + border[2]),
        ]

        # dilation on small box
        nd_dil = scipy.ndimage.binary_dilation(
            data3d_skel2[xlim[0] : xlim[1], ylim[0] : ylim[1], zlim[0] : zlim[1]] == 2,
            structure,
        )

        # nd_dil = nd_dil * 2

        data3d_skel2[xlim[0] : xlim[1], ylim[0] : ylim[1], zlim[0] : zlim[1]] = nd_dil

        return data3d_skel2

    def __label_edge_by_its_terminal(self, labeled_terminals):
        import functools
        import scipy

        def max_or_zero(a):
            return min(np.max(a), 0)

        fp = np.ones([3, 3, 3], dtype=np.int)
        median_filter = functools.partial(
            scipy.ndimage.generic_filter, function=np.max, footprint=fp
        )
        mf = median_filter(labeled_terminals)

        for label in list(range(np.min(labeled_terminals), 0)):
            neigh = np.min(mf[labeled_terminals == label])
            labeled_terminals[labeled_terminals == neigh] = label
        return labeled_terminals

    def filter_small_objects(self, skel, threshold=4):
        """
        Remove small objects from 
        terminals are connected to edges
        """
        skeleton_nodes = self.__skeleton_nodes(skel)
        logger.debug("skn 2 " + str(np.sum(skeleton_nodes == 2)))
        logger.debug("skn 3 " + str(np.sum(skeleton_nodes == 3)))
        # delete nodes
        nodes = skeleton_nodes == 2
        skeleton_nodes[nodes] = 0
        # pe = ped.sed3(skeleton_nodes)
        # pe.show()
        labeled_terminals = self.__generate_sklabel(skeleton_nodes)

        logger.debug("deleted nodes")
        labeled_terminals = self.__label_edge_by_its_terminal(labeled_terminals)
        # pe = ped.sed3(labeled_terminals)
        # pe.show()
        for i in list(range(np.min(labeled_terminals), 0)):
            lti = labeled_terminals == i
            if np.sum(lti) < threshold:
                # delete small
                labeled_terminals[lti] = 0
                logger.debug("mazani %s %s" % (str(i), np.sum(lti)))
        # bring nodes back
        labeled_terminals[nodes] = 1
        return (labeled_terminals != 0).astype(np.int)

    def __generate_sklabel(self, skelet_nodes):

        sklabel_edg, len_edg = scipy.ndimage.label(
            skelet_nodes == 1, structure=np.ones([3, 3, 3])
        )
        sklabel_nod, len_nod = scipy.ndimage.label(
            skelet_nodes > 1, structure=np.ones([3, 3, 3])
        )

        sklabel = sklabel_edg - sklabel_nod

        return sklabel

    def get_branch_label(self):
        """

        :return:
        """
        if self.branch_label is None:
            self.__generate_branch_label()
        if self.volume_data is not None:
            self.branch_label[self.volume_data == 0] = 0
        return self.branch_label

    def __generate_branch_label(self, ignore_nodes=True):
        # if self.sklabel is None:
        #     sknodes = self.__skeleton_nodes(self.data3d_skel)
        #     self.sklabel = self.__generate_sklabel(skelet_nodes=sknodes)

        import imma
        import imma.image_manipulation

        if ignore_nodes:
            import copy

            sklabel = self.sklabel.copy()
            # delete nodes
            sklabel[sklabel < 0] = 0

        else:
            sklabel = self.sklabel

        self.branch_label = imma.image_manipulation.distance_segmentation(sklabel)

        pass

    def __edge_vectors(self, edg_number, edg_stats):
        """
        | Return begin and end vector of edge.
        | run after __edge_curve()
        """
        # this edge
        try:
            curve_params = edg_stats["curve_params"]
            vectorA = self.__get_vector_from_curve(0.25, 0, curve_params)
            vectorB = self.__get_vector_from_curve(0.75, 1, curve_params)
        except:  # Exception as ex:
            logger.warning(traceback.format_exc())
            # print(ex)
            return {}

        return {"vectorA": vectorA.tolist(), "vectorB": vectorB.tolist()}

    def __vectors_to_angle_deg(self, v1, v2):
        """
        Return angle of two vectors in degrees
        """
        # get normalised vectors
        v1u = v1 / np.linalg.norm(v1)
        v2u = v2 / np.linalg.norm(v2)
        # print('v1u ', v1u, ' v2u ', v2u)

        angle = np.arccos(np.dot(v1u, v2u))
        # special cases
        if np.isnan(angle):
            if (v1u == v2u).all():
                angle == 0
            else:
                angle == np.pi

        angle_deg = np.degrees(angle)

        # print('angl ', angle, ' angl_deg ', angle_deg)
        return angle_deg

    def __vector_of_connected_edge(self, edg_number, stats, edg_end, con_edg_order):
        """
        | find common node with connected edge and its vector

        | edg_end: Which end of edge you want ('A' or 'B')
        | con_edg_order: Which edge of selected end of edge you want (0,1)
        """
        if edg_end == "A" and "connectedEdgesA" in stats[edg_number]:
            connectedEdges = stats[edg_number]["connectedEdgesA"]
            ndid = "nodeIdA"
        elif edg_end == "B" and "connectedEdgesB" in stats[edg_number]:
            connectedEdges = stats[edg_number]["connectedEdgesB"]
            ndid = "nodeIdB"
        else:
            logger.debug("Wrong edg_end in __vector_of_connected_edge()")
            return None
        if len(connectedEdges) <= con_edg_order:
            return None
        connected_edge_id = connectedEdges[con_edg_order]

        if len(stats) < connected_edge_id:
            logger.warning(
                "Not found connected edge with ID: " + str(connected_edge_id)
            )
            return None
        connectedEdgeStats = stats[connected_edge_id]
        # import pdb; pdb.set_trace()
        tagA = f"nodeA_ZYX_mm"
        tagB = f"nodeB_ZYX_mm"
        tag = f"node{edg_end}_ZYX_mm"
        tag_other = f"node{'A' if edg_end == 'A' else 'B'}_ZYX_mm"
        logger.trace(f"node{edg_end} = {stats[edg_number][tag]} -- {stats[edg_number][tag_other]}")
        logger.trace(f"connected_edge_id={connected_edge_id}, {connectedEdgeStats[tagA]} {connectedEdgeStats[tagB]}")


        if stats[edg_number][ndid] == connectedEdgeStats["nodeIdA"]:
            # sousední hrana u uzlu na konci 0 má stejný node na
            # svém konci 0 jako
            # nynější hrana
            if "vectorA" in connectedEdgeStats:
                vector = connectedEdgeStats["vectorA"]
            else:
                logger.debug(f"missing key vectorA in edg_number={edg_number}")
        elif stats[edg_number][ndid] == connectedEdgeStats["nodeIdB"]:
            if "vectorB" in connectedEdgeStats:
                vector = connectedEdgeStats["vectorB"]
            else:
                logger.debug(f"missing key vectorB in edg_number={edg_number}")

        return vector

    def perpendicular_to_two_vects(self, v1, v2):
        # determinant
        a = (v1[1] * v2[2]) - (v1[2] * v2[1])
        b = -((v1[0] * v2[2]) - (v1[2] * v2[0]))
        c = (v1[0] * v2[1]) - (v1[1] * v2[0])
        return [a, b, c]

    def projection_of_vect_to_xy_plane(self, vect, xy1, xy2, edg_number=None):
        """
        Return porojection of vect to xy plane given by vectprs xy1 and xy2
        :param edg_number: For debug reasons
        """
        normal_vector = self.perpendicular_to_two_vects(xy1, xy2)
        norm = np.linalg.norm(normal_vector)
        logger.trace(f"edge_vect={vect}, xy1={xy1}, xy2={xy2}, normal_vector={normal_vector}")
        if norm == 0:
            logger.debug(f"norm of vector of edge {edg_number} is 0")
            return None
        vect_proj = np.array(vect) - (
            np.dot(vect, normal_vector) / norm** 2
        ) * np.array(normal_vector)
        return vect_proj

    def __connected_edge_angle_on_one_end(self, edg_number, stats, edg_end):
        """

        creates phiXa, phiXb and phiXc.
        :param edg_number: integer with edg_number
        :param stats:  dictionary with all statistics and computations
        :param edg_end: letter 'A' or 'B'

        See Schwen2012 : Analysis and algorithmic generation of hepatic vascular
        system.
        """
        out = {}

        vector_key = "vector" + edg_end
        vectorX0 = None
        vectorX1 = None
        vector = None
        if vector_key in stats[edg_number]:
            vector = stats[edg_number][vector_key]
        else:
            logger.debug(f"Vector key {vector_key} not found for edge {edg_number}.")

        # try:
        vectorX0 = self.__vector_of_connected_edge(edg_number, stats, edg_end, 0)
        # phiXa = self.__vectors_to_angle_deg(vectorX0, vector)

        # out.update({'phiA0' + edg_end + 'a': phiXa.tolist()})
        # except:  # Exception as e:
        #     logger.debug(traceback.format_exc())
        # try:
        vectorX1 = self.__vector_of_connected_edge(edg_number, stats, edg_end, 1)
        # except:  # Exception as e:
        #     logger.debug(traceback.format_exc())
        out["phi" + "a"] = np.NaN
        out["phi" + "b"] = np.Nan
        out["phi" + "c"] = np.Nan
        out["vector" + "0"] = np.Nan
        out["vector" + "1"] = np.Nan

        if (vectorX0 is not None) and (vectorX1 is not None) and (vector is not None):
            norm_vectorX0 = np.linalg.norm(vectorX0)
            norm_vectorX1 = np.linalg.norm(vectorX1)
            if (norm_vectorX0 > 0) and (norm_vectorX1 > 0):
                vect_proj = self.projection_of_vect_to_xy_plane(vector, vectorX0, vectorX1, edg_number=edg_number)
                if vect_proj is not None:
                    phiXa = self.__vectors_to_angle_deg(vectorX0, vectorX1)
                    phiXb = self.__vectors_to_angle_deg(vector, vect_proj)
                    vectorX01avg = np.array(vectorX0 / norm_vectorX0) + np.array(
                        vectorX1 / norm_vectorX1
                    )
                    phiXc = self.__vectors_to_angle_deg(vectorX01avg, vect_proj)

                    out["phi" + "a"] = phiXa.tolist() if phiXa else np.NaN
                    out["phi" + "b"] = phiXb.tolist() if phiXb else np.NaN
                    out["phi" + "c"] = phiXc.tolist() if phiXc else np.NaN
                    out["vector" + "0"] = vectorX0 if vectorX0 else np.NaN
                    out["vector" + "1"] = vectorX1 if vectorX0 else np.NaN

            # out.update(
            #     {
            #         "phi" + "b": phiXb.tolist(),
            #         "phi" + "c": phiXc.tolist(),
            #         "vector" + "0": vectorX0,
            #         "vector" + "1": vectorX1,
            #     }
            # )
            # out.update({
            #     'phi' + edg_end + 'a': phiXa.tolist(),
            #     'phi' + edg_end + 'b': phiXb.tolist(),
            #     'phi' + edg_end + 'c': phiXc.tolist(),
            #     'vector' + edg_end + '0': vectorX0,
            #     'vector' + edg_end + '1': vectorX1,
            #     })
            return out
            # return phiXA, phiXb, phiXc, vectorX0, vectorX1

        # except:  # Exception as e:
        #     logger.warning(traceback.print_exc())

        return None

    def __connected_edge_angle(self, edg_number, stats):
        """
        count angles betwen end vectors of edges
        """

        def setAB(statsA, statsB):

            stA = {}
            stB = {}
            edg_end = "A"
            statstmp = statsA
            if statsA is not None:
                stA = {
                    "phi" + edg_end + "a": statstmp["phia"],
                    "phi" + edg_end + "b": statstmp["phib"],
                    "phi" + edg_end + "c": statstmp["phic"],
                    "vector" + edg_end + "0": statstmp["vector0"],
                    "vector" + edg_end + "1": statstmp["vector1"],
                }

            edg_end = "B"
            statstmp = statsB
            if statsB is not None:
                stB = {
                    "phi" + edg_end + "a": statstmp["phia"],
                    "phi" + edg_end + "b": statstmp["phib"],
                    "phi" + edg_end + "c": statstmp["phic"],
                    "vector" + edg_end + "0": statstmp["vector0"],
                    "vector" + edg_end + "1": statstmp["vector1"],
                }
            return stA, stB

        statsA = self.__connected_edge_angle_on_one_end(edg_number, stats, "A")
        statsB = self.__connected_edge_angle_on_one_end(edg_number, stats, "B")
        stA, stB = setAB(statsA, statsB)
        out = {}
        out.update(stA)

        out.update(stB)
        angleA0 = 0
        return out

    def __swapAB(self, edg_number, stats):
        """
        Function can swap A and B node
        :param edg_number:
        :param stats:
        :return:
        """
        import copy

        keys = stats[edg_number].keys()
        # vector = stats[edg_number][vector_key]
        for key in keys:
            k2 = copy.copy(key)
            idx = k2.find("A")
            k2[idx] = "B"
            if k2 in keys:
                tmp = stats[edg_number][key]
                stats[edg_number][key] = stats[edg_number][k2]

        pass

    def __get_vector_from_curve(self, t0, t1, curve_params):
        return np.array(curve_model(t1, curve_params)) - np.array(
            curve_model(t0, curve_params)
        )

    # def node_analysis(sklabel):
    # pass

    def __element_neighbors(self, el_number):
        """
        Gives array of element neighbors numbers (edges+nodes/terminals)

        | input:
        |   self.sklabel - original labeled data
        |   el_number - element label

        | uses/creates:
        |   self.shifted_sklabel - all labels shifted to positive numbers
        |   self.shifted_zero - value of original 0

        | returns:
        |   array of neighbor values
        |        - nodes for edge, edges for node
        |   element bounding box (with border)
        """
        # check if we have shifted sklabel, if not create it.
        # try:
        #     self.shifted_zero
        #     self.shifted_sklabel
        # except AttributeError:
        if (self.shifted_sklabel is None) or (self.shifted_zero is None):
            logger.debug("Generating shifted sklabel...")
            self.shifted_zero = abs(np.min(self.sklabel)) + 1
            self.shifted_sklabel = self.sklabel + self.shifted_zero

        el_number_shifted = el_number + self.shifted_zero

        BOUNDARY_PX = 5

        if el_number < 0:
            # cant have max_label<0
            box = scipy.ndimage.find_objects(
                self.shifted_sklabel, max_label=el_number_shifted
            )
        else:
            box = scipy.ndimage.find_objects(self.sklabel, max_label=el_number)
        box = box[len(box) - 1]

        d = max(0, box[0].start - BOUNDARY_PX)
        u = min(self.sklabel.shape[0], box[0].stop + BOUNDARY_PX)
        slice_z = slice(d, u)
        d = max(0, box[1].start - BOUNDARY_PX)
        u = min(self.sklabel.shape[1], box[1].stop + BOUNDARY_PX)
        slice_y = slice(d, u)
        d = max(0, box[2].start - BOUNDARY_PX)
        u = min(self.sklabel.shape[2], box[2].stop + BOUNDARY_PX)
        slice_x = slice(d, u)
        box = (slice_z, slice_y, slice_x)

        sklabelcr = self.sklabel[box]

        # element crop
        element = sklabelcr == el_number

        dilat_element = scipy.ndimage.morphology.binary_dilation(
            element, structure=np.ones([3, 3, 3])
        )

        neighborhood = sklabelcr * dilat_element

        neighbors = np.unique(neighborhood)
        neighbors = neighbors[neighbors != 0]
        neighbors = neighbors[neighbors != el_number]

        if el_number > 0:  # elnumber is edge
            neighbors = neighbors[neighbors < 0]  # return nodes
        elif el_number < 0:  # elnumber is node
            neighbors = neighbors[neighbors > 0]  # return edge
        else:
            logger.warning("Element is zero!!")
            neighbors = []

        return neighbors, box

    def __length_from_curve_spline(self, edg_stats, N=20, spline_order=3):
        """
        Get length from list of points in edge stats.

        :param edg_stats: dict with key "orderedPoints_mm"
        :param N: Number of points used for reconstruction
        :param spline_order: Order of spline
        :return:
        """
        pts_mm_ord = edg_stats["orderedPoints_mm"]
        if len(pts_mm_ord[0]) <= spline_order:
            return None
        tck, u = scipy.interpolate.splprep(
            pts_mm_ord, s=self.spline_smoothing, k=spline_order
        )
        t = np.linspace(0.0, 1.0, N)
        x, y, z = scipy.interpolate.splev(t, tck)
        length = self.__count_length(x, y, z, N)
        return length

    def __length_from_curve_poly(self, edg_stats, N=10):

        px = np.poly1d(edg_stats["curve_params"]["fitParamsX"])
        py = np.poly1d(edg_stats["curve_params"]["fitParamsY"])
        pz = np.poly1d(edg_stats["curve_params"]["fitParamsZ"])

        t = np.linspace(0.0, 1.0, N)

        x = px(t)
        y = py(t)
        z = pz(t)

        return self.__count_length(x, y, z, N)

    def __count_length(self, x, y, z, N):
        length = 0
        for i in list(range(N - 1)):
            p1 = np.asarray([x[i], y[i], z[i]])
            p2 = np.asarray([x[i + 1], y[i + 1], z[i + 1]])
            length += np.linalg.norm(p2 - p1)

        return length

    def __edge_length(self, edg_number, edg_stats):
        """
        Computes estimated length of edge, distance from end nodes and
        tortosity.

        | needs:
        |   edg_stats['nodeIdA']
        |   edg_stats['nodeIdB']
        |   edg_stats['nodeA_ZYX']
        |   edg_stats['nodeB_ZYX']

        | output:
        |    'lengthEstimation'  - Estimated length of edge
        |    'nodesDistance'     - Distance between connected nodes
        |    'tortuosity'        - Tortuosity
        """
        # test for needed data
        try:
            edg_stats["nodeIdA"]
            edg_stats["nodeA_ZYX"]
        except:
            hasNodeA = False
        else:
            hasNodeA = True

        try:
            edg_stats["nodeIdB"]
            edg_stats["nodeB_ZYX"]
        except:
            hasNodeB = False
        else:
            hasNodeB = True

        if (not hasNodeA) and (not hasNodeB):
            logger.warning(
                "__edge_length doesnt have needed data!!! Using unreliable" + "method."
            )
            length = float(
                np.sum(self.sklabel[self.elm_box[edg_number]] == edg_number) + 2
            )
            medium_voxel_length = (
                self.voxelsize_mm[0] + self.voxelsize_mm[1] + self.voxelsize_mm[2]
            ) / 3.0
            length = length * medium_voxel_length

            stats = {
                "lengthEstimation": float(length),
                "nodesDistance": None,
                "tortuosity": 1,
            }

            return stats

        # crop used area
        box = self.elm_box[edg_number]
        sklabelcr = self.sklabel[box]

        # get absolute position of nodes
        if hasNodeA and not hasNodeB:
            logger.warning("__edge_length has only one node!!! using one node mode.")
            nodeA_pos_abs = edg_stats["nodeA_ZYX"]
            one_node_mode = True
        elif hasNodeB and not hasNodeA:
            logger.warning("__edge_length has only one node!!! using one node mode.")
            nodeA_pos_abs = edg_stats["nodeB_ZYX"]
            one_node_mode = True
        else:
            nodeA_pos_abs = edg_stats["nodeA_ZYX"]
            nodeB_pos_abs = edg_stats["nodeB_ZYX"]
            one_node_mode = False

        # get realtive position of nodes [Z,Y,X]
        nodeA_pos = np.array(
            [
                nodeA_pos_abs[0] - box[0].start,
                nodeA_pos_abs[1] - box[1].start,
                nodeA_pos_abs[2] - box[2].start,
            ]
        )
        if not one_node_mode:
            nodeB_pos = np.array(
                [
                    nodeB_pos_abs[0] - box[0].start,
                    nodeB_pos_abs[1] - box[1].start,
                    nodeB_pos_abs[2] - box[2].start,
                ]
            )
        # get position in mm
        nodeA_pos = nodeA_pos * self.voxelsize_mm
        if not one_node_mode:
            nodeB_pos = nodeB_pos * self.voxelsize_mm
        else:
            nodeB_pos = None

        # get positions of edge points
        # points = (sklabelcr == edg_number).nonzero()
        # points_mm = [
        #     np.array(points[0] * self.voxelsize_mm[0]),
        #     np.array(points[1] * self.voxelsize_mm[1]),
        #     np.array(points[2] * self.voxelsize_mm[2])
        # ]
        #
        # _, length_pixel = self.__ordered_points_mm(
        #     points_mm, nodeA_pos, nodeB_pos, one_node_mode)
        # length_pixel = float(length_pixel)
        length_pixel = edg_stats["lengthEstimationPixel"]
        length = length_pixel
        length_poly = None
        length_spline = None
        if not one_node_mode:

            try:
                length_poly = self.__length_from_curve_poly(edg_stats)
            except:
                logger.debug(f"problem with length_poly edg_number={edg_number}")
            try:
                length_spline = self.__length_from_curve_spline(edg_stats)
            except:
                logger.info(traceback.format_exc())
                logger.info("problem with length_spline")
                logger.error(f"problem with spline edg_number={edg_number}")

            if length_spline is not None:
                length = length_spline
            else:
                pass
        # get distance between nodes
        pts_mm = np.asarray(edg_stats["orderedPoints_mm"])
        nodes_distance = np.linalg.norm(pts_mm[:, 0] - pts_mm[:, -1])

        stats = {
            "lengthEstimationPoly": float_or_none(length_poly),
            "lengthEstimationSpline": float_or_none(length_spline),
            "lengthEstimation": float(length),
            # 'lengthEstimationPixel': float(length_pixel),
            "nodesDistance": float_or_none(nodes_distance),
            "tortuosity": float(length / float(nodes_distance)),
        }

        return stats

    def __ordered_points_with_pixel_length(self, edg_number, edg_stats):
        box = self.elm_box[edg_number]

        sklabelcr = self.sklabel[box]
        # get positions of edge points
        point0_mm = np.array(edg_stats["nodeA_ZYX_mm"])
        point1_mm = np.array(edg_stats["nodeB_ZYX_mm"])

        pts_mm_ord, pixel_length = get_ordered_points_mm_from_labeled_image(
            sklabelcr,
            edg_number,
            self.voxelsize_mm,
            point0_mm,
            point1_mm,
            offset_mm=box,
        )

        # edg_stats["orderedPoints_mm"]
        edg_stats["orderedPoints_mm_X"] = pts_mm_ord[0]
        edg_stats["orderedPoints_mm_Y"] = pts_mm_ord[1]
        edg_stats["orderedPoints_mm_Z"] = pts_mm_ord[2]
        edg_stats["orderedPoints_mm"] = pts_mm_ord

        edg_stats["lengthEstimationPixel"] = pixel_length
        return edg_stats

    def __edge_curve(self, edg_number, edg_stats):
        """
        Return params of curve and its starts and ends locations

        | needs:
        |    edg_stats['nodeA_ZYX_mm']
        |    edg_stats['nodeB_ZYX_mm']
        """
        retval = {}
        if "orderedPoints_mm" not in edg_stats:
            edg_stats = self.__ordered_points_with_pixel_length(edg_number, edg_stats)
        pts_mm_ord = edg_stats["orderedPoints_mm"]
        try:
            point0_mm = np.array(edg_stats["nodeA_ZYX_mm"])
            point1_mm = np.array(edg_stats["nodeB_ZYX_mm"])
            t = np.linspace(0.0, 1.0, len(pts_mm_ord[0]))
            fitParamsX = np.polyfit(t, pts_mm_ord[0], self.curve_order)
            fitParamsY = np.polyfit(t, pts_mm_ord[1], self.curve_order)
            fitParamsZ = np.polyfit(t, pts_mm_ord[2], self.curve_order)
            # Spline
            # s - smoothing
            # w - weight
            w = np.ones(len(pts_mm_ord[0]))
            # first and last have big weight
            w[1] = len(pts_mm_ord[0])
            w[-1] = len(pts_mm_ord[0])
            # tckl = np.asarray(tck).tolist()

            retval = {
                "curve_params": {
                    "start": list(point0_mm.tolist()),
                    "vector": list((point1_mm - point0_mm).tolist()),
                    "fitParamsX": list(fitParamsX.tolist()),
                    "fitParamsY": list(fitParamsY.tolist()),
                    "fitParamsZ": list(fitParamsZ.tolist()),
                    "fitCurveStrX": str(np.poly1d(fitParamsX)),
                    "fitCurveStrY": str(np.poly1d(fitParamsY)),
                    "fitCurveStrZ": str(np.poly1d(fitParamsZ)),
                    # 'fitParamsSpline': tck
                }
            }

        except Exception as ex:
            logger.warning("Problem in __edge_curve()")
            logger.warning(traceback.format_exc())
            print(ex)
        edg_stats.update(retval)
        return edg_stats

    # def edge_analysis(sklabel, edg_number):
    # element dilate * sklabel[sklabel < 0]
    # pass
    def __radius_analysis_init(self):
        """
        Computes skeleton with distances from edge of volume.

        | sklabel: skeleton or labeled skeleton
        | volume_data: volumetric data with zeros and ones
        """
        uq = np.unique(self.volume_data)
        if (len(uq) != 2) or (uq[0] != 0) or (uq[1] != 1):
            logger.error(
                f"__radius_analysis_init() error. Values in volume data are expected be 0 and 1. Given values={uq}."
            )
            raise ValueError("Volumetric data are expected to be 0 and 1.")
            return None
        # if (len(uq) != 2) or (len(uq)):
        #     logger.error("labels 0 and 1 expected in volume data")
        #     raise ValueError("Volumetric data are expected to be 0 and 1.")
        #     return None
        # if (uq[0] == 0) & (uq[1] == 1):
        dst = scipy.ndimage.morphology.distance_transform_edt(
            self.volume_data, sampling=self.voxelsize_mm
        )

        # import ipdb; ipdb.set_trace() # BREAKPOINT
        dst = dst * (self.sklabel != 0)

        return dst

        # else:
        #     raise ValueError("Volumetric data are expected to be 0 and 1.")
        #     return None

    def __radius_analysis(self, edg_number, skdst):
        """
        Return smaller radius of tube
        """
        # returns mean distance from skeleton to vessel border = vessel radius
        edg_skdst = skdst * (self.sklabel == edg_number)
        return np.mean(edg_skdst[edg_skdst != 0])

    def __connection_analysis(self, edg_number):
        """
        Analysis of which edge is connected
        """
        edg_neigh = self.elm_neigh[edg_number]

        if len(edg_neigh) == 1:
            logger.warning(
                "Only one ("
                + str(edg_neigh)
                + ") connected node in connection_analysis()"
                + " for edge number "
                + str(edg_number)
            )

            # get edges connected to end nodes
            connectedEdgesA = np.array(self.elm_neigh[edg_neigh[0]])
            # remove edg_number from connectedEdges list
            connectedEdgesA = connectedEdgesA[connectedEdgesA != edg_number]

            # get pixel and mm position of end nodes
            # node A
            box0 = self.elm_box[edg_neigh[0]]
            nd00, nd01, nd02 = (edg_neigh[0] == self.sklabel[box0]).nonzero()
            point0_mean = [np.mean(nd00), np.mean(nd01), np.mean(nd02)]
            point0 = np.array(
                [
                    float(point0_mean[0] + box0[0].start),
                    float(point0_mean[1] + box0[1].start),
                    float(point0_mean[2] + box0[2].start),
                ]
            )

            # node position -> mm
            point0_mm = point0 * self.voxelsize_mm

            edg_stats = {
                "id": edg_number,
                "nodeIdA": int(edg_neigh[0]),
                "connectedEdgesA": connectedEdgesA.tolist(),
                "nodeA_ZYX": point0.tolist(),
                "nodeA_ZYX_mm": point0_mm.tolist(),
            }

        elif len(edg_neigh) != 2:
            logger.warning(
                "Wrong number ("
                + str(edg_neigh)
                + ") of connected nodes in connection_analysis()"
                + " for edge number "
                + str(edg_number)
            )
            edg_stats = {"id": edg_number}
        else:
            # get edges connected to end nodes
            connectedEdgesA = np.array(self.elm_neigh[edg_neigh[0]])
            connectedEdgesB = np.array(self.elm_neigh[edg_neigh[1]])
            # remove edg_number from connectedEdges list
            connectedEdgesA = connectedEdgesA[connectedEdgesA != edg_number]
            connectedEdgesB = connectedEdgesB[connectedEdgesB != edg_number]

            # get pixel and mm position of end nodes
            # node A
            box0 = self.elm_box[edg_neigh[0]]
            nd00, nd01, nd02 = (edg_neigh[0] == self.sklabel[box0]).nonzero()
            point0_mean = [np.mean(nd00), np.mean(nd01), np.mean(nd02)]
            point0 = np.array(
                [
                    float(point0_mean[0] + box0[0].start),
                    float(point0_mean[1] + box0[1].start),
                    float(point0_mean[2] + box0[2].start),
                ]
            )
            # node B
            box1 = self.elm_box[edg_neigh[1]]
            nd10, nd11, nd12 = (edg_neigh[1] == self.sklabel[box1]).nonzero()
            point1_mean = [np.mean(nd10), np.mean(nd11), np.mean(nd12)]
            point1 = np.array(
                [
                    float(point1_mean[0] + box1[0].start),
                    float(point1_mean[1] + box1[1].start),
                    float(point1_mean[2] + box1[2].start),
                ]
            )
            # node position -> mm
            point0_mm = point0 * self.voxelsize_mm
            point1_mm = point1 * self.voxelsize_mm

            edg_stats = {
                "id": edg_number,
                "nodeIdA": int(edg_neigh[0]),
                "nodeIdB": int(edg_neigh[1]),
                "connectedEdgesA": connectedEdgesA.tolist(),
                "connectedEdgesB": connectedEdgesB.tolist(),
                "nodeA_ZYX": point0.tolist(),
                "nodeB_ZYX": point1.tolist(),
                "nodeA_ZYX_mm": point0_mm.tolist(),
                "nodeB_ZYX_mm": point1_mm.tolist(),
            }

        return edg_stats


def generate_binary_elipsoid(ndradius=[1, 1, 1]):
    """
    generate binary elipsoid shape
    """
    ndradius = np.asarray(ndradius).astype(np.double)
    shape = ((ndradius * 2) + 1).astype(np.uint)
    logger.debug("elipsoid shape %s", str(shape))
    # import ipdb; ipdb.set_trace() #  noqa BREAKPOINT
    x, y, z = np.indices(shape)
    center1 = ndradius
    mask = (
        ((x - ndradius[0]) ** 2) / ndradius[0] ** 2
        + ((y - ndradius[1]) ** 2) / ndradius[1] ** 2
        + ((z - ndradius[2]) ** 2) / ndradius[2] ** 2
    )
    # (y - ndradius[1])**2 < radius1**2
    # mask = mask radius1**1
    return mask < 1


def float_or_none(number):
    if number is None:
        return None
    else:
        return float(number)


def curve_model(t, params):
    p0 = params["start"][0] + t * params["vector"][0]
    p1 = params["start"][1] + t * params["vector"][1]
    p2 = params["start"][2] + t * params["vector"][2]
    return [p0, p1, p2]


def get_ordered_points_mm(points_mm, nodeA_pos, nodeB_pos, one_node_mode=False):
    """

    :param points_mm: list of not ordered points
    :param nodeA_pos: start point
    :param nodeB_pos: end point
    :param one_node_mode: if no end point is given
    :return:
    """

    length = 0
    startpoint = nodeA_pos
    pt_mm = [[nodeA_pos[0]], [nodeA_pos[1]], [nodeA_pos[2]]]
    while len(points_mm[0]) != 0:
        # get closest point to startpoint
        p_length = float("Inf")  # get max length
        closest_num = -1
        for p in list(range(0, len(points_mm[0]))):
            test_point = np.array([points_mm[0][p], points_mm[1][p], points_mm[2][p]])
            p_length_new = np.linalg.norm(startpoint - test_point)
            if p_length_new < p_length:
                p_length = p_length_new
                closest_num = p
        closest = np.array(
            [
                points_mm[0][closest_num],
                points_mm[1][closest_num],
                points_mm[2][closest_num],
            ]
        )
        # add length
        pt_mm[0].append(points_mm[0][closest_num])
        pt_mm[1].append(points_mm[1][closest_num])
        pt_mm[2].append(points_mm[2][closest_num])
        length += np.linalg.norm(closest - startpoint)
        # replace startpoint with used point
        startpoint = closest
        # remove used point from points
        points_mm = [
            np.delete(points_mm[0], closest_num),
            np.delete(points_mm[1], closest_num),
            np.delete(points_mm[2], closest_num),
        ]
    # add length to nodeB
    if not one_node_mode:
        length += np.linalg.norm(nodeB_pos - startpoint)
        pt_mm[0].append(nodeB_pos[0])
        pt_mm[1].append(nodeB_pos[1])
        pt_mm[2].append(nodeB_pos[2])

    return np.asarray(pt_mm).tolist(), length


def get_ordered_points_mm_from_labeled_image(
    labeled_skeleton,
    edg_number,
    voxelsize_mm,
    start_point_mm,
    end_point_mm=None,
    offset_mm=None,
):
    """
    
    :param labeled_skeleton: image containing labeled lines. ndimage with integer numbers
    :param edg_number: number of requested line integer number
    :param voxelsize_mm: 
    :param start_point_mm: 
    :param end_point_mm:
    :param offset_mm: coordinate of very first voxel of the image
    :return: 
    """

    if offset_mm is None:
        offset_mm = [0, 0, 0]
    points = (labeled_skeleton == edg_number).nonzero()
    points_mm = [
        np.array((offset_mm[0].start + points[0]) * voxelsize_mm[0]),
        np.array((offset_mm[1].start + points[1]) * voxelsize_mm[1]),
        np.array((offset_mm[2].start + points[2]) * voxelsize_mm[2]),
    ]

    if end_point_mm is None:
        one_node_mode = True
    else:
        one_node_mode = False

    pts_mm_ord, pixel_length = get_ordered_points_mm(
        points_mm, start_point_mm, end_point_mm, one_node_mode=one_node_mode
    )

    return pts_mm_ord, pixel_length
