avg_spend_per_head_features = {
    'avg_spend_per_head_(8.707, 26.232]': 'cheap',
    'avg_spend_per_head_(26.232, 42.125]': 'mid-range',
    'avg_spend_per_head_(42.125, 66.642]': 'expensive',
    'avg_spend_per_head_(66.642, 99.819]': 'very expensive',
}

stars_features = {
    'stars_(2.499, 3.0]': ('3', 0),
    'stars_(3.0, 3.5]': ('3.5', 1),
    'stars_(3.5, 4.0]': ('4', 2),
    'stars_(4.0, 5.0]': ('more than 4', 3),
}

plural_contents_features = {
    'big gardens or farm to wander',
    'boats or mooring available',
    'countryside views',
    'sea views',
}

single_contents_features = {
    'baby sitting': 'a baby sitter',
    'barbecue': 'a barbecue',
    'broadband': 'a broadband internet connection',
    'enclosed garden': 'an enclosed garden',
    'fishing - private': 'a private fishing place',
    'games room': 'a games room',
    'golf course nearby': 'a golf course nearby',
    # 'high chair': 'high chairs',
    'hot tub': 'a hot tub',
    'indoor pool': 'a pool',
    'jacuzzi': 'a jacuzzi',
    'woodburner': 'a woodburner',
    'outdoor heated pool': 'a pool',
    'outdoor unheated pool': 'a pool',
    'piano': 'a piano',
    'pool': 'a pool',
    'pub 1 mile walk': 'a pub nearby',
    'sailing nearby': 'a sailing nearby',
    'sauna': 'a sauna',
    'snooker table': 'a snooker table',
    'steam room': 'a steam room',
    'tennis court': 'a tennis court',
    'farm help': 'a farmworker',
    'parking': 'a parking',
}

accessibility_features = {
    'part disabled': 'partially disabled people',
    'wheel chair facilities': 'people using wheel chairs'
}

general_conditions_features = {
    'no smoking': 'non-smoking',
    'pets': 'pets friendly',
    'good for honeymooners': 'good for honeymooners',
}


def concat_using_comma(values):
    return ", ".join(values)


def concat_using_comma_and_and(values):
    if len(values) <= 2:
        return " and ".join(values)
    else:
        values[-1] = "and %s" % values[-1]
        return ", ".join(values)


def select_the_best(values):
    value, weight = sorted(values, key=lambda x: x[1])[-1]
    return value
