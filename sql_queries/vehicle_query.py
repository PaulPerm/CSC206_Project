class Vehicles:
    VEHICLE_LIST_QUERY = """
        SELECT 
            v.vehicleID,
            v.vin,
            vt.vehicle_type_name,
            v.model_year,
            m.manufacturer_name,
            v.model_name,
            v.fuel_type,
            GROUP_CONCAT(DISTINCT c.color_name ORDER BY c.color_name SEPARATOR ', ') AS colors,
            ROUND(pt.purchase_price * 1.4 + IFNULL(SUM(p.cost * p.quantity) * 1.2, 0), 2) AS sales_price
        FROM vehicles v
        JOIN purchasetransactions pt ON pt.vehicleID = v.vehicleID
        JOIN manufacturers m ON v.manufacturerID = m.manufacturerID
        JOIN vehicletypes vt ON v.vehicle_typeID = vt.vehicle_typeID
        LEFT JOIN vehiclecolors vc ON v.vehicleID = vc.vehicleID
        LEFT JOIN colors c ON vc.colorID = c.colorID
        LEFT JOIN partorders po ON po.vehicleID = v.vehicleID
        LEFT JOIN parts p 
            ON p.part_orderID = po.part_orderID 
           AND p.status = 'Installed'
        WHERE NOT EXISTS (
            SELECT 1 
            FROM salestransactions st
            WHERE st.vehicleID = v.vehicleID
        )
        AND NOT EXISTS (
            SELECT 1
            FROM partorders po2
            JOIN parts p2 ON p2.part_orderID = po2.part_orderID
            WHERE po2.vehicleID = v.vehicleID
              AND p2.status <> 'Installed'
        )
        GROUP BY 
            v.vehicleID,
            v.vin,
            vt.vehicle_type_name,
            v.model_year,
            m.manufacturer_name,
            v.model_name,
            v.fuel_type,
            pt.purchase_price
        ORDER BY 
            v.model_year DESC,
            m.manufacturer_name ASC;
    """
