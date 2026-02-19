from app import create_app, db
from app.models import Doctor

app = create_app()

def seed_doctors():
    with app.app_context():
        # Check if doctors exist
        if Doctor.query.first():
            print("Doctors already exist.")
            return

        doctors_data = [
            {
                "name": "Sarah Jenkins",
                "specialization": "Cardiologist",
                "experience": "12 Years",
                "hospital": "City Heart Institute",
                "contact": "+1-555-0123",
                "image": "https://randomuser.me/api/portraits/women/1.jpg"
            },
            {
                "name": "Michael Chen",
                "specialization": "Endocrinologist",
                "experience": "8 Years",
                "hospital": "Metabolic Health Center",
                "contact": "+1-555-0124",
                "image": "https://randomuser.me/api/portraits/men/2.jpg"
            },
            {
                "name": "Emily Sharma",
                "specialization": "General Physician",
                "experience": "15 Years",
                "hospital": "Community Wellness Clinic",
                "contact": "+1-555-0125",
                "image": "https://randomuser.me/api/portraits/women/3.jpg"
            },
             {
                "name": "David Ross",
                "specialization": "Cardiologist",
                "experience": "20 Years",
                "hospital": "St. Mary's Hospital",
                "contact": "+1-555-0126",
                "image": "https://randomuser.me/api/portraits/men/4.jpg"
            },
             {
                "name": "Anita Patel",
                "specialization": "Diabetologist",
                "experience": "10 Years",
                "hospital": "Sugar Care Clinic",
                "contact": "+1-555-0127",
                "image": "https://randomuser.me/api/portraits/women/5.jpg"
            }
        ]

        for data in doctors_data:
            doctor = Doctor(**data)
            db.session.add(doctor)
        
        db.session.commit()
        print("Mock doctors seeded successfully!")

if __name__ == "__main__":
    seed_doctors()
