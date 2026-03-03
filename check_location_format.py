import os
import json
import sys
import logging

logging.basicConfig(format='%(filename)s:%(lineno)4d %(levelname)s:%(message)s', level=logging.WARNING)


def check_format_equivalence(location, solver_location):
    # Check the track equivalence
    result = []
    location_tracks_by_id = {t["id"]: t for t in location["trackParts"]}
    solver_tracks_by_id = {t["id"]: t for t in solver_location["trackParts"]}
    if len(location_tracks_by_id) != len(solver_tracks_by_id):
        result.append((logging.ERROR,
                       f"Different number of tracks in location.json ({len(location_tracks_by_id)}) vs location_solver.json ({len(solver_tracks_by_id)})"))
    for id, track in location_tracks_by_id.items():
        if id not in solver_tracks_by_id:
            result.append((logging.ERROR,
                           f"Track with id {id} from the location.json not found in location_solver.json"))
            break
        solver_track = solver_tracks_by_id[id]
        if track["name"] != solver_track["name"]:
            result.append((logging.ERROR,
                            f"Track with id {id} has different names: {track['name']} vs {solver_track['name']} in location_solver.json"))
        if track["type"] != solver_track["type"]:
            result.append((logging.ERROR,
                           f"Track with id {id} has different types: {track['type']} vs {solver_track['type']} in location_solver.json"))
        if track["length"] != solver_track["length"]:
            result.append((logging.ERROR,
                           f"Track with id {id} has different lengths: {track['length']} vs {solver_track['length']} in location_solver.json"))
        if [int(a) for a in track["aSide"]] != [int(a) for a in solver_track["aSide"]]:
            result.append((logging.ERROR,
                           f"Track with id {id} has different aSides: {track['aSide']} vs {solver_track['aSide']} in location_solver.json"))
        for aTrack in track["aSide"]:
            if str(aTrack) not in location_tracks_by_id:
                result.append((logging.ERROR,
                               f"Track with id {id} has aSide {aTrack}that is not a track in location.json"))
            if str(aTrack) not in solver_tracks_by_id:
                result.append((logging.ERROR,
                               f"Track with id {id} has aSide {aTrack}that is not a track in location_solver.json"))
        if [int(b) for b in track["bSide"]] != [int(b) for b in solver_track["bSide"]]:
            result.append((logging.ERROR,
                           f"Track with id {id} has different bSides: {track['bSide']} vs {solver_track['bSide']} in location_solver.json"))
        for bTrack in track["bSide"]:
            if str(bTrack) not in location_tracks_by_id:
                result.append((logging.ERROR,
                               f"Track with id {id} has bSide {bTrack}that is not a track in location.json"))
            if str(bTrack) not in solver_tracks_by_id:
                result.append((logging.ERROR,
                               f"Track with id {id} has bSide {bTrack}that is not a track in location_solver.json"))
        if track["parkingAllowed"] != solver_track["parkingAllowed"]:
            result.append((logging.ERROR,
                           f"Track with id {id} has different parkingAllowed: {track['parkingAllowed']} vs {solver_track['parkingAllowed']} in location_solver.json"))
        if track["sawMovementAllowed"] != solver_track["sawMovementAllowed"]:
            result.append((logging.ERROR,
                           f"Track with id {id} has different sawMovementAllowed: {track['sawMovementAllowed']} vs {solver_track['sawMovementAllowed']} in location_solver.json"))
    # Check the facility equivalence
    location_facilities_by_id = {f["id"]: f for f in location["facilities"]}
    solver_facilities_by_id = {f["id"]: f for f in solver_location["facilities"]}
    if len(location_facilities_by_id) != len(solver_facilities_by_id):
        result.append((logging.ERROR,
                       f"Different number of facilities in location.json ({len(location_facilities_by_id)}) vs location_solver.json ({len(solver_facilities_by_id)})"))
    for id, facility in location_facilities_by_id.items():
        if id not in solver_facilities_by_id:
            result.append((logging.ERROR,
                           f"Facility with id {id} from the location.json not found in location_solver.json"))
            break
        solver_facility = solver_facilities_by_id[id]
        if facility["type"] != solver_facility["type"]:
            result.append((logging.ERROR,
                           f"Facility with id {id} has different types: {facility['type']} vs {solver_facility['type']} in location_solver.json"))
        if facility["simultaneousUsageCount"] != solver_facility["simultaneousUsageCount"]:
            result.append((logging.ERROR,
                           f"Facility with id {id} has different simultaneousUsageCounts: {facility['simultaneousUsageCount']} vs {solver_facility['simultaneousUsageCount']} in location_solver.json"))
        if sorted(int(r) for r in facility["relatedTrackParts"]) != sorted(int(r) for r in solver_facility["relatedTrackParts"]):
            result.append((logging.ERROR,
                           f"Facility with id {id} has different relatedTrackParts: {facility['relatedTrackParts']} vs {solver_facility['relatedTrackParts']} in location_solver.json"))
        for track in facility["relatedTrackParts"]:
            if str(track) not in location_tracks_by_id:
                result.append((logging.ERROR,
                               f"Facility with id {id} has relatedTrackPart {track} not found in location.json"))
            if str(track) not in solver_tracks_by_id:
                result.append((logging.ERROR,
                               f"Facility with id {id} has relatedTrackPart {track} not found in location_solver.json"))
        if facility["taskTypes"] != solver_facility["taskTypes"]:
            result.append((logging.ERROR,
                           f"Facility with id {id} has different taskTypes: {facility['taskTypes']} vs {solver_facility['taskTypes']} in location_solver.json"))
    return result


