from collections import defaultdict

from .models import CollectionItem


def owned_by(user, games):
    """Za vsako igro vrne pare platforme in zbirke, v katerih ima uporabnik vsaj en izvod (US-10)."""
    pairs = (
        CollectionItem.objects.filter(collection__user=user, game__in=games)
        .values(
            'game_id', 'platform_id', 'platform__name', 'platform__abbreviation', 'collection_id', 'collection__name',
        )
        .distinct()
        .order_by('platform__abbreviation', 'platform__name', 'collection__name', 'collection_id')
    )
    owned = defaultdict(list)
    for pair in pairs:
        owned[pair['game_id']].append({
            'platform': {
                'id': pair['platform_id'],
                'name': pair['platform__name'],
                'abbreviation': pair['platform__abbreviation'],
            },
            'collection': {'id': pair['collection_id'], 'name': pair['collection__name']},
        })
    return owned
