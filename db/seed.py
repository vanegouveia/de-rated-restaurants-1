import asyncio
from connection import connect_to_db, close_db_connection
from dotenv import load_dotenv
import json

load_dotenv()


async def seed():
    conn = await connect_to_db()

    try:
        await conn.execute(
            "DROP TABLE IF EXISTS ratings;"
        )
        await conn.execute(
            "DROP TABLE IF EXISTS restaurants;"
        )
        await conn.execute(
            "DROP TABLE IF EXISTS areas;"
        )
        await conn.execute(
            "CREATE TABLE areas (\
        area_id SERIAL PRIMARY KEY,\
        area_name VARCHAR(40) NOT NULL\
        );"
        )
        await conn.execute(
            "CREATE TABLE restaurants (\
        restaurant_id SERIAL PRIMARY KEY,\
        restaurant_name VARCHAR(40) NOT NULL,\
        area_id INT REFERENCES areas(area_id),\
        cuisine VARCHAR(40),\
        website VARCHAR(40)\
        );"
        )
        await conn.execute(
            "CREATE TABLE ratings (\
        rating_id SERIAL PRIMARY KEY,\
        restaurant_id INT,\
        FOREIGN KEY (restaurant_id) REFERENCES restaurants(restaurant_id) ON DELETE CASCADE,\
        rating INT CHECK (rating >= 1 AND rating <= 5)\
        );"  # noqa
        )

        areas_path = "db/data/areas.json"
        with open(areas_path, "r") as file:
            data = json.load(file)
            rows = data["areas"]

        for row in rows:
            await conn.execute(
                "INSERT INTO areas (area_name) VALUES ($1)",
                row["area_name"],
            )

        restaurants_path = "db/data/restaurants.json"
        with open(restaurants_path, "r") as file:
            data = json.load(file)
            rows = data["restaurants"]

        for row in rows:
            rest_area_id = await conn.fetch(
                f"SELECT area_id FROM areas WHERE area_name = '{row['area_name']}'")  # noqa
            await conn.execute(
                "INSERT INTO restaurants (restaurant_name, area_id, cuisine, website) VALUES ($1, $2, $3, $4)",  # noqa
                row["restaurant_name"],
                dict(rest_area_id[0])['area_id'],  # noqa
                row["cuisine"],
                row["website"],
            )

        ratings_path = "db/data/ratings.json"
        with open(ratings_path, "r") as file:
            data = json.load(file)
            rows = data["ratings"]

        for row in rows:
            rest_name_id = await conn.fetch(
                f"SELECT restaurant_id FROM restaurants WHERE restaurant_name = '{row['restaurant_name']}'")  # noqa
            await conn.execute(
                "INSERT INTO ratings (restaurant_id, rating) VALUES ($1, $2)",
                dict(rest_name_id[0])['restaurant_id'],
                row["rating"]
            )

    finally:
        print("Seeding Complete.")
        await close_db_connection(conn)

asyncio.run(seed())
