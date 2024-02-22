# Management System for Store Operations
 
# The basic objectives of the project are:
    Implementation of web services that constitute the given system;
    Launching the system using container orchestration tools;

The system is intended for multi-user operation and therefore needs to be carefully designed to meet the requirements of correct and efficient operation. Part of the system's functionality is publicly available, while another part is provided only to users who can log in to the system.
The system is implemented using the Python programming language, Flask framework, and SQLAlchemy library. In addition to the code, Docker Image templates representing parts of the system that can be used to launch corresponding containers need to be provided. In addition to implementation, a configuration is written to enable the entire system to be launched using orchestration tools.

# Conceptual Description of the System
The system provide user registration (customer or courier). Customers can search and place orders. Couriers can deliver orders.
When the system is started, accounts for all store owners are provided in advance. Store owners can add products and view sales statistics.
Each user needs to be registered before using the system. The following information is stored within each user account: email address and password used for login, first name, last name, and user role. A user can have the role of a customer, a store owner, or a courier.
The following information is stored for products: the category to which the product belongs (there can be multiple categories), the name of the product, and its price. The product name is unique. The name of each category is stored.
Customers can search for products, place orders, and view placed orders.
An order is created in the system for each product purchase. The following information is kept for each order: a list of products, the total order price, its status, and the moment of its creation. Upon creation, the order is in the "pending" state until it is picked up by a courier, at which point it transitions to the "in transit" state. When the courier delivers the order to the customer, it transitions to the "completed" state.
