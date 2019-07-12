import module_Phase
import module_Resource
import collections
from enum import Enum, unique

ABBREV_NO_USE_EFFECT = 'N'  # type: str[1]
TXT_NO_USE_EFFECT = '(' + ABBREV_NO_USE_EFFECT + ' if you don\'t want to use the effect)'  # type: str

def Player():
    pass

def ColorPlayer():
    pass

def indent(n_indent: int) -> str:
    """Get a string in order to create an indentation."""
    return '  ' * n_indent

class Effect:
    """Effect (primary or secondary) of a building."""

    def __init__(self, text: str, phase: module_Phase.Phase, money_resources_cost=None, money_resources_gain=None):
        """Initialization of an effect of a building."""
        self.text = text  # type: str
        self.phase = phase  # type: Phase
        self.money_resources_cost = money_resources_cost  # unused
        self.money_resources_gain = money_resources_gain  # type: Tuple[module_Resource.MoneyResource, int]

class Building:
    """Buildings (cards)."""

    game_element = None  # type: GameElement # Used for the church and lawyer player buildings.

    def __init__(self, belongs_to_beginner_version: bool, can_be_a_prestige_building: bool,
                 allows_to_place_a_worker: bool, front_color: str, name: str, n_prestige_pts: int,
                 primary_effect: Effect, resource_costs):
        """Initialization of a building."""
        self.belongs_to_beginner_version = belongs_to_beginner_version  # type: bool
        self.can_be_a_prestige_building = can_be_a_prestige_building  # type: bool
        self.allows_to_place_a_worker = allows_to_place_a_worker  # type: bool
        self.front_color = front_color  # type: str
        self.name = name  # type: str
        self.n_prestige_pts = n_prestige_pts  # type: int
        self.primary_effect = primary_effect  # type: Effect
        self.resource_costs = resource_costs  # type: Dict[Optional[module_Resource.Resource], int]

    def txt_name_owner(self, with_owner: bool) -> str:
        """Get the text of the name of the building with the owner."""
        return self.name + (' which belongs to ' + self.color_player.player.name()
                            if with_owner
                               and self.get_building_type() in [BuildingType.PLAYER, BuildingType.BACKGROUND,
                                                                BuildingType.PRESTIGE]
                               and self.color_player is not None else '')

    def income_effect(self, income_phase: module_Phase.Phase = None) -> None:
        """Give some money to the player owing the building on the road."""
        pass  # No money is given excepted for each résidence player building and the hotel prestige building along the road.

    def apply_no_cost_only_gain_effect(self, money_resources_gain, player: Player = None) -> None:
        """Apply the effect of a building for (the worker of) the player. This effect doesn't require any cost and give some gain; so, we don't ask it hte player want it and give him."""
        if player is None:
            player = self.color_player.player
        money_resource, qty = money_resources_gain  # type: Tuple[module_Resource.MoneyResource, int]
        player.current_money_resources[money_resource] += qty
        print(indent(4) + player.txt_name_money_resources_workers_PPs_deck(True, True, False, False, False) + '.')

    def apply_peddler_effect(self, player: Player) -> None:
        """Apply the effect of a peddler (neutral or player) building."""
        """
        Buy 1 cube (any resource but gold) from the stock with 1 denier.
        """
        # Remark: Hard-coded! We don't use the tags <cost><n_deniers>-1 and <gain><CHOICES>... in <game_elements><buildings><player_buildings><player_building><secondary_effect>.
        money_resource_cost, qty_cost = module_Resource.Money.money, -1  # type: module_Resource.MoneyResource, int
        if player.current_money_resources[money_resource_cost] + \
                qty_cost < 0:  # Has the player enough money or resource?
            print(indent(4) + player.txt_name_money_resources_workers_PPs_deck(True, True, False, False, False) +
                  ' and can\'t apply the effect because he/she doesn\'t have enough money or resource as ' +
                  str(qty_cost) + ' ' + money_resource_cost.name + '(s) required.')
        else:
            resource_gain_choices, qty_gain = [resource for resource in module_Resource.Resource.resources.values()
                                               if not resource.is_wild()], \
                                              +1  # type: List[module_Resource.Resource], int
            resource_gain = player.choose_buy_resource(money_resource_cost, qty_cost, resource_gain_choices,
                                                       qty_gain)  # type:module_Resource.Resource
            if resource_gain is None:
                print(indent(4) + player.txt_name_money_resources_workers_PPs_deck(True, True, False, False, False) +
                      ' and had chosen to don\'t apply the effect.')
            else:
                print(indent(4) + player.name() + ' wants to consume ' + str(qty_cost) + ' ' +
                      money_resource_cost.name + '(s) to obtain ' + str(qty_gain) + ' ' + resource_gain.name + '(s).')
                player.current_money_resources[money_resource_cost] += qty_cost
                player.current_money_resources[resource_gain] += qty_gain
                print(indent(4) + player.txt_name_money_resources_workers_PPs_deck(True, True, False, False, False) +
                      ' once the effect applied.')

    def apply_effect_multi(self, player: Player, all_costs, resource_gain_choices, single_qty_gain: int) -> None:
        """Apply an effect with several choices (e.g. primary effects of bank and peddler player buildings)."""
        # :param all_costs:  # type: List[Tuple[module_Resource.Money, int]] # Must be ordered!
        # :param resource_gain_choices: # type: List[module_Resource.Resource]
        costs = [(money_resource_cost, qty_cost) for (money_resource_cost, qty_cost) in all_costs
                 if player.current_money_resources[money_resource_cost] + qty_cost >= 0]
        if not costs:  # Has the player enough money or resource?
            print(indent(4) + player.txt_name_money_resources_workers_PPs_deck(True, True, False, False, False) +
                  ' and can\'t apply the effect because he/she doesn\'t have enough money or resource as ' +
                  'either ' + ' or '.join(str(qty_cost) + ' ' + money_resource_cost.name + '(s)'
                                          for (money_resource_cost, qty_cost) in all_costs) + ' required.')
        elif len(costs) == 1:
            print(indent(4) + 'There exists only one choice according to money and resources you have.')
            money_resource_cost, qty_cost = costs[0]
            resource_gain = player.choose_buy_resource(money_resource_cost, qty_cost, resource_gain_choices,
                                                       single_qty_gain)  # type:module_Resource.Resource
            if resource_gain is None:
                print(indent(4) + player.txt_name_money_resources_workers_PPs_deck(True, True, False, False, False) +
                      ' and had chosen to don\'t apply the effect.')
            else:
                print(indent(4) + player.name() + ' wants to consume ' +
                      str(qty_cost) + ' ' + money_resource_cost.name + '(s) to obtain ' +
                      str(single_qty_gain) + ' ' + resource_gain.name + '(s).')
                player.current_money_resources[money_resource_cost] += qty_cost
                player.current_money_resources[resource_gain] += single_qty_gain
                print(indent(4) + player.txt_name_money_resources_workers_PPs_deck(True, True, False, False, False) +
                      ' once the effect applied.')
        else:
            resources_gain = player.choose_buy_resource_multi(costs, resource_gain_choices,
                                                              len(costs) * single_qty_gain)
            if not resources_gain:
                print(indent(4) + player.txt_name_money_resources_workers_PPs_deck(True, True, False, False, False) +
                      ' and had chosen to don\'t apply the effect.')
            else:
                money_resource_cost, qty_cost = costs[len(resources_gain) - 1]  # costs must be ordered!
                print(indent(4) + player.name() + ' wants to consume ' +
                      str(qty_cost) + ' ' + money_resource_cost.name + '(s).')
                player.current_money_resources[money_resource_cost] += qty_cost
                for resource_gain, qty_gain in collections.Counter(resources_gain).items():  # To group by resource.
                    print(indent(4) + player.name() + ' wants to obtain ' +
                          str(single_qty_gain * qty_gain) + ' ' + resource_gain.name + '(s).')
                    player.current_money_resources[resource_gain] += single_qty_gain * qty_gain
                print(indent(4) + player.txt_name_money_resources_workers_PPs_deck(True, True, False, False, False) +
                      ' once the effect applied.')


