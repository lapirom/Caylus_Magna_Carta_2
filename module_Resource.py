class MoneyResource:
    """Money or Resource."""

    def __init__(self, name: str, number: int):
        """Initialization of money or resource."""
        # Attributes obtained from the XML file.
        self.name = name  # type: str
        self.number = number  # type: int
        # Attributes to play a game.
        self.current_number = self.number  # type: int # Unused because money and resources can be considered infinite.

    def get_name_abbreviation(self) -> str:
        """Get the abbreviation of money or resource name."""
        return self.name[0].upper()


class Money(MoneyResource):
    """Money (coins)."""

    money = None  # type: Money
    class __Money:
        def __init__(self, name: str, number: int):
            self.val = arg
        def __str__(self):
            return repr(self) + self.val
    def __init__(self, name: str, number: int):
        """Initialization of the money."""
        MoneyResource.__init__(self, name, number)
        Money.money = self


class Resource(MoneyResource):
    """4 types of resources (cubes): food, wood, stone or gold."""
    """
    Gold is a wild resource: a cube of gold equals a cube of any type.
    """

    resources = {}  # type: Dict[str, Resource] # All resources where the key is the resource name and the value is the resource.

    def __init__(self, name: str, number: int):
        """Initialization of a resource."""
        MoneyResource.__init__(self, name, number)
        # self.is_wild = is_wild  # Unused because it is not present into the XML file. # Warning: it is commented in order to avoid a conflict with is_wild().
        Resource.resources[name] = self

    @staticmethod
    def get_resource(name: str):  # -> Resource
        """Get a resource from its name."""
        return Resource.resources.get(name)

    @staticmethod
    def get_name_abbreviation_resources(resources=None):  # -> Dict[str[1], Resource] # E.g. {'F': food, ...}.
        """Get the resource name abbreviations and the resources."""
        if resources is None:
            return {resource.get_name_abbreviation(): resource for resource in Resource.resources.values()}
        else:
            return {resource.get_name_abbreviation(): resource for resource in resources}

    def is_wild(self) -> bool:
        """Is it a wild resource?"""
        """
        Remark: this method exists only because such information lacks in the XML file. 
        """
        return self.name.lower() == 'gold'

    @staticmethod
    def get_wild_resource():  # -> Resource:
        """Get the (unique) wild resource."""
        return [resource for resource in Resource.resources.values() if resource.is_wild()][0]
