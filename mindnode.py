import xml.etree.ElementTree as ET
from subprocess import run
import shutil
import os
import re

from common import xml_key_find


class Mindnode:
    def __init__(self, mindnode_file):
        self.mindnode_file = mindnode_file
        self.xml_file = "/tmp/mindnode-contents.xml"
        self.xml_tree = None
        self.mind_maps = []

        self.open_xml()
        self.parse_mind_maps()

    def open_xml(self):
        shutil.copyfile(os.path.join(self.mindnode_file, "contents.xml"), self.xml_file)
        run(["plutil", "-convert", "xml1", self.xml_file], check=True)

        self.xml_tree = ET.parse(self.xml_file)

    def parse_mind_maps(self):
        canvas = xml_key_find(self.xml_tree.getroot()[0], "canvas")
        assert canvas is not None, f"No canvas key found in {self.mindnode_file}"

        for mind_map_elem in xml_key_find(canvas, "mindMaps"):

            main_node = xml_key_find(mind_map_elem, "mainNode")
            if main_node is None:
                continue

            tree = self.parse_sub_nodes(main_node)

            self.mind_maps.append(tree)

    def parse_sub_nodes(self, root_node):

        node = Node(self.find_node_title(root_node))

        sub_nodes = xml_key_find(root_node, "subnodes")
        if sub_nodes is not None and len(sub_nodes) > 0:
            for sub_node in sub_nodes:
                node.sub_nodes.append(self.parse_sub_nodes(sub_node))

        return node

    def find_node_title(self, elem):

        title_elem = xml_key_find(elem, "title")
        if not title_elem:
            return None

        text = title_elem.find("string").text
        if not text:
            return None

        return re.sub(r"<.*?>", "", text)


class Node:
    def __init__(self, title):
        self.title = title
        self.sub_nodes = []

    def __repr__(self):
        if not self.title:
            return "{}"

        value = {
            "title": self.title,
        }
        if len(self.sub_nodes) > 0:
            value["sub_nodes"] = self.sub_nodes

        return str(value)