class PlayerBuilding(Building):
    """A set per player of all 12 player buildings (cards of the color of the player): small farm, small sawmill,
    small quarry, peddler, market, lawyer, large farm, large sawmill, large quarry, gold mine, bank, church."""
    """
    Each player building is described by its front color, name, cost (number of food, wood, stone or of any type),
    number of prestige points, [optionally] construction (actions phase), primary and secondary effect (effect phase).
    """

    def __init__(self, belongs_to_beginner_version: bool, can_be_a_prestige_building: bool,
                 allows_to_place_a_worker: bool, front_color: str, name: str, n_prestige_pts: int,
                 primary_effect: Effect, resource_costs, can_be_a_residential_building: bool, secondary_effect: Effect,
                 color_player: ColorPlayer):
        """Initialization of a player building."""
        Building.__init__(self, belongs_to_beginner_version, can_be_a_prestige_building, allows_to_place_a_worker,
                          front_color, name, n_prestige_pts, primary_effect, resource_costs)
        # Specific attributes.
        self.can_be_a_residential_building = can_be_a_residential_building  # type: bool
        self.secondary_effect = secondary_effect  # type: Effect
        self.color_player = color_player  # type: ColorPlayer

    def get_building_type(self):  # -> BuildingType
        """Indicates that this building is a player building."""
        return BuildingType.PLAYER

    def apply_primary_effect(self, player: Player) -> None:
        """Apply the (default) primary effect of a player building."""
        print(indent(3) + 'Primary effect of the player building ' + self.txt_name_owner(True) +
              ' for a worker of the player ' + player.name() + ': ' + self.primary_effect.text)
        pass  # Nothing to do!

    def apply_secondary_effect(self) -> None:
        """Apply the (default) secondary effect of a player building."""
        print(indent(3) + 'Secondary effect of the player building ' + self.txt_name_owner(True) + ': ' +
              self.secondary_effect.text)
        pass  # Nothing to do!


