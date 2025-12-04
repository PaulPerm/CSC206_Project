class TransactionQueries:

    GET_CUSTOMERS = """
        SELECT customerID, first_name, last_name
        FROM customers
        ORDER BY last_name;

    """

    ADD_PURCHASE = """
        INSERT INTO purchasetransactions
            (vehicleID, customerID, userID, purchase_date, purchase_price, vehicle_condition)
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

    def insert_purchase(self):
        return self.ADD_PURCHASE

    def insert_sale(self):
        return self.ADD_SALE

    def vehicle_check(self):
        return self.VEHICLE_EXISTS
