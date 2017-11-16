"""
A pattern to create a booking cluster description

The properties in this group are mostly from {region} region.
The properties are usually booked during {breakpoint} breakpoints by {adults} with {children} and {babies}.
These are {avg_spend_per_head} {detached} properties in the {complex} close to {close_to}.
The group's properties are {no smoking}, {pets}, available for {shortbreakok}, and accessible to {accessebility}.
The properties have {content} and contain {sleeps} sleeping places.
The average rating of the properties is {stars} stars.
"""

from main.describer.common import avg_spend_per_head_features, stars_features, general_conditions_features, \
    accessibility_features, single_contents_features, plural_contents_features, concat_using_comma_and_and, \
    select_the_best, concat_using_comma
from main.describer.user import close_to_features


adults_features = {
    'adults_(0.999, 3.0]': ('small', 0),
    'adults_(3.0, 8.0]': ('medium', 1),
    'adults_(8.0, 16.0]': ('large', 2),
}

children_features = {
    'children_(-0.001, 1.0]': ('a child', 0),
    'children_(1.0, 3.0]': ('several children', 1),
    'children_(3.0, 6.0]': ('many children', 2),
}

sleeps_features = {
    "sleeps_(1.999, 4.0]": ("2-4", 0),
    "sleeps_(4.0, 7.0]": ("5-7", 1),
    "sleeps_(7.0, 11.0]": ("8-11", 2),
    "sleeps_(11.0, 17.0]": ("12-17", 3),
    "sleeps_(17.0, 22.0]": ("more than 17", 4),
}


def first_sentence(regions):
    sentence = "The properties in this group are mostly from the %s" % concat_using_comma_and_and(regions)
    sentence += " regions." if len(regions) > 1 else " region."
    return sentence


def second_sentence(breakpoints, adults, children, is_babies):
    sentence = "The properties are usually booked"
    if breakpoints:
        sentence += " during %s" % concat_using_comma_and_and(breakpoints)
        sentence += " breakpoints" if len(breakpoints) > 1 else " breakpoints"
    if adults:
        sentence += " by a %s company of people" % select_the_best(adults)
    if children:
        sentence += " with %s" % select_the_best(children)
    if is_babies:
        sentence += " and babies"
    sentence += "."
    return sentence


def third_sentence(avg_spend_per_head, is_detached, is_complex, close_to):
    sentence = "These are"
    if avg_spend_per_head:
        sentence += " %s" % concat_using_comma_and_and(avg_spend_per_head)
    if is_detached:
        sentence += " detached"
    sentence += " properties"
    if is_complex:
        sentence += " in a complex"
    if close_to:
        sentence += " close to %s" % concat_using_comma_and_and(close_to)
    sentence += "."
    return sentence


def fourth_sentence(general_conditions, is_shortbreakok, accessibility):
    sentence = "The properties are"
    if general_conditions:
        sentence += " %s" % concat_using_comma(general_conditions)
    if is_shortbreakok:
        sentence += ", available for a short break"
    if accessibility:
        if general_conditions:
            sentence += ", and accessible to %s" % concat_using_comma_and_and(accessibility)
        else:
            sentence += " accessible to %s" % concat_using_comma_and_and(accessibility)
    sentence += "."
    return sentence


def fifth_sentence(contents, sleeps):
    sentence = "The properties"
    if contents:
        sentence += " have %s" % concat_using_comma_and_and(contents)
    if sleeps:
        if contents:
            sentence += ", and contain %s sleeping places" % select_the_best(sleeps)
        else:
            sentence += " contain %s sleeping places" % select_the_best(sleeps)
    sentence += "."
    return sentence


def sixth_sentence(stars):
    sentence = "The average rating of the properties is %s stars." % select_the_best(stars)
    return sentence


def describe_booking_cluster(booking_cluster_features):
    regions = []
    breakpoints = []
    adults = []
    children = []
    is_babies = False
    avg_spend_per_head = []
    is_detached = False
    is_complex = False
    close_to = []
    general_conditions = []
    is_shortbreakok = False
    accessibility = []
    contents = set()
    sleeps = []
    stars = []

    for feature in booking_cluster_features:
        if feature == 'complex':
            is_complex = True
        elif feature == 'detached':
            is_detached = True
        elif feature == 'babies_(0.5, 2.0]':
            is_babies = True
        elif feature == 'shortbreakok':
            is_shortbreakok = True

        elif feature.startswith("breakpoint_"):
            breakpoints.append(feature.replace("breakpoint_", ""))
        elif feature.startswith("region_"):
            regions.append(feature.replace("region_", ""))

        elif feature.startswith("avg_spend_per_head_"):
            avg_spend_per_head.append(avg_spend_per_head_features[feature])
        elif feature.startswith("adults_"):
            adults.append(adults_features[feature])
        elif feature.startswith("children_"):
            children.append(children_features[feature])
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
    if regions:
        desc_sentences.append(first_sentence(regions))
    if breakpoints or adults:
        desc_sentences.append(second_sentence(breakpoints, adults, children, is_babies))
    if avg_spend_per_head or is_detached or is_complex or close_to:
        desc_sentences.append(third_sentence(avg_spend_per_head, is_detached, is_complex, close_to))
    if general_conditions or accessibility:
        desc_sentences.append(fourth_sentence(general_conditions, is_shortbreakok, accessibility))
    if contents or sleeps:
        desc_sentences.append(fifth_sentence(contents, sleeps))
    if stars:
        desc_sentences.append(sixth_sentence(stars))

    return " ".join(desc_sentences)