class SmallProductionPlayerBuilding(PlayerBuilding):
    """Small farm/sawmill/quarry (with construction) production of food/wood/stone player building."""

    def __init__(self, belongs_to_beginner_version: bool, can_be_a_prestige_building: bool,
                 allows_to_place_a_worker: bool, front_color: str, name: str, n_prestige_pts: int,
                 primary_effect: Effect, resource_costs, can_be_a_residential_building: bool, secondary_effect: Effect,
                 color_player: ColorPlayer, resource:module_Resource.Resource, n_cubes_into_area):
        """Initialization of a small production player building."""
        PlayerBuilding.__init__(self, belongs_to_beginner_version, can_be_a_prestige_building, allows_to_place_a_worker,
                                front_color, name, n_prestige_pts, primary_effect, resource_costs,
                                can_be_a_residential_building, secondary_effect, color_player)
        # Specific attributes.
        self.resource = resource  # type:module_Resource.Resource
        self.n_cubes_into_area = n_cubes_into_area  # type: List[int]
        # Attributes to play a game.
        self.current_n_cubes_into_area = None  # type: int

    def setup(self, n_players: int) -> None:
        """Setup this small production player building."""
        self.current_n_cubes_into_area = self.n_cubes_into_area[n_players]

    def apply_primary_effect(self, player: Player) -> None:
        """Apply the primary effect of this small production player building."""
        super().apply_primary_effect(player)
        self.apply_no_cost_only_gain_effect(self.primary_effect.money_resources_gain, player)

    def apply_secondary_effect(self) -> None:
        """Apply the secondary effect of this small production player building."""
        super().apply_secondary_effect()
        if self.current_n_cubes_into_area == 0:
            print(indent(4) + 'There is no cube left in this small production player building, the owner gets nothing.')
        else:
            self.current_n_cubes_into_area -= 1
            print(indent(4) + 'There is now ' + str(self.current_n_cubes_into_area) +
                  ' cube(s) into the area of this small production player building.')
            self.apply_no_cost_only_gain_effect(self.secondary_effect.money_resources_gain, self.color_player.player)


class LargeProductionPlayerBuilding(PlayerBuilding):
    """Large farm/sawmill/quarry production of food/wood/stone player building."""

    def __init__(self, belongs_to_beginner_version: bool, can_be_a_prestige_building: bool,
                 allows_to_place_a_worker: bool, front_color: str, name: str, n_prestige_pts: int,
                 primary_effect: Effect, resource_costs, can_be_a_residential_building: bool, secondary_effect: Effect,
                 color_player: ColorPlayer, resource:module_Resource.Resource):
        """Initialization of a large production player building."""
        PlayerBuilding.__init__(self, belongs_to_beginner_version, can_be_a_prestige_building, allows_to_place_a_worker,
                                front_color, name, n_prestige_pts, primary_effect, resource_costs,
                                can_be_a_residential_building, secondary_effect, color_player)
        # Specific attributes.
        self.resource = resource  # type:module_Resource.Resource

    def apply_primary_effect(self, player: Player) -> None:
        """Apply the primary effect of this large production player building."""
        super().apply_primary_effect(player)
        self.apply_no_cost_only_gain_effect(self.primary_effect.money_resources_gain, player)

    def apply_secondary_effect(self) -> None:
        """Apply the secondary effect of this large production player building."""
        super().apply_secondary_effect()
        self.apply_no_cost_only_gain_effect(self.secondary_effect.money_resources_gain, self.color_player.player)


