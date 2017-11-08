"""
A pattern to create a user description:

The user belongs to {oac_groupdesc} OAC group(s).
She usually books {is_detached} {avg_spend_per_head} properties with average
rating {stars} stars for the {breakpoint} breakpoint(s).
The average booking duration is {n_booked_days} days.

Previously booked properties were {is_complex} {close_to}.
The properties were {general_conditions} {accessibility} with {contents}.
The properties were reachable by car in {drivetime} hours.
"""

avg_spend_per_head_features = {
    'avg_spend_per_head_(8.707, 26.232]': 'cheap',
    'avg_spend_per_head_(26.232, 42.125]': 'mid-range',
    'avg_spend_per_head_(42.125, 66.642]': 'expensive',
    'avg_spend_per_head_(66.642, 99.819]': 'very expensive',
}

close_to_features = {
    'coast 5 miles': 'a coast',
    'railway 5 miles': 'a railway',
    'sandy beach 1 mile': 'a sandy beach'
}

drivetime_features = {
    'drivetime_(0.999, 3.0]': ('3', 0),
    'drivetime_(3.0, 4.0]': ('3-4', 1),
    'drivetime_(4.0, 7.0]': ('more than 4', 2),
}

n_booked_days_features = {
    'n_booked_days_(1.999, 4.0]': 'up to 4',
    'n_booked_days_(4.0, 9.0]': '5-9',
    'n_booked_days_(9.0, 13.0]': 'more than 10',
}

stars_features = {
    'stars_(2.499, 3.0]': ('3', 0),
    'stars_(3.0, 3.5]': ('3.5', 1),
    'stars_(3.5, 4.0]': ('4', 2),
    'stars_(4.0, 5.0]': ('more than 4', 3),
}

general_conditions_features = {
    'no smoking': 'non-smoking',
    'pets': 'pets friendly'
}

plural_contents_features = {
    'big gardens or farm to wander',
    'boats or mooring available',
    'countryside views',
    'parking',
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
    'high chair': 'high chairs',
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
}

accessibility_features = {
    'part disabled': 'partially disabled people',
    'wheel chair facilities': 'people using wheel chairs'
}


def concat_using_comma_and_and(values):
    if len(values) <= 2:
        return " and ".join(values)
    else:
        values[-1] = "and %s" % values[-1]
        return ", ".join(values)


def select_the_best(values):
    value, weight = sorted(values, key=lambda x: x[1])[-1]
    return value


def first_sentence(oac_groups):
    sentence = "The user belongs to " + concat_using_comma_and_and(oac_groups)
    sentence += " OAC groups." if len(oac_groups) > 1 else " OAC group."
    return sentence


def second_sentence(is_detached, avg_spend_per_head, stars, breakpoints):
    sentence = "She usually books"
    if is_detached:
        sentence += " detached"
    if avg_spend_per_head:
        sentence += " %s" % concat_using_comma_and_and(avg_spend_per_head)
    sentence += " properties"
    if stars:
        sentence += " with average rating %s" % select_the_best(stars)
    if breakpoints:
        sentence += " for the %s" % concat_using_comma_and_and(breakpoints)
        sentence += " breakpoints" if len(breakpoints) > 1 else " breakpoint"
    sentence += "."
    return sentence


def third_sentence(is_complex, close_to):
    sentence = "She prefers properties"
    if is_complex:
        sentence += " in the complex"
    if close_to:
        sentence += " close to %s" % concat_using_comma_and_and(close_to)
    sentence += "."
    return sentence


def fourth_sentence(general_conditions, accessibility, contents):
    sentence = "The previously booked properties were"
    if general_conditions:
        sentence += " %s" % concat_using_comma_and_and(general_conditions)
    if accessibility:
        sentence += " accessible for %s" % concat_using_comma_and_and(accessibility)
    if contents:
        sentence += " with %s" % concat_using_comma_and_and(contents)
    sentence += "."
    return sentence


def fifth_sentence(drivetime):
    sentence = "She could reach the properties by car in %s hours." % select_the_best(drivetime)
    return sentence


def describe_user(user_features):
    oac_groups = []
    is_detached = False
    avg_spend_per_head = []
    stars = []
    breakpoint = []
    n_booked_days = []
    is_complex = False
    close_to = []
    general_conditions = []
    accessibility = []
    contents = set()
    drivetime = []

    for feature in user_features:
        if feature == 'complex':
            is_complex = True
        elif feature == 'detached':
            is_detached = True

        elif feature.startswith("breakpoint_"):
            breakpoint.append(feature.replace("breakpoint_", ""))
        elif feature.startswith("oac_groupdesc_"):
            oac_groups.append('"%s"' % feature.replace("oac_groupdesc_", ""))

        elif feature.startswith("avg_spend_per_head_"):
            avg_spend_per_head.append(avg_spend_per_head_features[feature])
        elif feature.startswith("drivetime_"):
            drivetime.append(drivetime_features[feature])
        elif feature.startswith("n_booked_days_"):
            n_booked_days.append(n_booked_days_features[feature])
        elif feature.startswith("stars_"):
            stars.append(stars_features[feature])

        elif feature in general_conditions_features:
            general_conditions.append(general_conditions_features[feature])
        elif feature in accessibility_features:
            accessibility.append(accessibility_features[feature])
        elif feature in close_to_features:
            close_to.append(close_to_features[feature])

        elif feature in single_contents_features:
            contents.add(single_contents_features[feature])
        elif feature in plural_contents_features:
            contents.add(feature)

    contents = list(contents)

    desc_sentences = []
    if oac_groups:
        desc_sentences.append(first_sentence(oac_groups))
    if is_detached or avg_spend_per_head or stars or breakpoint:
        desc_sentences.append(second_sentence(oac_groups, avg_spend_per_head, stars, breakpoint))
    if is_complex or close_to:
        desc_sentences.append(third_sentence(is_complex, close_to))
    if general_conditions or accessibility or contents:
        desc_sentences.append(fourth_sentence(general_conditions, accessibility, contents))
    if drivetime:
        desc_sentences.append(fifth_sentence(drivetime))

    return " ".join(desc_sentences)


