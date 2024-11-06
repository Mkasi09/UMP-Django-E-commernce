This is a Django-based e-commerce application that provides a seamless shopping experience with features like discounts, product recommendations, reviews, and an advanced tracking system for orders.

## Features

- **User Authentication**: Secure login with email and password, allowing users to create and manage their accounts.
- **User Profile**: Users can view and edit their profile details.
- **Shopping Cart**: Add, view, and manage products in the cart with real-time updates.
- **Wishlist**: Save favorite items for future purchases.
- **Product Discount**: Display accurate discounts based on user type (e.g., student or staff).
- **Product & Vendor Pages**: Detailed pages for products and vendors, displaying relevant information and reviews.
- **Product Details & Vendor Details**: Detailed information for each product and vendor.
- **Tags**: Tags for products and blog posts to improve discoverability.
- **Category List Page**: Organized categories to help users navigate the product catalog.
- **Admin Panel**: Enhanced admin dashboard for managing users, products, categories, tags, discounts, and reviews.
- **Product Reviews**: Users can leave reviews for products, which helps other users make informed decisions.
- **Blog Post Comments**: Comment functionality on blog posts for user interaction.
- **Product Filters**: Filter products by category, tags, price, and other attributes for easier navigation.
- **Search Functionality**: Powerful search to help users find products or blog posts quickly.
- **Related Products**: Display similar products based on category and tags to increase user engagement.
- **Order Tracking System**: Real-time order tracking feature for users to monitor the status of their purchases from placement to delivery.

## Tech Stack

- **Backend**: Django
- **Database**: SQLite
- **Payment Integration**: PayFast (test mode available)
- **Frontend**: HTML, CSS, JavaScript (with Django templates)

## Getting Started

### Prerequisites

- **Python**: Version 3.8 or higher
- **Django**: Version 3.x or higher
- **Virtual Environment**: Recommended
- **SQLite**: Default Django database
- **PayFast credentials**: Passphrase for test mode: `gistoss756fcgc`

### Installation

1. **Clone the Repository**:
   - ```bash
     git clone https://github.com/Mkasi09/UMP-Django-E-commernce.git
     cd ecommerce-app
     ```

2. **Create and Activate a Virtual Environment**:
   - ```bash
     python3 -m venv venv
     source venv/bin/activate  # On Windows use `venv\Scripts\activate`
     ```

3. **Install Dependencies**:
   - ```bash
     pip install -r requirements.txt
     ```

4. **Apply Migrations**:
   - ```bash
     python manage.py migrate
     ```

5. **Create a Superuser**:
   - ```bash
     python manage.py createsuperuser
     ```

6. **Run the Development Server**:
   - ```bash
     python manage.py runserver
     ```

7. **Access the Application**:
   - **Main Site**: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
   - **Admin Panel**: [http://127.0.0.1:8000/admin](http://127.0.0.1:8000/admin)

## Configuration

### PayFast Payment Integration

- To test PayFast payments:
  - **Enable Test Mode** in `settings.py`:
    - ```python
      PAYFAST_MODE = 'test'
      PAYFAST_PASSPHRASE = 'gistoss756fcgc'
      ```
  - **Set Up PayFast Account**: Ensure you have PayFast test credentials in your `.env` file.

### Order Tracking System

- The order tracking system allows users to monitor their orders through various stages, such as:
  - **Order Placed**: Confirmation that the order has been successfully placed.
  - **Processing**: The order is being prepared for shipment.
  - **Shipped**: The order has been shipped and is on its way.
  - **Delivered**: The order has reached its final destination.
- Each stage of the order status is visible in the user's profile, providing a clear view of their purchase journey.

## Database Structure

- **Users**: Email, password, user_type (`Student No.` for students and `Staff No.` for staff)
- **Products**: Name, description, price, discount rate, tags, categories
- **Orders**: Managed through the admin interface and includes tracking status
- **Reviews**: User-submitted reviews for products
- **Blogs and Comments**: Blog posts and associated user comments

## Testing

- To test the application, run:
  - ```bash
    python manage.py test
    ```

## License

- This project is licensed under the MIT License.