class LawyerPlayerBuilding(PlayerBuilding):
    """Lawyer player building."""

    def __init__(self, belongs_to_beginner_version: bool, can_be_a_prestige_building: bool,
                 allows_to_place_a_worker: bool, front_color: str, name: str, n_prestige_pts: int,
                 primary_effect: Effect, resource_costs, can_be_a_residential_building: bool, secondary_effect: Effect,
                 color_player: ColorPlayer, n_residence_to_construct: int):
        """Initialization of a lawyer player building."""
        PlayerBuilding.__init__(self, belongs_to_beginner_version, can_be_a_prestige_building, allows_to_place_a_worker,
                                front_color, name, n_prestige_pts, primary_effect, resource_costs,
                                can_be_a_residential_building, secondary_effect, color_player)
        # Specific attributes.
        self.n_residence_to_construct = n_residence_to_construct  # type: int

    def apply_primary_effect(self, player: Player) -> None:
        """Apply the primary effect of a lawyer player building."""
        """
        Construct a residential building by paying 1 food cube and turning over one of your cards along the road (except a Lawyer).
        """
        # Remark: Hard-coded! We don't use the tags <cost><n_food_cubes>-1 and <gain><n_residence_to_construct>+1 AND algorithm... in <game_elements><buildings><player_buildings><player_building><primary_effect>.
        super().apply_primary_effect(player)
        print(indent(4) + 'The road consists in: ' + self.game_element.game.txt_road(False) + '.')
        resource_cost, qty_cost =module_Resource.Resource.get_resource('food'), -1  # type:module_Resource.Resource, int
        if player.current_money_resources[resource_cost] + \
                player.current_money_resources[module_Resource.Resource.get_wild_resource()] + qty_cost < 0:
            print(indent(4) + player.txt_name_money_resources_workers_PPs_deck(True, True, False, False, False) +
                  ' and can\'t apply the effect because he/she doesn\'t have enough resource as ' +
                  str(qty_cost) + ' ' + resource_cost.name + '(s) required (even by considering wild resource).')
        else:
            i_road_buildings_on_road = [(i_road, building_worker[0])
                                        for (i_road, building_worker) in enumerate(self.game_element.game.road)
                                        if building_worker[0].get_building_type() == BuildingType.PLAYER
                                        and building_worker[0].color_player.player == player and
                                        building_worker[0].can_be_a_residential_building
                                        ]  # type: List[Tuple[PlayerBuilding]]
            if not i_road_buildings_on_road:
                print(indent(4) + player.txt_name_money_resources_workers_PPs_deck(True, True, False, False, False) +
                      ' and can\'t apply the effect because he/she has no building to be constructed as a residential building along the road.')
            else:
                resource_costs = None  # type: List[Tuple[module_Resource.Resource, int]]
                qty_current_resource_cost = player.current_money_resources[resource_cost]
                if qty_current_resource_cost == 0:
                    resource_costs = [(Resource.get_wild_resource(), qty_cost)]
                elif qty_current_resource_cost >= abs(qty_cost):
                    resource_costs = [(resource_cost, qty_cost)]
                else:
                    resource_costs = [(resource_cost, -qty_current_resource_cost),
                                      (Resource.get_wild_resource(), qty_cost + qty_current_resource_cost)]
                i_road_building_to_construct_as_residence = player.choose_construct_residence(resource_costs,
                                                                                              i_road_buildings_on_road)
                if i_road_building_to_construct_as_residence is None:
                    print(indent(4) +
                          player.txt_name_money_resources_workers_PPs_deck(True, True, False, False, False) +
                          ' and had chosen to don\'t apply the effect.')
                else:
                    i_road = i_road_building_to_construct_as_residence[0]  # type: int
                    building_to_construct_as_residence = i_road_building_to_construct_as_residence[
                        1]  # type: PlayerBuilding
                    print(indent(4) + player.name() + ' wants to consume ' +
                          ' and '.join(str(qty_cost) + ' ' + resource_cost.name + '(s)'
                                       for (resource_cost, qty_cost) in resource_costs) +
                          ' to construct his/her ' + i_road_building_to_construct_as_residence[1].name +
                          ' building (the ' + ordinal_number(i_road + 1) +
                          ' building along the road) as a residential building.')
                    for (resource_cost, qty_cost) in resource_costs:
                        player.current_money_resources[resource_cost] += qty_cost
                    if self.game_element.game.road[i_road][1] is not None:
                        # Remark: building_to_construct_as_residence is equals to self.game_element.game.road[i_road][0].
                        self.game_element.game.road[i_road].append(building_to_construct_as_residence)
                    self.game_element.game.road[i_road][0] = player.get_residence_building()
                    player.deck[building_to_construct_as_residence] = Location.REPLACED
                    print(indent(4) + 'The road consists in: ' + self.game_element.game.txt_road(False) + '.')
                    print(indent(4) +
                          player.txt_name_money_resources_workers_PPs_deck(True, True, False, False, False) +
                          ' once the effect applied.')

    def apply_secondary_effect(self) -> None:
        """Apply the secondary effect of a lawyer player building."""
        super().apply_secondary_effect()
        self.apply_no_cost_only_gain_effect(self.secondary_effect.money_resources_gain, self.color_player.player)


class PeddlerPlayerBuilding(PlayerBuilding):
    """Peddler player building."""

    def __init__(self, belongs_to_beginner_version: bool, can_be_a_prestige_building: bool,
                 allows_to_place_a_worker: bool, front_color: str, name: str, n_prestige_pts: int,
                 primary_effect: Effect, resource_costs, can_be_a_residential_building: bool, secondary_effect: Effect,
                 color_player: ColorPlayer):
        """Initialization of a peddler player building."""
        PlayerBuilding.__init__(self, belongs_to_beginner_version, can_be_a_prestige_building, allows_to_place_a_worker,
                                front_color, name, n_prestige_pts, primary_effect, resource_costs,
                                can_be_a_residential_building, secondary_effect, color_player)

    def apply_primary_effect(self, player: Player) -> None:
        """Apply the primary effect of a peddler player building."""
        """
        Buy 1 or 2 cubes (any resource but gold) from the stock with 1 or 2 deniers.
        """
        # Remark: Hard-coded! We don't use the tag <CHOICES>... in <game_elements><buildings><player_buildings><player_building><secondary_effect>.
        super().apply_primary_effect(player)
        all_costs = [(module_Resource.Money.money, -1), (module_Resource.Money.money, -2)]  # type: List[Tuple[module_Resource.Money, int]] # Ordered!
        resource_gain_choices, single_qty_gain = [resource for resource in module_Resource.Resource.resources.values()
                                                  if not resource.is_wild()], \
                                                 +1  # type: List[module_Resource.Resource], int # single_qty_gain must be equals to one!
        self.apply_effect_multi(player, all_costs, resource_gain_choices, single_qty_gain)

    def apply_secondary_effect(self) -> None:
        """Apply the secondary effect of a peddler player building."""
        """
        Buy 1 cube (any resource but gold) from the stock with 1 denier.
        """
        # Remark: Hard-coded! We don't use the tags <cost><n_deniers>-1 and <gain><CHOICES>... in <game_elements><buildings><player_buildings><player_building><secondary_effect>.
        super().apply_secondary_effect()
        self.apply_peddler_effect(self.color_player.player)


