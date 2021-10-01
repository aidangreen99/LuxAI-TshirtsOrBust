import math, sys
from lux.game import Game
from lux.game_map import Cell, RESOURCE_TYPES, GameMap
from lux.constants import Constants
from lux.game_constants import GAME_CONSTANTS
from lux import annotate
import numpy as np
import matplotlib.pyplot as plt
import logging

from sklearn.cluster import KMeans
from sklearn.datasets import make_blobs

logging.basicConfig(filename='agent.log', level=logging.INFO, filemode='w')
DIRECTIONS = Constants.DIRECTIONS
game_state = None

possible_directions = [DIRECTIONS.NORTH]

def agent(observation, configuration):
    global game_state

    ### Do not edit ###
    if observation["step"] == 0:
        game_state = Game()
        game_state._initialize(observation["updates"])
        game_state._update(observation["updates"][2:])
        game_state.id = observation.player
    else:
        game_state._update(observation["updates"])
    
    actions = []

    ### AI Code goes down here! ### 
    player = game_state.players[observation.player]
    opponent = game_state.players[(observation.player + 1) % 2]
    width, height = game_state.map.width, game_state.map.height

    resource_tiles: list[Cell] = []
    for y in range(height):
        for x in range(width):
            cell = game_state.map.get_cell(x, y)
            if cell.has_resource():
                resource_tiles.append(cell)
    logging.info(f"{resource_tiles[0].resource.type}")

    # we iterate over all our units and do something with them
    for unit in player.units:
        if unit.is_worker() and unit.can_act():
            closest_dist = math.inf
            closest_resource_tile = None
            if unit.get_cargo_space_left() > 0:
                # if the unit is a worker and we have space in cargo, lets find the nearest resource tile and try to mine it
                for resource_tile in resource_tiles:
                    if resource_tile.resource.type == Constants.RESOURCE_TYPES.COAL and not player.researched_coal(): continue
                    if resource_tile.resource.type == Constants.RESOURCE_TYPES.URANIUM and not player.researched_uranium(): continue
                    dist = resource_tile.pos.distance_to(unit.pos)
                    if dist < closest_dist:
                        closest_dist = dist
                        closest_resource_tile = resource_tile
                if closest_resource_tile is not None:
                    actions.append(unit.move(unit.pos.direction_to(closest_resource_tile.pos)))
            else:
                # if unit is a worker and there is no cargo space left, and we have cities, lets return to them
                if len(player.cities) > 0:
                    closest_dist = math.inf
                    closest_city_tile = None
                    for k, city in player.cities.items():
                        for city_tile in city.citytiles:
                            dist = city_tile.pos.distance_to(unit.pos)
                            if dist < closest_dist:
                                closest_dist = dist
                                closest_city_tile = city_tile
                    # if the nearest city has 'low' fuel, go there and deposit it
                    if closest_city_tile is not None and player.cities[closest_city_tile.cityid].fuel <= 400:
                        move_dir = unit.pos.direction_to(closest_city_tile.pos)
                        actions.append(unit.move(move_dir))
                    # otherwise, go the first direction you can and try to build a city
                    elif closest_city_tile is not None:
                        for dir in [DIRECTIONS.NORTH, DIRECTIONS.SOUTH, DIRECTIONS.EAST, DIRECTIONS.WEST]:
                            cell = GameMap.get_cell_by_pos(game_state.map, unit.pos.translate(dir, 1))
                            if cell.has_resource() == False:
                                if unit.can_build(game_state.map):
                                    actions.append((unit.build_city()))
                                else:
                                    #check to make sure you aren't colliding with a fellow unit
                                    for comrade in player.units:
                                        if comrade.pos != cell.pos:
                                            move_dir = unit.pos.direction_to(cell.pos)
                                            actions.append(unit.move(move_dir))
                    #get the cities to build workers
                    for k, city in player.cities.items():
                        for city_tile in city.citytiles:
                            if city_tile.can_act():
                                actions.append(city_tile.build_worker())



    # you can add debug annotations using the functions in the annotate object
    # actions.append(annotate.circle(0, 0))
    
    return actions
