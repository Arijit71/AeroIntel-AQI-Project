#Linear Regression

# from sklearn.linear_model import LinearRegression


# def train_linear_regression(X_train, y_train):

#     model = LinearRegression()

#     model.fit(X_train, y_train)

#     return model

#Random Forest
from sklearn.ensemble import RandomForestRegressor


def train_random_forest(X_train, y_train):

    model = RandomForestRegressor(
        n_estimators=100,
        random_state=42
    )

    model.fit(X_train, y_train)

    return model

#Gradient Boosting

# from sklearn.ensemble import GradientBoostingRegressor


# def train_gradient_boosting(X_train, y_train):
#     """
#     Train a Gradient Boosting Regression model.
#     """

#     model = GradientBoostingRegressor(
#         n_estimators=100,
#         learning_rate=0.1,
#         random_state=42
#     )

#     model.fit(X_train, y_train)

#     return model


#Decision Tree

# from sklearn.tree import DecisionTreeRegressor


# def train_decision_tree(X_train, y_train):
#     """
#     Train a Decision Tree Regression model.
#     """

#     model = DecisionTreeRegressor(
#         random_state=42
#     )

#     model.fit(X_train, y_train)

#     return model