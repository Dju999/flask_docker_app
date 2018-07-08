"""
    Модуль рекомемедательной системы
"""
import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.linalg import svds


class SVDRecsys:
    def __init__(self, postgres_db, mongo_db, redis_db):
        self.postgres_db = postgres_db
        self.mongo_db = mongo_db
        self.redis_db = redis_db

        self.user_index = None
        self.item_index = None
        self.inverse_user_index = None
        self.inverse_item_index = None
        self.num_users = None
        self.num_items = None
        self.ui_matrix = None
        self.user_factors = None
        self.item_factors = None

        self.init_ui_matrix()
        self.fit()
        self.save_data()

    def init_ui_matrix(self):
        # параметры SQL-запроса
        user_item_query_config = {
            "MIN_USERS_FOR_ITEM": 10,
            "MIN_ITEMS_FOR_USER": 3,
            "MAX_ITEMS_FOR_USER": 50,
            "MAX_ROW_NUMBER": 100000
        }
        sql_str = (
            """
                SELECT 
                    ratings.userId, ratings.movieId, AVG(ratings.rating) as rating
                FROM ratings
                -- фильтруем фильмы, которые редко оценивают
                INNER JOIN (
                    SELECT 
                        movieId, count(*) as users_per_item
                    FROM ratings 
                    GROUP BY movieId 
                    HAVING COUNT(*) > %(MIN_USERS_FOR_ITEM)d
                ) as movie_agg
                    ON movie_agg.movieId = ratings.movieId
                -- фильтруем пользователей, у которых мало рейтингов
                INNER JOIN (
                    SELECT 
                        userId, count(*) as items_per_user
                    FROM ratings 
                    GROUP BY userId 
                    HAVING COUNT(*) BETWEEN %(MIN_ITEMS_FOR_USER)d AND %(MAX_ITEMS_FOR_USER)d 
                ) as user_agg
                    ON user_agg.userId = ratings.userId
                GROUP BY 1,2
                LIMIT %(MAX_ROW_NUMBER)d
            """ % user_item_query_config
        )

        ui_data = self.postgres_db.run_sql_str(sql_str)

        self.user_index = {
            i[1]: i[0][0]
            for i in np.ndenumerate(np.unique([triplet[0] for triplet in ui_data]))
        }
        self.inverse_user_index = {j: i for i, j in self.user_index.items()}
        self.item_index = {
            i[1]: i[0][0]
            for i in np.ndenumerate(np.unique([triplet[1] for triplet in ui_data]))
        }
        self.inverse_item_index = {j: i for i, j in self.item_index.items()}

        raiting_list = [row[2] for row in ui_data]
        user_index_plain = [self.user_index[row[0]] for row in ui_data]
        item_index_plain = [self.item_index[row[1]] for row in ui_data]

        self.ui_matrix = coo_matrix((raiting_list, (user_index_plain, item_index_plain))).astype(np.float32)

    def fit(self):
        self.num_users, self.num_items = self.ui_matrix.shape
        user_factors, scale, item_factors = svds(self.ui_matrix.asfptype(), k=50, return_singular_vectors=True)
        # create square matrix
        scale = np.diag(np.sqrt(scale))
        self.user_factors = np.dot(user_factors, scale).astype(np.float32)
        self.item_factors = np.dot(scale, item_factors).astype(np.float32)

        print(user_factors.shape, item_factors.shape)

    def save_data(self):
        # внимание: модель уже обучена, поэтому переходим от внутреннего индекса к userId
        user_factors = {
            int(self.inverse_user_index[user_id]): self.user_factors[user_id, :]
            for user_id in range(self.num_users)
        }
        self.mongo_db.load_data("user", user_factors)
        self.redis_db.load_data("item_factors", self.item_factors)

    def get_recommendations(self, user_id, top):
        user_factors = self.mongo_db.get_data("user", user_id)
        item_factors = self.redis_db.get_data("item_factors")

        personal_recs = user_factors.reshape(1, -1).dot(item_factors)
        return [self.inverse_item_index[i] for i in np.argsort(-personal_recs[0])][:top]
