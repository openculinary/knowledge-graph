def test_description_parsing(client):
    description_markup = {
        'Pre-heat the oven to 250 degrees F.': (
            'Pre-heat the <mark class="equipment appliance">oven</mark> '
            'to 250 degrees F.'
        ),
        'leave the Slow cooker on a low heat': (
            'leave the <mark class="equipment appliance">Slow cooker</mark> '
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

    response = client.post(
        '/equipment/query',
        data={'descriptions[]': list(description_markup.keys())}
    )
    for result in response.json:
        assert result['description'] in description_markup
        assert result['markup'] == description_markup[result['description']]
