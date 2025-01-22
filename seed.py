from app import app, db
from models.users_model import UserModel
from models.content_model import ContentModel
from models.carousel_model import CarouselModel

with app.app_context():

    try:
        print("connected")
        db.drop_all()
        db.create_all()

        Florent = UserModel(
            firstname="Florent",
            lastname="Giovannone",
            username="flo",
            email="f.giovannone@me.com",
            password="Hello123",
            password_confirmation="Hello123",
            image=""
        )

        db.session.add(Florent)
        db.session.commit()

        Content = ContentModel(
            about_title="Welcome to Chez Flo",
            about_text="A luxury brasserie where culinary artistry meets refined elegance. We craft a unique dining experience by blending classic techniques with modern innovation, using only the finest seasonal ingredients. Whether for an intimate evening or a celebratory feast, our impeccable service and sophisticated ambiance promise to elevate every moment. At Chez Flo, dining is more than a meal—it’s a journey of flavors, atmosphere, and unforgettable memories.",
            breakfast_menus_text="Breakfast",
            breakfast_menus_file="https://res.cloudinary.com/ded4jhx7i/image/upload/f_auto,q_auto/v1/Menus/breakfast",
            lunch_menus_text="Lunch & Dinner",
            lunch_menus_file="https://res.cloudinary.com/ded4jhx7i/image/upload/f_auto,q_auto/v1/Menus/all%20day",
            dessert_menus_text="Desserts",
            dessert_menus_file="https://res.cloudinary.com/ded4jhx7i/image/upload/f_auto,q_auto/v1/Menus/desserts",
            winelist_menus_text="Winelist",
            winelist_menus_file="https://res.cloudinary.com/ded4jhx7i/image/upload/f_auto,q_auto/v1/Menus/winelist",
            cocktail_menus_text="Cocktail List",
            cocktail_menus_file="https://res.cloudinary.com/ded4jhx7i/image/upload/f_auto,q_auto/cocktail%20menu",
            image_one="https://images.unsplash.com/photo-1432462770865-65b70566d673?ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&amp;ixlib=rb-1.2.1&amp;auto=format&amp;fit=crop&amp;w=1950&amp;q=80",
            image_two="https://images.unsplash.com/photo-1629367494173-c78a56567877?ixlib=rb-4.0.3&amp;ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&amp;auto=format&amp;fit=crop&amp;w=927&amp;q=80",
            image_three="https://images.unsplash.com/photo-1493246507139-91e8fad9978e?ixlib=rb-4.0.3&amp;ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&amp;auto=format&amp;fit=crop&amp;w=2940&amp;q=80",
            image_four="https://images.unsplash.com/photo-1552960562-daf630e9278b?ixlib=rb-4.0.3&amp;ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&amp;auto=format&amp;fit=crop&amp;w=687&amp;q=80",
            image_five="https://images.unsplash.com/photo-1540553016722-983e48a2cd10?ixlib=rb-1.2.1&amp;ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&amp;auto=format&amp;fit=crop&amp;w=800&amp;q=80",
            image_six="https://docs.material-tailwind.com/img/team-3.jpg",
            reservation_title="Make a reservation",
            reservation_text="We have outdoor seating available between noon and 4pm, which can be booked, or requested on arrival.",
            breakfast_timing_day_one="Monday-Friday",
            breakfast_timing_hours_one="07.30-11.00",
            breakfast_timing_day_two="Saturday-Sunday",
            breakfast_timing_hours_two="08.00-11.00",
            lunch_timing_day_one="Monday-Saturday",
            lunch_timing_hours_one="11.45-16.45",
            lunch_timing_day_two="Sunday",
            lunch_timing_hours_two="11.45-17.45",
            dinner_timing_day_one="Monday-Saturday",
            dinner_timing_hours_one="17.00-22.15 (last reservation at 22.00)",
            dinner_timing_day_two="Sunday",
            dinner_timing_hours_two="Lunch menu will be available until 19.00 (last reservation at 17.00)",
            reservation_line_one="No availability for your required number of guests?",
            reservation_line_two="Call us to discuss your booking.",
            phone="+44 222 3333 4444",
            email="reservations@chezflo.com",
            contact_title="In the heart of Southfield",
            contact_adress_one="139 Beaumont Road",
            contact_adress_two="London, SW19 6RY",
            contact_opening_day_one="Monday-Friday",
            contact_opening_hours_one="07:30-23:00",
            contact_opening_day_two="Saturday",
            contact_opening_hours_two="08:00-23:00",
            contact_opening_day_three="Sunday",
            contact_opening_hours_three="08:00-18:00",
            map="https://res.cloudinary.com/ded4jhx7i/image/upload/v1737487297/lpgcoxaeygtmizk1ac3z.png",
        )
        db.session.add(Content)
        db.session.commit()

        Carousel_one = CarouselModel(
            carousel_url="https://media.houseandgarden.co.uk/photos/6548bac4ae920bdd9a97b4d2/16:9/w_2580,c_limit/Restaurant%20Interior%20(Credit%20Ben%20Carpenter).jpg",
            content=Content,
        )
        Carousel_two = CarouselModel(
            carousel_url="https://www.thisisamber.co.uk/wp-content/uploads/2018/02/160-amb-23-2r-203-1-1600x708.jpg",
            content=Content,
        )
        Carousel_three = CarouselModel(
            carousel_url="https://www.claridges.co.uk/siteassets/restaurants--bars/claridges-restaurant/new-2023/claridges-restaurant-hero-1920_720.jpg",
            content=Content,
        )

        db.session.add(Carousel_one)
        db.session.add(Carousel_two)
        db.session.add(Carousel_three)
        db.session.commit()

        db.session.commit()
        print("seeded!")

    except Exception as e:
        print(e)
