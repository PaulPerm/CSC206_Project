class TransactionQueries:

    GET_CUSTOMERS = """
        SELECT customerID, first_name, last_name
        FROM customers
        ORDER BY last_name;
    """

    # vehicles table has:
    # vin, mileage, description, model_name, model_year, fuel_type, manufacturerID, vehicle_typeID
    ADD_VEHICLE = """
        INSERT INTO vehicles
            (vin, mileage, description, model_name, model_year, fuel_type, manufacturerID, vehicle_typeID)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
    """

    # purchasetransactions is:
    # (purchase_transactionID, vehicleID, userID, customerID, purchase_price, purchase_date, vehicle_condition)
    ADD_PURCHASE = """
        INSERT INTO purchasetransactions
            (vehicleID, userID, customerID, purchase_price, purchase_date, vehicle_condition)
        VALUES (%s, %s, %s, %s, %s, %s);
    """

    ADD_SALE = """
        INSERT INTO salestransactions
            (vehicleID, customerID, userID, sales_date)
        VALUES (%s, %s, %s, %s);
    """

    VEHICLE_EXISTS = """
        SELECT vehicleID
        FROM vehicles
        WHERE vehicleID = %s;
    """

    def customer_list(self):
        return self.GET_CUSTOMERS

    def insert_vehicle(self):
        return self.ADD_VEHICLE

    def insert_purchase(self):
        return self.ADD_PURCHASE

    def insert_sale(self):
        return self.ADD_SALE

    def vehicle_check(self):
        return self.VEHICLE_EXISTS
