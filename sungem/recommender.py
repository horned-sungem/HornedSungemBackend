import json
import threading

import implicit
import numpy as np
from django.contrib.auth.models import User
from scipy.sparse import csr_matrix

from sungem.models import Vote

MAXIMUM_RECOMMENDED_MODULES = 5
MINIMUM_ABSOLUTE_SIMILARITY = 0

# Create your views here.

# TODO: Adjust for new module_data
f = open('sungem/modules.json')
module_data = json.load(f)
f.close()
similarity = np.genfromtxt('sungem/similarity.csv', delimiter=',')

# Create dict with subset of attributes for faster recommendation

module_nr_map = {module['id']: (module, index) for index, module in enumerate(module_data)}

model = None
user_items = None
user_to_id = None

LINEAR_GROWTH_MAX = 2000
SIMILARITY_RATIO = 1
RECOMMENDATION_RATIO = 1


def combine_similarities(list1, list2, list2_to_list1_ratio=1, linear_growth=False):
    """
    Combines the two inputted lists and sorts them by their cumulative similarity.

    :param list1: first list of tuples (module, similarity)
    :param list2: second list of tuples (module, similarity). linear_growth is applied here
    :param list2_to_list1_ratio: ratio of list2 weight to list1 weight after growth period
    :param linear_growth: set to true if certainty doesn't scale by itself in list2
    :return: list of tuples (module, similarity)
    """
    weight = {module[0]: module[1] for module in list1}

    ratio = list2_to_list1_ratio * (min(1, Vote.objects.count() / 2000) if linear_growth else 1)

    for module in list2:
        if module[0] in weight:
            weight[module[0]] += ratio * module[1]
        else:
            weight[module[0]] = ratio * module[1]

    result = sorted(weight.items(), key=lambda x: x[1], reverse=True)

    return result


def content_similar_modules(n, module_id):
    """
    :return: n modules similar to module_id based on their content similarity
    """
    modules = [(i, similarity[module_id, i]) for i in range(len(module_data)) if similarity[module_id, i] > 0]

    return sorted(modules, key=lambda x: x[1], reverse=True)[:n]


def collaborative_similar_modules(n, module_id):
    """
    :return: n modules similar to module_id based on their collaborative similarity
    """
    # TODO: this is implicit. Should be changed to explicit for better results
    return [module for module in model.similar_items(module_id) if module[1] > 0]


def similar_modules(n, module_id):
    """
    :return: n modules similar to module_id based on their hybrid similarity
    """
    content_result = content_similar_modules(n, module_id=module_id)
    collaborative_result = collaborative_similar_modules(n, module_id=module_id)

    # TODO: return modules instead of id's
    return [module[0] for module in combine_similarities(content_result,
                                                         collaborative_result,
                                                         list2_to_list1_ratio=SIMILARITY_RATIO)]


def content_recommend_modules(user, n=5, min_sim=0, return_similarity=False):
    """
    :param min_sim: minimum absolute similarity to be included in result
    :param return_similarity: boolean flag whether result should include similarity
    :return: n modules recommended to user based on their content similarity
    """
    votes = {module_nr_map[vote.module][1]: vote.score for vote in Vote.objects.filter(user=user)}

    module_similarity = [(e, sum(similarity[e, module] * score for module, score in votes.items())) for e in
                         range(len(module_data))]

    filtered_module_similarity = [m for m in module_similarity if m[1] > min_sim and m[0] not in votes]

    recommended = sorted(filtered_module_similarity, key=lambda x: x[1], reverse=True)

    if return_similarity:
        return recommended[:n]

    return [m[0] for m in recommended[:n]]


def collaborative_recommend_modules(user, n=5, min_sim=0, return_similarity=False):
    """
    :param min_sim: minimum absolute similarity to be included in result
    :param return_similarity: boolean flag whether result should include similarity
    :return: n modules recommended to user based on their collaborative similarity
    """
    if return_similarity:
        return model.recommend(user_to_id[user], user_items)[:n]
    return [m[0] for m in model.recommend(user_to_id[user], user_items)[:n]]


def recommend_modules(user, n=5, min_sim=0):
    """
    :param min_sim: minimum absolute similarity to be included in result
    :return: n modules recommended to user based on their hybrid similarity
    """
    vote_count = Vote.objects.count()

    content_results = content_recommend_modules(user, n=n, min_sim=min_sim, return_similarity=True)
    collaborative_results = collaborative_recommend_modules(user, n=n, min_sim=min_sim, return_similarity=True)

    return [module[0] for module in combine_similarities(content_results,
                                                         collaborative_results,
                                                         list2_to_list1_ratio=RECOMMENDATION_RATIO)[:n]]


def update_model():
    """
    Updates the internal model used to calculate collaborative recommendations and similarities.
    """
    # task = asyncio.create_task(async_update_model())
    thread = threading.Thread(target=async_update_model)
    thread.start()


def async_update_model():
    """
    Helper method for updating the model asynchronously. Never should be called since it causes backend downtime.
    Call update_model() to run this in a separate thread.
    """

    global model, user_items, user_to_id

    try:
        users = User.objects.all()
        user_to_id = {user: index for index, user in enumerate(users)}

        modules_count = len(module_data)
        users_count = users.count()

        item_user = csr_matrix((modules_count, users_count))

        for vote in Vote.objects.all():
            # print(module_nr_map[vote.module][1], user_to_id[vote.user], vote.score)
            item_user[module_nr_map[vote.module][1], user_to_id[vote.user]] = vote.score

        model = implicit.als.AlternatingLeastSquares()

        model.fit(item_user, show_progress=False)

        user_items = item_user.T.tocsr()
    except:
        print('(ERROR) Failed generating similarity. May be ignored if database is being set up. (fix in future @lenny)')


async_update_model()  # initializes model synchronously to postpone requests until after model has been generated.