def check_location_file(location_json, dirname, gateway_track_id=None):
    result = []
    track_by_id = {int(t["id"]): t for t in location_json["trackParts"]}
    for id, track in track_by_id.items():
        for a in track["aSide"]:
            aTrack = track_by_id[int(a)]
            if int(id) not in [int(b) for b in aTrack["bSide"]]:
                result.append((logging.ERROR,
                               f"Track {id} has track {a} on its aSide, but track {a} does not have {id} on its bSide."))
        for b in track["bSide"]:
            bTrack = track_by_id[int(b)]
            if int(id) not in [int(a) for a in bTrack["aSide"]]:
                result.append((logging.ERROR,
                               f"Track {id} has track {a} on its bSide, but track {b} does not have {id} on its aSide."))
        if track["type"] == "RailRoad":
            if len(track["aSide"]) != 1:
                result.append((logging.ERROR,
                               f"RailRoad track {id} must have exactly one track part on its aSide: {track['aSide']}"))
            if len(track["bSide"]) != 1:
                result.append((logging.ERROR,
                               f"RailRoad track {id} must have exactly one track part on its bSide: {track['bSide']}"))
        if track["type"] == "Bumper":
            if len(track["aSide"]) == 0 and len(track["bSide"]) != 1:
                result.append((logging.ERROR,
                               f"Bumper track {id} must have one track on either side: a {track['aSide']} and b {track['bSide']}"))
            if len(track["bSide"]) == 0 and len(track["aSide"]) != 1:
                result.append((logging.ERROR,
                               f"Bumper track {id} must have one track on either side: a {track['aSide']} and b {track['bSide']}"))
    if gateway_track_id is not None:
        # TODO fix a simple graph drawing of the tracks starting from the gateway
        try:
            import networkx as nx
            import matplotlib.pyplot as plt
        except ModuleNotFoundError:
            logging.critical("Could not import networkx and/or matplotlib.")
            logging.critical("Please run from an enviroment providing these when supplying a gateway track id.")
            sys.exit(1)
        graph = nx.DiGraph()
        graph.add_node(int(gateway_track_id), type="Gateway", pos=(0,0), name = track_by_id[int(gateway_track_id)]["name"])
        gateway = track_by_id[int(gateway_track_id)]
        add_ab_nodes(graph, gateway, (0,0), track_by_id)

        plt.figure(figsize=(8, 6))
        nx.draw(graph, with_labels=True, pos=nx.get_node_attributes(graph, 'pos'))
        print(graph)
        plt.savefig(os.path.join(dirname, f"track_graph_from_gateway_{gateway_track_id}.png"))
        plt.show()
    return result

def add_ab_nodes(graph, track, pos, track_by_id):
    for i, a in enumerate(track["aSide"]):
        if int(a) not in graph.nodes:
            graph.add_node(int(a), type=track_by_id[int(a)]["type"], name = track_by_id[int(track["id"])]["name"], pos=(-1, i))
            new_position = (pos[0]-1, pos[1]+(1-i))
            print(f"Track {a} at {new_position}") 
            graph.add_edge(int(track["id"]), int(a), direction="aSide", pos=new_position)
            add_ab_nodes(graph, track_by_id[int(a)], new_position, track_by_id)
    for i, b in enumerate(track["bSide"]):
        if int(b) not in graph.nodes:
            graph.add_node(int(b), type=track_by_id[int(b)]["type"], name = track_by_id[int(track["id"])]["name"], pos=(1, i))
            new_position = (pos[0]+1, pos[1]+(1-i))
            print(f"Track {b} at {new_position}")
            graph.add_edge(int(track["id"]), int(b), direction="bSide", pos=new_position)
            add_ab_nodes(graph, track_by_id[int(b)], new_position, track_by_id)

if __name__ == "__main__":
    if len(sys.argv) <= 1:
        # Print usage and exit.
        print("%%%%%%%%%%%%%%%%%%%%\nGive the folder of the location (e.g. Location_KleineBinckhorst) to compare its location.json and location_solver.json filenames, possibly specify a second argument the id of the gateway track.\n%%%%%%%%%%%%%%%%%%%%")
        sys.exit(0)
    dirname = sys.argv[1]
    location_filename = location_solver_filename = None
    if os.path.isdir(dirname):
        if os.path.isfile(os.path.join(dirname, "location.json")):
            location_filename = os.path.join(dirname, "location.json")
        else:
            print(f"Could not find {dirname}/location.json.")
            sys.exit(1)
        if os.path.isfile(os.path.join(dirname, "location_solver.json")):
            location_solver_filename = os.path.join(dirname, "location_solver.json")
        else:
            print(f"Could not find {dirname}/location_solver.json.")
            sys.exit(1)
    else:
        print(f"Directory {dirname} not found.")
        sys.exit(1)
    try:
        with open(location_filename, "r") as f:
            location = json.load(f)
        with open(location_solver_filename, "r") as f:
            solver_location = json.load(f)
    except Exception as e:
        logging.exception("Error opening location files")
    gateway_track_id = None
    if len(sys.argv) >= 3:
        gateway_track_id = sys.argv[2]
    result = check_format_equivalence(location, solver_location)
    result += check_location_file(location, dirname, gateway_track_id)
    if result:
        for (level, msg) in result:
            logging.log(level, msg)
        sys.exit(1)
    else:
        print("Location formats OK!")