class MarketPlayerBuilding(PlayerBuilding):
    """Market player building."""

    def __init__(self, belongs_to_beginner_version: bool, can_be_a_prestige_building: bool,
                 allows_to_place_a_worker: bool, front_color: str, name: str, n_prestige_pts: int,
                 primary_effect: Effect, resource_costs, can_be_a_residential_building: bool, secondary_effect: Effect,
                 color_player: ColorPlayer):
        """Initialization of a market player building."""
        PlayerBuilding.__init__(self, belongs_to_beginner_version, can_be_a_prestige_building, allows_to_place_a_worker,
                                front_color, name, n_prestige_pts, primary_effect, resource_costs,
                                can_be_a_residential_building, secondary_effect, color_player)

    def apply_primary_effect(self, player: Player) -> None:
        """Apply the primary effect of a market player building."""
        """
        Exchange 1 cube from your personal stock with 4 deniers.
        """
        # Remark: Hard-coded! We don't use the tags <cost><CHOICES>... and <gain><n_deniers>+4... in <game_elements><buildings><player_buildings><player_building><primary_effect>.
        super().apply_primary_effect(player)
        money_resource_cost, qty_cost = None, -1  # type:module_Resource.Resource, int # None for any resource (including wild).
        money_resource_gain, qty_gain = module_Resource.Money.money, +4  # type: module_Resource.Money, int
        money_resource_cost_choices = [money_resource for money_resource, qty in player.current_money_resources.items()
                                       if money_resource != module_Resource.Money.money and qty + qty_cost >= 0
                                       ]  # type: List[module_Resource.Resource] # All suffisant available resources.
        if not money_resource_cost_choices:
            print(indent(4) + player.txt_name_money_resources_workers_PPs_deck(True, True, False, False, False) +
                  ' and can\'t apply the effect because he/she doesn\'t have resource as ' +
                  str(qty_cost) + ' required.')
        else:
            # The player do not have to use the effect; otherwie, the exchange is applied.
            money_resource_cost = player.choose_exchange_resource(True, qty_cost, money_resource_cost_choices,
                                                                  money_resource_gain, qty_gain)
            # We apply the exchange if the player wants to do it.
            if money_resource_cost is None:
                print(indent(4) + player.txt_name_money_resources_workers_PPs_deck(True, True, False, False, False) +
                      ' and didn\'t use the effect.')
            else:
                player.current_money_resources[money_resource_cost] += qty_cost
                player.current_money_resources[money_resource_gain] += qty_gain
                print(indent(4) +
                      player.txt_name_money_resources_workers_PPs_deck(True, True, False, False, False) + '.')

    def apply_secondary_effect(self) -> None:
        """Apply the secondary effect of a market player building."""
        super().apply_secondary_effect()
        self.apply_no_cost_only_gain_effect(self.secondary_effect.money_resources_gain, self.color_player.player)


class GoldMinePlayerBuilding(PlayerBuilding):
    """Gold mine player building."""

    def __init__(self, belongs_to_beginner_version: bool, can_be_a_prestige_building: bool,
                 allows_to_place_a_worker: bool, front_color: str, name: str, n_prestige_pts: int,
                 primary_effect: Effect, resource_costs, can_be_a_residential_building: bool, secondary_effect: Effect,
                 color_player: ColorPlayer):
        """Initialization of a gold mine player building."""
        PlayerBuilding.__init__(self, belongs_to_beginner_version, can_be_a_prestige_building, allows_to_place_a_worker,
                                front_color, name, n_prestige_pts, primary_effect, resource_costs,
                                can_be_a_residential_building, secondary_effect, color_player)

    def apply_primary_effect(self, player: Player) -> None:
        """Apply the primary effect of a gold mine player building."""
        super().apply_primary_effect(player)
        self.apply_no_cost_only_gain_effect(self.primary_effect.money_resources_gain, player)

    def apply_secondary_effect(self) -> None:
        """Apply the secondary effect of a gold mine player building."""
        """
        Exchange 1 cube from your personal stock with 1 gold cube from the stock.
        """
        # Remark: Hard-coded! We don't use the tags <cost><CHOICES>... and <gain><n_gold_cubes>+1... in <game_elements><buildings><player_buildings><player_building><secondary_effect>.
        super().apply_secondary_effect()
        money_resource_cost, qty_cost = None, -1  # type:module_Resource.Resource, int # None for any resource but we eliminate wild (to avoid the case to exchange 1 wild with 1 wild!).
        money_resource_gain, qty_gain =module_Resource.Resource.get_wild_resource(), +1  # type:module_Resource.Resource, int
        player = self.color_player.player  # type: Player
        money_resource_cost_choices = [money_resource for money_resource, qty in player.current_money_resources.items()
                                       if money_resource != module_Resource.Money.money and not money_resource.is_wild()
                                       and qty + qty_cost >= 0
                                       ]  # type: List[module_Resource.Resource] # All suffisant available resources excepted wild.
        if not money_resource_cost_choices:
            print(indent(4) + player.txt_name_money_resources_workers_PPs_deck(True, True, False, False, False) +
                  ' and can\'t apply the effect because he/she doesn\'t have resource (wild is not considered) as ' +
                  str(qty_cost) + ' required.')
        else:
            # The player can have or not the choice of the resource.
            if len(money_resource_cost_choices) == 1:
                money_resource_cost = money_resource_cost_choices[0]
                print(indent(4) +
                      player.name() + 'can only exchange resource ' + money_resource_cost.name + ', and it is done.')
            else:
                money_resource_cost = player.choose_exchange_resource(False, qty_cost, money_resource_cost_choices,
                                                                      money_resource_gain, qty_gain)
            # We apply the exchange.
            player.current_money_resources[money_resource_cost] += qty_cost
            player.current_money_resources[money_resource_gain] += qty_gain
            print(indent(4) + player.txt_name_money_resources_workers_PPs_deck(True, True, False, False, False) + '.')


