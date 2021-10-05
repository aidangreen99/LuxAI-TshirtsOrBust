import math, sys
from lux import game_map
from lux.game import Game
from lux.game_map import Cell, RESOURCE_TYPES, GameMap
from lux.constants import Constants
from lux.game_constants import GAME_CONSTANTS
from lux import annotate
from random import randint, sample

DIRECTIONS = Constants.DIRECTIONS
game_state = None

possible_directions = [DIRECTIONS.NORTH, DIRECTIONS.SOUTH, DIRECTIONS.EAST, DIRECTIONS.WEST]

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

    # we iterate over all our units and do something with them
    for unit in player.units:
        original_move_list_length = len(actions)
        if unit.is_worker() and unit.can_act():
            closest_dist = math.inf
            closest_resource_tile = None
            if unit.get_cargo_space_left() > 0:
                # if the unit is a worker and we have space in cargo, lets find the nearest resource tile and try to mine it
                for resource_tile in resource_tiles:
                    if resource_tile.resource.type == Constants.RESOURCE_TYPES.COAL and not player.researched_coal(): continue
                    if resource_tile.resource.type == Constants.RESOURCE_TYPES.URANIUM and not player.researched_uranium(): continue
                    dist = resource_tile.pos.distance_to(unit.pos)
                    if dist < closest_dist and (s for s in actions if closest_city_tile.pos not in s):
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
                            if dist < closest_dist and (s for s in actions if closest_city_tile.pos not in s):
                                closest_dist = dist
                                closest_city_tile = city_tile

                    if closest_city_tile is not None and player.cities[closest_city_tile.cityid].fuel <= 400:   
                        if len(actions) == original_move_list_length:
                            move_dir = unit.pos.direction_to(closest_city_tile.pos)
                            if unit.can_act():
                                actions.append(unit.move(move_dir))

                    elif closest_city_tile is not None:
                        for dir in sample(possible_directions, 4):
                            cell = GameMap.get_cell_by_pos(game_state.map, closest_city_tile.pos.translate(dir, 1))
                            if cell.has_resource() != True:
                                move_dir = unit.pos.direction_to(cell.pos)
                                if unit.can_build(game_state.map):
                                    if unit.can_act():
                                        actions.append((unit.build_city()))
                                        break
                                else:
                                    if unit.can_act():
                                        actions.append(unit.move(move_dir))
                                        break
                                
    for k, city in player.cities.items():
                        for city_tile in city.citytiles:
                            if city_tile.can_act() and len(player.cities) > len(player.units):
                                rand_int = randint(0,2)
                                if rand_int == 1:
                                    actions.append(city_tile.build_worker())
                                    break
                                else:
                                    actions.append(city_tile.build_cart())
                                    break
                            elif city_tile.can_act() and city_tile.research() not in actions:
                                actions.append(city_tile.research())
                                break
                                
                                
                                

    # you can add debug annotations using the functions in the annotate object
    # actions.append(annotate.circle(0, 0))
    
    return actions