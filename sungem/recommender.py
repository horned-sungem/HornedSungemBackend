from .models import Vote
from django.contrib.auth.models import User

import implicit
import numpy as np
import json
import threading
import surprise
import pandas as pd

from scipy.sparse import csr_matrix

MAXIMUM_RECOMMENDED_MODULES = 5
MINIMUM_ABSOLUTE_SIMILARITY = 0

# Create your views here.

# TODO: Adjust for new module_data
f = open('sungem/output.json')
module_data = json.load(f)
f.close()
similarity = np.genfromtxt('sungem/similarity.csv', delimiter=',')

# Create dict with subset of attributes for faster recommendation

module_nr_map = {module['Modul Nr.']: (module, index) for index, module in enumerate(module_data)}

model = None
user_items = None
user_to_id = None


def content_similar_modules(n, module_id):
    return sorted(range(len(module_data)), key=lambda i: similarity[module_id, i])[:n]


def collaborative_similar_modules(n, module_id):
    return model.similar_items(module_id)  # this is implicit. Changing to surprise for explicit data



def content_recommend_modules(user, n=5, min_sim=0, return_similarity=False):
    votes = {module_nr_map[vote.module][1]: vote.score for vote in Vote.objects.filter(user=user)}

    module_similarity = [(e, sum(similarity[e, module] * score for module, score in votes.items())) for e in
                         range(len(module_data))]

    filtered_module_similarity = [m for m in module_similarity if m[1] > min_sim and m[0] not in votes]

    recommended = sorted(filtered_module_similarity, key=lambda x: x[1], reverse=True)

    if return_similarity:
        return recommended[:n]

    return [m[0] for m in recommended[:n]]


def collaborative_recommend_modules(user, n=5, min_sim=0, return_similarity=False):
    print(model.recommend(user_to_id[user], user_items))
    if return_similarity:
        return model.recommend(user_to_id[user], user_items)[:n]
    return [m[0] for m in model.recommend(user_to_id[user], user_items)[:n]]


def recommend_modules(user, n=5, min_sim=0):
    vote_count = Vote.objects.count()

    content_results = content_recommend_modules(user, n=n, min_sim=min_sim)
    collaborative_results = collaborative_recommend_modules(user, n=n, min_sim=min_sim)
    return content_results  # TODO: Include collaborative


def update_model():
    # task = asyncio.create_task(async_update_model())
    thread = threading.Thread(target=async_update_model)
    thread.start()


def async_update_model():
    print('Updating....')

    global model, user_items, user_to_id

    users = User.objects.all()
    user_to_id = {user: index for index, user in enumerate(users)}

    modules_count = len(module_data)
    users_count = users.count()

    item_user = csr_matrix((modules_count, users_count))

    for vote in Vote.objects.all():
        print(module_nr_map[vote.module][1], user_to_id[vote.user], vote.score)
        item_user[module_nr_map[vote.module][1], user_to_id[vote.user]] = vote.score

    model = implicit.als.AlternatingLeastSquares()

    model.fit(item_user, show_progress=False)

    user_items = item_user.T.tocsr()


async_update_model()