class BankPlayerBuilding(PlayerBuilding):
    """Bank player building."""

    def __init__(self, belongs_to_beginner_version: bool, can_be_a_prestige_building: bool,
                 allows_to_place_a_worker: bool, front_color: str, name: str, n_prestige_pts: int,
                 primary_effect: Effect, resource_costs, can_be_a_residential_building: bool, secondary_effect: Effect,
                 color_player: ColorPlayer):
        """Initialization of a bank player building."""
        PlayerBuilding.__init__(self, belongs_to_beginner_version, can_be_a_prestige_building, allows_to_place_a_worker,
                                front_color, name, n_prestige_pts, primary_effect, resource_costs,
                                can_be_a_residential_building, secondary_effect, color_player)

    def apply_primary_effect(self, player: Player) -> None:
        """Apply the primary effect of a bank player building."""
        """
        Buy 1 gold from the stock with 1 denier or buy 2 gold from the stock with 3 deniers.
        """
        # Remark: Hard-coded! We don't use the tag <CHOICES>... in <game_elements><buildings><player_buildings><player_building><secondary_effect>.
        super().apply_primary_effect(player)
        all_costs = [(module_Resource.Money.money, -1), (module_Resource.Money.money, -3)]  # type: List[Tuple[module_Resource.Money, int]] # Ordered!
        resource_gain_choices, single_qty_gain = [module_Resource.Resource.get_wild_resource()], \
                                                 +1  # type: List[module_Resource.Resource], int # single_qty_gain must be equals to one!
        self.apply_effect_multi(player, all_costs, resource_gain_choices, single_qty_gain)

    def apply_secondary_effect(self) -> None:
        """Apply the secondary effect of a bank player building."""
        """
        Buy 1 gold from the stock with 2 deniers.
        """
        # Remark: Hard-coded! We don't use the tags <cost><n_deniers>-2 and <gain><n_gold_cubes>+1 in <game_elements><buildings><player_buildings><player_building><secondary_effect>.
        super().apply_secondary_effect()
        money_resource_cost, qty_cost = module_Resource.Money.money, -2  # type: module_Resource.Money, int
        player = self.color_player.player  # type: Player
        if player.current_money_resources[money_resource_cost] + \
                qty_cost < 0:  # Has the player enough money or resource?
            print(indent(4) + player.txt_name_money_resources_workers_PPs_deck(True, True, False, False, False) +
                  ' and can\'t apply the effect because he/she doesn\'t have enough money or resource as ' +
                  str(qty_cost) + ' ' + money_resource_cost.name + '(s) required.')
        else:
            resource_gain_choices, qty_gain = [module_Resource.Resource.get_wild_resource()], +1  # type: List[module_Resource.Resource], int
            resource_gain = player.choose_buy_resource(money_resource_cost, qty_cost, resource_gain_choices,
                                                       qty_gain)  # type:module_Resource.Resource
            if resource_gain is None:
                print(indent(4) + player.txt_name_money_resources_workers_PPs_deck(True, True, False, False, False) +
                      ' and had chosen to don\'t apply the effect.')
            else:
                print(indent(4) + player.name() + ' wants to consume ' +
                      str(qty_cost) + ' ' + money_resource_cost.name + '(s) to obtain ' +
                      str(qty_gain) + ' ' + resource_gain.name + '(s).')
                player.current_money_resources[money_resource_cost] += qty_cost
                player.current_money_resources[resource_gain] += qty_gain
                print(indent(4) + player.txt_name_money_resources_workers_PPs_deck(True, True, False, False, False) +
                      ' once the effect applied.')


