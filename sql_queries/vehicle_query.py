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
        c.color_name,
        pt.purchase_price * 1.4 AS sales_price
    FROM vehicles v
    JOIN purchasetransactions pt ON pt.vehicleID = v.vehicleID
    JOIN manufacturers m ON v.manufacturerID = m.manufacturerID
    JOIN vehicletypes vt ON v.vehicle_typeID = vt.vehicle_typeID
    LEFT JOIN vehiclecolors vc ON v.vehicleID = vc.vehicleID
    LEFT JOIN colors c ON vc.colorID = c.colorID
    WHERE NOT EXISTS (
        SELECT 1 FROM salestransactions st
        WHERE st.vehicleID = v.vehicleID
    )
    GROUP BY
        v.vehicleID,
        v.vin,
        vt.vehicle_type_name,
        v.model_year,
        m.manufacturer_name,
        v.model_name,
        v.fuel_type,
        pt.purchase_price,
        c.color_name
    ORDER BY
        v.model_year DESC,
        m.manufacturer_name ASC;
    '''

    def vehicle_list(self):
        return self.VEHICLE_LIST_QUERY
