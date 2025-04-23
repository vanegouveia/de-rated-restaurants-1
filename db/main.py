from fastapi import FastAPI
from db.connection import connect_to_db, close_db_connection
from pydantic import BaseModel

app = FastAPI()

@app.get("/api")
def get_api():
    return {"message": "all ok"}


# @app.get("/api/restaurants")
# def get_api_restaurants():
#     conn = connect_to_db()
#     restaurants_data = conn.run("""
#     SELECT * FROM restaurants;
# """)
#     restaurants_data = conn.run("""
#     SELECT restaurants.restaurant_id, restaurants.restaurant_name, areas.area_name, restaurants.cuisine, restaurants.website
#     FROM restaurants
#     JOIN areas ON restaurants.area_id = areas.area_id;
# """)

    # restaurants = []

    # for restaurant in restaurants_data:
    #     restaurant_id, restaurant_name, area_id, cuisine, website = restaurant
    #     restaurants.append(
    #         {
    #             "restaurant_id": restaurant_id,
    #             "restaurant_name": restaurant_name,
    #             "area_id": area_id,
    #             "cuisine": cuisine,
    #             "website": website
    #         }
    #     )
    # close_db_connection(conn)
    # return {"restaurants": restaurants}

class Restaurant(BaseModel):
    restaurant_id: int | None = None
    restaurant_name: str
    area_id: int
    cuisine: str
    website: str

@app.post("/api/restaurants", status_code=201)
def create_restaurant(restaurant: Restaurant):
    conn = connect_to_db()
    query = """
    INSERT INTO restaurants 
    (restaurant_name, area_id, cuisine, website) 
    VALUES 
    (:restaurant_name, :area_id, :cuisine, :website)
    RETURNING *;"""

    db_response = conn.run(
        query, 
        restaurant_name=restaurant.restaurant_name,
        area_id=restaurant.area_id,
        cuisine=restaurant.cuisine,
        website=restaurant.website
)
    restaurant_id, restaurant_name, area_id, cuisine, website = db_response[0]

    new_restaurant = {
        "restaurant_id": restaurant_id,
        "restaurant_name": restaurant_name,
        "area_id": area_id,
        "cuisine": cuisine,
        "website": website
    }

    close_db_connection(conn)
    return {"restaurant": new_restaurant}

@app.delete("/api/restaurants/{restaurant_id}", status_code=204)
def delete_restaurant(restaurant_id: int):
    conn = connect_to_db()
    conn.run(
        "DELETE FROM restaurants WHERE restaurant_id = :id;", 
        id=restaurant_id
    )
    close_db_connection(conn)
    return 


class RestaurantPatch(BaseModel):
    restaurant_id: int | None = None
    restaurant_name: str | None = None
    area_id: int
    cuisine: str | None = None
    website: str | None = None

@app.patch("/api/restaurants/{restaurant_id}")
def update_area_id_field(restaurant_id: int, restaurant: RestaurantPatch):
    conn = connect_to_db()

    query = """
            UPDATE restaurants
            SET area_id = :area_id
            WHERE restaurant_id = :restaurant_id
            RETURNING *;
        """

    db_response = conn.run(
        query,
        restaurant_id=restaurant_id,
        area_id=restaurant.area_id
    )

    restaurant_id, restaurant_name, area_id, cuisine, website = db_response[0]

    updated_restaurant = {
        "restaurant_id": restaurant_id,
        "restaurant_name": restaurant_name,
        "area_id": area_id,
        "cuisine": cuisine,
        "website": website
    }
    close_db_connection(conn)
    return {"restaurant": updated_restaurant}

@app.get("/api/areas/{area_id}/restaurants")
def get_api_areas(area_id: int):
    conn = connect_to_db()

    area_query = "SELECT * FROM areas WHERE area_id = :area_id"
    area_data = conn.run(area_query, area_id=area_id)
    area_id, area_name = area_data[0]


    count_query = "SELECT COUNT(*) FROM restaurants WHERE area_id = :area_id"
    count_data = conn.run(count_query, area_id=area_id)
    total_restaurants = count_data[0][0] 

    restaurants_query = """
        SELECT restaurant_id, restaurant_name, cuisine, website
        FROM restaurants
        WHERE area_id = :area_id
    """
    restaurants_data = conn.run(restaurants_query, area_id=area_id)

    restaurants = [
        {
            "restaurant_id": restaurant[0],
            "restaurant_name": restaurant[1],
            "area_id": area_id,
            "cuisine": restaurant[2],
            "website": restaurant[3]
        } for restaurant in restaurants_data
    ]

    area_dict = {
            "area_id": area_id,
            "name": area_name,
            "total_restaurants": total_restaurants,
            "restaurants": restaurants
        }
    
    close_db_connection(conn)
    return {"area": area_dict}


# Update the existing endpoint so that each restaurant dict has an average_rating property.
@app.get("/api/restaurants")
def get_api_restaurants():
    conn = connect_to_db()
    query = """
        SELECT restaurants.restaurant_id, restaurants.restaurant_name, restaurants.area_id, restaurants.cuisine, restaurants.website, AVG(ratings.rating) AS average_rating
        FROM restaurants 
        LEFT JOIN ratings ON restaurants.restaurant_id = ratings.restaurant_id
        GROUP BY restaurants.restaurant_id;
    """
    
    restaurants_data = conn.run(query)
    
    restaurants = []

    for restaurant in restaurants_data:
        restaurant_id, restaurant_name, area_id, cuisine, website, average_rating = restaurant
        restaurants.append(
            {
                "restaurant_id": restaurant_id,
                "restaurant_name": restaurant_name,
                "area_id": area_id,
                "cuisine": cuisine,
                "website": website,
                "average_rating": average_rating  
            }
        )

    close_db_connection(conn)
    return {"restaurants": restaurants}