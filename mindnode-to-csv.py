import csv
import os
from pathlib import Path

from common import find_in_list
from mindnode import Mindnode

HOME_PATH = os.environ["HOME"]
MINDNODE_FILE = (
    f"{HOME_PATH}/Library/Mobile"
    " Documents/W6L39UYL6Z~com~mindnode~MindNode/Documents/Swarm Engine.mindnode"
)
MINDMAP_NAME = "Swarm Engine"
CSV_FILE = f"{HOME_PATH}/Desktop/{MINDMAP_NAME.lower().replace(' ', '-')}.csv"

mindnode = Mindnode(MINDNODE_FILE)

mind_map = find_in_list(mindnode.mind_maps, lambda m: m.title == "Swarm Engine")

# Convert to CSV
def mind_map_to_2d_array(root_node):

    result = []

    for node in root_node.sub_nodes:

        lines = []

        if node.sub_nodes:
            sub_result = mind_map_to_2d_array(node)

            for line in sub_result:
                lines.append([node.title] + line)

        else:
            line = [node.title]

            line.append(str(node.hours) if node.hours else "")

            if node.done is not None:
                line.append("✅" if node.done else "")

            lines.append(line)

        result += lines

    return result


mind_map_array = mind_map_to_2d_array(mind_map)

compressed_array = [
    [line[0], " - ".join(line[1:-2]), line[-2], line[-1]] for line in mind_map_array
]

with open(CSV_FILE, "w", encoding="UTF8", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Category", "Task", "Est. Time", "Done"])
    writer.writerows(compressed_array)

print(f"Saved: {CSV_FILE}")