class ChurchPlayerBuilding(PlayerBuilding):
    """Church player building."""

    def __init__(self, belongs_to_beginner_version: bool, can_be_a_prestige_building: bool,
                 allows_to_place_a_worker: bool, front_color: str, name: str, n_prestige_pts: int,
                 primary_effect: Effect, resource_costs, can_be_a_residential_building: bool, secondary_effect: Effect,
                 color_player: ColorPlayer):
        """Initialization of a church player building."""
        PlayerBuilding.__init__(self, belongs_to_beginner_version, can_be_a_prestige_building, allows_to_place_a_worker,
                                front_color, name, n_prestige_pts, primary_effect, resource_costs,
                                can_be_a_residential_building, secondary_effect, color_player)

    def apply_primary_effect(self, player: Player) -> None:
        """Apply the primary effect of a church player building."""
        """
        Buy 1 Castle token with 2 deniers, or buy 2 Castle tokens with 5 deniers.
        """
        # Remark: Hard-coded! We don't use the tag <CHOICES>... in <game_elements><buildings><player_buildings><player_building><secondary_effect>.
        super().apply_primary_effect(player)
        self.apply_effect_buy_castle_multi(player, [(module_Resource.Money.money, -2), (module_Resource.Money.money, -5)])

    def apply_secondary_effect(self) -> None:
        """Apply the secondary effect of a church player building."""
        """
        Buy 1 Castle token with 3 deniers.
        """
        # Remark: Hard-coded! We don't use the tags <cost><n_deniers>-3 and <gain><n_castle_tokens>+1 in <game_elements><buildings><player_buildings><player_building><secondary_effect>.
        super().apply_secondary_effect()
        self.apply_effect_buy_castle_multi(self.color_player.player, [(module_Resource.Money.money, -3)])

    def apply_effect_buy_castle_multi(self, player: Player, all_costs) -> None:
        """Apply the primary or secondary effect of a church player building that is buy Castle tokens with deniers."""
        remaining_n_castle_tokens = Building.game_element.game.get_remaining_n_castle_tokens()  # type: int
        if remaining_n_castle_tokens == 0:
            print(indent(4) + 'The effect can\'t be applied because there are not tokens anymore in the castle.')
        else:
            # Display the tokens in the castle.
            print(indent(4) + 'The tokens in the castle are: ' +
                  TXT_SEPARATOR.join(str(castle.current_n_castle_tokens) + ' of ' + str(castle.n_prestige_pts) +
                                     ' prestige point(s) (' + castle.name + ')'
                                     for castle in Building.game_element.castle if castle.current_n_castle_tokens > 0) +
                  '.')
            # Prepare costs and gains.
            castle_gain_choices = [castle for castle in Building.game_element.castle
                                   for _counter in range(castle.current_n_castle_tokens)]  # type: List[Castle]
            single_qty_gain = +1  # type: int # Unused. # Must be equals to one!
            costs = [(money_resource_cost, qty_cost) for (money_resource_cost, qty_cost) in all_costs
                     if player.current_money_resources[money_resource_cost] + qty_cost >= 0]
            n_choices = min(len(costs), len(castle_gain_choices))  # type: int
            costs = costs[:n_choices]
            castle_gain_choices = castle_gain_choices[:n_choices]
            # Has the player enough money or resource?
            if n_choices == 0:
                print(indent(4) + player.txt_name_money_resources_workers_PPs_deck(True, False, False, True, False) +
                      ' and can\'t apply the effect because he/she doesn\'t have enough money or resource as ' +
                      'either ' + ' or '.join(str(qty_cost) + ' ' + money_resource_cost.name + '(s)'
                                              for (money_resource_cost, qty_cost) in all_costs) + ' required.')
            else:
                castles_gain = player.choose_buy_castle_multi(costs, castle_gain_choices)
                if not castles_gain:
                    print(indent(4) +
                          player.txt_name_money_resources_workers_PPs_deck(True, False, False, True, False) +
                          ' and had chosen to don\'t apply the effect.')
                else:
                    n_castles_gain = len(castles_gain)  # type: int
                    money_resource_cost, qty_cost = costs[
                        n_castles_gain - 1]  # type: List[module_Resource.MoneyResource], int # costs must be ordered!
                    print(indent(4) + player.name() + ' wants to consume ' +
                          str(qty_cost) + ' ' + money_resource_cost.name + '(s).')
                    player.current_money_resources[money_resource_cost] += qty_cost
                    for castle_gain, qty_gain in collections.Counter(castles_gain).items():  # To group by castle part.
                        print(indent(4) + player.name() + ' wants to obtain ' +
                              str(qty_gain) + ' ' + castle_gain.name + '(s) each giving ' +
                              str(castle_gain.n_prestige_pts) + ' prestige point(s).')
                        player.current_n_prestige_pts += castle_gain.n_prestige_pts * qty_gain
                        castle_gain.current_n_castle_tokens -= qty_gain
                    print(indent(4) +
                          player.txt_name_money_resources_workers_PPs_deck(True, False, False, True, False) +
                          ' once the effect applied.')


class BackgroundPlayerBuilding(Building):
    """Background of all the player buildings (green cards) corresponding to the résidence player building."""
    """
    Exists exactly one background player building for each color of player and conversely exists exactly one color of player for each background player building.
    So, each player has got exactly one background player building (for one color of player).
    Each player building transformed into a résidence refers to the same background player building.
    """

    def __init__(self, belongs_to_beginner_version: bool, can_be_a_prestige_building: bool,
                 allows_to_place_a_worker: bool, front_color: str, name: str, n_prestige_pts: int,
                 primary_effect: Effect, resource_costs, color_player: ColorPlayer = None):
        """Initialization of a background player building."""
        Building.__init__(self, belongs_to_beginner_version, can_be_a_prestige_building, allows_to_place_a_worker,
                          front_color, name, n_prestige_pts, primary_effect, resource_costs)
        # Specific attributes.
        self.color_player = color_player  # type: ColorPlayer

    def get_building_type(self):  # -> BuildingType
        """Indicates that this building is a background player building."""
        return BuildingType.BACKGROUND

    def income_effect(self, income_phase: module_Phase.Phase = None) -> None:
        """Give some money to the player owing this background player building on the road."""
        n_deniers = income_phase.n_deniers_per_residence  # type: int
        print(indent(2) + self.color_player.player.name() + ' obtains ' + str(n_deniers) + ' ' + module_Resource.Money.money.name +
              '(s) for a(n) ' + self.name + ' building along the road.')
        self.color_player.player.current_money_resources[module_Resource.Money.money] += n_deniers


