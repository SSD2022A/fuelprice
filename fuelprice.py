#!/usr/bin/python3
"""Display petrol fuel prices.  Prices are obtained from a web service.

   Requires requests package ('pip install --upgrade requests')
"""
import xml.dom, xml.dom.minidom
import requests

URL = "https://www.bangchak.co.th/api/oilprice"

class FuelPrice:
    @classmethod
    def get_fuel_prices(cls):
        """Get petrol fuel prices from a web service."""
        response = requests.get(URL)
        if response.status_code != 200:
            print(f"Response code {response.status_code} from {URL}")
            return
        return response.content
    
    @classmethod
    def parse_data(cls, data: str):
        """Parse XML data containing fuel prices, using Bangchak's schema.
    
        :param data:  string containing XML format data for fuel prices.
        :returns:  array of fuel price info, each one a dictionary. Keys are
             the tags in the fuel xml data.
             Reformatting Fuel 'type' values: the fuel 'type' contains
             Bangchak brand names with "EVO" and "S".  Remove the "EVO" and "S"
             and convert names to Title Case.
    
        Oil prices are contained in "item" elements of the XML.
        Each oil price element contains 
        ```
        <item>
          <type>fuel type</type>
          <today>price today</today>
          <tomorrow>price tomorrow</tomorrow>
          <yesterday>price yesterday</yesterday>
          <unit_th>บาท/ลิตร</unit_th>
          <unit_en>Baht/Liter</unit_en>
          <image>url</image>
          <image2>url</image2>
        </item>
        ```
        """
        document = xml.dom.minidom.parseString(data)
        elements = document.getElementsByTagName("item")
        fuels = []
        for element in elements:
            # the child nodes are element.childNodes
            fuel = {}
            for node in element.childNodes:
                tagName = node.tagName
                if tagName in ['image','image2']: continue  # skip image URLs
                fuel[node.tagName] = node.firstChild.nodeValue
            # clean up 'type' attribute
            if 'type' in fuel:
                fuel['type'] = fuel['type'].replace(' S','').replace(' EVO','')
                fuel['type'] = fuel['type'].title()  # use title case
            fuels.append(fuel)
        return fuels
    
    @classmethod
    def get_date(cls, data):
        """Get the date of publication of the data."""
        document = xml.dom.minidom.parseString(data)
        elements = document.getElementsByTagName("update_date")
        date_str = elements[0].firstChild.nodeValue
        return date_str
    


def print_fuel_prices(date, fuels):
    """Print the fuel names and prices in a useful format."""
    print(f"{'Fuel Type':20}  Today        Tomorrow")
    for fuel in fuels:
        fueltype = fuel['type']
        change = float(fuel['today']) - float(fuel['yesterday'])
        print(f"{fueltype:20}  {fuel['today']:5} {change:+0.2f}  {fuel['tomorrow']:6} {fuel['unit_en']}")
    print(date)

def print_raw_prices(fuels):
    """Print actual values from the dictionary of fuel price data."""
    # headers
    print(f"{'Fuel Type':20} {'Yesterday':10} {'Today':10} {'Tomorrow':10}")
    for fuel in fuels:
        fueltype = fuel['type']
        yesterday = fuel['yesterday']
        today = fuel['today']
        tomorrow = fuel['tomorrow']
        print(f"{fueltype:20} {yesterday:10} {today:10} {tomorrow:10}")


if __name__ == '__main__':
    data = FuelPrice.get_fuel_prices()
    fuels = FuelPrice.parse_data(data)
    # the publication date
    date = FuelPrice.get_date(data)
    # print only Gasohol prices (comment out to include Diesel fuels)
    fuels = [fuel for fuel in fuels if 'Gasohol' in fuel['type']]
    fuels = sorted(fuels, key=lambda fuel: fuel['type'])
    print_fuel_prices(date, fuels)
