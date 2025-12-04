class Vehicles:

    VEHICLE_LIST_QUERY = '''
    SELECT
        v.vehicleID,
        v.vin,
        vt.vehicle_type_name,
        v.model_year,
        m.manufacturer_name,
        v.model_name,
        v.fuel_type,
        GROUP_CONCAT(c.color_name SEPARATOR ', ') AS colors,
        pt.purchase_price * 1.4 AS sales_price
    FROM vehicles v
    LEFT JOIN purchasetransactions pt ON pt.vehicleID = v.vehicleID
    JOIN manufacturers m ON v.manufacturerID = m.manufacturerID
    JOIN vehicletypes vt ON v.vehicle_typeID = vt.vehicle_typeID
    LEFT JOIN vehiclecolors vc ON vc.vehicleID = v.vehicleID
    LEFT JOIN colors c ON vc.colorID = c.colorID
    WHERE NOT EXISTS (
        SELECT 1 
        FROM salestransactions st
        WHERE st.vehicleID = v.vehicleID
    )
    GROUP BY v.vehicleID
    ORDER BY v.model_year DESC, m.manufacturer_name ASC;
    '''

    ALL_VEHICLES_QUERY = '''
    SELECT 
        v.vehicleID,
        v.vin,
        vt.vehicle_type_name,
        v.model_year,
        m.manufacturer_name,
        v.model_name,
        v.fuel_type,
        GROUP_CONCAT(c.color_name SEPARATOR ', ') AS colors,
        (pt.purchase_price * 1.4) AS sales_price
    FROM vehicles v
        LEFT JOIN purchasetransactions pt ON pt.vehicleID = v.vehicleID
        LEFT JOIN vehiclecolors vc ON vc.vehicleID = v.vehicleID
        LEFT JOIN colors c ON c.colorID = vc.colorID
        JOIN manufacturers m ON v.manufacturerID = m.manufacturerID
        JOIN vehicletypes vt ON v.vehicle_typeID = vt.vehicle_typeID
    GROUP BY v.vehicleID;
    '''

    VEHICLE_DETAILS_QUERY = '''
    SELECT 
        v.vehicleID,
        v.vin,
        vt.vehicle_type_name,
        v.model_year,
        m.manufacturer_name,
        v.model_name,
        v.fuel_type,
        GROUP_CONCAT(c.color_name SEPARATOR ',') AS colors,
        v.description
    FROM vehicles v
        JOIN manufacturers m ON v.manufacturerID = m.manufacturerID
        JOIN vehicletypes vt ON v.vehicle_typeID = vt.vehicle_typeID
        LEFT JOIN vehiclecolors vc ON vc.vehicleID = v.vehicleID
        LEFT JOIN colors c ON c.colorID = vc.colorID
    WHERE v.vehicleID = %s
    GROUP BY v.vehicleID;
    '''

    VEHICLE_PARTS_QUERY = '''
    SELECT 
        p.part_number,
        p.description,
        p.cost,
        p.quantity,
        p.status,
        p.part_orderID
    FROM partorders po
        JOIN parts p ON p.part_orderID = po.part_orderID
    WHERE po.vehicleID = %s;
    '''

    VEHICLE_SELLER_QUERY = '''
    SELECT 
        c.first_name, 
        c.last_name,
        c.phone_number,
        c.email_address,
        c.street,
        c.city,
        c.state,
        c.postal_code
    FROM customers c
    WHERE c.customerID = (
        SELECT customerID
        FROM purchasetransactions
        WHERE vehicleID = %s
    );
    '''

    VEHICLE_BUYER_QUERY = '''
    SELECT 
        c.first_name, 
        c.last_name,
        c.phone_number,
        c.email_address,
        c.street,
        c.city,
        c.state,
        c.postal_code
    FROM customers c
    WHERE c.customerID = (
        SELECT customerID
        FROM salestransactions
        WHERE vehicleID = %s
    );
    '''

    def vehicle_list(self):
        return self.VEHICLE_LIST_QUERY

    def all_vehicles_list(self):
        return self.ALL_VEHICLES_QUERY
        
    def vehicle_details(self):
        return self.VEHICLE_DETAILS_QUERY
    
    def vehicle_parts(self):
        return self.VEHICLE_PARTS_QUERY

    def vehicle_seller(self):
        return self.VEHICLE_SELLER_QUERY

    def vehicle_buyer(self):
        return self.VEHICLE_BUYER_QUERY