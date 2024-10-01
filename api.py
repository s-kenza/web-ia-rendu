from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.model_selection import train_test_split
from loguru import logger
import uvicorn
import numpy as np
import pandas as pd

app = FastAPI()


class PredictionPrice(BaseModel):
    accommodates: int
    cleaning_fee: bool
    instant_bookable: bool
    city: str


class PredictionCleaning(BaseModel):
    price_by_night: int
    city: str


model_lin = LinearRegression()
model_log = LogisticRegression()

is_models_trained = False
cities = {}

def prepare_city(city):
    match city:
        case 'NYC':
            return [1, 0, 0, 0, 0, 0]
        case 'DC':
            return [0, 1, 0, 0, 0, 0]
        case 'SF':
            return [0, 0, 1, 0, 0, 0]
        case 'LA':
            return [0, 0, 0, 1, 0, 0]
        case 'Chicago':
            return [0, 0, 0, 0, 1, 0]
        case 'Boston':
            return [0, 0, 0, 0, 0, 1]


@app.post("/train")
async def train():
    global is_models_trained

    df = pd.read_csv('./data/data.csv')
    df = df[['log_price', 'accommodates', 'cleaning_fee', 'city', 'instant_bookable']]

    df['cleaning_fee'] = df['cleaning_fee'].astype(int)
    df['instant_bookable'] = df['instant_bookable'].apply(lambda x: 1 if x == 'f' else 0)
    df['price_by_night'] = np.exp(df['log_price'])
    df = df.drop(labels='log_price', axis=1)
    cities = df['city'].unique()
    city = df['city']
    df = pd.get_dummies(df, columns=['city'], dtype=int)
    df['city'] = city

    averages = {}
    for city in cities:
        df_city = df[df['city'] == city]
        df_city['price_per_person'] = df_city['price_by_night'] / df_city['accommodates']
        average = df_city['price_per_person'].mean()
        averages[city] = average

    def categorize_price(row):
        price = row['price_by_night'] / row['accommodates']
        average = averages[row['city']]

        if price < average * 0.4:
            return 'little'
        elif price < average * 0.7:
            return 'low'
        elif price < average * 1.3:
            return 'normal'
        elif price < average * 1.7:
            return 'high'
        else:
            return 'scam'

    df['category'] = df.apply(categorize_price, axis=1)
    df = df[~df['category'].isin(['little', 'scam'])]

    lin_X = df[['accommodates', 'cleaning_fee', 'instant_bookable', 'city_NYC', 'city_DC', 'city_SF', 'city_LA', 'city_Chicago', 'city_Boston']]
    lin_y = df['price_by_night']
    log_X = df[['price_by_night', 'city_NYC', 'city_DC', 'city_SF', 'city_LA', 'city_Chicago', 'city_Boston']]
    log_y = df['cleaning_fee']

    lin_X_train, lin_X_test, lin_y_train, lin_y_test = train_test_split(
        lin_X, lin_y, test_size=0.2, random_state=42)
    log_X_train, log_X_test, log_y_train, log_y_test = train_test_split(
        log_X, log_y, test_size=0.2, random_state=42)

    model_lin.fit(lin_X_train, lin_y_train)
    model_log.fit(log_X_train, log_y_train)

    is_models_trained = True

    logger.info("Modèles entraîné avec succès.")
    logger.info(f"[LINEAR] Coefficients: {model_lin.coef_}, Intercept: {model_lin.intercept_}")
    logger.info(f"[LOGISTIC] Coefficients: {model_log.coef_}, Intercept: {model_log.intercept_}")

    return {"message": "Modèles entraînés avec succès."}


@app.post("/predict-price")
async def predict(data: PredictionPrice):
    global is_models_trained

    # Vérifier si le modèle a été entraîné
    if not is_models_trained:
        raise HTTPException(
            status_code=400, detail="Le modèle n'est pas encore entraîné. Veuillez entraîner le modèle d'abord.")

    data.cleaning_fee = 1 if data.cleaning_fee else 0
    data.instant_bookable = 1 if data.instant_bookable else 0
    cities = prepare_city(data.city)
    cities = [data.accommodates, data.cleaning_fee, data.instant_bookable] + cities
    X_new = np.array([cities,])

    # Prédire le prix
    predicted_price = model_lin.predict(X_new)[0]

    # Logging avec Loguru
    logger.info(f"Prédiction faite pour \naccommodates : {data.accommodates}\ncleaning_fee : {data.cleaning_fee}\ninstant_bookable : {data.instant_bookable}\ncity : {data.city}")
    logger.info(f"Prix prédit : {predicted_price}")

    return {"predicted_price": predicted_price}


@app.post("/predict-cleaning")
async def predict_category(data: PredictionCleaning):
    global is_models_trained

    # Vérifier si le modèle a été entraîné
    if not is_models_trained:
        raise HTTPException(
            status_code=400, detail="Le modèle n'est pas encore entraîné. Veuillez entraîner le modèle d'abord.")

    # Prédire si il y a des frais de ménage
    cities = prepare_city(data.city)
    cities.insert(0, data.price_by_night)
    X_new = np.array([cities,])
    predicted_cleaning = model_log.predict(X_new)
    predicted_cleaning = True if predicted_cleaning == [1] else False

    # Logging avec Loguru
    logger.info(f"Prédiction faite pour\n price : {data.price_by_night}\n city : {data.city}")
    logger.info(f"Frais de service existant prédit : {predicted_cleaning}")

    return {"cleaning": predicted_cleaning}


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=5000)
