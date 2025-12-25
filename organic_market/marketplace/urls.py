from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about_us, name='about_us'),
    path('contact/', views.contact_us, name='contact_us'),
    # Products
    path('products/', views.products_list, name='products_list'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('product/<int:pk>/rate/', views.rate_product, name='rate_product'),


    # Auth
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),

    # Cart & Checkout
    path('cart/', views.cart_view, name='cart'),
    
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),

    path('update-cart/<int:item_id>/', views.update_cart, name='update_cart'),
    path('remove-cart/<int:item_id>/', views.remove_cart, name='remove_cart'),
    path('checkout/', views.checkout, name='checkout'),

    # Orders
    
    path('order-success/', views.order_success, name='order_success'),
    path('orders/', views.orders_view, name='orders'),
    path('order/<int:pk>/', views.order_detail, name='order_detail'),

    # Rating
    path('rate/<int:pk>/', views.rate_product, name='rate_product'),

    # Farmer
    path('farmer/dashboard/', views.farmer_dashboard, name='farmer_dashboard'),
    path('farmer/products/', views.list_products, name='list_products'),
    path('farmer/product/add/', views.add_product, name='add_product'),
    path('farmer/product/edit/<int:pk>/', views.edit_product, name='edit_product'),
    path('farmer/product/delete/<int:pk>/', views.delete_product, name='delete_product'),
    path('farmer/product/update-stock/<int:pk>/', views.update_stock, name='update_stock'),
    path('farmer/track-orders/', views.track_orders, name='track_orders'),
    path('farmer/queries/', views.customer_queries, name='customer_queries'),
    path('farmer/query/respond/<int:pk>/', views.respond_query, name='respond_query'),

    # Admin
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/farmers/', views.manage_farmers, name='manage_farmers'),
    path('admin/customers/', views.manage_customers, name='manage_customers'),
    path('admin/approve-products/', views.approve_products, name='approve_products'),
    path('admin/reports/', views.reports, name='reports'),
    path('admin/categories/', views.categories_view, name='categories'),
    path('admin/categories/delete/<int:pk>/', views.delete_category, name='delete_category'),
    path('admin/user/toggle/<int:user_id>/', views.admin_toggle_user, name='admin_toggle_user'),
    path('admin/user/delete/<int:user_id>/', views.admin_delete_user, name='admin_delete_user'),
    path('admin/farmer/<int:farmer_id>/products/', views.admin_farmer_products, name='admin_farmer_products'),

    # Customer
    path('admin/customers/', views.manage_customers, name='manage_customers'),
    path('admin/customer/<int:customer_id>/orders/', views.admin_customer_orders, name='admin_customer_orders'),
    path('admin/customer/<int:customer_id>/toggle/', views.admin_toggle_customer, name='admin_toggle_customer'),

    path('customer/dashboard/', views.customer_dashboard, name='customer_dashboard'),

    path('farmer/queries/', views.farmer_queries, name='farmer_queries'),
    path('submit_query/<int:pk>/', views.submit_query, name='submit_query'),
    path('farmer/queries/', views.customer_queries, name='farmer_queries'),



     path('farmer/query/respond/<int:query_id>/', views.respond_query, name='respond_query'),



  
 
]
