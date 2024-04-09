from connection import connect_to_db, close_db_connection
import json


def seed():
    conn = connect_to_db()

    try:
        conn.run(
            "DROP TABLE IF EXISTS ratings;"
        )
        conn.run(
            "DROP TABLE IF EXISTS restaurants;"
        )
        conn.run(
            "DROP TABLE IF EXISTS areas;"
        )
        conn.run(
            "CREATE TABLE areas (\
                area_id SERIAL PRIMARY KEY,\
                area_name VARCHAR(40) NOT NULL\
            );"
        )
        conn.run(
            "CREATE TABLE restaurants (\
                restaurant_id SERIAL PRIMARY KEY,\
                restaurant_name VARCHAR(40) NOT NULL,\
                area_id INT REFERENCES areas(area_id),\
                cuisine VARCHAR(40),\
                website VARCHAR(40)\
            );"
        )
        conn.run(
            "CREATE TABLE ratings (\
                rating_id SERIAL PRIMARY KEY,\
                restaurant_id INT,\
                FOREIGN KEY (restaurant_id) REFERENCES restaurants(restaurant_id) ON DELETE CASCADE,\
                rating INT CHECK (rating >= 1 AND rating <= 5)\
            );"
        )

        areas_path = "db/data/areas.json"
        with open(areas_path, "r") as file:
            data = json.load(file)
            rows = data["areas"]

        for row in rows:
            conn.run(
                "INSERT INTO areas (area_name) VALUES (:area_name)",
                area_name=row["area_name"],
            )

        restaurants_path = "db/data/restaurants.json"
        with open(restaurants_path, "r") as file:
            data = json.load(file)
            rows = data["restaurants"]

        for row in rows:
            rest_area_id = conn.run(
                "SELECT area_id FROM areas WHERE area_name = :area_name",
                area_name=row['area_name']
            )
            conn.run(
                "INSERT INTO restaurants \
                    (restaurant_name, area_id, cuisine, website) \
                VALUES \
                    (:restaurant_name, :area_id, :cuisine, :website);",
                restaurant_name=row["restaurant_name"],
                area_id=rest_area_id[0][0],
                cuisine=row["cuisine"],
                website=row["website"],
            )

        ratings_path = "db/data/ratings.json"
        with open(ratings_path, "r") as file:
            data = json.load(file)
            rows = data["ratings"]

        for row in rows:
            rest_name_id = conn.run(
                "SELECT restaurant_id FROM restaurants WHERE restaurant_name = :restaurant_name",
                restaurant_name=row['restaurant_name']    
            )
            conn.run(
                "INSERT INTO ratings (restaurant_id, rating) VALUES (:restaurant_id, :rating)",
                restaurant_id=rest_name_id[0][0],
                rating=row["rating"]
            )

    finally:
        print("Seeding Complete.")
        close_db_connection(conn)


seed()