class NeutralBuilding(Building):
    """All 5 neutral buildings (pink cards): park, forest, quarry, peddler, trading post."""
    """
    Each neutral building is described by its name and effect (effect phase).
    """

    # belongs_to_beginner_version = None  # type: bool
    # front_color = None  # type: str
    # n_prestige_pts = 0  # type: int
    neutral_buildings = {}  # type: Dict[str, NeutralBuilding] # All neutral buildings where key is name and value is NeutralBuilding.

    def __init__(self, belongs_to_beginner_version: bool, can_be_a_prestige_building: bool,
                 allows_to_place_a_worker: bool, front_color: str, name: str, n_prestige_pts: int,
                 primary_effect: Effect, resource_costs=None):
        """Initialization of a neutral building."""
        # We have: belongs_to_beginner_version = None, front_color = None, n_prestige_pts = 0, resource_costs = None.
        Building.__init__(self, belongs_to_beginner_version, can_be_a_prestige_building, allows_to_place_a_worker,
                          front_color, name, n_prestige_pts, primary_effect, resource_costs)
        NeutralBuilding.neutral_buildings[name] = self

    @staticmethod
    def get_neutral_building(name: str):  # -> NeutralBuilding
        """Get a neutral building from its name."""
        return NeutralBuilding.neutral_buildings.get(name)

    def get_building_type(self):  # -> BuildingType
        """Indicates that this building is a neutral building."""
        return BuildingType.NEUTRAL

    def apply_primary_effect(self, player: Player) -> None:
        """Apply the (default that is for park, forest, quarry and trading post) effect of a neutral building."""
        print(indent(3) + 'Effect of the neutral building ' + self.name +
              ' for a worker of the player ' + player.name() + ': ' + self.primary_effect.text)
        self.apply_no_cost_only_gain_effect(self.primary_effect.money_resources_gain, player)


class PeddlerNeutralBuilding(NeutralBuilding):
    """Peddler neutral building."""

    def __init__(self, belongs_to_beginner_version: bool, can_be_a_prestige_building: bool,
                 allows_to_place_a_worker: bool, front_color: str, name: str, n_prestige_pts: int,
                 primary_effect: Effect, resource_costs):
        """Initialization of a peddler neutral building."""
        NeutralBuilding.__init__(self, belongs_to_beginner_version, can_be_a_prestige_building,
                                 allows_to_place_a_worker, front_color, name, n_prestige_pts, primary_effect,
                                 resource_costs)

    def apply_primary_effect(self, player: Player) -> None:
        """Apply the effect of a peddler neutral building."""
        """
        Buy 1 cube (any resource but gold) from the stock with 1 denier.
        """
        # Remark: Hard-coded! We don't use the tags <cost><n_deniers>-1 and <gain><CHOICES>... in <game_elements><buildings><neutral_buildings><neutral_building>.
        print(indent(3) + 'Effect of the neutral building ' + self.name +
              ' for a worker of the player ' + player.name() + ': ' + self.primary_effect.text)
        self.apply_peddler_effect(player)


class PrestigeBuilding(Building):
    """All 7 prestige buildings (blue cards): theatre, statue, hotel, stables, town hall, monument, cathedral."""
    """
    Each prestige building is described by its name, cost (number of food, wood, stone or gold), number of prestige
    points and [optionally] effect (income phase).
    """

    # front_color = None  # type: str

    def __init__(self, belongs_to_beginner_version: bool, can_be_a_prestige_building: bool,
                 allows_to_place_a_worker: bool, front_color: str, name: str, n_prestige_pts: int,
                 primary_effect: Effect, resource_costs, color_player: ColorPlayer = None):
        """Initialization of a prestige building."""
        Building.__init__(self, belongs_to_beginner_version, can_be_a_prestige_building, allows_to_place_a_worker,
                          front_color, name, n_prestige_pts, primary_effect, resource_costs)
        # Specific attributes.
        self.color_player = color_player  # type: ColorPlayer

    def get_building_type(self):  # -> BuildingType
        """Indicates that this building is a prestige building."""
        return BuildingType.PRESTIGE


class HotelPrestigeBuilding(PrestigeBuilding):
    """Hotel prestige building."""

    def __init__(self, belongs_to_beginner_version: bool, can_be_a_prestige_building: bool,
                 allows_to_place_a_worker: bool, front_color: str, name: str, n_prestige_pts: int,
                 primary_effect: Effect, resource_costs, color_player: ColorPlayer = None):
        """Initialization of an hotel prestige building."""
        PrestigeBuilding.__init__(self, belongs_to_beginner_version, can_be_a_prestige_building,
                                  allows_to_place_a_worker, front_color, name, n_prestige_pts, primary_effect,
                                  resource_costs, color_player)

    def income_effect(self, income_phase: module_Phase.Phase = None) -> None:
        """Give some money to the player owing this hotel prestige building on the road."""
        n_deniers = income_phase.n_deniers_if_hotel  # type: int
        print(indent(2) + self.color_player.player.name() + ' obtains ' + str(n_deniers) + ' ' + module_Resource.Money.money.name +
              '(s) for a(n) ' + self.name + ' building along the road.')
        self.color_player.player.current_money_resources[module_Resource.Money.money] += n_deniers


@unique
class BuildingType(Enum):
    """Enumeration of all the types of buildings."""
    """
    We choose to code the building type with an enumeration instead of using .__class__ or type() into Building classes.
    """
    PRESTIGE = 0
    NEUTRAL = 1
    BACKGROUND = 2
    PLAYER = 3
