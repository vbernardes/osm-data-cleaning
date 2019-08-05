#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
This script contains functions used to explore the database and create visualizations.
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import difflib
from collections import OrderedDict


def get_db():
    """Return a pointer to the local database."""
    from pymongo import MongoClient
    client = MongoClient('localhost:27017')
    db = client.osm
    return db


def get_element_types(db):
    """Count the different types of main elements."""
    pipeline = [ { '$group' : { '_id' : '$element_type',
                                'count' : { '$sum' : 1 } } },
                 { '$sort' : { 'count' : -1 } }
    ]
    return aggregate(db, pipeline)


def get_amenities(db):
    """Get the 5 most popular amenities."""
    pipeline = [ { '$match' : { 'amenity' : { '$ne' : None } } },
                 { '$group' : { '_id' : '$amenity',
                                'count' : { '$sum' : 1 } } },
                 { '$sort' : { 'count' : -1 } },
                 { '$limit' : 5 }
    ]
    return aggregate(db, pipeline)


def get_cuisines(db):
    """Get the 5 most popular cuisine types in the data set."""
    pipeline = [ { '$match' : { 'cuisine' : { '$ne' : None } } },
                 { '$group' : { '_id' : '$cuisine',
                                'count' : { '$sum' : 1 } } },
                 { '$sort' : { 'count' : -1 } },
                 { '$limit' : 5 }
    ]
    return aggregate(db, pipeline)


def get_fuel_stations(db):
    """Get the 5 most popular fuel station brands."""
    pipeline = [ { '$match' : { '$and' : [ { 'amenity' : 'fuel' }, { 'brand' : { '$ne' : None } } ] } },
                 { '$group' : { '_id' : '$brand',
                                'count' : { '$sum' : 1 } } },
                 { '$sort' : { 'count' : -1 } },
                 { '$limit' : 5 }
    ]
    return aggregate(db, pipeline)


def get_top_contributors(db):
    """Get the users with most entries to the data set, along with the number of entries."""
    pipeline = [ { '$group' : { '_id' : '$created.user',
                                'count' : { '$sum' : 1 } } },
                              { '$sort' : { 'count' : -1 } },
                              { '$limit' : 8 }
    ]
    return aggregate(db, pipeline)


def count_unique_users(db):
    return len(db.southeast.distinct('created.user'))


def viz_times(db):
    """Plot the number of entries per year."""
    time_results = db.southeast.find(projection={'created.timestamp':1, '_id':0})

    years = []
    for time in time_results:
        years.append(time['created']['timestamp'][:4]) # we just want the year

    plt.figure()

    time_series = pd.Series(years)
    time_count = time_series.value_counts().sort_index()
    time_count.iloc[1:-1].plot.line(rot=1)  # we are excluding the first and last elements
                                            # because we only want whole years
    plt.title('Entries per year')
    plt.ylabel('Number of entries')
    plt.xlabel('Year')
    plt.savefig('entries_per_year.png', dpi=400)


def convert_result_into_counts(results, key_field='_id'):
    """Convert result from database into dictionary with keys and respective counts."""
    count_data = OrderedDict()
    for dic in results:
        count_data[dic[key_field]] = dic['count']
    return count_data


def viz_top_contributors(results):
    """Create a visualization of the results received about the top contributors."""
    count_data = convert_result_into_counts(results)

    plt.figure()

    series = pd.Series(count_data)
    series.sort_values(ascending=False).plot.bar(rot=1)
    plt.title('Users with most entries created')
    plt.ylabel('Number of entries')
    plt.xlabel('User name')
    plt.savefig('top_contributors.png', dpi=400)


def viz_common_items(db):
    """Create a figure with some common items found in the data set."""

    # Create 1x3 figure
    fig, ax = plt.subplots(nrows=3, ncols=1)
    fig.set_size_inches(6, 7)
    fig.tight_layout()

    # Figure 1: Common amenities
    amenity_count = convert_result_into_counts(get_amenities(db))
    amenity_series = pd.Series(amenity_count)
    amenity_series.sort_values(ascending=False).plot.bar(rot=1, ax=ax[0])
    ax[0].set_title('Amenities')

    # Figure 2: Common cuisines
    cuisine_count = convert_result_into_counts(get_cuisines(db))
    cuisine_series = pd.Series(cuisine_count)
    cuisine_series.sort_values(ascending=False).plot.bar(rot=1, ax=ax[1])
    ax[1].set_title('Cuisines')

    # Figure 3: Common fuel station brands
    fuel_count = convert_result_into_counts(get_fuel_stations(db))
    fuel_series = pd.Series(fuel_count)
    fuel_series.sort_values(ascending=False).plot.bar(rot=1, ax=ax[2])
    ax[2].set_title('Fuel station brands')

    plt.savefig('common_items.png', dpi=400)


def count_unique_cities(db):
    return len(db.southeast.distinct('address.city'))


def get_street_names(db):
    """Get unique street names from 'way' elements in the data set."""
    result = db.southeast.find({'element_type':'way', 'highway':'residential', 'name':{'$ne':None}},
                               projection={ 'name':1, '_id':0 })

    # Get list of unique names from DB
    names = set()
    for item in result:
        if isinstance(item['name'], basestring):
            names.add(item['name'])

    num_names = len(names)
    print "Total number of street names:", num_names

    # Compare each street name to each other and find similar ones
    for name in names:
        for name_to_compare in names:
            if name != name_to_compare:  # we don't want to compare it to itself
                ratio = difflib.SequenceMatcher(lambda x: x == ' ', name, name_to_compare).ratio()
                if ratio > 0.9:
                    print name, '/', name_to_compare


def aggregate(db, pipeline):
    """Pass the given pipeline to MongoDB aggregation framework."""
    result = db.southeast.aggregate(pipeline)
    return result


def print_count_results(result_set):
    counts = convert_result_into_counts(result_set)
    for k, v in counts.iteritems():
        print(k+': '+unicode(v))


def main():
    db = get_db()

    # Insert desired function here. Examples:
    # print_count_results(get_fuel_stations(db))
    # print_count_results(get_top_contributors(db))

if __name__ == '__main__':
    main()