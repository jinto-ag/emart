# emart

This is a django based e-commerce website.
development in progress

## Managing Environment Variables

- Create .env file in emart/ folder
- Add following variables

`

  # Django secret key here
  SECRET_KEY='django-secret-key here'

  # Email Integration
  EMAIL_HOST="smtp.gmail.com"
  EMAIL_PORT=587
  EMAIL_HOST_USER="username_here@gmail.com"
  EMAIL_HOST_PASSWORD="Password"

  # Razorpay Integration
  RAZORPAY_KEY_ID=
  RAZORPAY_KEY_SECRET=

  # Google recaptcha
  GOOGLE_RECAPTCHA_SITE_KEY=
  GOOGLE_RECAPTCHA_SECRET_KEY=

  # Google API KEY
  GOOGLE_API_KEY=

  # Social media Integration
  # Google
  GOOGLE_CLIENT_ID=
  GOOGLE_CLIENT_SECRET=

`
## Getting Started

- Clone the repository by running git clone https://github.com/<username>/emart.git
- Create a virtual environment by running python -m venv env
- Activate the virtual environment by running source env/bin/activate on Linux or env\Scripts\activate on Windows
- Install the requirements by running pip install -r requirements.txt
- Run the server by running python manage.py runserver
- Go to http://localhost:8000 in your browser to view the website

## Features

- Product listing and filtering
- Shopping cart functionality
- Checkout and payment integration with Razorpay
- User authentication and authorization
- Email integration for password reset and order confirmation
- Google reCAPTCHA integration for form submission
- Google Maps integration for displaying store locations
- Social media login integration with Google

## Deployment

The application can be deployed on a web server such as Apache or Nginx using mod_wsgi or gunicorn. It can also be deployed on a platform like Heroku or AWS Elastic Beanstalk. Make sure to set the environment variables in the server as well.

## Contribution

We welcome contributions to this project. If you would like to contribute, please follow the guidelines in the CONTRIBUTING.md file.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Acknowledgments

- Django - The web framework used
- Razorpay - Payment gateway integration
- Google reCAPTCHA - Form submission protection
- Google Maps - Store location display
- Bootstrap - CSS framework
- jQuery - JavaScript library
