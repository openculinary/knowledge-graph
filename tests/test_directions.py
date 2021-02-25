def test_description_parsing(client):
    description_markup = {
        'Pre-heat the oven to 250 degrees F.': (
            'Pre-heat the <mark class="equipment appliance">oven</mark> '
            'to 250 degrees F.'
        ),
        'leave the Slow cooker on a low heat': (
            '<mark class="verb action">leave</mark> the '
            '<mark class="equipment appliance">Slow cooker</mark> '
            'on a low heat'
        ),
        'place casserole dish in oven': (
            'place <mark class="equipment vessel">casserole dish</mark> '
            'in <mark class="equipment appliance">oven</mark>'
        ),
        'empty skewer into the karahi': (
            'empty <mark class="equipment utensil">skewer</mark> into the '
            '<mark class="equipment vessel">karahi</mark>'
        ),
    }

    description_entities = {
        'Pre-heat the oven to 250 degrees F.': ['oven'],
        'leave the Slow cooker on a low heat': ['slow cooker'],
        'place casserole dish in oven': ['oven', 'casserole dish'],
        'empty skewer into the karahi': ['skewer', 'karahi'],
    }

    response = client.post(
        '/directions/query',
        data={'descriptions[]': list(description_markup.keys())}
    )
    for result in response.json:
        description = result['description']
        assert description in description_markup
        assert result['markup'] == description_markup[description]

        entity_names = [entity['name'] for entity in result['entities']]
        assert description in description_entities
        assert entity_names == description_entities[description]
