import re

from ._abstract import AbstractScraper
from ._grouping_utils import IngredientGroup
from ._utils import get_minutes, get_yields, normalize_string


class PureWow(AbstractScraper):
    @classmethod
    def host(cls):
        return "purewow.com"

    def author(self):
        return self.soup.select_one(".byline .author a").get_text()

    def title(self):
        return self.soup.select_one("h1.hed").get_text()

    def total_time(self):
        return get_minutes(
            self.soup.select_one(".recipe-time-byline-bottom .total").get_text()
        )

    def yields(self):
        servings = self.soup.select_one(".recipe-time-byline-bottom .serves").get_text()
        # Ignore asides after the servings: "(about 12 cups)", "+ 1 cup pesto"
        return get_yields(re.split(r"[(+]", servings)[0])

    def ingredients(self):
        return [
            ingredient
            for group in self.ingredient_groups()
            for ingredient in group.ingredients
        ]

    def ingredient_groups(self):
        groups = [IngredientGroup(ingredients=[])]
        for element in self.soup.select(".ingredient"):
            text = normalize_string(element.get_text())
            if element.select_one("strong"):
                groups.append(IngredientGroup(ingredients=[], purpose=text))
            elif text:
                groups[-1].ingredients.append(text)
        return [group for group in groups if group.ingredients]

    def instructions(self):
        return "\n".join(
            re.sub(r"^\d+\.\s*", "", normalize_string(instruction.get_text()))
            for instruction in self.soup.select(".recipe-direction")
            if instruction.get_text(strip=True)
        )

    def description(self):
        return self.opengraph.description()
