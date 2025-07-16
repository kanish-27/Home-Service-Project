# 🏠 Home Service Admin Guide

## 🔐 Admin Access

**Admin Panel URL:** http://127.0.0.1:8000/admin/

**Login Credentials:**
- **Email:** admin@homeservice.com
- **Password:** admin123

---

## 🎯 Admin Features

### 1. 🛠️ **Manage Services**
**Location:** Admin Panel → Services → Services

**What you can do:**
- ✅ **Add New Services** - Create home services with Indian Rupee pricing
- ✅ **Edit Services** - Update service details, prices, descriptions
- ✅ **Enable/Disable Services** - Control service availability
- ✅ **View Service Statistics** - See booking counts per service

**Service Fields:**
- **Name:** Service title (e.g., "Electrical Installation")
- **Description:** Detailed service description
- **Category:** Service category (Electrical, Plumbing, etc.)
- **Provider:** Assigned service provider
- **Price:** Cost in Indian Rupees (₹)
- **Duration:** Service duration in hours
- **Status:** Active/Inactive, Available/Unavailable

### 2. 📋 **View All Bookings**
**Location:** Admin Panel → Services → Bookings

**What you can see:**
- ✅ **All Customer Bookings** - Complete booking history
- ✅ **Booking Details** - Customer info, service, date, status
- ✅ **Payment Status** - Paid/Unpaid status
- ✅ **Booking Management** - Update status, view details

**Booking Information:**
- **Booking ID:** Unique identifier (BK-000001)
- **Service:** Booked service name
- **Customer:** Customer name and email
- **Date:** Scheduled service date
- **Status:** Pending, Confirmed, Completed, Cancelled
- **Amount:** Total cost in Indian Rupees (₹)
- **Payment:** Payment status with visual indicators

### 3. 📂 **Manage Categories**
**Location:** Admin Panel → Services → Service Categories

**What you can do:**
- ✅ **Add Categories** - Create new service categories
- ✅ **Edit Categories** - Update category details
- ✅ **Organize Services** - Group services by category

**Default Categories:**
- 🔌 **Electrical** - Electrical installations and repairs
- 🚰 **Plumbing** - Plumbing services and repairs
- 🧹 **Cleaning** - Home and office cleaning services
- 🌱 **Gardening** - Garden maintenance and landscaping
- 🔧 **Home Repair** - General home repairs

### 4. 👥 **Manage Providers**
**Location:** Admin Panel → Services → Provider Profiles

**What you can do:**
- ✅ **View Providers** - See all registered service providers
- ✅ **Verify Providers** - Approve/verify provider accounts
- ✅ **Manage Availability** - Control provider availability
- ✅ **Provider Details** - Company info, contact details

### 5. ⭐ **View Reviews**
**Location:** Admin Panel → Services → Reviews

**What you can see:**
- ✅ **Customer Reviews** - All service reviews and ratings
- ✅ **Review Details** - Rating, comments, booking info
- ✅ **Quality Monitoring** - Track service quality

---

## 🚀 **Getting Started**

### Step 1: Login to Admin
1. Go to http://127.0.0.1:8000/admin/
2. Enter admin credentials
3. Click "Log in"

### Step 2: Add Service Categories
1. Go to **Services → Service Categories**
2. Click **"Add Service Category"**
3. Fill in category details
4. Save

### Step 3: Add Services
1. Go to **Services → Services**
2. Click **"Add Service"**
3. Fill in service details:
   - Name: "Electrical Installation"
   - Description: "Professional electrical services"
   - Category: Select from dropdown
   - Price: Enter amount in rupees (e.g., 2500)
   - Duration: Enter hours (e.g., 3:00:00 for 3 hours)
4. Save

### Step 4: Monitor Bookings
1. Go to **Services → Bookings**
2. View all customer bookings
3. Update booking status as needed
4. Monitor payment status

---

## 💰 **Currency Information**

All prices are displayed in **Indian Rupees (₹)**:
- Service prices: ₹1,000 - ₹5,000
- Booking amounts: Shown with ₹ symbol
- Payment tracking: In rupees

---

## 📊 **Admin Dashboard Features**

### Service Management
- **Add/Edit/Delete** services
- **Price management** in Indian Rupees
- **Service availability** control
- **Provider assignment**

### Booking Monitoring
- **Real-time booking** updates
- **Customer information** access
- **Payment status** tracking
- **Service scheduling** overview

### Provider Management
- **Provider verification** system
- **Service quality** monitoring
- **Provider availability** management

---

## 🎯 **Key Benefits**

1. **Complete Control** - Manage all home services from one place
2. **Real-time Monitoring** - See bookings as they happen
3. **Revenue Tracking** - Monitor earnings in Indian Rupees
4. **Quality Assurance** - Review customer feedback
5. **Provider Management** - Control service provider network

---

## 📞 **Support**

For admin support or questions:
- Check the Django admin documentation
- Review booking details for customer issues
- Monitor service quality through reviews

**Happy Managing! 🎉**
